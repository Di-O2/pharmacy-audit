from datetime import datetime
import base64
import json
import os
import uuid
import zoneinfo
import requests
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. إعدادات الصفحة الرسمية والتوقيت الزمني للسعودية
# ==========================================
OFFICIAL_REPORT_TITLE = "تقرير الزيارة الميدانية | إدارة الخدمات الصيدلانية"
OFFICIAL_FOOTER = "إدارة الخدمات الصيدلانية لمراكز الرعاية الصحية الأولية - تجمع الرياض الصحي الثاني"
TOTAL_AUDIT_ITEMS = 38
NEAR_EXPIRY_ITEM_ID = 39
NEAR_EXPIRY_SECTION = "محور مخزن الأدوية"
NEAR_EXPIRY_MAX_ITEMS = 30

st.set_page_config(
    page_title=OFFICIAL_REPORT_TITLE,
    page_icon="🏥",
    layout="wide",
)

# ----------------------------------------------------
# وسوم تحسين معاينة الرابط والصورة على واتساب (Open Graph)
# ----------------------------------------------------
OG_IMAGE_URL = "https://raw.githubusercontent.com/Di-02/pharmacy-audit/main/header.PNG"

meta_tags = f"""
    <!-- Open Graph / WhatsApp Preview -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://pharmacy-audit.streamlit.app/">
    <meta property="og:title" content="تقرير الزيارة الميدانية | إدارة الخدمات الصيدلانية">
    <meta property="og:description" content="المنصة الرقمية الموحدة لتقييم الامتثال الصيدلاني والتفتيش الفني المباشر">
    <meta property="og:image" content="{OG_IMAGE_URL}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
"""
st.markdown(meta_tags, unsafe_allow_html=True)

saudi_tz = zoneinfo.ZoneInfo("Asia/Riyadh")
saudi_now = datetime.now(saudi_tz)

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyP4fuoXF_VFeeEaOQV3DaGZO0XGsKVDiOxvPrGG5Q0wk0RpbHaNvSX4PSEDZIxWXGb/exec"
SPREADSHEET_ID = "1QBq_OUsbNsc3lklC8_tvFAygRhlaT7MKZ6yMyiyLkNw"

