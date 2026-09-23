// =============================================================================
// سكريبت المنصة الرقمية المعتمد - نظام الزيارات الميدانية لقسم الصيدلة
// القالب الحالي: 5 محاور و 39 بنداً، والبند 39 حالته يوجد / لا يوجد
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
    appendArchiveRow(masterSs, data, centerFileUrl);
    logVisitReference(masterSs, data, centerFileUrl);
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

function displayStatus(rawStatus) {
  var status = String(rawStatus || "").trim();
  if (status === "مطابق") {
    return { text: "مطابق", pct: "100.00%", priority: "Low" };
  }
  if (status === "جزئي" || status === "مطابق جزئياً") {
    return { text: "مطابق جزئياً", pct: "50.00%", priority: "Medium" };
  }
  if (status === "لا يوجد") {
    return { text: "لا يوجد", pct: "100.00%", priority: "Low" };
  }
  if (status === "يوجد") {
    return { text: "يوجد", pct: "0.00%", priority: "High" };
  }
  if (status === "غير محدد" || status === "") {
    return { text: "غير مطابق (غير مكتمل)", pct: "0.00%", priority: "High" };
  }
  return { text: "غير مطابق", pct: "0.00%", priority: "High" };
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

  var notes = String(item.notes || "").trim();
  if (!notes || notes === "غير محددة" || notes === "ملاحظة غير محددة") {
    return "";
  }
  return notes;
}

function collectWeakItems(data) {
  var weakItems = [];
  if (data.responses && data.responses.length > 0) {
    for (var i = 0; i < data.responses.length; i++) {
      var item = data.responses[i];
      if (isWeakStatus(String(item.status || "").trim())) {
        weakItems.push(item);
      }
    }
  }
  return weakItems;
}

function buildWeakSummary(data) {
  var weakSummaryList = [];
  var weakItems = collectWeakItems(data);
  for (var i = 0; i < weakItems.length; i++) {
    var item = weakItems[i];
    var notePart = formatItemNotes(item);
    notePart = notePart ? " (" + notePart.replace(/\n/g, " | ") + ")" : "";
    weakSummaryList.push("بند " + (item.id || (i + 1)) + ": " + displayStatus(item.status).text + notePart);
  }
  return weakSummaryList.length > 0 ? weakSummaryList.join(" | \n") : "لا توجد نقاط ضعف (مطابق 100%)";
}

function findRowByText(sheet, text) {
  var last = Math.max(sheet.getLastRow(), 8);
  var values = sheet.getRange(1, 1, last, 3).getValues();
  for (var i = 0; i < values.length; i++) {
    var joined = String(values[i][0] || "") + " " + String(values[i][1] || "") + " " + String(values[i][2] || "");
    if (joined.indexOf(text) !== -1) {
      return i + 1;
    }
  }
  return -1;
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
      var sameRequest = requestId !== "" && String(rows[i][12] || "") === requestId;
      var sameVisit = String(rows[i][1] || "") === center &&
        String(rows[i][2] || "") === inspector &&
        String(rows[i][3] || "") === date &&
        String(rows[i][5] || "").indexOf(rate) !== -1;
      var recent = registered && (now - new Date(registered).getTime()) < 3 * 60 * 1000;
      if ((sameRequest || (sameVisit && recent)) && rows[i][11]) {
        return String(rows[i][11]);
      }
    }
  } catch (err) {}
  return "";
}

function appendArchiveRow(masterSs, data, centerFileUrl) {
  var archiveSheet = masterSs.getSheetByName("الأرشيف");
  if (!archiveSheet) {
    archiveSheet = masterSs.insertSheet("الأرشيف");
  }
  archiveSheet.setRightToLeft(true);
  if (archiveSheet.getLastRow() === 0) {
    archiveSheet.appendRow([
      "تاريخ التسجيل",
      "اسم المركز الصحي",
      "اسم المُفتش الميداني",
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
    buildWeakSummary(data),
    '=HYPERLINK("' + centerFileUrl + '", "عرض تقرير المركز 📄")',
    data.request_id || ""
  ]);
}

function ensureSheetWithHeaders(ss, sheetName, headers) {
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
  }
  sheet.setRightToLeft(true);
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(headers);
    sheet.getRange(1, 1, 1, headers.length)
      .setFontWeight("bold")
      .setBackground("#1F4E79")
      .setFontColor("#FFFFFF");
  }
  return sheet;
}

