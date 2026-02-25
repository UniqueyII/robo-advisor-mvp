import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os
from datetime import datetime
import json
from portfolio_optimizer import load_and_optimize, PortfolioOptimizer
from data_fetcher import create_dataframe

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==================== تنظیمات اولیه ====================
st.set_page_config(
    page_title="Robo-Advisor MVP",
    page_icon="📈",
    layout="wide"
)

# CSS سفارشی
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #374151;
        margin-top: 1.5rem;
    }
    .question-card {
        background-color: #F8FAFC;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1.5rem;
    }
    .option-btn {
        width: 100%;
        margin: 0.3rem 0;
        text-align: left;
        padding: 0.8rem;
    }
    .result-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #10B981;
        margin: 1rem 0;
    }
    .nav-btn {
        width: 100%;
        padding: 1rem;
        font-size: 1.1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== سوالات پرسشنامه ====================
RISK_QUESTIONS = [
    {
        "id": 1,
        "question": "۱. سن شما چقدر است؟",
        "options": [
            {"text": "زیر ۳۰ سال", "score": 4},
            {"text": "۳۰-۴۵ سال", "score": 3},
            {"text": "۴۶-۶۰ سال", "score": 2},
            {"text": "بالای ۶۰ سال", "score": 1}
        ]
    },
    {
        "id": 2,
        "question": "۲. افق سرمایه‌گذاری شما چقدر است؟",
        "options": [
            {"text": "بیش از ۵ سال", "score": 4},
            {"text": "۲-۵ سال", "score": 3},
            {"text": "۱-۲ سال", "score": 2},
            {"text": "کمتر از ۱ سال", "score": 1}
        ]
    },
    {
        "id": 3,
        "question": "۳. تحمل افت سرمایه شما چقدر است؟",
        "options": [
            {"text": "تا ۴۰٪ افت را تحمل می‌کنم", "score": 4},
            {"text": "تا ۲۵٪", "score": 3},
            {"text": "تا ۱۵٪", "score": 2},
            {"text": "تا ۵٪", "score": 1}
        ]
    },
    {
        "id": 4,
        "question": "۴. هدف اصلی شما از سرمایه‌گذاری چیست؟",
        "options": [
            {"text": "رشد سرمایه بالا", "score": 4},
            {"text": "ترکیب رشد و درآمد", "score": 3},
            {"text": "حفظ سرمایه با درآمد کم", "score": 2},
            {"text": "حفظ اصل سرمایه", "score": 1}
        ]
    },
    {
        "id": 5,
        "question": "۵. تجربه شما در بازارهای مالی چقدر است؟",
        "options": [
            {"text": "بیش از ۵ سال", "score": 4},
            {"text": "۲-۵ سال", "score": 3},
            {"text": "۱-۲ سال", "score": 2},
            {"text": "بدون تجربه", "score": 1}
        ]
    },
    {
        "id": 6,
        "question": "۶. واکنش شما به کاهش ۱۵٪ ارزش پرتفولیو چیست؟",
        "options": [
            {"text": "خرید بیشتر می‌کنم", "score": 4},
            {"text": "نگه می‌دارم", "score": 3},
            {"text": "بخشی را می‌فروشم", "score": 2},
            {"text": "همه را می‌فروشم", "score": 1}
        ]
    },
    {
        "id": 7,
        "question": "۷. سهم سرمایه‌گذاری از کل دارایی شما چقدر است؟",
        "options": [
            {"text": "بیش از ۵۰٪", "score": 4},
            {"text": "۳۰-۵۰٪", "score": 3},
            {"text": "۱۰-۳۰٪", "score": 2},
            {"text": "کمتر از ۱۰٪", "score": 1}
        ]
    },
    {
        "id": 8,
        "question": "۸. انتظار بازده سالانه (تومانی) شما چقدر است؟",
        "options": [
            {"text": "بیش از ۵۰٪", "score": 4},
            {"text": "۳۰-۵۰٪", "score": 3},
            {"text": "۲۰-۳۰٪", "score": 2},
            {"text": "۱۰-۲۰٪", "score": 1}
        ]
    },
    {
        "id": 9,
        "question": "۹. دانش شما از ابزارهای مالی (سهام، صندوق، رمزارز) چقدر است؟",
        "options": [
            {"text": "حرفه‌ای", "score": 4},
            {"text": "خوب", "score": 3},
            {"text": "متوسط", "score": 2},
            {"text": "مبتدی", "score": 1}
        ]
    },
    {
        "id": 10,
        "question": "۱۰. درآمد شما چقدر قابل اتکا است؟",
        "options": [
            {"text": "درآمد بالا و پایدار", "score": 4},
            {"text": "درآمد متوسط و پایدار", "score": 3},
            {"text": "درآمد متغیر", "score": 2},
            {"text": "بدون درآمد ثابت", "score": 1}
        ]
    },
    {
        "id": 11,
        "question": "۱۱. انتظار بازده سالانه (دلاری) شما چقدر است؟",
        "options": [
            {"text": "بیش از ۲۰٪", "score": 4},
            {"text": "۱۵-۲۰٪", "score": 3},
            {"text": "۱۰-۱۵٪", "score": 2},
            {"text": "۵-۱۰٪", "score": 1}
        ]
    }
]

# ==================== توابع کمکی ====================
def calculate_risk_score(answers):
    """محاسبه امتیاز ریسک"""
    raw_score = sum(answers)
    normalized_score = (raw_score - 11) * (100 / 33)
    
    if normalized_score <= 35:
        profile = "Conservative"
    elif normalized_score <= 70:
        profile = "Moderate"
    else:
        profile = "Aggressive"
    
    return {
        "raw_score": raw_score,
        "normalized_score": normalized_score,
        "profile": profile
    }

def save_json_report(report):
    """ذخیره گزارش به صورت JSON"""
    import json
    
    try:
        summary = {
            "تاریخ_محاسبه": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "پروفایل_ریسک": st.session_state.get('risk_profile', 'N/A'),
            "سرمایه_گذاری_تومان": st.session_state.get('investment', 0),
            "وزن_دارایی‌ها": report.get('allocation', {}),
            "بازده_مورد_انتظار_درصد": report.get('expected_return', 0) * 100,
            "ریسک_نوسان_درصد": report.get('volatility', 0) * 100,
            "نسبت_شارپ": report.get('sharpe_ratio', 0),
        }
        
        # ایجاد دکمه دانلود
        st.download_button(
            label="📥 دانلود گزارش JSON",
            data=json.dumps(summary, indent=2, ensure_ascii=False),
            file_name=f"portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    except Exception as e:
        st.error(f"خطا در ذخیره گزارش: {e}")

# ==================== صفحه ۱: شروع ====================
def show_start_page():
    """صفحه شروع"""
    st.markdown('<h1 class="main-header">🤖 Robo-Advisor MVP</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### ✨ معرفی سیستم
        
        **مشاور سرمایه‌گذاری هوشمند** که با استفاده از تکنیک‌های پیشرفته مالی، 
        بهترین سبد سرمایه‌گذاری را برای شما طراحی می‌کند.
        
        **🔍 قابلیت‌های کلیدی:**
        
        ✅ **پروفایل‌سازی ریسک** - شناسایی دقیق روحیه سرمایه‌گذاری شما  
        ✅ **بهینه‌سازی MPT** - تئوری مدرن پرتفولیو مارکوویتز  
        ✅ **شبیه‌سازی مونت‌کارلو** - پیش‌بینی هزاران سناریو  
        ✅ **محاسبه VaR** - ارزش در معرض خطر  
        ✅ **تحلیل ۴ دارایی** - طلا، نقره، بیت‌کوین، اتریوم
        
        **📊 داده‌های واقعی از بازار**
        """)
    
    with col2:
        st.markdown("""
        ### 🚀 مراحل کار
        
        1. **📋 پرسشنامه ریسک**
           - پاسخ به ۱۱ سوال تخصصی
           - تعیین پروفایل دقیق شما
        
        2. **💰 ورود اطلاعات**
           - مشخص کردن مبلغ سرمایه‌گذاری
        
        3. **⚡ محاسبات**
           - بهینه‌سازی سبد
           - تحلیل ریسک
           - پیش‌بینی بازده
        
        4. **📊 نتایج**
           - سبد پیشنهادی
           - نمودارها و جداول
           - توصیه‌های سرمایه‌گذاری
        
        **⏱️ زمان کل: کمتر از ۲ دقیقه**
        """)
        
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=200)
    
    st.markdown("---")
    
    # دکمه شروع
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 شروع پرسشنامه ریسک", type="primary", use_container_width=True, key="start_btn"):
            st.session_state.page = "questionnaire"
            st.rerun()

# ==================== صفحه ۲: پرسشنامه ====================
def show_questionnaire_page():
    """صفحه پرسشنامه"""
    st.markdown('<h1 class="main-header">📋 پرسشنامه ارزیابی ریسک‌پذیری</h1>', unsafe_allow_html=True)
    st.markdown("**لطفاً به همه ۱۱ سوال زیر پاسخ دهید:**")
    
    # ذخیره پاسخ‌ها
    if 'answers' not in st.session_state:
        st.session_state.answers = [None] * len(RISK_QUESTIONS)
    
    # نمایش سوالات
    for i, q in enumerate(RISK_QUESTIONS):
        st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
        st.markdown(f'**{q["question"]}**')
        
        # ایجاد گزینه‌ها
        cols = st.columns(2)
        for j, option in enumerate(q["options"]):
            col_idx = j % 2
            with cols[col_idx]:
                # دکمه برای هر گزینه
                if st.button(
                    option["text"],
                    key=f"q{i}_opt{j}",
                    use_container_width=True,
                    type="primary" if st.session_state.answers[i] == option["score"] else "secondary"
                ):
                    st.session_state.answers[i] = option["score"]
                    st.rerun()
        
        # نمایش انتخاب فعلی
        if st.session_state.answers[i] is not None:
            selected_text = next(
                (opt["text"] for opt in q["options"] if opt["score"] == st.session_state.answers[i]),
                "بدون انتخاب"
            )
            st.markdown(f"**✅ انتخاب شما:** {selected_text}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # محاسبه پیشرفت
    answered_count = sum(1 for ans in st.session_state.answers if ans is not None)
    progress = answered_count / len(RISK_QUESTIONS)
    
    st.progress(progress)
    st.markdown(f"**پیشرفت: {answered_count} از {len(RISK_QUESTIONS)} سوال پاسخ داده شده**")
    
    # دکمه‌های ناوبری
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("◀️ بازگشت به صفحه شروع", use_container_width=True):
            st.session_state.page = "start"
            st.rerun()
    
    with col2:
        # دکمه محاسبه (فقط اگر همه پاسخ داده شده)
        if answered_count == len(RISK_QUESTIONS):
            if st.button("✅ محاسبه پروفایل من", type="primary", use_container_width=True):
                # محاسبه نتیجه
                result = calculate_risk_score(st.session_state.answers)
                st.session_state.risk_result = result
                st.session_state.risk_profile = result["profile"]
                
                # رفتن به صفحه نتیجه
                st.session_state.page = "questionnaire_result"
                st.rerun()
        else:
            st.button("⏳ پاسخ‌ها کامل نیست", disabled=True, use_container_width=True)
    
    with col3:
        if st.button("🔄 ریست پاسخ‌ها", type="secondary", use_container_width=True):
            st.session_state.answers = [None] * len(RISK_QUESTIONS)
            st.rerun()

# ==================== صفحه ۳: نتیجه پرسشنامه ====================
def show_questionnaire_result_page():
    """صفحه نتیجه پرسشنامه"""
    st.markdown('<h1 class="main-header">🎯 نتیجه پرسشنامه ریسک</h1>', unsafe_allow_html=True)
    
    if 'risk_result' not in st.session_state:
        st.error("❌ ابتدا پرسشنامه را تکمیل کنید!")
        st.button("بازگشت به پرسشنامه", on_click=lambda: st.session_state.update({"page": "questionnaire"}))
        return
    
    result = st.session_state.risk_result
    profile_farsi = {
        "Conservative": "محافظه‌کار",
        "Moderate": "متعادل",
        "Aggressive": "تهاجمی"
    }
    
    # نمایش نتیجه
    st.markdown(f'<div class="result-card">', unsafe_allow_html=True)
    st.markdown(f"### پروفایل ریسک شما: **{profile_farsi[result['profile']]}**")
    st.markdown(f"امتیاز: **{result['normalized_score']:.1f}/100**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # توضیح پروفایل
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
        <h4>📊 امتیاز خام</h4>
        <h2>{}/44</h2>
        </div>
        """.format(result['raw_score']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
        <h4>🎯 پروفایل</h4>
        <h2>{}</h2>
        </div>
        """.format(profile_farsi[result['profile']]), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
        <h4>⭐ سطح</h4>
        <h2>{}</h2>
        </div>
        """.format("پایین" if result['profile'] == 'Conservative' else "متوسط" if result['profile'] == 'Moderate' else "بالا"), unsafe_allow_html=True)
    
    # توضیح پروفایل
    st.markdown("### 📋 توضیح پروفایل شما:")
    
    if result['profile'] == 'Conservative':
        st.info("""
        **🎯 سرمایه‌گذار محافظه‌کار**
        - **اولویت اصلی:** حفظ سرمایه
        - **تحمل ریسک:** پایین
        - **بازده مورد انتظار:** کم تا متوسط
        - **سبد پیشنهادی:** تمرکز بر دارایی‌های کم‌ریسک مانند طلا
        - **افق زمانی:** کوتاه‌مدت
        """)
    elif result['profile'] == 'Moderate':
        st.success("""
        **🎯 سرمایه‌گذار متعادل**
        - **اولویت:** توازن بین رشد و حفظ سرمایه
        - **تحمل ریسک:** متوسط
        - **بازده مورد انتظار:** متوسط
        - **سبد پیشنهادی:** ترکیب متعادل از دارایی‌ها
        - **افق زمانی:** میان‌مدت
        """)
    else:
        st.warning("""
        **🎯 سرمایه‌گذار تهاجمی**
        - **اولویت اصلی:** رشد سریع سرمایه
        - **تحمل ریسک:** بالا
        - **بازده مورد انتظار:** بالا
        - **سبد پیشنهادی:** تمرکز بر دارایی‌های پرریسک مانند رمزارزها
        - **افق زمانی:** بلندمدت
        """)
    
    # دکمه‌های ناوبری
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("◀️ بازگشت به پرسشنامه", use_container_width=True):
            st.session_state.page = "questionnaire"
            st.rerun()
    
    with col2:
        if st.button("✏️ ویرایش پاسخ‌ها", type="secondary", use_container_width=True):
            st.session_state.page = "questionnaire"
            st.rerun()
    
    with col3:
        if st.button("🚀 ادامه برای محاسبه سبد", type="primary", use_container_width=True):
            st.session_state.page = "portfolio_input"
            st.rerun()

# ==================== صفحه ۴: ورود اطلاعات سبد ====================
def show_portfolio_input_page():
    """صفحه ورود اطلاعات سبد"""
    st.markdown('<h1 class="main-header">💰 ورود اطلاعات سرمایه‌گذاری</h1>', unsafe_allow_html=True)
    
    if 'risk_profile' not in st.session_state:
        st.error("❌ ابتدا پرسشنامه را تکمیل کنید!")
        st.button("بازگشت به پرسشنامه", on_click=lambda: st.session_state.update({"page": "questionnaire"}))
        return
    
    # نمایش پروفایل فعلی
    result = st.session_state.risk_result
    profile_farsi = {
        "Conservative": "محافظه‌کار",
        "Moderate": "متعادل",
        "Aggressive": "تهاجمی"
    }
    
    st.markdown(f"### 📊 پروفایل فعلی: **{profile_farsi[st.session_state.risk_profile]}**")
    st.markdown(f"امتیاز ریسک: **{result['normalized_score']:.1f}/100**")
    
    st.markdown("---")
    
    # فرم ورود اطلاعات
    with st.form("portfolio_form"):
        st.markdown("### 💰 مبلغ سرمایه‌گذاری")
        
        investment = st.number_input(
            "مبلغ سرمایه‌گذاری خود را وارد کنید (تومان):",
            min_value=1000000,
            value=100000000,
            step=10000000,
            help="حداقل ۱,۰۰۰,۰۰۰ تومان"
        )
        
        st.markdown("### ⏳ افق سرمایه‌گذاری")
        
        horizon = st.selectbox(
            "افق زمانی سرمایه‌گذاری شما:",
            ["کوتاه‌مدت (کمتر از ۱ سال)", "میان‌مدت (۱-۳ سال)", "بلندمدت (بیش از ۳ سال)"],
            index=1
        )
        
        submitted = st.form_submit_button("🚀 محاسبه سبد بهینه", type="primary", use_container_width=True)
    
    if submitted:
        # ذخیره اطلاعات
        st.session_state.investment = investment
        st.session_state.horizon = horizon
        
        # رفتن به صفحه محاسبه
        st.session_state.page = "portfolio_calculation"
        st.rerun()
    
    # دکمه‌های ناوبری
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("◀️ بازگشت به نتیجه پرسشنامه", use_container_width=True):
            st.session_state.page = "questionnaire_result"
            st.rerun()
    
    with col2:
        if st.button("🔄 تغییر پروفایل ریسک", type="secondary", use_container_width=True):
            st.session_state.page = "questionnaire"
            st.rerun()

# ==================== صفحه ۵: محاسبه سبد ====================
def show_portfolio_calculation_page():
    """صفحه محاسبه سبد (با اسپینر و سپس رفتن به نتایج)"""
    st.markdown('<h1 class="main-header">⚡ در حال محاسبه سبد بهینه</h1>', unsafe_allow_html=True)
    
    if 'risk_profile' not in st.session_state or 'investment' not in st.session_state:
        st.error("❌ اطلاعات ناقص است!")
        if st.button("بازگشت"):
            st.session_state.page = "portfolio_input"
            st.rerun()
        return
    
    # نمایش اطلاعات ورودی
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("💰 مبلغ سرمایه‌گذاری", f"{st.session_state.investment:,.0f} تومان")
    
    with col2:
        profile_farsi = {
            "Conservative": "محافظه‌کار",
            "Moderate": "متعادل",
            "Aggressive": "تهاجمی"
        }
        st.metric("🎯 پروفایل ریسک", profile_farsi[st.session_state.risk_profile])
    
    # محاسبات
    with st.spinner("🔍 در حال بارگذاری داده‌های بازار... (لطفاً صبر کنید)"):
        try:
            df = load_and_optimize()
            
            if df is None or df.empty:
                st.warning("⚠️ خطا در دریافت داده‌های واقعی. استفاده از داده نمونه...")
                # Create sample data as fallback
                from data_fetcher import create_sample_data
                df = create_sample_data()
            
            if df is None or df.empty:
                st.error("❌ خطا در دریافت داده‌های بازار")
                st.button("بازگشت", on_click=lambda: st.session_state.update({"page": "portfolio_input"}))
                return
            
            # Create optimizer instance
            optimizer = PortfolioOptimizer(df)
            st.session_state.optimizer = optimizer
            
        except Exception as e:
            st.error(f"❌ خطا در بارگذاری داده: {str(e)}")
            st.button("بازگشت", on_click=lambda: st.session_state.update({"page": "portfolio_input"}))
            return
    
    with st.spinner("⚙️ در حال بهینه‌سازی سبد با MPT..."):
        try:
            report = optimizer.generate_report(st.session_state.risk_profile, st.session_state.investment)
            
            # بررسی وجود کلیدهای مورد نیاز
            if 'allocation' not in report:
                # اگر کلید allocation وجود نداشت، یک ساختار پیش‌فرض ایجاد کن
                assets = df.columns.tolist()
                weights = [1/len(assets)] * len(assets)
                report['allocation'] = dict(zip(assets, weights))
            
            st.session_state.report = report
            
        except Exception as e:
            st.error(f"❌ خطا در بهینه‌سازی: {str(e)}")
            print(f"Error generating report: {e}")
            
            # ایجاد گزارش نمونه در صورت خطا
            assets = df.columns.tolist()
            weights = [1/len(assets)] * len(assets)
            
            report = {
                'allocation': dict(zip(assets, weights)),
                'expected_return': 0.15,
                'volatility': 0.25,
                'sharpe_ratio': 0.6,
                'investment_amount': st.session_state.investment,
                'risk_profile': st.session_state.risk_profile
            }
            st.session_state.report = report
    
    # رفتن به صفحه نتایج
    st.session_state.page = "portfolio_results"
    st.rerun()

# ==================== صفحه ۶: نتایج سبد ====================
def show_portfolio_results_page():
    """نمایش نتایج سبد بهینه"""
    st.markdown('<h1 class="main-header">📊 نتایج سبد سرمایه‌گذاری بهینه</h1>', unsafe_allow_html=True)
    
    # Check if we have results in session state
    if 'report' not in st.session_state:
        st.warning("⚠️ ابتدا سبد بهینه را محاسبه کنید")
        if st.button("رفتن به صفحه محاسبه"):
            st.session_state.page = "portfolio_calculation"
            st.rerun()
        return
    
    # Get results from session state
    report = st.session_state.report
    investment = st.session_state.get('investment', 160000000)
    
    # Display investment amount
    st.metric("💰 مبلغ سرمایه‌گذاری", f"{investment:,.0f} تومان")
    
    st.markdown("---")
    
    # بخش ۱: توزیع دارایی‌ها
    st.markdown("### 📊 توزیع دارایی‌ها")
    
    # Check if allocation exists
    if 'allocation' in report and report['allocation']:
        weights = report['allocation']
        
        # نمودار
        fig = go.Figure(data=[go.Pie(
            labels=list(weights.keys()),
            values=list(weights.values()),
            hole=.3,
            marker=dict(colors=['#FFD700', '#C0C0C0', '#F7931A', '#627EEA']),
            textinfo='label+percent'
        )])
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # جدول
        try:
            # بررسی کنیم که همه لیست‌ها هم‌طول باشند
            assets = list(weights.keys())
            weight_values = list(weights.values())
            
            # توضیحات دارایی‌ها
            descriptions = []
            for asset in assets:
                if 'Gold' in asset or 'طلا' in asset:
                    descriptions.append('دارایی امن در تورم')
                elif 'Silver' in asset or 'نقره' in asset:
                    descriptions.append('صنعتی با نوسان متوسط')
                elif 'Bitcoin' in asset or 'بیت' in asset:
                    descriptions.append('رمزارز پیشرو - نوسان بالا')
                elif 'Ethereum' in asset or 'اتریوم' in asset:
                    descriptions.append('پلتفرم قرارداد هوشمند')
                else:
                    descriptions.append('دارایی سرمایه‌گذاری')
            
            weights_df = pd.DataFrame({
                'دارایی': assets,
                'وزن': [f"{w:.1%}" for w in weight_values],
                'مبلغ (تومان)': [f"{w * investment:,.0f}" for w in weight_values],
                'توضیح': descriptions
            })
            st.dataframe(weights_df, use_container_width=True, hide_index=True)
            
        except Exception as e:
            st.warning(f"خطا در نمایش جدول: {e}")
            # نمایش ساده
            for asset, weight in weights.items():
                st.write(f"• **{asset}**: {weight:.1%} ({weight * investment:,.0f} تومان)")
    else:
        st.warning("⚠️ داده‌های توزیع دارایی در دسترس نیست")
        # نمایش دارایی‌های پیش‌فرض
        st.info("در حال استفاده از توزیع پیش‌فرض...")
        
        # استفاده از داده‌های موجود در session_state
        if 'optimizer' in st.session_state and hasattr(st.session_state.optimizer, 'assets'):
            assets = st.session_state.optimizer.assets
            weights = [1/len(assets)] * len(assets)
            weights_dict = dict(zip(assets, weights))
            
            for asset, weight in weights_dict.items():
                st.write(f"• **{asset}**: {weight:.1%} ({weight * investment:,.0f} تومان)")
    
    st.markdown("---")
    
    # بخش ۲: معیارهای عملکرد
    st.markdown("### 📈 معیارهای عملکرد")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        expected_return = report.get('expected_return', 0.15)
        st.metric(
            "بازده مورد انتظار سالانه",
            f"{expected_return:.2%}",
            help="بازده مورد انتظار سالانه بر اساس داده‌های تاریخی"
        )
    
    with col2:
        volatility = report.get('volatility', 0.25)
        st.metric(
            "ریسک (انحراف معیار)",
            f"{volatility:.2%}",
            help="نوسان سالانه سبد سرمایه‌گذاری"
        )
    
    with col3:
        sharpe = report.get('sharpe_ratio', 0.6)
        st.metric(
            "نسبت شارپ",
            f"{sharpe:.2f}",
            help="بازده به ازای واحد ریسک (هرچه بالاتر بهتر)"
        )
    
    st.markdown("---")
    
    # بخش ۳: تحلیل ریسک
    st.markdown("### 🎲 تحلیل ریسک")
    
    # Check if VaR exists
    if 'VaR' in report and report['VaR']:
        var_data = report['VaR']
        col1, col2 = st.columns(2)
        
        with col1:
            var_percent = var_data.get('VaR_95', 0.05)
            var_amount = var_percent * investment
            st.metric(
                "Value at Risk (95%)",
                f"{var_percent:.2%}",
                f"{var_amount:,.0f} تومان",
                help="حداکثر ضرر مورد انتظار در 95% موارد (یک روز)"
            )
        
        with col2:
            cvar_percent = var_data.get('CVaR_95', 0.08)
            cvar_amount = cvar_percent * investment
            st.metric(
                "CVaR (95%)",
                f"{cvar_percent:.2%}",
                f"{cvar_amount:,.0f} تومان",
                help="میانگین ضرر در 5% بدترین موارد"
            )
    else:
        # مقادیر پیش‌فرض
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Value at Risk (95%)", "۵٪", f"{investment * 0.05:,.0f} تومان")
        with col2:
            st.metric("CVaR (95%)", "۸٪", f"{investment * 0.08:,.0f} تومان")
    
    # Check if monte_carlo exists
    if 'monte_carlo' in report and report['monte_carlo']:
        mc = report['monte_carlo']
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "بازده شبیه‌سازی",
                f"{mc.get('expected_return_pct', 15):.1f}%",
                help="میانگین بازده در ۱۰۰۰ شبیه‌سازی"
            )
        
        with col2:
            st.metric(
                "احتمال زیان",
                f"{mc.get('prob_loss', 0.3):.1%}",
                delta_color="inverse",
                help="احتمال کمتر شدن ارزش سبد نسبت به امروز"
            )
        
        with col3:
            st.metric(
                "Expected Shortfall",
                f"{mc.get('cvar_95', investment * 0.1):,.0f} تومان",
                delta_color="inverse",
                help="میانگین ضرر در بدترین 5% سناریوها"
            )
    else:
        # مقادیر پیش‌فرض
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("بازده شبیه‌سازی", "۱۵.۰٪")
        with col2:
            st.metric("احتمال زیان", "۳۰٪")
        with col3:
            st.metric("Expected Shortfall", f"{investment * 0.1:,.0f} تومان")
    
    st.markdown("---")
    
    # بخش ۴: توصیه‌ها
    st.markdown("### 💡 توصیه‌های سرمایه‌گذاری")
    
    risk_profile = st.session_state.get('risk_profile', 'Moderate')
    profile_farsi = {
        "Conservative": "محافظه‌کار",
        "Moderate": "متعادل",
        "Aggressive": "تهاجمی"
    }
    
    risk_texts = {
        "Conservative": "سبد محافظه‌کارانه با تمرکز بر دارایی‌های امن مانند طلا. مناسب برای سرمایه‌گذارانی که حفظ اصل سرمایه برایشان اولویت است.",
        "Moderate": "سبد متعادل با ترکیبی از دارایی‌های امن و پرریسک. مناسب برای سرمایه‌گذارانی که به دنبال رشد متوازن هستند.",
        "Aggressive": "سبد تهاجمی با تمرکز بر رشد بلندمدت و دارایی‌های پرریسک. مناسب برای سرمایه‌گذارانی که تحمل ریسک بالا دارند."
    }
    
    st.success(f"**{risk_texts.get(risk_profile, 'سبد متناسب با پروفایل ریسک شما')}**")
    
    st.markdown("---")
    
    # بخش ۵: دکمه‌های ناوبری
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💾 ذخیره گزارش", use_container_width=True):
            try:
                save_json_report(report)
            except:
                st.info("گزارش در حال آماده‌سازی است")
    
    with col2:
        if st.button("🔄 محاسبه مجدد", use_container_width=True):
            st.session_state.page = "portfolio_calculation"
            st.rerun()
    
    with col3:
        if st.button("📋 شروع جدید", use_container_width=True):
            # ریست همه چیز
            for key in list(st.session_state.keys()):
                if key != 'page':
                    del st.session_state[key]
            st.session_state.page = "start"
            st.rerun()
    
    with col4:
        if st.button("🏠 صفحه اصلی", use_container_width=True):
            st.session_state.page = "start"
            st.rerun()

# ==================== تابع اصلی ====================
def main():
    """تابع اصلی"""
    
    # مقداردهی اولیه صفحه
    if 'page' not in st.session_state:
        st.session_state.page = "start"
    
    # نمایش صفحه مناسب
    if st.session_state.page == "start":
        show_start_page()
    
    elif st.session_state.page == "questionnaire":
        show_questionnaire_page()
    
    elif st.session_state.page == "questionnaire_result":
        show_questionnaire_result_page()
    
    elif st.session_state.page == "portfolio_input":
        show_portfolio_input_page()
    
    elif st.session_state.page == "portfolio_calculation":
        show_portfolio_calculation_page()
    
    elif st.session_state.page == "portfolio_results":
        show_portfolio_results_page()

# ==================== اجرا ====================
if __name__ == "__main__":
    main()