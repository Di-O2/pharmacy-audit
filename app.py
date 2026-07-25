import streamlit as st
import datetime
import streamlit.components.v1 as components

# إعدادات الصفحة
st.set_page_config(page_title="نظام التفتيش والتقييم الصيدلاني المباشر", page_icon="🏥", layout="wide")

# استدعاء خط تجوال العربي وضبط الاتجاه لمنع تقطيع الحروف
st.markdown("""
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap" rel="stylesheet">
        <style>
            html, body, [class*="css"], font, label, input, button {
                font-family: 'Tajawal', sans-serif !important;
                direction: rtl;
                text-align: right;
            }
            .stMetric { text-align: right; }
        </style>
    </head>
""", unsafe_allow_html=True)
import streamlit as st
import datetime
import streamlit.components.v1 as components

# إعدادات الصفحة
st.set_page_config(page_title="نظام التفتيش الصيدلاني المباشر", page_icon="🏥", layout="wide")

# تنسيق الواجهة باللغة العربية
st.markdown("""
    <style>
    body, div, h1, h2, h3, p, label { direction: rtl; text-align: right; }
    .stMetric { text-align: right; }
    </style>
""", unsafe_allow_html=True)

st.title("🏥 نظام التفتيش والتقييم الصيدلاني المباشر")
st.write("قم بتعبئة النموذج الميداني أدناه للحصول على التقييم الفوري وتوليد تقرير PDF مطبوع مباشرة دون الحاجة للتعامل مع الإكسل.")

st.divider()

# البيانات الأساسية (فارغة)
st.subheader("📌 البيانات الأساسية للزيارة التفتيشية")
c1, c2, c3 = st.columns(3)
with c1:
    center_name = st.text_input("اسم المركز الصحي", value="", placeholder="أدخل اسم المركز الصحي")
with c2:
    inspector_name = st.text_input("اسم المفتش الميداني", value="", placeholder="أدخل اسم المفتش الميداني")
with c3:
    inspection_date = st.date_input("تاريخ التفتيش", value=datetime.date.today())

st.divider()

# البنود الـ 38
items_data = [
    # محور 'رقيم' والسياسات العامة
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
    
    # محور غرفة الأدوية والصيدلية وغرفة الطوارئ
    ("17", "محور غرفة الأدوية والصيدلية وغرفة الطوارئ", "ضبط درجة حرارة الغرفة (18-25م) وتوفر سجل متابعة يومي."),
    ("18", "محور غرفة الأدوية والصيدلية وغرفة الطوارئ", "ترتيب الأدوية حسب الشكل الصيدلاني وتاريخ الصلاحية مع وضع التصنيف اللوني (Code Coloring)."),
    ("19", "محور غرفة الأدوية والصيدلية وغرفة الطوارئ", "تخزين أدوية LASA (المتشابهة شكلاً أو نطقا) وفصلها بلواصق تحذيرية."),
    ("20", "محور غرفة الأدوية والصيدلية وغرفة الطوارئ", "فصل الأدوية عالية الخطورة ووضع لواصق تعريفية."),
    ("21", "محور غرفة الأدوية والصيدلية وغرفة الطوارئ", "الالتزام باللواصق التعريفية للجرعات المتعددة بعد الفتح."),
    ("22", "محور غرفة الأدوية والصيدلية وغرفة الطوارئ", "وجود رف للأدوية قريبة الانتهاء توضح بها تاريخ الانتهاء الصريح."),
    ("23", "محور غرفة الأدوية والصيدلية وغرفة الطوارئ", "وجود جدول لثباتية الأدوية ذات الجرعات المتعددة."),
    ("24", "محور غرفة الأدوية والصيدلية وغرفة الطوارئ", "فصل الأدوية عن المواد الكيميائية وأدوات النظافة."),
    
    # الثلاجة الطبية
    ("25", "الثلاجة الطبية", "مطابقة الثلاجة للمعايير وضبط درجات الحرارة الخاصة بحفظ الأدوية المبردة (2 إلى 8 درجات)على مدار 24 ساعة."),
    ("26", "الثلاجة الطبية", "وجود جهاز رقمي معتمد ومثبت لقياس درجات الحرارة والرطوبة داخل الثلاجة."),
    ("27", "الثلاجة الطبية", "تثبيت قائمة محدثة بالأدوية المبردة على باب الثلاجة."),
    ("28", "الثلاجة الطبية", "الإلتزام بوضع لواصق تعريفية للأدوية المفتوحة داخل الثلاجة."),
    ("29", "الثلاجة الطبية", "الإلتزام بوضع لواصق عالية الخطورة و LASA على الأدوية المبردة الخاصة بها."),
    ("30", "الثلاجة الطبية", "فصل الادوية عن اللقاحات والأمصال."),
    
    # محور عربة الطوارئ والحقيبة الإسعافية
    ("31", "محور عربة الطوارئ والحقيبة الإسعافية", "توفر مؤشر واستمارت اكتمال أدوية الطوارئ وجاهزيتها بنسبة 100% بداخل المركز."),
    ("32", "محور عربة الطوارئ والحقيبة الإسعافية", "سلامة وجاهزية الحقيبة الإسعافية."),
    ("33", "محور عربة الطوارئ والحقيبة الإسعافية", "وجود جهاز قياس درجة الحرارة والرطوبة مخصص لغرفة الطوارئ لضمان سلامة الأدوية."),
    ("34", "محور عربة الطوارئ والحقيبة الإسعافية", "توفر نموذج عربة الطوارئ."),
    ("35", "محور عربة الطوارئ والحقيبة الإسعافية", "توفر جميع الأدوية المطلوبة مع مقارنة قائمة الجرعات بالأدوية المتوفرة."),
    ("36", "محور عربة الطوارئ والحقيبة الإسعافية", "ترتيب الأدوية بشكل قياسي وواضح لسرعة الوصول."),
    ("37", "محور عربة الطوارئ والحقيبة الإسعافية", "الإلتزام بتوفير الكميات المطلوبة وعدم وجود أدوية زائدة أو منتهية الصلاحية."),
    ("38", "محور عربة الطوارئ والحقيبة الإسعافية", "اكتمال محاضر الفتح والأقفال البلاستيكية.")
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
                        index=None,  # يبدأ فارغاً بدون تحديد
                        horizontal=True,
                        key=f"status_{num}",
                        label_visibility="collapsed"
                    )
                with col_note:
                    note = st.text_input(
                        f"ملاحظة البند {num}",
                        placeholder="ملاحظات المفتش (إن وجدت)",
                        key=f"note_{num}",
                        label_visibility="collapsed"
                    )
                responses.append({
                    'id': num,
                    'section': sec_name,
                    'criterion': crit,
                    'status': status,
                    'notes': note
                })
    
    submit_btn = st.form_submit_button("🚀 اعتماد التفتيش وإصدار التقرير", use_container_width=True)