# ==========================================
# 2. خط Cairo وإخفاء شوائب Streamlit وتحسين الكاردات
# ==========================================
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

        header, footer, #MainMenu,
        [data-testid="stHeader"],
        [data-testid="stFooter"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stBottom"],
        [data-testid="stBottomBlockContainer"],
        [data-testid="manage-app-button"],
        .stDeployButton,
        .stAppDeployButton {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }

        div[class*="viewerBadge"],
        div[class*="viewerBadge_container"],
        div[class*="styles_viewerBadge"],
        div[class*="StyledAppViewerFooter"],
        div[class*="AppViewerFooter"],
        div[class*="stAppFooter"],
        div[class*="manageApp"],
        div[class*="FloatingContainer"],
        [data-testid="stActionButton"],
        a[href*="streamlit.io"],
        a[href*="github.com"],
        a[aria-label*="Streamlit"],
        a[aria-label*="GitHub"],
        div:has(> a[href*="streamlit.io"]),
        div:has(> a[href*="github.com"]),
        div:has(> [class*="viewerBadge"]) {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
            height: 0 !important;
            width: 0 !important;
        }

        div[style*="position: fixed"][style*="bottom"],
        div[style*="position: fixed"][style*="bottom: 0px"],
        div[style*="position: fixed"][style*="bottom: 0"],
        div[style*="bottom: 0px"],
        div[style*="bottom: 0"] {
            display: none !important;
            visibility: hidden !important;
        }

        html, body, [data-testid="stAppViewContainer"], .stApp,
        p, label, input, button, select, textarea, h1, h2, h3, h4,
        [data-testid="stMarkdownContainer"],
        [data-testid="stWidgetLabel"],
        [data-testid="stCaptionContainer"] {
            font-family: 'Cairo', 'Segoe UI', 'Arial', sans-serif !important;
            direction: rtl !important;
            text-align: right !important;
        }

        .stMetric { text-align: right; }

        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stWidgetLabel"] p,
        [data-testid="stCaptionContainer"],
        [data-testid="stHorizontalBlock"] {
            direction: rtl !important;
            text-align: right !important;
            unicode-bidi: isolate;
            width: 100%;
        }

        .item-criterion {
            font-family: 'Cairo', sans-serif !important;
            direction: rtl !important;
            text-align: right !important;
            unicode-bidi: isolate;
            width: 100%;
            margin: 0;
            line-height: 1.85;
        }

        [data-testid="stExpanderToggleIcon"],
        [data-testid="stExpander"] summary svg,
        [data-testid="stExpander"] summary [data-testid="stIcon"],
        [data-testid="stExpander"] summary [data-testid="stIconMaterial"],
        [data-testid="stExpander"] summary span[translate="no"] {
            display: none !important;
        }

        .material-symbols-rounded,
        .material-symbols-outlined,
        .material-icons,
        span[class*="material"] {
            font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
            direction: ltr !important;
        }

        div[data-testid="stInputInstructions"],
        [data-testid="InputInstructions"],
        small[data-testid="stWidgetInstructions"] {
            display: none !important;
        }

        [data-testid="stImage"] {
            display: flex !important;
            justify-content: center !important;
            margin: 0 auto 8px !important;
        }

        [data-testid="stImage"] img {
            max-width: min(720px, 88vw) !important;
            width: 100% !important;
            height: auto !important;
            margin: 0 auto !important;
            border-radius: 16px !important;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.10) !important;
        }

        .official-title {
            font-family: 'Cairo', sans-serif !important;
            font-size: 28px;
            font-weight: 700;
            text-align: center;
            margin: 8px 0 6px;
            line-height: 1.6;
        }

        .official-subtitle {
            font-family: 'Cairo', sans-serif !important;
            text-align: center;
            color: #64748b;
            font-size: 15px;
            margin-bottom: 18px;
        }

        .fallback-header {
            background: linear-gradient(135deg, #0b192c 0%, #1e3e62 50%, #001427 100%);
            border: 1px solid rgba(212, 175, 55, 0.7);
            border-radius: 16px;
            padding: 24px 28px;
            color: white;
            direction: rtl;
            text-align: center;
            margin: 0 auto 22px;
            max-width: 920px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.18);
        }

        [data-testid="stMarkdownContainer"] .hero-card {
            position: relative;
            direction: rtl !important;
            text-align: center !important;
            color: #f8fafc;
            background:
                radial-gradient(900px 220px at 100% 0%, rgba(255, 255, 255, 0.14), transparent 58%),
                linear-gradient(165deg, #1e7596 0%, #155974 48%, #0e4156 100%);
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 22px;
            padding: 16px 22px 26px;
            margin: 2px auto 8px;
            max-width: 1040px;
            box-shadow: 0 18px 42px rgba(8, 28, 40, 0.30);
            overflow: hidden;
        }

        [data-testid="stMarkdownContainer"] .hero-logo-row {
            display: flex !important;
            direction: rtl !important;
            justify-content: flex-start !important;
            margin: 2px 4px 10px;
        }

        [data-testid="stMarkdownContainer"] .hero-logo {
            width: 236px;
            max-width: 46vw;
            height: auto;
            display: block;
            background: transparent;
            opacity: 0.96;
        }

        [data-testid="stMarkdownContainer"] .hero-org,
        [data-testid="stMarkdownContainer"] .hero-title,
        [data-testid="stMarkdownContainer"] .hero-desc,
        [data-testid="stMarkdownContainer"] .hero-en,
        [data-testid="stMarkdownContainer"] .hero-chip {
            font-family: 'Cairo', sans-serif !important;
            color: #f8fafc !important;
            text-align: center !important;
            margin: 0;
        }

        [data-testid="stMarkdownContainer"] .hero-org {
            font-size: 26px;
            font-weight: 700;
            line-height: 1.55;
            margin-top: 2px;
        }

        [data-testid="stMarkdownContainer"] .hero-en {
            direction: ltr !important;
            unicode-bidi: isolate;
            font-weight: 600;
            letter-spacing: 0.1px;
        }

        [data-testid="stMarkdownContainer"] .hero-org-en {
            font-size: 15px;
            opacity: 0.92;
            margin-top: 4px;
        }

        [data-testid="stMarkdownContainer"] .hero-rule {
            width: 64px;
            height: 3px;
            border-radius: 99px;
            margin: 16px auto 14px;
            background: rgba(255, 255, 255, 0.62);
        }

        [data-testid="stMarkdownContainer"] .hero-kicker {
            font-size: 20px;
            margin-top: 2px;
        }

        [data-testid="stMarkdownContainer"] .hero-title {
            font-size: 40px;
            font-weight: 700;
            line-height: 1.35;
            margin-top: 2px;
        }

        [data-testid="stMarkdownContainer"] .hero-desc {
            font-size: 16px;
            line-height: 1.7;
            opacity: 0.94;
            margin-top: 8px;
        }

        [data-testid="stMarkdownContainer"] .hero-chips {
            display: flex !important;
            direction: rtl !important;
            justify-content: center !important;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 18px;
        }

        [data-testid="stMarkdownContainer"] .hero-chip {
            display: inline-flex !important;
            direction: rtl !important;
            align-items: center;
            gap: 8px;
            border: 1px solid rgba(255, 255, 255, 0.28);
            background: rgba(7, 36, 52, 0.28);
            border-radius: 12px;
            padding: 8px 16px;
            font-size: 15px;
            font-weight: 600;
            line-height: 1.4;
        }

        [data-testid="stMarkdownContainer"] .hero-chip svg {
            display: block;
            flex: 0 0 auto;
        }

        @media (max-width: 760px) {
            [data-testid="stMarkdownContainer"] .hero-org {
                font-size: 20px;
            }
            [data-testid="stMarkdownContainer"] .hero-title {
                font-size: 30px;
            }
            [data-testid="stMarkdownContainer"] .hero-org-en,
            [data-testid="stMarkdownContainer"] .hero-desc,
            [data-testid="stMarkdownContainer"] .hero-kicker {
                font-size: 14px;
            }
        }

        .section-card,
        div[data-testid="stExpander"] {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(148, 163, 184, 0.28) !important;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06) !important;
            border-radius: 14px !important;
        }

        div[data-testid="stExpander"] details,
        div[data-testid="stExpander"] details summary {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
        }

        div[data-testid="stExpander"] details summary {
            display: block !important;
            border-bottom: 1px solid rgba(148, 163, 184, 0.18) !important;
            padding: 12px 12px 12px 36px !important;
            direction: rtl !important;
            text-align: right !important;
            position: relative !important;
            unicode-bidi: isolate !important;
        }

        div[data-testid="stExpander"] details summary p,
        div[data-testid="stExpander"] details summary span,
        div[data-testid="stExpander"] details summary div {
            font-family: 'Cairo', sans-serif !important;
            direction: rtl !important;
            text-align: right !important;
            unicode-bidi: isolate;
        }

        div[data-testid="stExpander"] details summary::after {
            content: "▾";
            position: absolute;
            left: 12px;
            right: auto;
            top: 50%;
            transform: translateY(-50%);
            font-family: 'Cairo', sans-serif !important;
            font-size: 16px;
            pointer-events: none;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stTextArea"] textarea {
            border: 1px solid rgba(148, 163, 184, 0.35) !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04) !important;
            direction: rtl !important;
            text-align: right !important;
        }

        div[data-testid="stDateInput"] input {
            border: 1px solid rgba(148, 163, 184, 0.35) !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04) !important;
            direction: ltr !important;
            text-align: left !important;
        }

        [data-testid="stExpander"] details,
        [data-testid="stExpanderDetails"],
        [data-testid="stDateInput"] {
            overflow: visible !important;
        }

        [data-baseweb="popover"],
        [data-baseweb="calendar"] {
            z-index: 1000002 !important;
            direction: ltr !important;
        }

        [data-testid="stRadio"],
        [data-testid="stRadio"] > div {
            direction: rtl !important;
            text-align: right !important;
        }

        [data-testid="stTextArea"] textarea {
            min-height: 120px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
        }

        .official-footer {
            font-family: 'Cairo', sans-serif !important;
            text-align: center;
            font-size: 14px;
            color: #64748b;
            padding: 22px 8px 30px;
            margin-top: 18px;
            border-top: 1px solid rgba(148, 163, 184, 0.22);
        }

        .item-row {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 12px;
            padding: 10px 12px;
            margin-bottom: 10px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 3. عرض الترويسة الرئيسية
# ==========================================
def cluster_logo_data_uri():
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "cluster_logo_light.png")
    if not os.path.exists(logo_path):
        return ""
    with open(logo_path, "rb") as logo_file:
        encoded = base64.b64encode(logo_file.read()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


logo_uri = cluster_logo_data_uri()
if logo_uri:
    st.markdown(
        f"""
        <div class="hero-card" dir="rtl">
            <div class="hero-logo-row">
                <img class="hero-logo" src="{logo_uri}" alt="شعار تجمع الرياض الصحي الثاني">
            </div>
            <div class="hero-org">إدارة الخدمات الصيدلانية لمراكز الرعاية الصحية الأولية</div>
            <div class="hero-en hero-org-en">Pharmaceutical Services Management - Primary Healthcare Centers</div>
            <div class="hero-rule"></div>
            <div class="hero-en hero-kicker">Field Visit Report</div>
            <div class="hero-title">تقرير الزيارة الميدانية</div>
            <div class="hero-desc">المنصة الرقمية الموحدة لتقييم مؤشرات الامتثال الصيدلاني والتفتيش الفني المباشر</div>
            <div class="hero-chips">
                <span class="hero-chip">
                    <span>تقييم امتثال فوري</span>
                    <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true">
                        <rect x="1" y="9" width="4" height="8" rx="1" fill="#34d399"></rect>
                        <rect x="7" y="5" width="4" height="12" rx="1" fill="#60a5fa"></rect>
                        <rect x="13" y="1" width="4" height="16" rx="1" fill="#f87171"></rect>
                    </svg>
                </span>
                <span class="hero-chip">
                    <span>تقارير <span dir="ltr">PDF</span> مباشرة</span>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#e2e8f0" stroke-width="1.8" aria-hidden="true">
                        <path d="M6 9V3h12v6"></path>
                        <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
                        <rect x="6" y="14" width="12" height="7" rx="1"></rect>
                    </svg>
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"""
        <div class="fallback-header">
            <div style="font-size: 15px; color: #f3e5ab; margin-bottom: 10px;">تجمع الرياض الصحي الثاني</div>
            <div style="font-size: 28px; font-weight: 700;">{OFFICIAL_REPORT_TITLE}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    '<p class="official-subtitle">أدخل بيانات الزيارة وبنود التفتيش، ثم اعتمد النموذج لإصدار التقييم الفوري والتقرير المطبوع.</p>',
    unsafe_allow_html=True,
)

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
        "اسم المُفتش الميداني",
        value="",
        placeholder="أدخل اسم المُفتش الميداني",
    )
