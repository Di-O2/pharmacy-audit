// =============================================================================
// سكريبت المنصة الرقمية المعتمد - نظام الزيارات الميدانية لقسم الصيدلة
// النسخة المعتمدة: نموذج 38 بنداً + الإخفاء الديناميكي + توقيت الرياض الصريح
// =============================================================================

var TEMPLATE_FILE_ID = "1QBq_OUsbNsc3lklC8_tvFAygRhlaT7MKZ6yMyiyLkNw";
var TARGET_FOLDER_ID = "1fxe6hGCG7TRZZ6aG7xQ_vTi-yQpD3hSD";
var RECIPIENT_EMAIL = "da720883@gmail.com";

function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({
    "status": "online",
    "message": "خدمة أتمتة تقارير الزيارات الميدانية متصلة وجاهزة بنسبة 100%."
  })).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
   
    // 1. توليد تقرير المركز المستقل أولاً والحصول على الرابط
    var centerFileUrl = createCustomCenterReport(data);

    // 2. الأرشفة المركزية بتوقيت الرياض الصريح (Asia/Riyadh)
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
        "رابط التقرير المعتمد"
      ]);
      archiveSheet.getRange("A1:L1").setFontWeight("bold").setBackground("#1F4E79").setFontColor("#FFFFFF");
    }
   
    var weakSummaryList = [];
    if (data.responses && data.responses.length > 0) {
      for (var i = 0; i < data.responses.length; i++) {
        var rItem = data.responses[i];
        var rStatus = (rItem.status || "").trim();
        if (rStatus !== "مطابق") {
          var notePart = (rItem.notes && rItem.notes.trim() !== "") ? " (" + rItem.notes.trim() + ")" : "";
          weakSummaryList.push("بند " + (rItem.id || (i + 1)) + ": " + rStatus + notePart);
        }
      }
    }
    var readableWeakSummary = weakSummaryList.length > 0 ? weakSummaryList.join(" | \n") : "لا توجد نقاط ضعف (مطابق 100%)";
    var hyperlinkFormula = '=HYPERLINK("' + centerFileUrl + '", "عرض تقرير المركز 📄")';

    // تثبيت توقيت التسجيل بتوقيت الرياض الرسمي كنص صريح يمنع تغيير المنطقة الزمنية
    var saudiRegistrationTime = "'" + Utilities.formatDate(new Date(), "Asia/Riyadh", "dd/MM/yyyy HH:mm:ss");

    archiveSheet.appendRow([
      saudiRegistrationTime,
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
      hyperlinkFormula
    ]);

    // 3. إرسال الإشعار البريدي الرسمي
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
  }
}

