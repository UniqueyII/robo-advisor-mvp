# dashboard.py - FIXED VERSION WITH REAL DATA ONLY

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os
from datetime import datetime
import json

# Import our modules
from portfolio_optimizer import PortfolioOptimizer
from data_fetcher import create_dataframe, validate_data

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Robo-Advisor MVP - Real Data Only",
    page_icon="📈",
    layout="wide"
)

# ==================== CUSTOM CSS ====================
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
    .metric-card {
        background-color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #10B981;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FEF3C7;
        border-left: 5px solid #F59E0B;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #D1FAE5;
        border-left: 5px solid #10B981;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== RISK QUESTIONS ====================
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
        "question": "۸. انتظار بازده سالانه شما چقدر است؟",
        "options": [
            {"text": "بیش از ۳۰٪", "score": 4},
            {"text": "۲۰-۳۰٪", "score": 3},
            {"text": "۱۵-۲۰٪", "score": 2},
            {"text": "۱۰-۱۵٪", "score": 1}
        ]
    },
    {
        "id": 9,
        "question": "۹. دانش شما از ابزارهای مالی چقدر است؟",
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
    }
]

# ==================== HELPER FUNCTIONS ====================
def validate_data(df):
    """
    Validate that the DataFrame contains clean, usable data.
    Returns (is_valid: bool, message: str)
    """
    if df is None:
        return False, "No data received"
    if df.empty:
        return False, "DataFrame is empty"
    if df.isnull().any().any():
        return False, "Data contains NaN values"
    if (df <= 0).any().any():
        return False, "Data contains non-positive values (prices must be >0)"
    return True, "Data is valid"

def calculate_risk_score(answers):
    """Calculate risk score from questionnaire answers"""
    raw_score = sum(answers)
    # Normalize to 0-100 (min 10, max 40)
    normalized_score = (raw_score - 10) * (100 / 30)
    
    if normalized_score <= 35:
        profile = "Conservative"
        description = "محافظه‌کار - حفظ سرمایه اولویت اصلی شماست"
    elif normalized_score <= 70:
        profile = "Moderate"
        description = "متعادل - به دنبال تعادل بین ریسک و بازده هستید"
    else:
        profile = "Aggressive"
        description = "تهاجمی - به دنبال رشد بالا با پذیرش ریسک بیشتر هستید"
    
    return {
        "raw_score": raw_score,
        "normalized_score": normalized_score,
        "profile": profile,
        "description": description
    }