with c3:
    inspection_date = st.date_input(
        "تاريخ التفتيش",
        value=saudi_now.date(),
        format="YYYY/MM/DD",
    )

# ==========================================
# 5. بنود التقييم الـ 39
# ==========================================
items_data = [
    ("1", "محور 'رقيم' والسياسات العامة", "مطابقة الجرد الفعلي للأدوية مع النظام الإلكتروني رقيم."),
    ("2", "محور 'رقيم' والسياسات العامة", "معالجة وصرف جميع الوصفات الطبية عبر نظام رقيم من قبل مسؤول غرفة الأدوية."),
    ("3", "محور 'رقيم' والسياسات العامة", "توفر سياسات صيدلانية محدثة ومعتمدة بالمراكز الصحية وتوفر BNF."),
    ("4", "محور 'رقيم' والسياسات العامة", "ساعات العمل مثبتة على الباب الخارجي مع ملصق ممنوع الأكل والتدخين."),
    ("5", "محور 'رقيم' والسياسات العامة", "توفر الهيكل التنظيمي العام والخاص."),
    ("6", "محور 'رقيم' والسياسات العامة", "وجود الرؤية والرسالة الخاصة."),
    ("7", "محور 'رقيم' والسياسات العامة", "توفر قائمة بالامتيازات للأطباء وقائمة الاختصارات المسموحة والممنوعة."),
    ("8", "محور 'رقيم' والسياسات العامة", "وجود قائمة للإتصال بمعلومات الأدويه والسموم."),
    ("9", "محور 'رقيم' والسياسات العامة", "وجود قائمة محدثة بالمخزون وقائمة المصرح لهم بدخول الصيدلية (خلال الدوام وخارجه)."),
    ("10", "محور 'رقيم' والسياسات العامة", "توفر قائمة LASA وقائمة الأدوية عالية الخطورة."),
    ("11", "محور 'رقيم' والسياسات العامة", "وجود جدول لثباتية الأدوية ذات الجرعات المتعددة."),
    ("12", "محور 'رقيم' والسياسات العامة", "وجود قائمة المصرح لهم بكتابة الوصفة الطبية المخدرة."),
    ("13", "محور 'رقيم' والسياسات العامة", "وجود قائمة للمصرح لهم بحمل مفتاح خزنة الأدوية المخدرة."),
    ("14", "محور 'رقيم' والسياسات العامة", "توفر ملف مخصص لإتلاف الأدوية وتوثيق تعاميم السحب (Recall)."),
    ("15", "محور 'رقيم' والسياسات العامة", "توفر وتوثيق المؤشرات الصفرية (الأخطاء الدوائية والتفاعلات العكسية)."),
    ("16", "محور 'رقيم' والسياسات العامة", "توفر مؤشرات واستمارة اكتمال الوصفة الطبية ومؤشر الهدف الثالث."),
    ("17", "محور غرفة الأدوية والصيدلية وغرفة الطوارئ", "ضبط درجة حرارة الغرفة (18-25م) وتوفر سجل متابعة يومي."),
    ("18", "محور غرفة الأدوية والصيدلية وغرفة الطوارئ", "ترتيب الأدوية حسب الشكل الصيدلاني وتاريخ الصلاحية مع وضع التصنيف اللوني (Code Coloring)."),
    ("19", "محور غرفة الأدوية والصيدلية وغرفة الطوارئ", "تخزين أدوية LASA (المتشابهة شكلاً أو نطقا) وفصلها بلواصق تحذيرية."),
    ("20", "محور غرفة الأدوية والصيدلية وغرفة الطوارئ", "فصل الأدوية عالية الخطورة ووضع لواصق تعريفية."),
    ("21", "محور غرفة الأدوية والصيدلية وغرفة الطوارئ", "الالتزام باللواصق التعريفية للجرعات المتعددة بعد الفتح."),
    ("22", "محور غرفة الأدوية والصيدلية وغرفة الطوارئ", "وجود رف للأدوية قريبة الانتهاء توضح بها تاريخ الانتهاء الصريح."),
    ("23", "محور غرفة الأدوية والصيدلية وغرفة الطوارئ", "وجود جدول لثباتية الأدوية ذات الجرعات المتعددة."),
    ("24", "محور غرفة الأدوية والصيدلية وغرفة الطوارئ", "فصل الأدوية عن المواد الكيميائية وأدوات النظافة."),
    ("25", "محور الثلاجة الطبية", "مطابقة الثلاجة للمعايير وضبط درجات الحرارة الخاصة بحفظ الأدوية المبردة (2 إلى 8 درجات)على مدار 24 ساعة."),
    ("26", "محور الثلاجة الطبية", "وجود جهاز رقمي معتمد ومثبت لقياس درجات الحرارة والرطوبة داخل الثلاجة."),
    ("27", "محور الثلاجة الطبية", "تثبيت قائمة محدثة بالأدوية المبردة على باب الثلاجة."),
    ("28", "محور الثلاجة الطبية", "الإلتزام بوضع لواصق تعريفية للأدوية المفتوحة داخل الثلاجة."),
    ("29", "محور الثلاجة الطبية", "الإلتزام بوضع لواصق عالية الخطورة و LASA على الأدوية المبردة الخاصة بها."),
    ("30", "محور الثلاجة الطبية", "فصل الادوية عن اللقاحات والأمصال."),
    ("31", "محور عربة الطوارئ والحقيبة الإسعافية", "توفر مؤشر واستمارت اكتمال أدوية الطوارئ وجاهزيتها بنسبة 100% بداخل المركز."),
    ("32", "محور عربة الطوارئ والحقيبة الإسعافية", "سلامة وجاهزية الحقيبة الإسعافية."),
    ("33", "محور عربة الطوارئ والحقيبة الإسعافية", "وجود جهاز قياس درجة الحرارة والرطوبة مخصص لغرفة الطوارئ لضمان سلامة الأدوية."),
    ("34", "محور عربة الطوارئ والحقيبة الإسعافية", "توفر نموذج عربة الطوارئ."),
    ("35", "محور عربة الطوارئ والحقيبة الإسعافية", "توفر جميع الأدوية المطلوبة مع مقارنة قائمة الجرعات بالأدوية المتوفرة."),
    ("36", "محور عربة الطوارئ والحقيبة الإسعافية", "ترتيب الأدوية بشكل قياسي وواضح لسرعة الوصول."),
    ("37", "محور عربة الطوارئ والحقيبة الإسعافية", "الإلتزام بتوفير الكميات المطلوبة وعدم وجود أدوية زائدة أو منتهية الصلاحية."),
    ("38", "محور عربة الطوارئ والحقيبة الإسعافية", "اكتمال محاضر الفتح والأقفال البلاستيكية."),
    ("39", NEAR_EXPIRY_SECTION, "وجود أصناف دوائية قاربت على انتهاء الصلاحية (Near-Expiry)"),
]