function logVisitReference(masterSs, data, centerFileUrl) {
  var visitsSheet = ensureSheetWithHeaders(masterSs, "الزيارات", [
    "اسم المركز",
    "تاريخ الزيارة",
    "نسبة الامتثال",
    "اسم المُفتش الميداني",
    "وقت الزيارة",
    "رابط التقرير المعتمد",
    "تاريخ التسجيل",
    "معرف الطلب"
  ]);

  visitsSheet.appendRow([
    data.center_name || "غير محدد",
    data.inspection_date || "-",
    (data.compliance_rate || "0") + "%",
    data.inspector_name || "غير محدد",
    data.inspection_time || "-",
    '=HYPERLINK("' + centerFileUrl + '", "عرض تقرير المركز 📄")',
    new Date(),
    data.request_id || ""
  ]);
}

function createCustomCenterReport(data) {
  var centerName = data.center_name || "غير محدد";
  var inspectorName = data.inspector_name || "غير محدد";
  var inspectionDate = data.inspection_date || "-";
  var complianceRate = data.compliance_rate || "0";
  var matchedCnt = data.matched_cnt || 0;
  var partialCnt = data.partial_cnt || 0;
  var unmatchedCnt = data.unmatched_cnt || 0;
  var weakItems = collectWeakItems(data);
  var totalItems = getTotalItems(data);

  var fileName = "تقرير زيارة ميدانية - " + centerName + " - " + inspectionDate;
  var newFile = DriveApp.getFileById(TEMPLATE_FILE_ID).makeCopy(fileName, DriveApp.getFolderById(TARGET_FOLDER_ID));
  var newSpreadsheet = SpreadsheetApp.open(newFile);
  removeReferenceSheetsFromCopy(newSpreadsheet);

  var sheet1 = newSpreadsheet.getSheetByName("تقرير الزيارة الميدانية") || newSpreadsheet.getSheets()[0];
  sheet1.setRightToLeft(true);

  fillReportHeader(sheet1, centerName, inspectorName, inspectionDate);
  sheet1.getRange("A6").setValue(complianceRate + "%");
  sheet1.getRange("C6").setValue(matchedCnt + " من أصل " + totalItems + " بنداً");

  var weakCell = findHeaderCell(sheet1, "نقاط الضعف");
  if (weakCell) {
    sheet1.getRange(weakCell.row + 1, weakCell.col).setValue(weakItems.length + " (نقاط ضعف وملاحظات)");
  } else {
    sheet1.getRange("F6").setValue(weakItems.length + " (نقاط ضعف وملاحظات)");
  }

  fillAxisSummary(sheet1, data, matchedCnt, partialCnt, unmatchedCnt, complianceRate, totalItems);
  fillWeaknessAndActionTables(sheet1, weakItems);

  var sheet2 = newSpreadsheet.getSheetByName("قائمة التدقيق الديناميكية");
  if (sheet2) {
    fillAuditChecklistSheet(sheet2, data, centerName, inspectorName, complianceRate);
  }

  newSpreadsheet.setActiveSheet(sheet1);
  return newFile.getUrl();
}

function fillReportHeader(sheet1, centerName, inspectorName, inspectionDate) {
  sheet1.getRange("A2").setValue("مركز الرعاية الصحية الأولية : " + centerName);
  var row2 = sheet1.getRange(2, 1, 1, 8).getValues()[0];
  var inspectorWritten = false;
  var dateWritten = false;

  for (var i = 1; i < row2.length; i++) {
    var text = String(row2[i] || "");
    if (!inspectorWritten && (text.indexOf("المفتش") !== -1 || text.indexOf("المُفتش") !== -1)) {
      sheet1.getRange(2, i + 1).setValue("| إسم المُفتش الميداني : " + inspectorName);
      inspectorWritten = true;
    } else if (!dateWritten && text.indexOf("تاريخ") !== -1) {
      sheet1.getRange(2, i + 1).setValue("| تاريخ الجولة : " + inspectionDate);
      dateWritten = true;
    }
  }

  if (!inspectorWritten) {
    sheet1.getRange("B2").setValue("| إسم المُفتش الميداني : " + inspectorName);
  }
  if (!dateWritten) {
    sheet1.getRange("C2").setValue("| تاريخ الجولة : " + inspectionDate);
  }
}