def get_profile_interpretation(profile, normalized_score):
    """Get detailed interpretation of risk profile"""
    interpretations = {
        "Conservative": {
            "title": "🛡️ سرمایه‌گذار محافظه‌کار",
            "characteristics": [
                "حفظ اصل سرمایه برای شما اولویت اول است",
                "تحمل کمی برای نوسانات و ریسک دارید",
                "ترجیح می‌دهید رشد آهسته‌تر اما پایدار داشته باشید",
                "دارایی‌های امن مانند طلا برای شما مناسب‌تر است"
            ],
            "recommendations": [
                "سبد شما بیشتر شامل طلا و نقره خواهد بود",
                "حداکثر ۲۰٪ در کریپتوکارنسی‌ها سرمایه‌گذاری می‌شود",
                "انتظار بازده سالانه ۸-۱۲٪ با ریسک کم",
                "مناسب برای افق زمانی میان‌مدت تا بلندمدت"
            ],
            "warnings": [
                "بازده کمتر از سبدهای پرریسک‌تر",
                "در بازارهای صعودی ممکن است عقب بمانید"
            ]
        },
        "Moderate": {
            "title": "⚖️ سرمایه‌گذار متعادل",
            "characteristics": [
                "به دنبال تعادل مناسب بین ریسک و بازده هستید",
                "تحمل نوسانات متوسط را دارید",
                "می‌خواهید در فرصت‌های رشد شرکت کنید",
                "اما همچنان به امنیت سرمایه اهمیت می‌دهید"
            ],
            "recommendations": [
                "سبد شما ترکیبی متوازن از همه دارایی‌هاست",
                "حدود ۵۰٪ در طلا و نقره، ۵۰٪ در کریپتو",
                "انتظار بازده سالانه ۱۲-۱۸٪ با ریسک متوسط",
                "نیاز به بررسی و تعادل دوره‌ای دارد"
            ],
            "warnings": [
                "نیاز به نظارت منظم بر سبد",
                "در بازارهای نزولی نوسان خواهید داشت"
            ]
        },
        "Aggressive": {
            "title": "🚀 سرمایه‌گذار تهاجمی",
            "characteristics": [
                "به دنبال رشد حداکثری سرمایه هستید",
                "تحمل بالایی برای ریسک و نوسانات دارید",
                "افق زمانی بلندمدت دارید",
                "از ویژگی‌های بازارهای پرنوسان استفاده می‌کنید"
            ],
            "recommendations": [
                "سبد شما بیشتر شامل کریپتوکارنسی‌هاست",
                "حدود ۷۵٪ در Bitcoin و Ethereum",
                "انتظار بازده سالانه ۲۰-۳۰٪ با ریسک بالا",
                "آماده نوسانات شدید باشید"
            ],
            "warnings": [
                "⚠️ احتمال ضرر ۳۰-۴۰٪ در سناریوهای بد",
                "⚠️ فقط با سرمایه‌ای سرمایه‌گذاری کنید که از دست دادنش مشکلی ایجاد نمی‌کند",
                "⚠️ نیاز به روحیه قوی و تحمل نوسانات شدید"
            ]
        }
    }
    
    return interpretations.get(profile, interpretations["Moderate"])