sections = {}
for num, sec, crit in items_data:
    sections.setdefault(sec, []).append((num, crit))


def collect_near_expiry_items():
    status_value = st.session_state.get("status_39")
    if status_value != "يوجد":
        return []
    raw_count = st.session_state.get("near_exp_count", 0) or 0
    item_count = int(raw_count)
    collected_items = []
    for slot in range(1, item_count + 1):
        drug_name = str(st.session_state.get(f"near_exp_name_{slot}", "") or "").strip()
        quantity = str(st.session_state.get(f"near_exp_qty_{slot}", "") or "").strip()
        expiry_date = format_expiry_date(st.session_state.get(f"near_exp_date_{slot}"))
        if drug_name or quantity or expiry_date:
            collected_items.append({
                "slot": slot,
                "drug_name_strength": drug_name,
                "quantity": quantity,
                "expiry_date": expiry_date,
            })
    return collected_items


def format_expiry_date(raw_value):
    if raw_value is None:
        return ""
    if hasattr(raw_value, "strftime"):
        return raw_value.strftime("%Y/%m/%d")
    return str(raw_value).strip()


def format_item_count_label(count):
    if count == 1:
        return "بند واحد فقط"
    if count == 2:
        return "بندان"
    if 3 <= count <= 10:
        return f"{count} بنود"
    return f"{count} بنداً"


