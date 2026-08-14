from datetime import datetime
import json
import os
import zoneinfo
import requests
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. إعدادات الصفحة الرسمية والتوقيت الزمني للسعودية
# ==========================================
st.set_page_config(
    page_title="تقرير الزيارة الميدانية | إدارة الخدمات الصيدلانية",
    page_icon="🏥",
    layout="wide",
)

# ضبط توقيت المملكة العربية السعودية (توقيت الرياض)
saudi_tz = zoneinfo.ZoneInfo("Asia/Riyadh")
saudi_now = datetime.now(saudi_tz)

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwNVcGm7Ct1YiI9ZxXziNHyTKjpkOTkthkkaD1JvyY1DL4airewyogDV727XUweCLXJ/exec"

# ==========================================
# 2. تنسيق الخطوط وإزالة الإطارات والهلامات والشارات نهائياً
# ==========================================
st.markdown(
    """
    <style>
        /* 1. إخفاء الشريط العلوي والمنيو والهيدر والفوتر */
        header, footer, #MainMenu, 
        [data-testid="stHeader"], 
        [data-testid="stFooter"], 
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stBottom"],
        [data-testid="stBottomBlockContainer"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }

        /* 2. إخفاء الشارات العائمة السفلية (Hosted with Streamlit / شارة GitHub) */
        div[class*="viewerBadge"],
        div[class*="viewerBadge_container"],
        div[class*="styles_viewerBadge"],
        div[class*="StyledAppViewerFooter"],
        div[class*="AppViewerFooter"],
        div[class*="stAppFooter"],
        .stAppDeployButton,
        .stAppFooter,
        a[href*="streamlit.io"],
        a[aria-label*="Streamlit"],
        div:has(> a[href*="streamlit.io"]),
        div:has(> [class*="viewerBadge"]) {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
            height: 0 !important;
            width: 0 !important;
        }

        /* 3. إخفاء العناصر العائمة بأسفل الشاشة على الجوال */
        div[style*="position: fixed"][style*="bottom"],
        div[style*="position: fixed"][style*="bottom: 0px"],
        div[style*="position: fixed"][style*="bottom: 0"],
        div[style*="bottom: 0px"],
        div[style*="bottom: 0"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* 4. إزالة الإطارات الخارجية والحدود الرمادية والهلامات من القوائم والبنود */
        div[data-testid="stExpander"],
        div[data-testid="stExpander"] details,
        div[data-testid="stExpander"] details summary,
        div[data-testid="stForm"],
        div[data-testid="stVerticalBlock"] > div:has(div.stRadio),
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
            border-radius: 0px !important;
        }

        /* 5. ضبط خلفية ونظافة القوائم المنسدلة */
        div[data-testid="stExpander"] details summary {
            border-bottom: 1px solid #e2e8f0 !important;
            padding: 10px 0 !important;
        }

        /* 6. إخفاء تعليمات الإدخال الإنجليزية */
        div[data-testid="stInputInstructions"],
        [data-testid="InputInstructions"],
        small[data-testid="stWidgetInstructions"] {
            display: none !important;
        }

        /* 7. ضبط الخطوط والاتجاه من اليمين لليسار */
        html, body, [class*="css"], font, label, input, button, select, p, div, h1, h2, h3 {
            font-family: 'Calibri', 'Segoe UI', 'Arial', sans-serif !important;
            direction: rtl;
            text-align: right;
        }
        .stMetric { text-align: right; }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 3. عرض الترويسة الرئيسية
# ==========================================
header_files = [
    "header.PNG",
    "header.png",
    "HEADER.PNG",
    "header.jpg",
    "header.jpeg",
    "IMG_3602.PNG",
]
image_found = False
for img_file in header_files:
    if os.path.exists(img_file):
        st.image(img_file, use_container_width=True)
        image_found = True
        break

if not image_found:
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #0b192c 0%, #1e3e62 50%, #001427 100%);
            border: 2px solid #d4af37;
            border-radius: 16px;
            padding: 25px 30px;
            color: white;
            font-family: 'Calibri', 'Segoe UI', Arial, sans-serif;
            direction: rtl;
            text-align: right;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        ">
            <div style="border-bottom: 1px solid rgba(212, 175, 55, 0.4); padding-bottom: 12px; margin-bottom: 15px;">
                <span style="background: linear-gradient(90deg, #d4af37, #f3e5ab); color: #0b192c; font-size: 15px; font-weight: bold; padding: 4px 14px; border-radius: 6px; font-family: Calibri, sans-serif;">🏛️ التجمع الصحي الثاني</span>
                <div style="font-size: 22px; font-weight: bold; color: #ffffff; margin-top: 10px; font-family: Calibri, sans-serif;">إدارة الخدمات الصيدلانية لمراكز الرعاية الصحية الأولية</div>
            </div>
            <div style="margin-bottom: 15px;">
                <span style="font-size: 36px; font-weight: bold; color: #ffffff; font-family: Calibri, sans-serif;">تقرير الزيارة الميدانية</span>
            </div>
            <div style="font-size: 16px; color: #cbd5e1; margin-bottom: 15px; font-family: Calibri, sans-serif;">
                المنصة الرقمية الموحدة لتقييم مؤشرات الامتثال الصيدلاني والتفتيش الفني المباشر.
            </div>
            <div>
                <span style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.25); color: white; padding: 5px 14px; border-radius: 8px; font-size: 14px; font-family: Calibri, sans-serif; margin-left: 8px;">📊 تقييم امتثال فوري</span>
                <span style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.25); color: white; padding: 5px 14px; border-radius: 8px; font-size: 14px; font-family: Calibri, sans-serif;">🖨️ تقارير PDF مباشرة</span>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

st.write(
    "قم بتعبئة النموذج الميداني أدناه للحصول على التقييم الفوري وتوليد تقرير PDF مطبوع مباشرة دون الحاجة للتعامل مع الإكسل."
)
st.divider()

# ==========================================
# 4. البيانات الأساسية للزيارة التفتيشية
# ==========================================
st.subheader("📌 البيانات الأساسية للزيارة التفتيشية")
c1, c2, c3 = st.columns(3)
with c1:
    center_name = st.text_input(
        "اسم المركز الصحي", value="", placeholder="أدخل اسم المركز الصحي"
    )
with c2:
    inspector_name = st.text_input(
        "اسم المفتش الميداني",
        value="",
        placeholder="أدخل اسم المفتش الميداني",
    )
with c3:
    inspection_date = st.date_input(
        "تاريخ التفتيش",
        value=saudi_now.date(),
        min_value=saudi_now.date(),
        format="YYYY/MM/DD",
    )

st.divider()

# ==========================================
# 5. بنود التقييم الـ 38 (Pharmacy Audit)
# ==========================================
items_data = [
    (
        "1",
        "محور 'رقيم' والسياسات العامة",
        "مطابقة الجرد الفعلي للأدوية مع النظام الإلكتروني رقيم.",
    ),
    (
        "2",
        "محور 'رقيم' والسياسات العامة",
        "معالجة وصرف جميع الوصفات الطبية عبر نظام رقيم من قبل مسؤول غرفة الأدوية.",
    ),
    (
        "3",
        "محور 'رقيم' والسياسات العامة",
        "توفر سياسات صيدلانية محدثة ومعتمدة بالمراكز الصحية وتوفر BNF.",
    ),
    (
        "4",
        "محور 'رقيم' والسياسات العامة",
        "ساعات العمل مثبتة على الباب الخارجي مع ملصق ممنوع الأكل والتدخين.",
    ),
    ("5", "محور 'رقيم' والسياسات العامة", "توفر الهيكل التنظيمي العام والخاص."),
    ("6", "محور 'رقيم' والسياسات العامة", "وجود الرؤية والرسالة الخاصة."),
    (
        "7",
        "محور 'رقيم' والسياسات العامة",
        "توفر قائمة بالامتيازات للأطباء وقائمة الاختصارات المسموحة والممنوعة.",
    ),
    (
        "8",
        "محور 'رقيم' والسياسات العامة",
        "وجود قائمة للإتصال بمعلومات الأدويه والسموم.",
    ),
    (
        "9",
        "محور 'رقيم' والسياسات العامة",
        "وجود قائمة محدثة بالمخزون وقائمة المصرح لهم بدخول الصيدلية (خلال الدوام وخارجه).",
    ),
    (
        "10",
        "محور 'رقيم' والسياسات العامة",
        "توفر قائمة LASA وقائمة الأدوية عالية الخطورة.",
    ),
    (
        "11",
        "محور 'رقيم' والسياسات العامة",
        "وجود جدول لثباتية الأدوية ذات الجرعات المتعددة.",
    ),
    (
        "12",
        "محور 'رقيم' والسياسات العامة",
        "وجود قائمة المصرح لهم بكتابة الوصفة الطبية المخدرة.",
    ),
    (
        "13",
        "محور 'رقيم' والسياسات العامة",
        "وجود قائمة للمصرح لهم بحمل مفتاح خزنة الأدوية المخدرة.",
    ),
    (
        "14",
        "محور 'رقيم' والسياسات العامة",
        "توفر ملف مخصص لإتلاف الأدوية وتوثيق تعاميم السحب (Recall).",
    ),
    (
        "15",
        "محور 'رقيم' والسياسات العامة",
        "توفر وتوثيق المؤشرات الصفرية (الأخطاء الدوائية والتفاعلات العكسية).",
    ),
    (
        "16",
        "محور 'رقيم' والسياسات العامة",
        "توفر مؤشرات واستمارة اكتمال الوصفة الطبية ومؤشر الهدف الثالث.",
    ),
    (
        "17",
        "محور غرفة الأدوية والصيدلية وغرفة الطوارئ",
        "ضبط درجة حرارة الغرفة (18-25م) وتوفر سجل متابعة يومي.",
    ),
    (
        "18",
        "محور غرفة الأدوية والصيدلية وغرفة الطوارئ",
        "ترتيب الأدوية حسب الشكل الصيدلاني وتاريخ الصلاحية مع وضع التصنيف اللوني (Code Coloring).",
    ),
    (
        "19",
        "محور غرفة الأدوية والصيدلية وغرفة الطوارئ",
        "تخزين أدوية LASA (المتشابهة شكلاً أو نطقا) وفصلها بلواصق تحذيرية.",
    ),
    (
        "20",
        "محور غرفة الأدوية والصيدلية وغرفة الطوارئ",
        "فصل الأدوية عالية الخطورة ووضع لواصق تعريفية.",
    ),
    (
        "21",
        "محور غرفة الأدوية والصيدلية وغرفة الطوارئ",
        "الالتزام باللواصق التعريفية للجرعات المتعددة بعد الفتح.",
    ),
    (
        "22",
        "محور غرفة الأدوية والصيدلية وغرفة الطوارئ",
        "وجود رف للأدوية قريبة الانتهاء توضح بها تاريخ الانتهاء الصريح.",
    ),
    (
        "23",
        "محور غرفة الأدوية والصيدلية وغرفة الطوارئ",
        "وجود جدول لثباتية الأدوية ذات الجرعات المتعددة.",
    ),
    (
        "24",
        "محور غرفة الأدوية والصيدلية وغرفة الطوارئ",
        "فصل الأدوية عن المواد الكيميائية وأدوات النظافة.",
    ),
    (
        "25",
        "الثلاجة الطبية",
        "مطابقة الثلاجة للمعايير وضبط درجات الحرارة الخاصة بحفظ الأدوية المبردة (2 إلى 8 درجات)على مدار 24 ساعة.",
    ),
    (
        "26",
        "الثلاجة الطبية",
        "وجود جهاز رقمي معتمد ومثبت لقياس درجات الحرارة والرطوبة داخل الثلاجة.",
    ),
    (
        "27",
        "الثلاجة الطبية",
        "تثبيت قائمة محدثة بالأدوية المبردة على باب الثلاجة.",
    ),
    (
        "28",
        "الثلاجة الطبية",
        "الإلتزام بوضع لواصق تعريفية للأدوية المفتوحة داخل الثلاجة.",
    ),
    (
        "29",
        "الثلاجة الطبية",
        "الإلتزام بوضع لواصق عالية الخطورة و LASA على الأدوية المبردة الخاصة بها.",
    ),
    ("30", "الثلاجة الطبية", "فصل الادوية عن اللقاحات والأمصال."),
    (
        "31",
        "محور عربة الطوارئ والحقيبة الإسعافية",
        "توفر مؤشر واستمارت اكتمال أدوية الطوارئ وجاهزيتها بنسبة 100% بداخل المركز.",
    ),
    (
        "32",
        "محور عربة الطوارئ والحقيبة الإسعافية",
        "سلامة وجاهزية الحقيبة الإسعافية.",
    ),
    (
        "33",
        "محور عربة الطوارئ والحقيبة الإسعافية",
        "وجود جهاز قياس درجة الحرارة والرطوبة مخصص لغرفة الطوارئ لضمان سلامة الأدوية.",
    ),
    (
        "34",
        "محور عربة الطوارئ والحقيبة الإسعافية",
        "توفر نموذج عربة الطوارئ.",
    ),
    (
        "35",
        "محور عربة الطوارئ والحقيبة الإسعافية",
        "توفر جميع الأدوية المطلوبة مع مقارنة قائمة الجرعات بالأدوية المتوفرة.",
    ),
    (
        "36",
        "محور عربة الطوارئ والحقيبة الإسعافية",
        "ترتيب الأدوية بشكل قياسي وواضح لسرعة الوصول.",
    ),
    (
        "37",
        "محور عربة الطوارئ والحقيبة الإسعافية",
        "الإلتزام بتوفير الكميات المطلوبة وعدم وجود أدوية زائدة أو منتهية الصلاحية.",
    ),
    (
        "38",
        "محور عربة الطوارئ والحقيبة الإسعافية",
        "اكتمال محاضر الفتح والأقفال البلاستيكية.",
    ),
]

sections = {}
for num, sec, crit in items_data:
    sections.setdefault(sec, []).append((num, crit))

st.subheader("📋 نموذج تقييم بنود التفتيش الفني")

responses = []

with st.form("inspection_form"):
    for sec_name, items in sections.items():
        with st.expander(f"🔹 {sec_name} ({len(items)} بند)", expanded=True):
            for num, crit in items:
                col_crit, col_status, col_note = st.columns([4, 3, 3])
                with col_crit:
                    st.markdown(f"**{num}.** {crit}")
                with col_status:
                    status = st.radio(
                        f"حالة البند {num}",
                        ["مطابق", "جزئي", "غير مطابق"],
                        index=None,
                        horizontal=True,
                        key=f"status_{num}",
                        label_visibility="collapsed",
                    )
                with col_note:
                    note = st.text_input(
                        f"ملاحظة البند {num}",
                        placeholder="ملاحظات المفتش (إن وجدت)",
                        key=f"note_{num}",
                        label_visibility="collapsed",
                    )
                responses.append({
                    "id": int(num),
                    "section": sec_name,
                    "criterion": crit,
                    "status": status,
                    "notes": note,
                })

    submit_btn = st.form_submit_button(
        "🚀 اعتماد التفتيش وإصدار التقرير", use_container_width=True
    )

# ==========================================
# 6. معالجة النتائج وإصدار التقرير
# ==========================================
if submit_btn:
    total_score = 0.0
    matched_cnt = 0
    partial_cnt = 0
    unmatched_cnt = 0

    for r in responses:
        st_val = r["status"]
        if st_val == "مطابق":
            total_score += 1.0
            matched_cnt += 1
        elif st_val == "جزئي":
            total_score += 0.5
            partial_cnt += 1
        else:
            unmatched_cnt += 1

    compliance_rate = (total_score / len(responses)) * 100
    display_center = center_name if center_name.strip() else "غير محدد"
    display_inspector = (
        inspector_name if inspector_name.strip() else "غير محدد"
    )
    
    current_saudi_time = datetime.now(saudi_tz)
    formatted_time_str = current_saudi_time.strftime("%I:%M %p")

    axis_summary = {
        "axis1": {
            "total": 16,
            "matched": sum(
                1 for r in responses[:16] if r["status"] == "مطابق"
            ),
            "partial": sum(1 for r in responses[:16] if r["status"] == "جزئي"),
            "unmatched": sum(
                1
                for r in responses[:16]
                if r["status"] in ["غير مطابق", None]
            ),
        },
        "axis2": {
            "total": 8,
            "matched": sum(
                1 for r in responses[16:24] if r["status"] == "مطابق"
            ),
            "partial": sum(
                1 for r in responses[16:24] if r["status"] == "جزئي"
            ),
            "unmatched": sum(
                1
                for r in responses[16:24]
                if r["status"] in ["غير مطابق", None]
            ),
        },
        "axis3": {
            "total": 6,
            "matched": sum(
                1 for r in responses[24:30] if r["status"] == "مطابق"
            ),
            "partial": sum(
                1 for r in responses[24:30] if r["status"] == "جزئي"
            ),
            "unmatched": sum(
                1
                for r in responses[24:30]
                if r["status"] in ["غير مطابق", None]
            ),
        },
        "axis4": {
            "total": 8,
            "matched": sum(
                1 for r in responses[30:38] if r["status"] == "مطابق"
            ),
            "partial": sum(
                1 for r in responses[30:38] if r["status"] == "جزئي"
            ),
            "unmatched": sum(
                1
                for r in responses[30:38]
                if r["status"] in ["غير مطابق", None]
            ),
        },
    }

    if GOOGLE_SCRIPT_URL:
        payload = {
            "center_name": display_center,
            "inspector_name": display_inspector,
            "inspection_date": str(inspection_date),
            "inspection_time": formatted_time_str,
            "compliance_rate": f"{compliance_rate:.2f}",
            "matched_cnt": matched_cnt,
            "partial_cnt": partial_cnt,
            "unmatched_cnt": unmatched_cnt,
            "responses": responses,
            "axis_summary": axis_summary,
        }
        try:
            headers = {"Content-Type": "application/json"}
            res = requests.post(
                GOOGLE_SCRIPT_URL,
                data=json.dumps(payload),
                headers=headers,
                timeout=30,
            )
            if res.status_code in [200, 302]:
                st.success(
                    "✅ تم حفظ التقرير بصفحتين في Google Drive وإرسال رابط"
                    " الملف فوراً!"
                )
            else:
                st.warning(
                    "⚠️ تم حساب النتائج وتوليد التقرير محلياً (استجابة"
                    f" السكريبت: {res.status_code})."
                )
        except Exception:
            st.warning("⚠️ تم حساب النتائج وتوليد التقرير المطبوع محلياً.")

    st.subheader("📊 ملخص نتائج التقييم")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🏥 المركز الصحي", display_center)
    m2.metric("👨‍⚕️ المفتش الميداني", display_inspector)
    m3.metric(
        "📅 تاريخ ووقت التفتيش",
        f"{inspection_date.strftime('%Y/%m/%d')} ({formatted_time_str})",
    )
    m4.metric("📈 نسبة الامتثال الإجمالية", f"{compliance_rate:.2f}%")

    c1, c2, c3 = st.columns(3)
    c1.success(f"✅ مطابق: {matched_cnt}")
    c2.warning(f"⚠️ جزئي: {partial_cnt}")
    c3.error(f"❌ غير مطابق / لم يحدد: {unmatched_cnt}")

    st.divider()

    st.subheader("🖨️ التقرير المطبوع (PDF)")

    html_report = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Calibri', Arial, sans-serif; padding: 20px; direction: rtl; text-align: right; }}
            .header {{ background-color: #0b192c; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-right: 6px solid #d4af37; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
            th {{ background-color: #f2f2f2; }}
            .warning {{ color: #d35400; font-weight: bold; }}
            .danger {{ color: #c0392b; font-weight: bold; }}
            .print-btn {{ background-color: #1e3e62; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; margin-bottom: 15px; }}
        </style>
    </head>
    <body>
        <button class="print-btn" onclick="window.print()">🖨️ اضغط هنا للطباعة أو الحفظ كـ PDF</button>
        <hr>
        <div class="header">
            <p style="font-size:14px; color:#f3e5ab; margin-bottom:5px;">🏛️ التجمع الصحي الثاني - إدارة الخدمات الصيدلانية لمراكز الرعاية الصحية الأولية</p>
            <h2>تقرير الزيارة الميدانية</h2>
            <p><strong>اسم المركز:</strong> {display_center} | <strong>المفتش الميداني:</strong> {display_inspector} | <strong>التاريخ والوقت:</strong> {inspection_date.strftime('%Y/%m/%d')} - {formatted_time_str}</p>
            <p><strong>نسبة الامتثال الإجمالية:</strong> {compliance_rate:.2f}%</p>
        </div>
        
        <h3>📋 تفاصيل بنود التفتيش والملاحظات:</h3>
    """

    for sec_name, items in sections.items():
        html_report += f"<h4>🔹 {sec_name}</h4><table><tr><th>م</th><th>المعيار</th><th>الحالة</th><th>ملاحظات المفتش</th></tr>"
        sec_responses = [r for r in responses if r["section"] == sec_name]
        for it in sec_responses:
            st_text = it["status"] if it["status"] else "غير محدد"
            status_class = (
                "warning"
                if st_text == "جزئي"
                else (
                    "danger"
                    if st_text in ["غير مطابق", "غير محدد"]
                    else ""
                )
            )
            html_report += f"<tr><td>{it['id']}</td><td>{it['criterion']}</td><td class='{status_class}'>{st_text}</td><td>{it['notes']}</td></tr>"
        html_report += "</table>"

    html_report += "</body></html>"

    components.html(html_report, height=700, scrolling=True)

# ==========================================
# 7. تذييل الصفحة الرسمي
# ==========================================
st.markdown("---")
st.caption(
    "إدارة الخدمات الصيدلانية لمراكز الرعاية الصحية الأولية - تجمع الرياض الصحي الثاني"
)
