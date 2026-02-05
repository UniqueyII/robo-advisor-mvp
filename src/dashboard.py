# src/dashboard.py - نسخه کامل

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os
from datetime import datetime
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.portfolio_optimizer import load_and_optimize

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
    """صفحه محاسبه سبد"""
    st.markdown('<h1 class="main-header">⚡ در حال محاسبه سبد بهینه</h1>', unsafe_allow_html=True)
    
    if 'risk_profile' not in st.session_state or 'investment' not in st.session_state:
        st.error("❌ اطلاعات ناقص است!")
        st.button("بازگشت", on_click=lambda: st.session_state.update({"page": "portfolio_input"}))
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
        optimizer = load_and_optimize()
        st.session_state.optimizer = optimizer
    
    with st.spinner("⚙️ در حال بهینه‌سازی سبد با MPT..."):
        pass  # برای نشان دادن progress
    
    with st.spinner("🎲 در حال شبیه‌سازی مونت‌کارلو..."):
        pass  # برای نشان دادن progress
    
    with st.spinner("📊 در حال محاسبه معیارهای ریسک..."):
        report = optimizer.generate_report(st.session_state.risk_profile, st.session_state.investment)
        st.session_state.report = report
    
    # رفتن به صفحه نتایج
    st.session_state.page = "portfolio_results"
    st.rerun()