def format_near_expiry_notes(collected_items, inspector_notes=""):
    note_lines = []
    for item in collected_items:
        note_lines.append(
            f"{item['slot']}. {item['drug_name_strength']} — الكمية: {item['quantity']} — تاريخ الانتهاء: {item['expiry_date']}"
        )
    extra_text = str(inspector_notes or "").strip()
    if extra_text:
        note_lines.append(f"ملاحظات المُفتش: {extra_text}")
    return "\n".join(note_lines)


st.subheader("📋 نموذج تقييم بنود التفتيش الفني")

responses = []

for sec_name, items in sections.items():
    with st.expander(f"\u200f{sec_name}  ·  {format_item_count_label(len(items))}", expanded=True):
        for num, crit in items:
            item_id = int(num)
            criterion_html = (
                f'<p class="item-criterion" dir="rtl"><strong>{num}.</strong> {crit}</p>'
            )
            if item_id == NEAR_EXPIRY_ITEM_ID:
                col_crit, col_status = st.columns([5, 3])
                with col_crit:
                    st.markdown(criterion_html, unsafe_allow_html=True)
                with col_status:
                    status = st.radio(
                        f"حالة البند {num}",
                        ["يوجد", "لا يوجد"],
                        index=None,
                        horizontal=True,
                        key=f"status_{num}",
                        label_visibility="collapsed",
                    )

                near_expiry_items = []
                inspector_near_notes = ""
                if status == "يوجد":
                    count_col, inspector_note_col = st.columns([1, 2])
                    with count_col:
                        item_count = st.number_input(
                            "عدد الأصناف",
                            min_value=1,
                            max_value=NEAR_EXPIRY_MAX_ITEMS,
                            value=1,
                            step=1,
                            key="near_exp_count",
                        )
                    with inspector_note_col:
                        inspector_near_notes = st.text_input(
                            "ملاحظات المُفتش (إن وجدت)",
                            placeholder="أدخل ملاحظة المُفتش على هذه الأصناف إن وجدت",
                            key="near_exp_inspector_notes",
                        )
                    header_c1, header_c2, header_c3, header_c4 = st.columns([1, 4, 2, 3])
                    header_c1.markdown('<p class="item-criterion" dir="rtl"><strong>م</strong></p>', unsafe_allow_html=True)
                    header_c2.markdown('<p class="item-criterion" dir="rtl"><strong>اسم الدواء والتركيز</strong></p>', unsafe_allow_html=True)
                    header_c3.markdown('<p class="item-criterion" dir="rtl"><strong>الكمية</strong></p>', unsafe_allow_html=True)
                    header_c4.markdown('<p class="item-criterion" dir="rtl"><strong>تاريخ الانتهاء</strong></p>', unsafe_allow_html=True)
                    for slot in range(1, int(item_count) + 1):
                        slot_c1, slot_c2, slot_c3, slot_c4 = st.columns([1, 4, 2, 3])
                        with slot_c1:
                            st.markdown(f'<p class="item-criterion" dir="rtl">{slot}</p>', unsafe_allow_html=True)
                        with slot_c2:
                            st.text_input(
                                f"اسم الدواء والتركيز {slot}",
                                placeholder="مثال: باراسيتامول 500 ملغ",
                                key=f"near_exp_name_{slot}",
                                label_visibility="collapsed",
                            )
                        with slot_c3:
                            st.text_input(
                                f"كمية الصنف {slot}",
                                placeholder="الكمية",
                                key=f"near_exp_qty_{slot}",
                                label_visibility="collapsed",
                            )
                        with slot_c4:
                            st.date_input(
                                f"تاريخ انتهاء الصنف {slot}",
                                value=None,
                                format="YYYY/MM/DD",
                                key=f"near_exp_date_{slot}",
                                label_visibility="collapsed",
                            )
                    near_expiry_items = collect_near_expiry_items()

                responses.append({
                    "id": item_id,
                    "section": sec_name,
                    "criterion": crit,
                    "status": status,
                    "notes": format_near_expiry_notes(near_expiry_items, inspector_near_notes),
                    "near_expiry_items": near_expiry_items,
                })
            else:
                col_crit, col_status, col_note = st.columns([4, 3, 3])
                with col_crit:
                    st.markdown(criterion_html, unsafe_allow_html=True)
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
                        placeholder="ملاحظات المُفتش (إن وجدت)",
                        key=f"note_{num}",
                        label_visibility="collapsed",
                    )
                responses.append({
                    "id": item_id,
                    "section": sec_name,
                    "criterion": crit,
                    "status": status,
                    "notes": note,
                })