function findHeaderCell(sheet, text) {
  var lastRow = Math.max(sheet.getLastRow(), 8);
  var lastCol = Math.max(sheet.getLastColumn(), 7);
  var values = sheet.getRange(1, 1, lastRow, lastCol).getValues();
  for (var r = 0; r < values.length; r++) {
    for (var c = 0; c < values[r].length; c++) {
      if (String(values[r][c] || "").indexOf(text) !== -1) {
        return { row: r + 1, col: c + 1 };
      }
    }
  }
  return null;
}

function fillAxisSummary(sheet1, data, matchedCnt, partialCnt, unmatchedCnt, complianceRate, totalItems) {
  var axisRows = {
    "رقيم": ["axis1", 16],
    "غرفة الأدوية": ["axis2", 8],
    "الثلاجة": ["axis3", 6],
    "عربة الطوارئ": ["axis4", 8],
    "مخزن الأدوية": ["axis5", 1]
  };

  var last = Math.max(sheet1.getLastRow(), 20);
  var labels = sheet1.getRange(1, 1, last, 3).getValues();

  for (var i = 0; i < labels.length; i++) {
    var label = String(labels[i][0] || "") + " " + String(labels[i][1] || "");
    for (var key in axisRows) {
      if (label.indexOf(key) !== -1 && label.indexOf("الإجمالي") === -1) {
        var axisKey = axisRows[key][0];
        var fallbackTotal = axisRows[key][1];
        var ax = (data.axis_summary && data.axis_summary[axisKey]) ? data.axis_summary[axisKey] : {};
        var m = ax.matched || 0;
        var p = ax.partial || 0;
        var u = ax.unmatched || 0;
        var t = ax.total || fallbackTotal;
        var rate = (t > 0) ? (((m + (p * 0.5)) / t) * 100).toFixed(2) + "%" : "0.00%";
        sheet1.getRange(i + 1, 3, 1, 5).setValues([[t, m, p, u, rate]]);
      }
    }
    if (label.indexOf("الإجمالي") !== -1) {
      sheet1.getRange(i + 1, 3, 1, 5).setValues([[totalItems, matchedCnt, partialCnt, unmatchedCnt, complianceRate + "%"]]);
    }
  }
}