function createCustomCenterReport(data) {
  var centerName = data.center_name || "غير محدد";
  var inspectorName = data.inspector_name || "غير محدد";
  var inspectionDate = data.inspection_date || "-";
  var complianceRate = data.compliance_rate || "0";
  var matchedCnt = data.matched_cnt || 0;
  var partialCnt = data.partial_cnt || 0;
  var unmatchedCnt = data.unmatched_cnt || 0;
  var weakTotal = partialCnt + unmatchedCnt;

  var fileName = "تقرير زيارة ميدانية - " + centerName + " - " + inspectionDate;
 
  var templateFile = DriveApp.getFileById(TEMPLATE_FILE_ID);
  var targetFolder = DriveApp.getFolderById(TARGET_FOLDER_ID);
 
  var newFile = templateFile.makeCopy(fileName, targetFolder);
  var newSpreadsheet = SpreadsheetApp.open(newFile);

  var archiveInCopy = newSpreadsheet.getSheetByName("الأرشيف");
  if (archiveInCopy && newSpreadsheet.getSheets().length > 1) {
    newSpreadsheet.deleteSheet(archiveInCopy);
  }
 
  // الورقة الأولى: تقرير الزيارة الميدانية التنفيذي
  var sheet1 = newSpreadsheet.getSheetByName("تقرير الزيارة الميدانية") || newSpreadsheet.getSheets()[0];
  sheet1.setRightToLeft(true);

  sheet1.getRange("A2").setValue("مركز الرعاية الصحية الأولية : " + centerName);
  sheet1.getRange("C2").setValue("| إسم المفتش الميداني : " + inspectorName);
  sheet1.getRange("D2").setValue("| إسم المفتش الميداني : " + inspectorName);
  sheet1.getRange("E2").setValue("| تاريخ الجولة : " + inspectionDate);
  sheet1.getRange("F2").setValue("| تاريخ الجولة : " + inspectionDate);
  sheet1.getRange("A3").setValue("جهة التقييم: إدارة الخدمات الصيدلانية لمراكز الرعاية الصحية الأولية");
 
  sheet1.getRange("A6").setValue(complianceRate + "%");
  sheet1.getRange("C6").setValue(matchedCnt + " من أصل 38 بنداً");
  sheet1.getRange("F6").setValue(weakTotal + " (نقاط ضعف وملاحظات)");

  // ملخص أداء المحاور (نموذج 38 بنداً: 16، 8، 6، 8)
  if (data.axis_summary) {
    var totalsPerAxis = [16, 8, 6, 8];
    var axesKeys = ["axis1", "axis2", "axis3", "axis4"];
    var summaryRows = [];

    for (var a = 0; a < axesKeys.length; a++) {
      var ax = data.axis_summary[axesKeys[a]] || {matched: 0, partial: 0, unmatched: 0};
      var m = ax.matched || 0;
      var p = ax.partial || 0;
      var u = ax.unmatched || 0;
      var t = totalsPerAxis[a];
      var r = (t > 0) ? (((m + (p * 0.5)) / t) * 100).toFixed(2) + "%" : "0.00%";
      if (ax.rate !== undefined) {
        r = ax.rate + "%";
      }
      summaryRows.push([m, p, u, r]);
    }

    sheet1.getRange("D11:G14").setValues(summaryRows);
    sheet1.getRange("D15:G15").setValues([[matchedCnt, partialCnt, unmatchedCnt, complianceRate + "%"]]);
  }

  // تنظيف الجداول وإظهار كافة الصفوف تحسباً
  sheet1.getRange("A19:G23").clearContent();
  sheet1.getRange("A27:G31").clearContent();
  sheet1.showRows(19, 13);

  var weakItems = [];
  if (data.responses && data.responses.length > 0) {
    for (var i = 0; i < data.responses.length; i++) {
      var item = data.responses[i];
      var st = (item.status || "").trim();
      if (st !== "مطابق") {
        weakItems.push(item);
      }
    }
  }

  if (weakItems.length > 0) {
    var weakRows = [];
    var actionRows = [];
    var displayCount = Math.min(weakItems.length, 5);

    for (var w = 0; w < displayCount; w++) {
      var wItem = weakItems[w];
      var currentSt = (wItem.status || "").trim();
      var statusText = "غير مطابق";
      var statusPct = "0.0%";
      var priorityText = "High";

      if (currentSt === "جزئي" || currentSt === "مطابق جزئياً") {
        statusText = "مطابق جزئياً";
        statusPct = "50.0%";
        priorityText = "Medium";
      } else if (currentSt === "غير محدد" || currentSt === "") {
        statusText = "غير مطابق (غير مكتمل)";
      }

      var diagnosisNote = (wItem.notes && wItem.notes.trim() !== "") ? wItem.notes.trim() : "يتطلب استكمال المتطلب وتصحيحه عاجلاً.";
      var criterionText = (wItem.criterion || wItem.text || wItem.title || "").trim();
      var fullCriterionName = "بند " + (wItem.id || (w + 1)) + (criterionText ? (" : " + criterionText) : "");
      var axisTitle = wItem.section || wItem.axis || "محور التقييم";

      weakRows.push([
        axisTitle,
        fullCriterionName,
        "", 
        statusText,
        statusPct,
        diagnosisNote,
        priorityText
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

    // الإخفاء الديناميكي التلقائي عند وجود أقل من 5 ملاحظات
    if (displayCount < 5) {
      var rowsToHide = 5 - displayCount;
      sheet1.hideRows(19 + displayCount, rowsToHide);
      sheet1.hideRows(27 + displayCount, rowsToHide);
    }

  } else {
    // حالة الامتثال التام 100% (إظهار صف واحد وتقليص الجداول)
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

  // الورقة الثانية: قائمة التدقيق الديناميكية
  var sheet2 = newSpreadsheet.getSheetByName("قائمة التدقيق الديناميكية");
  if (sheet2) {
    sheet2.setRightToLeft(true);
    sheet2.getRange("A2").setValue("اسم المركز : " + centerName);
    sheet2.getRange("D3").setValue(complianceRate + "%");

    var row2LastCol = Math.max(sheet2.getLastColumn(), 7);
    var row2Range = sheet2.getRange(2, 1, 1, row2LastCol);
    var row2Vals = row2Range.getValues()[0];
    var updatedInspector = false;

    for (var colIdx = 0; colIdx < row2Vals.length; colIdx++) {
      var cellStr = String(row2Vals[colIdx]);
      if (cellStr.indexOf("المفتش") !== -1 || cellStr.indexOf("متعبة") !== -1) {
        sheet2.getRange(2, colIdx + 1).setValue("اسم المفتش : " + inspectorName);
        updatedInspector = true;
        break;
      }
    }

    if (!updatedInspector) {
      sheet2.getRange("E2").setValue("اسم المفتش : " + inspectorName);
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

    if (numRows > 0) {
      var dataRange = sheet2.getRange(startRow, 1, numRows, 5);
      var values = dataRange.getValues();

      for (var k = 0; k < values.length; k++) {
        var num = parseInt(values[k][0]);
        if (!isNaN(num) && respMap[num]) {
          var currentResp = respMap[num];
          var rawStatus = (currentResp.status || "").trim();
          var matchStatus = "غير مطابق";
          var matchPct = "0.0%";

          if (rawStatus === "مطابق") {
            matchStatus = "مطابق";
            matchPct = "100.0%";
          } else if (rawStatus === "جزئي" || rawStatus === "مطابق جزئياً") {
            matchStatus = "مطابق جزئياً";
            matchPct = "50.0%";
          } else if (rawStatus === "غير محدد" || rawStatus === "") {
            matchStatus = "غير مطابق (غير محدد)";
            matchPct = "0.0%";
          }

          values[k][2] = matchStatus;
          values[k][3] = matchPct;
          values[k][4] = currentResp.notes || "";
        }
      }

      dataRange.setValues(values);
    }

    var totalBottomRow = sheet2.getLastRow();
    sheet2.getRange(totalBottomRow, 4).setValue(complianceRate + "%");
  }

  newSpreadsheet.setActiveSheet(sheet1);
  return newFile.getUrl();
}

function sendApprovedEmailReport(data, centerFileUrl) {
  var recipientEmail = RECIPIENT_EMAIL;
  var inspectorName = data.inspector_name || "غير محدد";
  var centerName = data.center_name || "غير محدد";
  var complianceRate = data.compliance_rate || "0";
  var generalNotes = data.general_notes ? data.general_notes : "لا توجد ملاحظات عامة مسجلة.";
  var subject = "تقرير تقييم جديد: " + inspectorName + " - اسم المركز: " + centerName + " - نسبة الامتثال: " + complianceRate + "%";
 
  var itemsDetailsText = "";
  if (data.responses && data.responses.length > 0) {
    for (var i = 0; i < data.responses.length; i++) {
      var item = data.responses[i];
      var itemId = item.id || (i + 1);
      var itemStatus = item.status || "غير محدد";
      var itemNote = (item.notes && item.notes.trim() !== "") ? " (ملاحظة: " + item.notes.trim() + " )" : "";
      itemsDetailsText += "بند " + itemId + ": " + itemStatus + itemNote + "\n";
    }
  }
 
  var bodyText =
    "تم اعتماد تقرير الزيارة الميدانية عبر المنصة الرقمية:\n\n\n" +
    "البيانات الأساسية:\n" +
    "• المركز الصحي: " + centerName + "\n" +
    "• تاريخ التفتيش: " + (data.inspection_date || "-") + "\n" +
    "• نسبة الامتثال الإجمالية: " + complianceRate + "%\n\n" +
    "ملخص النتائج:\n" +
    "• عدد البنود المطابقة: " + (data.matched_cnt || 0) + "\n" +
    "• عدد البنود الجزئية: " + (data.partial_cnt || 0) + "\n" +
    "• عدد البنود غير المطابقة: " + (data.unmatched_cnt || 0) + "\n\n" +
    "📝 الملاحظات والتوصيات العامة:\n" +
    generalNotes + "\n\n" +
    "تفاصيل التقييم والملاحظات:\n" +
    itemsDetailsText + "\n\n" +
    "📄 يمكنك الاطلاع على ملف تقرير المركز المنسق عبر الرابط:\n" +
    centerFileUrl + "\n\n" +
    "إدارة الخدمات الصيدلانية";
   
  MailApp.sendEmail({
    to: recipientEmail,
    subject: subject,
    body: bodyText
  });
}

// دالة تصحيح السجلات القديمة المعروضة بتوقيت السيرفر في ورقة الأرشيف (اختيارية)
function fixPastArchiveTimestamps() {
  var ss = SpreadsheetApp.openById(TEMPLATE_FILE_ID);
  var sheet = ss.getSheetByName("الأرشيف");
  var lastRow = sheet.getLastRow();
  
  if (lastRow > 1) {
    var range = sheet.getRange(2, 1, lastRow - 1, 1);
    var values = range.getValues();
    
    for (var i = 0; i < values.length; i++) {
      var cellVal = values[i][0];
      if (cellVal) {
        var dateObj = new Date(cellVal);
        if (!isNaN(dateObj.getTime())) {
          values[i][0] = "'" + Utilities.formatDate(dateObj, "Asia/Riyadh", "dd/MM/yyyy HH:mm:ss");
        }
      }
    }
    range.setValues(values);
  }
}