if submit_btn:
    total_score = 0.0
    matched_cnt = 0
    partial_cnt = 0
    unmatched_cnt = 0
    
    for r in responses:
        st_val = r['status']
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
    display_inspector = inspector_name if inspector_name.strip() else "غير محدد"
    
    st.success("تم حساب النتائج وإصدار التقرير بنجاح!")
    
    st.subheader("📊 ملخص نتائج التقييم")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🏥 المركز الصحي", display_center)
    m2.metric("👨‍⚕️ المفتش الميداني", display_inspector)
    m3.metric("📅 تاريخ التفتيش", str(inspection_date))
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
            body {{ font-family: Arial, sans-serif; padding: 20px; direction: rtl; text-align: right; }}
            .header {{ background-color: #1A5276; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
            th {{ background-color: #f2f2f2; }}
            .warning {{ color: #d35400; font-weight: bold; }}
            .danger {{ color: #c0392b; font-weight: bold; }}
            .print-btn {{ background-color: #27ae60; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; margin-bottom: 15px; }}
        </style>
    </head>
    <body>
        <button class="print-btn" onclick="window.print()">🖨️ اضغط هنا للطباعة أو الحفظ كـ PDF</button>
        <hr>
        <div class="header">
            <h2>🏥 تقرير التفتيش الصيدلاني الدوري</h2>
            <p><strong>اسم المركز:</strong> {display_center} | <strong>المفتش الميداني:</strong> {display_inspector} | <strong>التاريخ:</strong> {inspection_date}</p>
            <p><strong>نسبة الامتثال الإجمالية:</strong> {compliance_rate:.2f}%</p>
        </div>
        
        <h3>📋 تفاصيل بنود التفتيش والملاحظات:</h3>
    """

    for sec_name, items in sections.items():
        html_report += f"<h4>🔹 {sec_name}</h4><table><tr><th>م</th><th>المعيار</th><th>الحالة</th><th>ملاحظات المفتش</th></tr>"
        sec_responses = [r for r in responses if r['section'] == sec_name]
        for it in sec_responses:
            st_text = it['status'] if it['status'] else "غير محدد"
            status_class = "warning" if st_text == 'جزئي' else ("danger" if st_text in ['غير مطابق', 'غير محدد'] else "")
            html_report += f"<tr><td>{it['id']}</td><td>{it['criterion']}</td><td class='{status_class}'>{st_text}</td><td>{it['notes']}</td></tr>"
        html_report += "</table>"

    html_report += "</body></html>"

    components.html(html_report, height=700, scrolling=True)