function fillWeaknessAndActionTables(sheet1, weakItems) {
  var weakHeader = findRowByText(sheet1, "رصد");
  var actionHeader = findRowByText(sheet1, "الخطة العلاجية");
  if (weakHeader < 0) {
    weakHeader = 17;
  }
  if (actionHeader < 0) {
    actionHeader = 25;
  }

  var weakStart = weakHeader + 2;
  var actionStart = actionHeader + 2;
  var maxSlots = 5;

  sheet1.getRange(weakStart, 1, maxSlots, 7).clearContent();
  sheet1.getRange(actionStart, 1, maxSlots, 7).clearContent();
  sheet1.showRows(weakStart, maxSlots);
  sheet1.showRows(actionStart, maxSlots);

  if (weakItems.length === 0) {
    sheet1.getRange(weakStart, 1, 1, 6).setValues([[
      "-",
      "جميع البنود مطابقة تماماً دون وجود أي نقاط ضعف.",
      "مطابق",
      "100.00%",
      "الوضع الميداني ممتاز ولا توجد ملاحظات.",
      "Low"
    ]]);
    sheet1.getRange(actionStart, 1, 1, 5).setValues([[
      "1",
      "الاستمرار في الحفاظ على نسبة الامتثال المرتفعة والمتابعة الدورية.",
      "100% امتثال مستمر",
      "المتابعة الدورية",
      "منجز ومعتمد"
    ]]);
    sheet1.getRange(actionStart, 1).setNumberFormat("@");
    sheet1.hideRows(weakStart + 1, maxSlots - 1);
    sheet1.hideRows(actionStart + 1, maxSlots - 1);
    return;
  }

  var displayCount = Math.min(weakItems.length, maxSlots);
  var weakRows = [];
  var actionRows = [];

  for (var w = 0; w < displayCount; w++) {
    var item = weakItems[w];
    var mapped = displayStatus(item.status);
    var criterionText = String(item.criterion || "").trim();
    var itemId = item.id || (w + 1);
    weakRows.push([
      item.section || "محور التقييم",
      "بند " + itemId + (criterionText ? (" : " + criterionText) : ""),
      mapped.text,
      mapped.pct,
      formatItemNotes(item) || "يتطلب استكمال المتطلب وتصحيحه عاجلاً.",
      mapped.priority
    ]);
    actionRows.push([
      String(w + 1),
      "معالجة واستكمال الملاحظة المرصودة في البند " + itemId + (criterionText ? (" : " + criterionText) : ""),
      "توفر الاستكمال بنسبة 100%",
      "المعاينة الميدانية والتدقيق",
      "قيد التنفيذ"
    ]);
  }

  sheet1.getRange(weakStart, 1, weakRows.length, 6).setValues(weakRows);
  sheet1.getRange(weakStart, 1, weakRows.length, 6).setWrap(true);
  sheet1.getRange(actionStart, 1, actionRows.length, 5).setValues(actionRows);
  sheet1.getRange(actionStart, 1, actionRows.length, 1).setNumberFormat("@");

  if (displayCount < maxSlots) {
    sheet1.hideRows(weakStart + displayCount, maxSlots - displayCount);
    sheet1.hideRows(actionStart + displayCount, maxSlots - displayCount);
  }
}

function fillAuditChecklistSheet(sheet2, data, centerName, inspectorName, complianceRate) {
  sheet2.setRightToLeft(true);
  sheet2.getRange("A2").setValue("اسم المركز : " + centerName);

  var row2 = sheet2.getRange(2, 1, 1, Math.max(sheet2.getLastColumn(), 7)).getValues()[0];
  var inspectorWritten = false;
  for (var colIdx = 0; colIdx < row2.length; colIdx++) {
    var cellStr = String(row2[colIdx] || "");
    if (cellStr.indexOf("المفتش") !== -1 || cellStr.indexOf("المُفتش") !== -1) {
      sheet2.getRange(2, colIdx + 1).setValue("اسم المُفتش : " + inspectorName);
      inspectorWritten = true;
      break;
    }
  }
  if (!inspectorWritten) {
    sheet2.getRange("E2").setValue("اسم المُفتش : " + inspectorName);
  }

  var rateCell = findHeaderCell(sheet2, "نسبة الامتثال");
  if (rateCell) {
    sheet2.getRange(rateCell.row + 1, rateCell.col).setValue(complianceRate + "%");
  } else {
    sheet2.getRange("D3").setValue(complianceRate + "%");
  }

  var respMap = {};
  if (data.responses && data.responses.length > 0) {
    for (var r = 0; r < data.responses.length; r++) {
      respMap[data.responses[r].id || (r + 1)] = data.responses[r];
    }
  }

  var startRow = 6;
  var lastRow = sheet2.getLastRow();
  if (lastRow >= startRow) {
    var values = sheet2.getRange(startRow, 1, lastRow - startRow + 1, 5).getValues();
    for (var k = 0; k < values.length; k++) {
      var num = parseInt(values[k][0], 10);
      if (!isNaN(num) && respMap[num]) {
        var mapped = displayStatus(respMap[num].status);
        values[k][2] = mapped.text;
        values[k][3] = mapped.pct;
        values[k][4] = formatItemNotes(respMap[num]);
      }
    }
    sheet2.getRange(startRow, 1, values.length, 5).setValues(values);
    sheet2.getRange(startRow, 5, values.length, 1).setWrap(true);
  }

  var totalRow = findRowByText(sheet2, "النتيجة النهائية");
  if (totalRow > 0) {
    sheet2.getRange(totalRow, 4).setValue(complianceRate + "%");
  } else {
    sheet2.getRange(sheet2.getLastRow(), 4).setValue(complianceRate + "%");
  }
}