# ==================== صفحه ۶: نتایج سبد ====================
def show_portfolio_results_page():
    """صفحه نمایش نتایج سبد"""
    st.markdown('<h1 class="main-header">📊 نتایج سبد سرمایه‌گذاری</h1>', unsafe_allow_html=True)
    
    if 'report' not in st.session_state:
        st.error("❌ ابتدا محاسبات را انجام دهید!")
        st.button("بازگشت", on_click=lambda: st.session_state.update({"page": "portfolio_input"}))
        return
    
    report = st.session_state.report
    profile_farsi = {
        "Conservative": "محافظه‌کار",
        "Moderate": "متعادل",
        "Aggressive": "تهاجمی"
    }
    
    # خلاصه
    st.markdown(f'<div class="result-card">', unsafe_allow_html=True)
    st.markdown(f"### سبد بهینه برای پروفایل **{profile_farsi[report['risk_profile']]}**")
    st.markdown(f"سرمایه: **{report['investment_amount']:,.0f} تومان**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # معیارهای کلیدی
    st.markdown("### 📈 معیارهای کلیدی")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "بازده مورد انتظار",
            f"{report['optimal_portfolio']['stats']['return']*100:.1f}%",
            help="بازده سالانه مورد انتظار"
        )
    
    with col2:
        st.metric(
            "ریسک (نوسان)",
            f"{report['optimal_portfolio']['stats']['volatility']*100:.1f}%",
            delta_color="inverse",
            help="انحراف معیار بازده‌ها"
        )
    
    with col3:
        st.metric(
            "نسبت شارپ",
            f"{report['optimal_portfolio']['stats']['sharpe_ratio']:.2f}",
            help="بازده به ازای هر واحد ریسک"
        )
    
    with col4:
        var = report['risk_metrics']['var_historical']
        var_pct = (var / report['investment_amount']) * 100
        st.metric(
            "VaR (95%)",
            f"{var:,.0f} تومان",
            delta=f"{var_pct:.1f}% سرمایه",
            delta_color="inverse",
            help="حداکثر ضرر احتمالی با احتمال 95%"
        )
    
    st.markdown("---")
    
    # بخش ۱: توزیع دارایی‌ها
    st.markdown("### 📊 توزیع دارایی‌ها")
    
    weights = report['optimal_portfolio']['weights']
    
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
    weights_df = pd.DataFrame({
        'دارایی': list(weights.keys()),
        'وزن': [f"{w:.1%}" for w in weights.values()],
        'مبلغ (تومان)': [f"{w * report['investment_amount']:,.0f}" for w in weights.values()],
        'توضیح': [
            'دارایی امن در تورم',
            'صنعتی با نوسان متوسط',
            'رمزارز پیشرو - نوسان بالا',
            'پلتفرم قرارداد هوشمند'
        ]
    })
    st.dataframe(weights_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # بخش ۲: تحلیل ریسک
    st.markdown("### 🎲 تحلیل ریسک و بازده")
    
    mc = report['monte_carlo']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "بازده مورد انتظار شبیه‌سازی",
            f"{mc['expected_return_pct']:.1f}%",
            help="میانگین بازده در ۱۰۰۰ شبیه‌سازی"
        )
    
    with col2:
        st.metric(
            "احتمال زیان",
            f"{mc['prob_loss']:.1%}",
            delta_color="inverse",
            help="احتمال کمتر شدن ارزش سبد نسبت به امروز"
        )
    
    with col3:
        st.metric(
            "Expected Shortfall",
            f"{mc['cvar_95']:,.0f} تومان",
            delta_color="inverse",
            help="میانگین ضرر در بدترین 5% سناریوها"
        )
    
    st.markdown("---")
    
    # بخش ۳: توصیه‌ها
    st.markdown("### 💡 توصیه‌های سرمایه‌گذاری")
    
    rec = report['recommendation']
    
    st.success(f"**{rec['text']}**")
    
    st.markdown(f"""
    #### 📋 خلاصه توصیه‌ها:
    
    - **سطح ریسک:** {rec['risk_level']}
    - **افق زمانی پیشنهادی:** {rec['suggested_horizon']}
    - **بازده مورد انتظار:** {rec['expected_return']:.1f}%
    - **ریسک قابل توجه:** حداکثر ضرر احتمالی (VaR) = {report['risk_metrics']['var_historical']:,.0f} تومان
    - **نکته مهم:** این تحلیل بر اساس داده‌های تاریخی است و تضمینی برای آینده نیست
    """)
    
    st.markdown("---")
    
    # بخش ۴: خروجی
    st.markdown("### 📥 خروجی‌ها")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 ذخیره گزارش JSON", use_container_width=True):
            save_json_report(report)
    
    with col2:
        if st.button("🖨️ چاپ گزارش", use_container_width=True):
            st.info("در نسخه کامل، گزارش PDF تولید می‌شود")
    
    with col3:
        if st.button("🔄 محاسبه مجدد", type="secondary", use_container_width=True):
            # پاک کردن محاسبات قبلی
            for key in ['report', 'optimizer']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.page = "portfolio_input"
            st.rerun()
    
    st.markdown("---")
    
    # دکمه‌های ناوبری نهایی
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("◀️ بازگشت به ورود اطلاعات", use_container_width=True):
            st.session_state.page = "portfolio_input"
            st.rerun()
    
    with col2:
        if st.button("📋 شروع پرسشنامه جدید", type="secondary", use_container_width=True):
            # ریست همه چیز
            for key in list(st.session_state.keys()):
                if key != 'page':
                    del st.session_state[key]
            st.session_state.page = "questionnaire"
            st.rerun()
    
    with col3:
        if st.button("🚀 محاسبه با اطلاعات جدید", type="primary", use_container_width=True):
            # فقط ریست محاسبات
            for key in ['report', 'optimizer']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.page = "portfolio_input"
            st.rerun()

def save_json_report(report):
    """ذخیره گزارش به صورت JSON"""
    import json
    
    summary = {
        "تاریخ_محاسبه": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "پروفایل_ریسک": report['risk_profile'],
        "سرمایه_گذاری_تومان": report['investment_amount'],
        "وزن_دارایی‌ها": report['optimal_portfolio']['weights'],
        "بازده_مورد_انتظار_درصد": report['optimal_portfolio']['stats']['return'] * 100,
        "ریسک_نوسان_درصد": report['optimal_portfolio']['stats']['volatility'] * 100,
        "نسبت_شارپ": report['optimal_portfolio']['stats']['sharpe_ratio'],
        "VaR_95_تومان": report['risk_metrics']['var_historical'],
        "Expected_Shortfall": report['monte_carlo']['cvar_95'],
        "احتمال_زیان": report['monte_carlo']['prob_loss'],
        "توصیه": report['recommendation']['text']
    }
    
    # ایجاد دکمه دانلود
    st.download_button(
        label="📥 دانلود گزارش JSON",
        data=json.dumps(summary, indent=2, ensure_ascii=False),
        file_name=f"portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

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