general_notes = st.text_area(
    "الملاحظات فيما يخص جميع البنود",
    placeholder="أي ملاحظات عامة أو توصيات ختامية، أو لأي بند من البنود لم يُذكر سابقاً",
    height=120,
    key="general_notes_audit",
)

if "report_issued" not in st.session_state:
    st.session_state.report_issued = False
if "awaiting_reissue_confirm" not in st.session_state:
    st.session_state.awaiting_reissue_confirm = False
if "issue_report_now" not in st.session_state:
    st.session_state.issue_report_now = False
if "submit_request_id" not in st.session_state:
    st.session_state.submit_request_id = ""

submit_btn = st.button(
    "🚀 اعتماد التفتيش وإصدار التقرير",
    use_container_width=True,
    type="primary",
)

if submit_btn and not st.session_state.report_issued:
    st.session_state.submit_request_id = str(uuid.uuid4())
    st.session_state.issue_report_now = True
elif submit_btn and st.session_state.report_issued:
    st.session_state.awaiting_reissue_confirm = True

if st.session_state.awaiting_reissue_confirm and not st.session_state.issue_report_now:
    st.warning("تم إصدار التقرير مسبقاً. هل تريد تأكيد إصداره مرة أخرى؟")
    confirm_col, cancel_col = st.columns(2)
    with confirm_col:
        if st.button("موافق", type="primary", use_container_width=True, key="confirm_reissue_btn"):
            st.session_state.submit_request_id = str(uuid.uuid4())
            st.session_state.awaiting_reissue_confirm = False
            st.session_state.issue_report_now = True
            st.rerun()
    with cancel_col:
        if st.button("إلغاء", use_container_width=True, key="cancel_reissue_btn"):
            st.session_state.awaiting_reissue_confirm = False
            st.rerun()

