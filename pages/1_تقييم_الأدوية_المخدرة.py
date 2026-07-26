import streamlit as st
import datetime
import streamlit.components.v1 as components
import requests
import json

# رابط السكربت الخاص بك والمربوط بـ Google Drive (أضف الرابط هنا إن أردت ربطه التلقائي)
GOOGLE_SCRIPT_URL = ""

# إعدادات الصفحة الرسمية
st.set_page_config(
    page_title="تقرير الأدوية المخدرة والمؤثرات العقلية | إدارة الخدمات الصيدلانية", 
    page_icon="💊", 
    layout="wide"
)

# ضبط الخط الافتراضي للتطبيق كاملاً إلى Calibri والتجاه لليمين
st.markdown("""
    <style>
        html, body, [class*="css"], font, label, input, button, select, p, div, h1, h2, h3 {
            font-family: 'Calibri', 'Segoe UI', 'Arial', sans-serif !important;
            direction: rtl;
            text-align: right;
        }
        .stMetric { text-align: right; }
    </style>
""", unsafe_allow_html=True)

# ترويسة البانر الحكومي المعتمد
st.markdown("""
    <div style="
        background: linear-gradient(135deg, #052e24 0%, #004d40 45%, #00695c 100%);
        border: 2px solid #d4af37;
        border-radius: 16px;
        padding: 25px 30px;
        color: white;
        font-family: 'Calibri', 'Segoe UI', Arial, sans-serif;
        direction: rtl;
        text-align: right;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.25);
    ">
        <div style="border-bottom: 1px solid rgba(212, 175, 55, 0.4); padding-bottom: 12px; margin-bottom: 15px;">
            <span style="background: linear-gradient(90deg, #d4af37, #f3e5ab); color: #052e24; font-size: 15px; font-weight: bold; padding: 4px 14px; border-radius: 6px; font-family: Calibri, sans-serif;">🏛️ التجمع الصحي الثاني</span>
            <div style="font-size: 22px; font-weight: bold; color: #ffffff; margin-top: 10px; font-family: Calibri, sans-serif;">إدارة الخدمات الصيدلانية لمراكز الرعاية الصحية الأولية</div>
            <div style="font-size: 14px; color: #a3c9bc; direction: ltr; text-align: right; font-family: Calibri, sans-serif;">Department of Pharmaceutical Services - Primary Healthcare Centers</div>
        </div>
        <div style="margin-bottom: 15px;">
            <span style="font-size: 34px; font-weight: bold; color: #ffffff; font-family: Calibri, sans-serif;">تقرير تقييم الأدوية المخدرة والمؤثرات العقلية</span>
            <span style="font-size: 18px; font-weight: bold; color: #d4af37; direction: ltr; display: inline-block; margin-right: 15px; border-right: 2px solid rgba(255,255,255,0.3); padding-right: 15px; font-family: Calibri, sans-serif;">Narcotic & Controlled Substances Report</span>
        </div>
        <div style="font-size: 16px; color: #d0e8e0; margin-bottom: 15px; font-family: Calibri, sans-serif;">
            المنصة الرقمية الموحدة لتقييم ومتابعة امتثال ضوابط الأدوية المخدرة والمؤثرات العقلية.
        </div>
        <div>
            <span style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.25); color: white; padding: 5px 14px; border-radius: 8px; font-size: 14px; font-family: Calibri, sans-serif; margin-left: 8px;">📊 تقييم رقابي فوري</span>
            <span style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.25); color: white; padding: 5px 14px; border-radius: 8px; font-size: 14px; font-family: Calibri, sans-serif;">🖨️ تقارير PDF مباشرة</span>
        </div>
    </div>
""", unsafe_allow_html=True)

st.write("قم بتعبئة النموذج الميداني أدناه لتقييم ضوابط الأدوية المخدرة والحصول على التقييم الفوري وتوليد التقرير المطبوع مباشرة.")

st.divider()

# البيانات الأساسية
st.subheader("📌 البيانات الأساسية للزيارة التفتيشية")
c1, c2, c3 = st.columns(3)
with c1:
    center_name = st.text_input("اسم المركز الصحي", value="", placeholder="أدخل اسم المركز الصحي")
with c2:
    inspector_name = st.text_input("اسم المفتش الميداني", value="", placeholder="أدخل اسم المفتش الميداني")
with c3:
    inspection_date = st.date_input("تاريخ التفتيش", value=datetime.date.today())

st.divider()

