import streamlit as st
import requests

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="المصحف المعلم - متعدد القراء",
    page_icon="🕌",
    layout="centered"
)

# --- تنسيق التصميم (CSS) ---
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    .stSelectbox, .stNumberInput, .stButton { direction: rtl; }
    
    /* تنسيق الآية */
    .quran-text {
        font-family: 'Amiri', serif;
        font-size: 32px;
        color: #0d47a1;
        text-align: center;
        background-color: #f5f7fa;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid #e3e6e8;
    }
    
    /* تنسيق صندوق التفسير */
    .tafsir-box {
        background-color: #fff9c4;
        border-right: 6px solid #fbc02d;
        padding: 20px;
        border-radius: 8px;
        margin-top: 15px;
        font-size: 18px;
        line-height: 1.8;
    }
    </style>
    """, unsafe_allow_html=True)

# --- قائمة القراء المعتمدة ---
RECITERS = {
    "الشيخ مشاري العفاسي (الكويت)": "ar.alafasy",
    "الشيخ محمد صديق المنشاوي (مصر - مجود)": "ar.minshawi",
    "الشيخ محمود خليل الحصري (مصر - مرتل)": "ar.husary",
    "القارئ شهريار برهيزقار (إيران)": "ar.parhizgar"
}

# --- العمليات الخلفية (Backend) ---

@st.cache_data
def get_surahs():
    """جلب قائمة السور"""
    try:
        resp = requests.get("http://api.alquran.cloud/v1/surah")
        if resp.status_code == 200:
            data = resp.json()['data']
            return {s['name']: s['number'] for s in data}, data
    except:
        return {}, []
    return {}, []

def get_ayah_data(surah_num, ayah_num, reciter_id):
    """جلب البيانات بناءً على القارئ المختار"""
    try:
        # رابط الصوت حسب القارئ المختار
        url_text = f"http://api.alquran.cloud/v1/ayah/{surah_num}:{ayah_num}/{reciter_id}"
        # رابط التفسير الميسر
        url_tafsir = f"http://api.alquran.cloud/v1/ayah/{surah_num}:{ayah_num}/ar.muyassar"
        
        r1 = requests.get(url_text).json()
        r2 = requests.get(url_tafsir).json()

        if r1['code'] == 200 and r2['code'] == 200:
            return {
                "text": r1['data']['text'],
                "audio": r1['data']['audio'],
                "tafsir": r2['data']['text'],
                "surah": r1['data']['surah']['name']
            }
    except:
        return None
    return None

# --- واجهة المستخدم (UI) ---

st.title("🕌 المصحف المعلم")
st.caption("اختر القارئ، السورة، ورقم الآية")

# 1. قائمة اختيار القارئ
selected_reciter_name = st.selectbox("🎙️ اختر القارئ:", list(RECITERS.keys()))
reciter_id = RECITERS[selected_reciter_name]

st.markdown("---")

# 2. تحميل السور واختيار الآية
surah_map, surah_list = get_surahs()

if surah_map:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        sel_surah = st.selectbox("اختر السورة:", list(surah_map.keys()))
        s_num = surah_map[sel_surah]
        limit = next((x['numberOfAyahs'] for x in surah_list if x['number'] == s_num), 286)
        
    with col2:
        a_num = st.number_input("رقم الآية:", 1, limit, 1)

    if st.button("عرض واستماع", use_container_width=True):
        
        with st.spinner('جاري التحميل...'):
            data = get_ayah_data(s_num, a_num, reciter_id)
            
            if data:
                # عرض النص
                st.markdown(f'<div class="quran-text">{data["text"]}</div>', unsafe_allow_html=True)
                
                # مشغل الصوت
                st.audio(data['audio'])
                
                # عرض التفسير
                st.markdown("### 📚 التفسير الميسر:")
                st.markdown(f'<div class="tafsir-box">{data["tafsir"]}</div>', unsafe_allow_html=True)
            else:
                st.error("حدث خطأ في جلب البيانات، يرجى المحاولة مرة أخرى.")

else:
    st.error("تأكد من اتصالك بالإنترنت.")

st.markdown("---")
st.markdown("*تم التطوير باستخدام Python & Streamlit*")
st.markdown("**@boood0003**")