# ==========================================
# 6. معالجة النتائج وإصدار التقرير
# ==========================================
if st.session_state.issue_report_now:
    st.session_state.issue_report_now = False
    st.session_state.awaiting_reissue_confirm = False
    near_expiry_items = collect_near_expiry_items()
    formatted_near_notes = format_near_expiry_notes(
        near_expiry_items,
        st.session_state.get("near_exp_inspector_notes", ""),
    )
    for r in responses:
        if r["id"] == NEAR_EXPIRY_ITEM_ID:
            r["near_expiry_items"] = near_expiry_items
            r["notes"] = formatted_near_notes

    # حصر التقييم وحساب النقاط على أول 38 بنداً فقط وعزل البند 39 اللوجستي
    total_score = 0.0
    matched_cnt = 0
    partial_cnt = 0
    unmatched_cnt = 0

    for r in responses:
        item_id = int(r["id"])
        if item_id == NEAR_EXPIRY_ITEM_ID:
            continue  # استبعاد تام من معادلة الدرجات والعدادات
        st_val = r.get("status")
        if st_val == "مطابق":
            total_score += 1.0
            matched_cnt += 1
        elif st_val == "جزئي":
            total_score += 0.5
            partial_cnt += 1
        else:
            unmatched_cnt += 1

    # حساب النسبة المئوية الدقيقة من أصل 38 مع سقف أقصى 100%
    raw_rate = (total_score / TOTAL_AUDIT_ITEMS) * 100 if TOTAL_AUDIT_ITEMS > 0 else 0.0
    compliance_rate = min(raw_rate, 100.0)

    display_center = center_name if center_name.strip() else "غير محدد"
    display_inspector = inspector_name if inspector_name.strip() else "غير محدد"
    current_saudi_time = datetime.now(saudi_tz)
    formatted_time_str = current_saudi_time.strftime("%I:%M %p")

    axis_summary = {
        "axis1": {
            "total": 16,
            "matched": sum(1 for r in responses[:16] if r["status"] == "مطابق"),
            "partial": sum(1 for r in responses[:16] if r["status"] == "جزئي"),
            "unmatched": sum(1 for r in responses[:16] if r["status"] in ["غير مطابق", None]),
        },
        "axis2": {
            "total": 8,
            "matched": sum(1 for r in responses[16:24] if r["status"] == "مطابق"),
            "partial": sum(1 for r in responses[16:24] if r["status"] == "جزئي"),
            "unmatched": sum(1 for r in responses[16:24] if r["status"] in ["غير مطابق", None]),
        },
        "axis3": {
            "total": 6,
            "matched": sum(1 for r in responses[24:30] if r["status"] == "مطابق"),
            "partial": sum(1 for r in responses[24:30] if r["status"] == "جزئي"),
            "unmatched": sum(1 for r in responses[24:30] if r["status"] in ["غير مطابق", None]),
        },
        "axis4": {
            "total": 8,
            "matched": sum(1 for r in responses[30:38] if r["status"] == "مطابق"),
            "partial": sum(1 for r in responses[30:38] if r["status"] == "جزئي"),
            "unmatched": sum(1 for r in responses[30:38] if r["status"] in ["غير مطابق", None]),
        },
    }

    if GOOGLE_SCRIPT_URL:
        payload = {
            "spreadsheet_id": SPREADSHEET_ID,
            "official_report_title": OFFICIAL_REPORT_TITLE,
            "total_items": TOTAL_AUDIT_ITEMS,
            "center_name": display_center,
            "inspector_name": display_inspector,
            "request_id": st.session_state.get("submit_request_id") or str(uuid.uuid4()),
            "inspection_date": inspection_date.strftime("%Y/%m/%d"),
            "inspection_time": formatted_time_str,
            "compliance_rate": f"{compliance_rate:.2f}",
            "matched_cnt": matched_cnt,
            "partial_cnt": partial_cnt,
            "unmatched_cnt": unmatched_cnt,
            "general_notes": general_notes,
            "near_expiry_items": near_expiry_items,
            "responses": responses,
            "axis_summary": axis_summary,
        }

        with st.spinner("⏳ جاري توليد التقرير التنفيذي، والأرشفة في قوقل درايف، وإرسال الإشعار البريدي... يُرجى الانتظار ثوانٍ"):
            try:
                headers = {"Content-Type": "application/json"}
                res = requests.post(
                    GOOGLE_SCRIPT_URL,
                    data=json.dumps(payload),
                    headers=headers,
                    timeout=60,
                )
                if res.status_code in [200, 302]:
                    st.session_state.report_issued = True
                    st.success("🎉 تم اعتماد التفتيش وتوليد التقرير الميداني بنجاح تام!")
                    st.balloons()
                else:
                    st.warning(f"⚠️ استجابة السكريبت: رمز الحالة {res.status_code}")
            except requests.exceptions.Timeout:
                st.session_state.report_issued = True
                st.warning("⚠️ استغرق إنشاء التقرير وقتاً أطول من المعتاد بسبب ضغط خوادم قوقل، والعملية جارية في الخلفية. يرجى مراجعة بريدك الإلكتروني.")
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء الاتصال: {e}")

    st.subheader("📊 ملخص نتائج التقييم")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🏥 المركز الصحي", display_center)
    m2.metric("👨‍⚕️ المُفتش الميداني", display_inspector)
    m3.metric(
        "📅 تاريخ ووقت التفتيش",
        f"{inspection_date.strftime('%Y/%m/%d')} ({formatted_time_str})",
    )
    m4.metric("📈 نسبة الامتثال الإجمالية", f"{compliance_rate:.2f}%")

    c1, c2, c3 = st.columns(3)
    c1.success(f"✅ مطابق: {matched_cnt} من أصل {TOTAL_AUDIT_ITEMS}")
    c2.warning(f"⚠️ جزئي: {partial_cnt}")
    c3.error(f"❌ غير مطابق / لم يحدد: {unmatched_cnt}")

    display_notes_html = (
        f"<div style='background:#f8fafc; border-right:4px solid #1e3e62; padding:10px; margin-top:15px; border-radius:8px;'><strong>📝 الملاحظات فيما يخص جميع البنود:</strong><br>{general_notes}</div>"
        if general_notes.strip()
        else ""
    )

    html_report = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Cairo', Arial, sans-serif; padding: 20px; direction: rtl; text-align: right; }}
            .header {{ background-color: #0b192c; color: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-right: 6px solid #d4af37; box-shadow: 0 6px 16px rgba(15, 23, 42, 0.12); }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
            th {{ background-color: #f2f2f2; }}
            .info {{ color: #1e7596; font-weight: bold; }}
            .warning {{ color: #d35400; font-weight: bold; }}
            .danger {{ color: #c0392b; font-weight: bold; }}
            .print-btn {{ background-color: #1e3e62; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 8px; cursor: pointer; margin-bottom: 15px; }}
            .report-footer {{ text-align: center; margin-top: 24px; color: #64748b; font-size: 13px; }}
        </style>
    </head>
    <body>
        <button class="print-btn" onclick="window.print()">🖨️ اضغط هنا للطباعة أو الحفظ كـ PDF</button>
        <hr>
        <div class="header">
            <h2>{OFFICIAL_REPORT_TITLE}</h2>
            <p><strong>اسم المركز:</strong> {display_center} | <strong>المُفتش الميداني:</strong> {display_inspector} | <strong>التاريخ والوقت:</strong> {inspection_date.strftime('%Y/%m/%d')} - {formatted_time_str}</p>
            <p><strong>نسبة الامتثال الإجمالية:</strong> {compliance_rate:.2f}%</p>
        </div>
        {display_notes_html}
        <h3>📋 تفاصيل بنود التفتيش والملاحظات:</h3>
    """

    for sec_name, items in sections.items():
        html_report += f"<h4>🔹 {sec_name}</h4><table><tr><th>م</th><th>المعيار</th><th>الحالة</th><th>ملاحظات المُفتش</th></tr>"
        sec_responses = [r for r in responses if r["section"] == sec_name]
        for it in sec_responses:
            st_text = it["status"] if it["status"] else "غير محدد"
            if it["id"] == NEAR_EXPIRY_ITEM_ID:
                status_class = "info"
            else:
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
            if it["id"] == NEAR_EXPIRY_ITEM_ID and it.get("near_expiry_items"):
                html_report += (
                    "</table><h5>أصناف قريبة من انتهاء الصلاحية</h5>"
                    "<table><tr><th>م</th><th>اسم الدواء والتركيز</th><th>الكمية</th><th>تاريخ الانتهاء</th></tr>"
                )
                for near_item in it["near_expiry_items"]:
                    html_report += (
                        f"<tr><td>{near_item['slot']}</td>"
                        f"<td>{near_item['drug_name_strength']}</td>"
                        f"<td>{near_item['quantity']}</td>"
                        f"<td>{near_item['expiry_date']}</td></tr>"
                    )
        html_report += "</table>"

    html_report += f'<div class="report-footer">{OFFICIAL_FOOTER}</div></body></html>'

    st.subheader("🖨️ التقرير المطبوع (PDF)")
    components.html(html_report, height=700, scrolling=True)

# ==========================================
# 7. تذييل الصفحة الرسمي
# ==========================================
st.markdown(
    f'<div class="official-footer">{OFFICIAL_FOOTER}</div>',
    unsafe_allow_html=True,
)