# البنود الـ 13 الخاصة بالأدوية المخدرة والمؤثرات العقلية
items_data = [
    ("1", "محور الأدوية المخدرة والمؤثرات العقلية", "مطابقة إجراءات طلب واستلام الأدوية من الشركة الوطنية (نوبكو) للضوابط والتعاميم المعتمدة."),
    ("2", "محور الأدوية المخدرة والمؤثرات العقلية", "الالتزام بآلية توريد وتسليم الأدوية للمراكز الصحية التابعة وفق النموذج النظامي."),
    ("3", "محور الأدوية المخدرة والمؤثرات العقلية", "توفر وضبط آلية صرف وتسليم دفاتر الوصفات المقيدة للأدوية المخدرة للمراكز عند الاحتياج."),
    ("4", "محور الأدوية المخدرة والمؤثرات العقلية", "مطابقة المخزون الفعلي للأدوية المخدرة والتسجيل المنتظم بسجل العهدة الرسمي."),
    ("5", "محور الأدوية المخدرة والمؤثرات العقلية", "توفر وتوثيق سجل المتابعة والتدقيق اليومي للأدوية المخدرة بداخل المركز الصحي."),
    ("6", "محور الأدوية المخدرة والمؤثرات العقلية", "التوثيق النظامي واكتمال محاضر إتلاف الأمبولات الفارغة للأدوية المخدرة."),
    ("7", "محور الأدوية المخدرة والمؤثرات العقلية", "توثيق إتلاف المتبقي من الأدوية المستخدمة."),
    ("8", "محور الأدوية المخدرة والمؤثرات العقلية", "إجراء المطابقة الدورية، الجرد الفعلي، وتدوير المخزون (المدور) للمراكز الصحية."),
    ("9", "محور الأدوية المخدرة والمؤثرات العقلية", "توفر وتحديث محاضر تشكيل لجنة الوصف والصرف للأدوية المخدرة بالمراكز بصورة مستمرة."),
    ("10", "محور الأدوية المخدرة والمؤثرات العقلية", "توثيق محاضر اجتماعات لجنة الوصف والصرف للأدوية المخدرة (مرة واحدة سنوياً على الأقل)."),
    ("11", "محور الأدوية المخدرة والمؤثرات العقلية", "التحقق من اكتمال كافة البيانات الاشتراطية بالوصفة الطبية المخدرة قبل الصرف ومتابعة نواقصها."),
    ("12", "محور الأدوية المخدرة والمؤثرات العقلية", "متابعة تواريخ الصلاحية والالتزام باستبدال الأدوية المخدرة قريبة الانتهاء قبل (6 أشهر) من تاريخ انتهائها."),
    ("13", "محور الأدوية المخدرة والمؤثرات العقلية", "التوثيق الفوري والدقيق لكافة حركة الوارد والمنصرف بسجل العهدة الخاص بالأدوية المخدرة.")
]

sections = {}
for num, sec, crit in items_data:
    sections.setdefault(sec, []).append((num, crit))

st.subheader("📋 نموذج تقييم ضوابط الأدوية المخدرة والمؤثرات العقلية")

responses = []

with st.form("narcotic_inspection_form"):
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
                        key=f"status_narc_{num}",
                        label_visibility="collapsed"
                    )
                with col_note:
                    note = st.text_input(
                        f"ملاحظة البند {num}",
                        placeholder="ملاحظات المفتش (إن وجدت)",
                        key=f"note_narc_{num}",
                        label_visibility="collapsed"
                    )
                responses.append({
                    'id': int(num),
                    'section': sec_name,
                    'criterion': crit,
                    'status': status,
                    'notes': note
                })
    
    submit_btn = st.form_submit_button("🚀 اعتماد التقييم وإصدار التقرير", use_container_width=True)

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
    
    if GOOGLE_SCRIPT_URL:
        payload = {
            "center_name": display_center,
            "inspector_name": display_inspector,
            "inspection_date": str(inspection_date),
            "compliance_rate": f"{compliance_rate:.2f}",
            "matched_cnt": matched_cnt,
            "partial_cnt": partial_cnt,
            "unmatched_cnt": unmatched_cnt,
            "responses": responses
        }
        try:
            res = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=10)
            st.success("✅ تم حفظ التقرير وإرسال الإشعار بنجاح!")
        except Exception:
            st.warning("⚠️ تم حساب النتائج وتوليد التقرير المطبوع محلياً.")

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
            body {{ font-family: 'Calibri', Arial, sans-serif; padding: 20px; direction: rtl; text-align: right; }}
            .header {{ background-color: #052e24; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-right: 6px solid #d4af37; }}
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
            <p style="font-size:14px; color:#f3e5ab; margin-bottom:5px;">🏛️ التجمع الصحي الثاني - إدارة الخدمات الصيدلانية لمراكز الرعاية الصحية الأولية</p>
            <h2>تقرير تقييم الأدوية المخدرة والمؤثرات العقلية</h2>
            <p><strong>اسم المركز:</strong> {display_center} | <strong>المفتش الميداني:</strong> {display_inspector} | <strong>التاريخ:</strong> {inspection_date}</p>
            <p><strong>نسبة الامتثال الإجمالية:</strong> {compliance_rate:.2f}%</p>
        </div>
        
        <h3>📋 تفاصيل بنود تقييم الأدوية المخدرة والملاحظات:</h3>
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