function removeReferenceSheetsFromCopy(newSpreadsheet) {
  var referenceNames = ["الأرشيف", "الزيارات"];
  for (var i = 0; i < referenceNames.length; i++) {
    var refSheet = newSpreadsheet.getSheetByName(referenceNames[i]);
    if (refSheet && newSpreadsheet.getSheets().length > 1) {
      newSpreadsheet.deleteSheet(refSheet);
    }
  }
}

function buildEmailSubject(data) {
  return (
    "\u200Fاسم المركز : " + (data.center_name || "غير محدد") +
    "                   تاريخ الزيارة : " + (data.inspection_date || "-") +
    "                       نسبة الامتثال : " + (data.compliance_rate || "0") + "%"
  );
}

function sendApprovedEmailReport(data, centerFileUrl) {
  var inspectorName = data.inspector_name || "غير محدد";
  var centerName = data.center_name || "غير محدد";
  var inspectionDate = data.inspection_date || "-";
  var complianceRate = data.compliance_rate || "0";
  var generalNotes = data.general_notes ? data.general_notes : "لا توجد ملاحظات عامة مسجلة.";
  var subject = buildEmailSubject(data);

  var itemsDetailsHtml = "";
  var itemsDetailsText = "";
  if (data.responses && data.responses.length > 0) {
    for (var i = 0; i < data.responses.length; i++) {
      var item = data.responses[i];
      var mapped = displayStatus(item.status);
      var itemNote = formatItemNotes(item);
      var noteHtml = itemNote ? " (ملاحظة: " + escapeHtml(itemNote).replace(/\n/g, "<br>") + ")" : "";
      var noteText = itemNote ? " (ملاحظة: " + itemNote.replace(/\n/g, " | ") + ")" : "";
      itemsDetailsHtml += "بند " + (item.id || (i + 1)) + ": " + escapeHtml(mapped.text) + noteHtml + "<br>";
      itemsDetailsText += "بند " + (item.id || (i + 1)) + ": " + mapped.text + noteText + "\n";
    }
  }

  var bodyText =
    "تم اعتماد تقرير الزيارة الميدانية عبر المنصة الرقمية:\n\n" +
    "اسم المركز : " + centerName + "\n" +
    "تاريخ الزيارة : " + inspectionDate + "\n" +
    "نسبة الامتثال : " + complianceRate + "%\n" +
    "اسم المُفتش الميداني : " + inspectorName + "\n\n" +
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
    "<p>اسم المركز : " + escapeHtml(centerName) + "<br>" +
    "تاريخ الزيارة : " + escapeHtml(String(inspectionDate)) + "<br>" +
    "نسبة الامتثال : " + escapeHtml(String(complianceRate)) + "%<br>" +
    "اسم المُفتش الميداني : " + escapeHtml(inspectorName) + "</p>" +
    "<p><strong>ملخص النتائج</strong><br>" +
    "• عدد البنود المطابقة: " + escapeHtml(String(data.matched_cnt || 0)) + "<br>" +
    "• عدد البنود الجزئية: " + escapeHtml(String(data.partial_cnt || 0)) + "<br>" +
    "• عدد البنود غير المطابقة: " + escapeHtml(String(data.unmatched_cnt || 0)) + "</p>" +
    "<p><strong>الملاحظات والتوصيات العامة</strong><br>" + escapeHtml(generalNotes).replace(/\n/g, "<br>") + "</p>" +
    "<p><strong>تفاصيل التقييم والملاحظات</strong><br>" + itemsDetailsHtml + "</p>" +
    '<p>يمكنك الاطلاع على ملف تقرير المركز المنسق عبر الرابط:<br><a href="' + escapeHtml(centerFileUrl) + '">' + escapeHtml(centerFileUrl) + "</a></p>" +
    "<p>إدارة الخدمات الصيدلانية</p></div>";

  MailApp.sendEmail({
    to: RECIPIENT_EMAIL,
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