def save_json_report(report, risk_profile, investment):
    """Save complete report as JSON"""
    try:
        summary = {
            "calculation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "risk_profile": risk_profile,
            "investment_toman": investment,
            "portfolio": {
                "weights": report.get('weights_dict', {}),
                "expected_return_percent": report.get('expected_return_pct', 0),
                "volatility_percent": report.get('volatility_pct', 0),
                "sharpe_ratio": report.get('sharpe_ratio', 0),
                "sortino_ratio": report.get('sortino_ratio', 0),
                "max_drawdown_percent": report.get('max_drawdown_pct', 0),
                "calmar_ratio": report.get('calmar_ratio', 0)
            },
            "risk_metrics": {
                "var_95_percent": report.get('var_pct', 0),
                "var_95_toman": report.get('var', 0),
                "cvar_95_percent": report.get('cvar_pct', 0),
                "cvar_95_toman": report.get('cvar', 0)
            },
            "monte_carlo": {
                "mean_value_toman": report.get('mc_mean_value', 0),
                "best_case_toman": report.get('mc_best_case', 0),
                "worst_case_toman": report.get('mc_worst_case', 0),
                "probability_of_loss": report.get('mc_prob_loss', 0),
                "expected_return_percent": report.get('mc_expected_return_pct', 0)
            }
        }
        
        json_str = json.dumps(summary, indent=2, ensure_ascii=False)
        
        st.download_button(
            label="📥 دانلود گزارش کامل (JSON)",
            data=json_str,
            file_name=f"portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"خطا در ذخیره گزارش: {e}")

# ==================== PAGE 1: START ====================
def show_start_page():
    """Start page"""
    st.markdown('<h1 class="main-header">🤖 Robo-Advisor MVP</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #6B7280;">مشاور سرمایه‌گذاری هوشمند با داده‌های واقعی</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### ✨ ویژگی‌های سیستم
        
        ✅ **داده‌های واقعی از Yahoo Finance**
        - قیمت‌های لحظه‌ای طلا، نقره، Bitcoin، Ethereum
        - بدون داده‌های فیک یا هاردکد شده
        
        ✅ **بهینه‌سازی حرفه‌ای پرتفولیو**
        - Modern Portfolio Theory (MPT)
        - بیشینه‌سازی نسبت شارپ
        - شبیه‌سازی مونت‌کارلو با ۱۰,۰۰۰ سناریو
        
        ✅ **تحلیل ریسک پیشرفته**
        - محاسبه VaR و CVaR
        - بررسی بهترین و بدترین سناریوها
        - احتمال زیان و سود
        """)
    
    with col2:
        st.markdown("""
        ### 📋 مراحل کار
        
        **۱. ارزیابی ریسک‌پذیری**
        - پاسخ به ۱۰ سوال
        - تعیین پروفایل ریسک شما
        
        **۲. ورود اطلاعات سرمایه‌گذاری**
        - مبلغ سرمایه‌گذاری
        - تأیید پروفایل ریسک
        
        **۳. دریافت پرتفولیوی بهینه**
        - توزیع دارایی‌ها
        - معیارهای عملکرد
        - تحلیل ریسک
        - توصیه‌های سرمایه‌گذاری
        """)
    
    st.markdown("---")
    
    # Important notice
    st.markdown("""
    <div class="warning-box">
    <strong>⚠️ توجه مهم:</strong>
    <ul>
        <li>این سیستم از داده‌های واقعی Yahoo Finance استفاده می‌کند</li>
        <li>تمام محاسبات بر اساس قیمت‌های واقعی بازار انجام می‌شود</li>
        <li>هیچ عدد هاردکد یا فیکی در گزارش‌ها وجود ندارد</li>
        <li>نتایج بر اساس تحلیل آماری داده‌های تاریخی است</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Start button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 شروع ارزیابی ریسک", use_container_width=True, type="primary"):
            st.session_state.page = "questionnaire"
            st.rerun()

# ==================== PAGE 2: QUESTIONNAIRE ====================
def show_questionnaire_page():
    """Risk assessment questionnaire"""
    st.markdown('<h1 class="main-header">📋 ارزیابی ریسک‌پذیری</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="success-box">
    لطفاً به سوالات زیر با دقت پاسخ دهید. این پرسشنامه به ما کمک می‌کند پروفایل ریسک شما را تعیین کنیم.
    </div>
    """, unsafe_allow_html=True)
    
    answers = []
    
    # Display all questions
    for q in RISK_QUESTIONS:
        st.markdown(f"### {q['question']}")
        
        # Create radio buttons for options
        options_text = [opt['text'] for opt in q['options']]
        selected = st.radio(
            f"انتخاب کنید:",
            options=options_text,
            key=f"q_{q['id']}",
            label_visibility="collapsed"
        )
        
        # Get score for selected option
        score = next(opt['score'] for opt in q['options'] if opt['text'] == selected)
        answers.append(score)
        
        st.markdown("---")
    
    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ محاسبه پروفایل ریسک", use_container_width=True, type="primary"):
            result = calculate_risk_score(answers)
            st.session_state.risk_result = result
            st.session_state.page = "questionnaire_result"
            st.rerun()

# ==================== PAGE 3: RISK PROFILE RESULT ====================
def show_questionnaire_result_page():
    """Display risk profile result"""
    st.markdown('<h1 class="main-header">📊 نتیجه ارزیابی ریسک</h1>', unsafe_allow_html=True)
    
    result = st.session_state.get('risk_result', {})
    profile = result.get('profile', 'Moderate')
    normalized_score = result.get('normalized_score', 50)
    
    # Display score
    st.markdown(f"""
    <div class="result-card">
        <h2>امتیاز شما: {normalized_score:.0f}/100</h2>
        <h1>{result.get('description', '')}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Get detailed interpretation
    interpretation = get_profile_interpretation(profile, normalized_score)
    
    # Display characteristics
    st.markdown(f"## {interpretation['title']}")
    st.markdown("### 🎯 ویژگی‌های شما:")
    for char in interpretation['characteristics']:
        st.markdown(f"- {char}")
    
    st.markdown("---")
    
    # Display recommendations
    st.markdown("### 💡 توصیه‌های سرمایه‌گذاری:")
    for rec in interpretation['recommendations']:
        st.markdown(f"- {rec}")
    
    st.markdown("---")
    
    # Display warnings if any
    if interpretation['warnings']:
        st.markdown("### ⚠️ نکات مهم:")
        for warning in interpretation['warnings']:
            st.warning(warning)
    
    st.markdown("---")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 ارزیابی مجدد", use_container_width=True):
            st.session_state.page = "questionnaire"
            st.rerun()
    
    with col2:
        if st.button("➡️ ادامه به سرمایه‌گذاری", use_container_width=True, type="primary"):
            st.session_state.risk_profile = profile
            st.session_state.page = "portfolio_input"
            st.rerun()

# ==================== PAGE 4: PORTFOLIO INPUT ====================
def show_portfolio_input_page():
    """Investment amount input"""
    st.markdown('<h1 class="main-header">💰 اطلاعات سرمایه‌گذاری</h1>', unsafe_allow_html=True)
    
    result = st.session_state.get('risk_result', {})
    profile = result.get('profile', 'Moderate')
    
    st.markdown(f"""
    <div class="success-box">
    <strong>پروفایل ریسک شما:</strong> {result.get('description', profile)}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Investment amount input
    st.markdown("### 💵 مبلغ سرمایه‌گذاری")
    
    investment = st.number_input(
        "مبلغ سرمایه‌گذاری خود را به تومان وارد کنید:",
        min_value=10000000,  # 10 million Toman minimum
        max_value=10000000000,  # 10 billion Toman maximum
        value=100000000,  # Default 100 million
        step=10000000,
        format="%d"
    )
    
    st.markdown(f"**مبلغ انتخابی: {investment:,} تومان**")
    
    st.markdown("---")
    
    # Confirmation
    st.markdown("### ✅ تأیید اطلاعات")
    st.markdown(f"""
    - **پروفایل ریسک:** {profile}
    - **مبلغ سرمایه‌گذاری:** {investment:,} تومان
    """)
    
    st.markdown("---")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 بازگشت", use_container_width=True):
            st.session_state.page = "questionnaire_result"
            st.rerun()
    
    with col2:
        if st.button("🚀 محاسبه پرتفولیو بهینه", use_container_width=True, type="primary"):
            st.session_state.investment = investment
            st.session_state.page = "portfolio_calculation"
            st.rerun()

# ==================== PAGE 5: PORTFOLIO CALCULATION ====================
def show_portfolio_calculation_page():
    """Calculate optimal portfolio"""
    st.markdown('<h1 class="main-header">⚙️ در حال محاسبه پرتفولیوی بهینه</h1>', unsafe_allow_html=True)
    
    risk_profile = st.session_state.get('risk_profile', 'Moderate')
    investment = st.session_state.get('investment', 100000000)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Fetch real data
        status_text.text("۱/۴ دریافت داده‌های واقعی از Yahoo Finance...")
        progress_bar.progress(10)
        
        def update_progress(message):
            status_text.text(f"۱/۴ {message}")
        
        df = create_dataframe(use_real=True, years=3, progress_callback=update_progress)
        progress_bar.progress(30)
        
        if df is None or df.empty:
            st.error("❌ خطا در دریافت داده‌ها از Yahoo Finance")
            st.stop()
        
        # Validate data
        is_valid, message = validate_data(df)
        if not is_valid:
            st.error(f"❌ داده‌های دریافتی معتبر نیستند: {message}")
            st.stop()
        
        st.success(f"✅ داده‌ها دریافت شد: {len(df)} روز، {len(df.columns)} دارایی")
        
        # Step 2: Initialize optimizer
        status_text.text("۲/۴ آماده‌سازی محاسبات...")
        progress_bar.progress(40)
        
        optimizer = PortfolioOptimizer(df)
        st.session_state.optimizer = optimizer
        progress_bar.progress(50)
        
        # Step 3: Generate report (includes optimization + Monte Carlo)
        status_text.text("۳/۴ بهینه‌سازی سبد (این مرحله ممکن است چند ثانیه طول بکشد)...")
        progress_bar.progress(60)
        
        report = optimizer.generate_report(risk_profile, investment)
        progress_bar.progress(90)
        
        # Step 4: Save results
        status_text.text("۴/۴ آماده‌سازی گزارش نهایی...")
        st.session_state.portfolio_report = report
        progress_bar.progress(100)
        
        status_text.text("✅ محاسبات با موفقیت انجام شد!")
        
        # Wait a moment then redirect
        import time
        time.sleep(1)
        st.session_state.page = "portfolio_results"
        st.rerun()
        
    except Exception as e:
        progress_bar.progress(100)
        st.error(f"❌ خطا در محاسبات: {str(e)}")
        st.exception(e)
        
        # Back button
        if st.button("🔙 بازگشت"):
            st.session_state.page = "portfolio_input"
            st.rerun()

# ==================== PAGE 6: PORTFOLIO RESULTS ====================
def show_portfolio_results_page():
    """Display portfolio results"""
    st.markdown('<h1 class="main-header">📊 پرتفولیوی بهینه شما</h1>', unsafe_allow_html=True)
    
    report = st.session_state.get('portfolio_report', {})
    risk_profile = st.session_state.get('risk_profile', 'Moderate')
    investment = st.session_state.get('investment', 100000000)
    
    if not report:
        st.error("گزارشی یافت نشد. لطفاً مجدداً محاسبه کنید.")
        if st.button("🔄 محاسبه مجدد"):
            st.session_state.page = "portfolio_calculation"
            st.rerun()
        return
    
    # Profile badge
    profile_colors = {
        "Conservative": "🛡️",
        "Moderate": "⚖️",
        "Aggressive": "🚀"
    }
    profile_names = {
        "Conservative": "محافظه‌کار",
        "Moderate": "متعادل",
        "Aggressive": "تهاجمی"
    }
    
    st.markdown(f"""
    <div class="success-box">
    <h3>{profile_colors.get(risk_profile, '📊')} پروفایل: {profile_names.get(risk_profile, risk_profile)}</h3>
    <p>مبلغ سرمایه‌گذاری: <strong>{investment:,} تومان</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Section 1: Asset Allocation
    st.markdown("## 📁 توزیع دارایی‌ها")
    
    weights_dict = report.get('weights_dict', {})
    
    if weights_dict:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Pie chart
            fig = go.Figure(data=[go.Pie(
                labels=list(weights_dict.keys()),
                values=list(weights_dict.values()),
                hole=.3,
                marker=dict(colors=['#FFD700', '#C0C0C0', '#F7931A', '#627EEA']),
                textinfo='label+percent',
                textposition='auto'
            )])
            fig.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Table
            weights_df = pd.DataFrame({
                'دارایی': list(weights_dict.keys()),
                'وزن': [f"{w:.2%}" for w in weights_dict.values()],
                'مبلغ (تومان)': [f"{w * investment:,.0f}" for w in weights_dict.values()]
            })
            st.dataframe(weights_df, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ اطلاعات توزیع دارایی‌ها موجود نیست")
    
    st.markdown("---")
    
    # Section 2: Performance Metrics (ALL REAL DATA)
    st.markdown("## 📈 معیارهای عملکرد (داده‌های واقعی)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "بازده سالانه",
            f"{report.get('expected_return_pct', 0):.2f}%",
            help="بازده مورد انتظار سالانه بر اساس داده‌های تاریخی واقعی"
        )
    
    with col2:
        st.metric(
            "ریسک (نوسان)",
            f"{report.get('volatility_pct', 0):.2f}%",
            help="نوسان سالانه محاسبه شده از داده‌های واقعی"
        )
    
    with col3:
        st.metric(
            "نسبت شارپ",
            f"{report.get('sharpe_ratio', 0):.3f}",
            help="بازده به ازای واحد ریسک (محاسبه شده از داده‌های واقعی)"
        )
    
    with col4:
        st.metric(
            "نسبت سورتینو",
            f"{report.get('sortino_ratio', 0):.3f}",
            help="نسبت بازده به ریسک نزولی"
        )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "حداکثر افت",
            f"{report.get('max_drawdown_pct', 0):.2f}%",
            delta_color="inverse",
            help="بیشترین افت تاریخی"
        )
    
    with col2:
        st.metric(
            "نسبت کالمار",
            f"{report.get('calmar_ratio', 0):.3f}",
            help="بازده تقسیم بر حداکثر افت"
        )
    
    st.markdown("---")
    
    # Section 3: Risk Analysis (ALL REAL DATA)
    st.markdown("## 🎲 تحلیل ریسک (محاسبه شده از داده‌های واقعی)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        var_pct = report.get('var_pct', 0)
        var_amount = report.get('var', 0)
        st.metric(
            "Value at Risk (95%)",
            f"{var_pct:.2f}%",
            f"{var_amount:,.0f} تومان",
            delta_color="inverse",
            help="حداکثر ضرر محتمل در 95% موارد (محاسبه شده از شبیه‌سازی مونت‌کارلو)"
        )
    
    with col2:
        cvar_pct = report.get('cvar_pct', 0)
        cvar_amount = report.get('cvar', 0)
        st.metric(
            "CVaR (95%)",
            f"{cvar_pct:.2f}%",
            f"{cvar_amount:,.0f} تومان",
            delta_color="inverse",
            help="میانگین ضرر در 5% بدترین سناریوها"
        )
    
    st.markdown("---")
    
    # Section 4: Monte Carlo Results (10,000 SIMULATIONS WITH REAL DATA)
    st.markdown("## 🎰 نتایج شبیه‌سازی مونت‌کارلو (۱۰,۰۰۰ سناریو با داده‌های واقعی)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "میانگین ارزش نهایی",
            f"{report.get('mc_mean_value', 0):,.0f} تومان",
            help="میانگین ارزش سبد پس از یک سال در 10,000 شبیه‌سازی"
        )
    
    with col2:
        st.metric(
            "بهترین سناریو (95%)",
            f"{report.get('mc_best_case', 0):,.0f} تومان",
            help="ارزش سبد در بهترین 5% سناریوها"
        )
    
    with col3:
        st.metric(
            "بدترین سناریو (5%)",
            f"{report.get('mc_worst_case', 0):,.0f} تومان",
            delta_color="inverse",
            help="ارزش سبد در بدترین 5% سناریوها"
        )
    
    with col4:
        st.metric(
            "احتمال زیان",
            f"{report.get('mc_prob_loss', 0):.1%}",
            delta_color="inverse",
            help="احتمال کاهش ارزش سبد نسبت به امروز"
        )
    
    st.markdown("---")
    
    # Section 5: Recommendation
    st.markdown("## 💡 توصیه")
    recommendation = report.get('recommendation', 'توصیه‌ای موجود نیست')
    st.markdown(recommendation)
    
    st.markdown("---")
    
    # Section 6: Action Buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        save_json_report(report, risk_profile, investment)
    
    with col2:
        if st.button("🔄 محاسبه مجدد", use_container_width=True):
            st.session_state.page = "portfolio_calculation"
            st.rerun()
    
    with col3:
        if st.button("📋 شروع جدید", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key != 'page':
                    del st.session_state[key]
            st.session_state.page = "start"
            st.rerun()
    
    with col4:
        if st.button("🏠 صفحه اصلی", use_container_width=True):
            st.session_state.page = "start"
            st.rerun()
    
    # Data source note
    st.markdown("---")
    st.markdown("""
    <div class="success-box">
    <strong>📊 منبع داده‌ها:</strong> تمام اعداد و آمار بالا از داده‌های واقعی Yahoo Finance محاسبه شده‌اند.
    هیچ عدد هاردکد یا فرضی در این گزارش وجود ندارد.
    </div>
    """, unsafe_allow_html=True)

# ==================== MAIN FUNCTION ====================
def main():
    """Main application function"""
    
    # Initialize page
    if 'page' not in st.session_state:
        st.session_state.page = "start"
    
    # Route to appropriate page
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

# ==================== RUN ====================
if __name__ == "__main__":
    main()
