// =============================================================================
// سكريبت المنصة الرقمية المعتمد - نظام الزيارات الميدانية لقسم الصيدلة
// الإصدار المصحح: 39 بنداً، حالة يوجد / لا يوجد، منع التكرار، وإيميل عربي باتجاه صحيح
// =============================================================================

var TEMPLATE_FILE_ID = "1QBq_OUsbNsc3lklC8_tvFAygRhlaT7MKZ6yMyiyLkNw";
var TARGET_FOLDER_ID = "1fxe6hGCG7TRZZ6aG7xQ_vTi-yQpD3hSD";
var RECIPIENT_EMAIL = "da720883@gmail.com";
var DEFAULT_TOTAL_ITEMS = 39;

function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({
    "status": "online",
    "message": "خدمة أتمتة تقارير الزيارات الميدانية متصلة وجاهزة بنسبة 100%."
  })).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(30000);
    var data = JSON.parse(e.postData.contents);

    var duplicateUrl = findRecentDuplicateUrl(data);
    if (duplicateUrl) {
      return ContentService.createTextOutput(JSON.stringify({
        "result": "success",
        "duplicate": true,
        "center_file_url": duplicateUrl
      })).setMimeType(ContentService.MimeType.JSON);
    }

    var centerFileUrl = createCustomCenterReport(data);

    var masterSs = SpreadsheetApp.openById(TEMPLATE_FILE_ID);
    var archiveSheet = masterSs.getSheetByName("الأرشيف");
    if (!archiveSheet) {
      archiveSheet = masterSs.insertSheet("الأرشيف");
    }
    archiveSheet.setRightToLeft(true);

    if (archiveSheet.getLastRow() === 0) {
      archiveSheet.appendRow([
        "تاريخ التسجيل",
        "اسم المركز الصحي",
        "اسم المفتش الميداني",
        "تاريخ التفتيش",
        "وقت التفتيش",
        "نسبة الامتثال %",
        "مطابق",
        "جزئي",
        "غير مطابق",
        "الملاحظات العامة",
        "ملخص نقاط الضعف والملاحظات",
        "رابط التقرير المعتمد",
        "معرف الطلب"
      ]);
      archiveSheet.getRange("A1:M1").setFontWeight("bold").setBackground("#1F4E79").setFontColor("#FFFFFF");
    }

    var readableWeakSummary = buildWeakSummary(data);
    var hyperlinkFormula = '=HYPERLINK("' + centerFileUrl + '", "عرض تقرير المركز 📄")';

    archiveSheet.appendRow([
      new Date(),
      data.center_name || "غير محدد",
      data.inspector_name || "غير محدد",
      data.inspection_date || "-",
      data.inspection_time || "-",
      (data.compliance_rate || "0") + "%",
      data.matched_cnt || 0,
      data.partial_cnt || 0,
      data.unmatched_cnt || 0,
      data.general_notes || "لا توجد ملاحظات",
      readableWeakSummary,
      hyperlinkFormula,
      data.request_id || ""
    ]);

    sendApprovedEmailReport(data, centerFileUrl);

    return ContentService.createTextOutput(JSON.stringify({
      "result": "success",
      "center_file_url": centerFileUrl
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      "result": "error",
      "message": error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  } finally {
    try {
      lock.releaseLock();
    } catch (lockError) {}
  }
}

function getTotalItems(data) {
  var total = parseInt(data.total_items, 10);
  return isNaN(total) || total <= 0 ? DEFAULT_TOTAL_ITEMS : total;
}

function isCompliantStatus(status) {
  return status === "مطابق" || status === "لا يوجد";
}

function isWeakStatus(status) {
  return !isCompliantStatus(status);
}

function formatItemNotes(item) {
  if (item.near_expiry_items && item.near_expiry_items.length > 0) {
    var lines = [];
    for (var n = 0; n < item.near_expiry_items.length; n++) {
      var nearItem = item.near_expiry_items[n];
      lines.push(
        (nearItem.slot || (n + 1)) + ". " +
        (nearItem.drug_name_strength || "-") +
        " — الكمية: " + (nearItem.quantity || "-") +
        " — تاريخ الانتهاء: " + (nearItem.expiry_date || "-")
      );
    }
    var extraNote = "";
    if (item.inspector_notes && String(item.inspector_notes).trim() !== "") {
      extraNote = String(item.inspector_notes).trim();
    } else if (item.notes && String(item.notes).indexOf("ملاحظات المُفتش:") !== -1) {
      extraNote = String(item.notes).split("ملاحظات المُفتش:").pop().trim();
    }
    if (extraNote) {
      lines.push("ملاحظات المُفتش: " + extraNote);
    }
    return lines.join("\n");
  }

  var notes = (item.notes || "").trim();
  if (!notes || notes === "غير محددة" || notes === "ملاحظة غير محددة") {
    return "";
  }
  return notes;
}

function displayStatus(rawStatus) {
  var status = (rawStatus || "").trim();
  if (status === "مطابق") {
    return { text: "مطابق", pct: "100.0%", priority: "Low" };
  }
  if (status === "جزئي" || status === "مطابق جزئياً") {
    return { text: "مطابق جزئياً", pct: "50.0%", priority: "Medium" };
  }
  if (status === "لا يوجد") {
    return { text: "لا يوجد", pct: "100.0%", priority: "Low" };
  }
  if (status === "يوجد") {
    return { text: "يوجد", pct: "0.0%", priority: "High" };
  }
  if (status === "غير محدد" || status === "") {
    return { text: "غير مطابق (غير مكتمل)", pct: "0.0%", priority: "High" };
  }
  return { text: "غير مطابق", pct: "0.0%", priority: "High" };
}

function buildWeakSummary(data) {
  var weakSummaryList = [];
  if (data.responses && data.responses.length > 0) {
    for (var i = 0; i < data.responses.length; i++) {
      var rItem = data.responses[i];
      var rStatus = (rItem.status || "").trim();
      if (isWeakStatus(rStatus)) {
        var notePart = formatItemNotes(rItem);
        notePart = notePart ? " (" + notePart.replace(/\n/g, " | ") + ")" : "";
        weakSummaryList.push("بند " + (rItem.id || (i + 1)) + ": " + displayStatus(rStatus).text + notePart);
      }
    }
  }
  return weakSummaryList.length > 0 ? weakSummaryList.join(" | \n") : "لا توجد نقاط ضعف (مطابق 100%)";
}

function findRecentDuplicateUrl(data) {
  try {
    var masterSs = SpreadsheetApp.openById(TEMPLATE_FILE_ID);
    var archiveSheet = masterSs.getSheetByName("الأرشيف");
    if (!archiveSheet || archiveSheet.getLastRow() < 2) {
      return "";
    }

    var lastRow = archiveSheet.getLastRow();
    var lookback = Math.min(8, lastRow - 1);
    var rows = archiveSheet.getRange(lastRow - lookback + 1, 1, lookback, 13).getValues();
    var now = new Date().getTime();
    var requestId = String(data.request_id || "");
    var center = String(data.center_name || "غير محدد");
    var inspector = String(data.inspector_name || "غير محدد");
    var date = String(data.inspection_date || "-");
    var rate = String(data.compliance_rate || "0");

    for (var i = rows.length - 1; i >= 0; i--) {
      var registered = rows[i][0];
      var rowCenter = String(rows[i][1] || "");
      var rowInspector = String(rows[i][2] || "");
      var rowDate = String(rows[i][3] || "");
      var rowRate = String(rows[i][5] || "");
      var rowUrl = String(rows[i][11] || "");
      var rowRequestId = String(rows[i][12] || "");
      var sameRequest = requestId !== "" && rowRequestId === requestId;
      var sameVisit = rowCenter === center && rowInspector === inspector && rowDate === date && rowRate.indexOf(rate) !== -1;
      var recent = registered && (now - new Date(registered).getTime()) < 3 * 60 * 1000;
      if ((sameRequest || (sameVisit && recent)) && rowUrl) {
        return rowUrl;
      }
    }
  } catch (err) {}
  return "";
}

function createCustomCenterReport(data) {
  var centerName = data.center_name || "غير محدد";
  var inspectorName = data.inspector_name || "غير محدد";
  var inspectionDate = data.inspection_date || "-";
  var complianceRate = data.compliance_rate || "0";
  var matchedCnt = data.matched_cnt || 0;
  var partialCnt = data.partial_cnt || 0;
  var unmatchedCnt = data.unmatched_cnt || 0;
  var weakTotal = collectWeakItems(data).length;
  var totalItems = getTotalItems(data);

  var fileName = "تقرير زيارة ميدانية - " + centerName + " - " + inspectionDate;

  var templateFile = DriveApp.getFileById(TEMPLATE_FILE_ID);
  var targetFolder = DriveApp.getFolderById(TARGET_FOLDER_ID);

  var newFile = templateFile.makeCopy(fileName, targetFolder);
  var newSpreadsheet = SpreadsheetApp.open(newFile);

  var archiveInCopy = newSpreadsheet.getSheetByName("الأرشيف");
  if (archiveInCopy && newSpreadsheet.getSheets().length > 1) {
    newSpreadsheet.deleteSheet(archiveInCopy);
  }

  var sheet1 = newSpreadsheet.getSheetByName("تقرير الزيارة الميدانية") || newSpreadsheet.getSheets()[0];
  sheet1.setRightToLeft(true);

  sheet1.getRange("A2").setValue("مركز الرعاية الصحية الأولية : " + centerName);
  sheet1.getRange("C2").setValue("| إسم المُفتش الميداني : " + inspectorName);
  sheet1.getRange("E2").setValue("| تاريخ الجولة : " + inspectionDate);
  sheet1.getRange("A3").setValue("جهة التقييم: إدارة الخدمات الصيدلانية لمراكز الرعاية الصحية الأولية");

  sheet1.getRange("A6").setValue(complianceRate + "%");
  sheet1.getRange("C6").setValue(matchedCnt + " من أصل " + totalItems + " بنداً");
  sheet1.getRange("F6").setValue(weakTotal + " (نقاط ضعف وملاحظات)");

  if (data.axis_summary) {
    var totalsPerAxis = [16, 8, 6, 8];
    var axesKeys = ["axis1", "axis2", "axis3", "axis4"];
    var summaryRows = [];

    for (var a = 0; a < axesKeys.length; a++) {
      var ax = data.axis_summary[axesKeys[a]] || {matched: 0, partial: 0, unmatched: 0};
      var m = ax.matched || 0;
      var p = ax.partial || 0;
      var u = ax.unmatched || 0;
      var t = ax.total || totalsPerAxis[a];
      var r = (t > 0) ? (((m + (p * 0.5)) / t) * 100).toFixed(2) + "%" : "0.00%";
      if (ax.rate !== undefined) {
        r = ax.rate + "%";
      }
      summaryRows.push([m, p, u, r]);
    }

    sheet1.getRange("D11:G14").setValues(summaryRows);
    sheet1.getRange("C15").setValue(totalItems);
    sheet1.getRange("D15:G15").setValues([[matchedCnt, partialCnt, unmatchedCnt, complianceRate + "%"]]);
  }

  sheet1.getRange("A19:G23").clearContent();
  sheet1.getRange("A27:G31").clearContent();
  sheet1.showRows(19, 13);

  var weakItems = collectWeakItems(data);

  if (weakItems.length > 0) {
    var weakRows = [];
    var actionRows = [];
    var displayCount = Math.min(weakItems.length, 5);

    for (var w = 0; w < displayCount; w++) {
      var wItem = weakItems[w];
      var mapped = displayStatus(wItem.status);
      var diagnosisNote = formatItemNotes(wItem) || "يتطلب استكمال المتطلب وتصحيحه عاجلاً.";
      var criterionText = (wItem.criterion || wItem.text || wItem.title || "").trim();
      var fullCriterionName = "بند " + (wItem.id || (w + 1)) + (criterionText ? (" : " + criterionText) : "");
      var axisTitle = wItem.section || wItem.axis || "محور التقييم";

      weakRows.push([
        axisTitle,
        fullCriterionName,
        "",
        mapped.text,
        mapped.pct,
        diagnosisNote,
        mapped.priority
      ]);

      actionRows.push([
        (w + 1),
        "معالجة واستكمال الملاحظة المرصودة في البند " + (wItem.id || (w + 1)) + (criterionText ? (" : " + criterionText) : ""),
        "",
        "توفر الاستكمال بنسبة 100%",
        "المعاينة الميدانية والتدقيق",
        "قيد التنفيذ",
        ""
      ]);
    }

    sheet1.getRange(19, 1, weakRows.length, 7).setValues(weakRows);
    sheet1.getRange(27, 1, actionRows.length, 7).setValues(actionRows);
    sheet1.getRange(27, 1, actionRows.length, 1).setNumberFormat("@");

    if (displayCount < 5) {
      var rowsToHide = 5 - displayCount;
      sheet1.hideRows(19 + displayCount, rowsToHide);
      sheet1.hideRows(27 + displayCount, rowsToHide);
    }

  } else {
    sheet1.getRange(19, 1, 1, 7).setValues([[
      "-",
      "جميع البنود مطابقة تماماً دون وجود أي نقاط ضعف.",
      "",
      "مطابق",
      "100.0%",
      "الوضع الميداني ممتاز ولا توجد ملاحظات.",
      "Low"
    ]]);

    sheet1.getRange(27, 1, 1, 7).setValues([[
      1,
      "الاستمرار في الحفاظ على نسبة الامتثال المرتفعة والمتابعة الدورية.",
      "",
      "100% امتثال مستمر",
      "المتابعة الدورية",
      "منجز ومعتمد",
      ""
    ]]);
    sheet1.getRange("A27").setNumberFormat("@");
    sheet1.hideRows(20, 4);
    sheet1.hideRows(28, 4);
  }

  var sheet2 = newSpreadsheet.getSheetByName("قائمة التدقيق الديناميكية");
  if (sheet2) {
    fillAuditChecklistSheet(sheet2, data, centerName, inspectorName, complianceRate);
  }

  newSpreadsheet.setActiveSheet(sheet1);
  return newFile.getUrl();
}

function collectWeakItems(data) {
  var weakItems = [];
  if (data.responses && data.responses.length > 0) {
    for (var i = 0; i < data.responses.length; i++) {
      var item = data.responses[i];
      var st = (item.status || "").trim();
      if (isWeakStatus(st)) {
        weakItems.push(item);
      }
    }
  }
  return weakItems;
}

function fillAuditChecklistSheet(sheet2, data, centerName, inspectorName, complianceRate) {
  sheet2.setRightToLeft(true);
  sheet2.getRange("A2").setValue("اسم المركز : " + centerName);
  sheet2.getRange("D3").setValue(complianceRate + "%");

  var row2LastCol = Math.max(sheet2.getLastColumn(), 7);
  var row2Range = sheet2.getRange(2, 1, 1, row2LastCol);
  var row2Vals = row2Range.getValues()[0];
  var updatedInspector = false;

  for (var colIdx = 0; colIdx < row2Vals.length; colIdx++) {
    var cellStr = String(row2Vals[colIdx]);
    if (cellStr.indexOf("المفتش") !== -1 || cellStr.indexOf("المُفتش") !== -1 || cellStr.indexOf("متعبة") !== -1) {
      sheet2.getRange(2, colIdx + 1).setValue("اسم المُفتش : " + inspectorName);
      updatedInspector = true;
      break;
    }
  }

  if (!updatedInspector) {
    sheet2.getRange("E2").setValue("اسم المُفتش : " + inspectorName);
  }

  var respMap = {};
  if (data.responses && data.responses.length > 0) {
    for (var r = 0; r < data.responses.length; r++) {
      var respItem = data.responses[r];
      var itemNum = respItem.id || (r + 1);
      respMap[itemNum] = respItem;
    }
  }

  var maxRows2 = sheet2.getLastRow();
  var startRow = 6;
  var numRows = maxRows2 - startRow + 1;
  var found39 = false;

  if (numRows > 0) {
    var dataRange = sheet2.getRange(startRow, 1, numRows, 5);
    var values = dataRange.getValues();

    for (var k = 0; k < values.length; k++) {
      var num = parseInt(values[k][0], 10);
      if (!isNaN(num) && respMap[num]) {
        if (num === 39) {
          found39 = true;
        }
        var currentResp = respMap[num];
        var mapped = displayStatus(currentResp.status);
        values[k][2] = mapped.text;
        values[k][3] = mapped.pct;
        values[k][4] = formatItemNotes(currentResp);
      }
    }

    dataRange.setValues(values);
  }

  if (!found39 && respMap[39]) {
    appendNearExpiryChecklistRow(sheet2, respMap[39]);
  }

  var totalBottomRow = sheet2.getLastRow();
  sheet2.getRange(totalBottomRow, 4).setValue(complianceRate + "%");
}

function appendNearExpiryChecklistRow(sheet2, item39) {
  var lastRow = sheet2.getLastRow();
  var lastFirst = String(sheet2.getRange(lastRow, 1).getValue() || "");
  var insertAt = lastRow;
  if (isNaN(parseInt(lastFirst, 10))) {
    sheet2.insertRowBefore(lastRow);
    insertAt = lastRow;
  } else {
    insertAt = lastRow + 1;
    sheet2.insertRowAfter(lastRow);
  }

  var mapped = displayStatus(item39.status);
  sheet2.getRange(insertAt, 1, 1, 5).setValues([[
    39,
    item39.criterion || "وجود أصناف دوائية قاربت على انتهاء الصلاحية (Near-Expiry)",
    mapped.text,
    mapped.pct,
    formatItemNotes(item39)
  ]]);
}

function sendApprovedEmailReport(data, centerFileUrl) {
  var recipientEmail = RECIPIENT_EMAIL;
  var inspectorName = data.inspector_name || "غير محدد";
  var centerName = data.center_name || "غير محدد";
  var complianceRate = data.compliance_rate || "0";
  var generalNotes = data.general_notes ? data.general_notes : "لا توجد ملاحظات عامة مسجلة.";
  var subject = "\u200Fتقرير تقييم جديد: " + inspectorName + " - اسم المركز: " + centerName + " - نسبة الامتثال: " + complianceRate + "%";

  var itemsDetailsHtml = "";
  var itemsDetailsText = "";
  if (data.responses && data.responses.length > 0) {
    for (var i = 0; i < data.responses.length; i++) {
      var item = data.responses[i];
      var itemId = item.id || (i + 1);
      var mapped = displayStatus(item.status);
      var itemNote = formatItemNotes(item);
      var noteHtml = itemNote ? " (ملاحظة: " + escapeHtml(itemNote).replace(/\n/g, "<br>") + ")" : "";
      var noteText = itemNote ? " (ملاحظة: " + itemNote.replace(/\n/g, " | ") + ")" : "";
      itemsDetailsHtml += "بند " + itemId + ": " + escapeHtml(mapped.text) + noteHtml + "<br>";
      itemsDetailsText += "بند " + itemId + ": " + mapped.text + noteText + "\n";
    }
  }

  var bodyText =
    "تم اعتماد تقرير الزيارة الميدانية عبر المنصة الرقمية:\n\n" +
    "البيانات الأساسية:\n" +
    "• المركز الصحي: " + centerName + "\n" +
    "• تاريخ التفتيش: " + (data.inspection_date || "-") + "\n" +
    "• نسبة الامتثال الإجمالية: " + complianceRate + "%\n\n" +
    "ملخص النتائج:\n" +
    "• عدد البنود المطابقة: " + (data.matched_cnt || 0) + "\n" +
    "• عدد البنود الجزئية: " + (data.partial_cnt || 0) + "\n" +
    "• عدد البنود غير المطابقة: " + (data.unmatched_cnt || 0) + "\n\n" +
    "الملاحظات والتوصيات العامة:\n" +
    generalNotes + "\n\n" +
    "تفاصيل التقييم والملاحظات:\n" +
    itemsDetailsText + "\n" +
    "يمكنك الاطلاع على ملف تقرير المركز المنسق عبر الرابط:\n" +
    centerFileUrl + "\n\n" +
    "إدارة الخدمات الصيدلانية";

  var htmlBody =
    '<div dir="rtl" style="font-family:Tahoma,Arial,sans-serif;text-align:right;line-height:1.8;font-size:15px;">' +
    "<p>تم اعتماد تقرير الزيارة الميدانية عبر المنصة الرقمية.</p>" +
    "<p><strong>البيانات الأساسية</strong><br>" +
    "• المركز الصحي: " + escapeHtml(centerName) + "<br>" +
    "• تاريخ التفتيش: " + escapeHtml(String(data.inspection_date || "-")) + "<br>" +
    "• نسبة الامتثال الإجمالية: " + escapeHtml(String(complianceRate)) + "%</p>" +
    "<p><strong>ملخص النتائج</strong><br>" +
    "• عدد البنود المطابقة: " + escapeHtml(String(data.matched_cnt || 0)) + "<br>" +
    "• عدد البنود الجزئية: " + escapeHtml(String(data.partial_cnt || 0)) + "<br>" +
    "• عدد البنود غير المطابقة: " + escapeHtml(String(data.unmatched_cnt || 0)) + "</p>" +
    "<p><strong>الملاحظات والتوصيات العامة</strong><br>" + escapeHtml(generalNotes).replace(/\n/g, "<br>") + "</p>" +
    "<p><strong>تفاصيل التقييم والملاحظات</strong><br>" + itemsDetailsHtml + "</p>" +
    '<p>يمكنك الاطلاع على ملف تقرير المركز المنسق عبر الرابط:<br><a href="' + escapeHtml(centerFileUrl) + '">' + escapeHtml(centerFileUrl) + "</a></p>" +
    "<p>إدارة الخدمات الصيدلانية</p>" +
    "</div>";

  MailApp.sendEmail({
    to: recipientEmail,
    subject: subject,
    body: bodyText,
    htmlBody: htmlBody
  });
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
