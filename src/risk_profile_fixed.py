# src/risk_profile.py

QUESTIONS = [
    {
        "question": "۱. سن شما چقدر است؟",
        "options": [
            ("زیر ۳۰ سال", 4),
            ("۳۰-۴۵ سال", 3),
            ("۴۶-۶۰ سال", 2),
            ("بالای ۶۰ سال", 1)
        ]
    },
    {
        "question": "۲. افق سرمایه‌گذاری شما چقدر است؟",
        "options": [
            ("بیش از ۵ سال", 4),
            ("۲-۵ سال", 3),
            ("۱-۲ سال", 2),
            ("کمتر از ۱ سال", 1)
        ]
    },
    {
        "question": "۳. تحمل افت سرمایه شما چقدر است؟",
        "options": [
            ("تا ۴۰٪ افت را تحمل می‌کنم", 4),
            ("تا ۲۵٪", 3),
            ("تا ۱۵٪", 2),
            ("تا ۵٪", 1)
        ]
    },
    {
        "question": "۴. هدف اصلی شما از سرمایه‌گذاری چیست؟",
        "options": [
            ("رشد سرمایه بالا", 4),
            ("ترکیب رشد و درآمد", 3),
            ("حفظ سرمایه با درآمد کم", 2),
            ("حفظ اصل سرمایه", 1)
        ]
    },
    {
        "question": "۵. تجربه شما در بازارهای مالی چقدر است؟",
        "options": [
            ("بیش از ۵ سال", 4),
            ("۲-۵ سال", 3),
            ("۱-۲ سال", 2),
            ("بدون تجربه", 1)
        ]
    },
    {
        "question": "۶. واکنش شما به کاهش ۱۵٪ ارزش پرتفولیو چیست؟",
        "options": [
            ("خرید بیشتر می‌کنم", 4),
            ("نگه می‌دارم", 3),
            ("بخشی را می‌فروشم", 2),
            ("همه را می‌فروشم", 1)
        ]
    },
    {
        "question": "۷. سهم سرمایه‌گذاری از کل دارایی شما چقدر است؟",
        "options": [
            ("بیش از ۵۰٪", 4),
            ("۳۰-۵۰٪", 3),
            ("۱۰-۳۰٪", 2),
            ("کمتر از ۱۰٪", 1)
        ]
    },
    {
        "question": "۸. انتظار بازده سالانه (تومانی) شما چقدر است؟",
        "options": [
            ("بیش از ۵۰٪", 4),
            ("۳۰-۵۰٪", 3),
            ("۲۰-۳۰٪", 2),
            ("۱۰-۲۰٪", 1)
        ]
    },
    {
        "question": "۹. دانش شما از ابزارهای مالی (سهام، صندوق، رمزارز) چقدر است؟",
        "options": [
            ("حرفه‌ای", 4),
            ("خوب", 3),
            ("متوسط", 2),
            ("مبتدی", 1)
        ]
    },
    {
        "question": "۱۰. درآمد شما چقدر قابل اتکا است؟",
        "options": [
            ("درآمد بالا و پایدار", 4),
            ("درآمد متوسط و پایدار", 3),
            ("درآمد متغیر", 2),
            ("بدون درآمد ثابت", 1)
        ]
    },
    {
        "question": "۱۱. انتظار بازده سالانه (دلاری) شما چقدر است؟",
        "options": [
            ("بیش از ۲۰٪", 4),
            ("۱۵-۲۰٪", 3),
            ("۱۰-۱۵٪", 2),
            ("۵-۱۰٪", 1)
        ]
    }
]

def calculate_risk_profile(answers):
    """
    answers: لیست امتیازات (اعداد ۱ تا ۴) برای ۱۱ سؤال
    """
    raw_score = sum(answers)
    # نرمال‌سازی به ۰-۱۰۰ (حداقل ۱۱، حداکثر ۴۴)
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

def display_questionnaire():
    """نمایش پرسشنامه و دریافت پاسخ‌ها"""
    print("📋 پرسشنامه ارزیابی ریسک‌پذیری\n")
    answers = []
    
    for i, q in enumerate(QUESTIONS):
        print(f"{q['question']}")
        for idx, (text, score) in enumerate(q['options']):
            print(f"  {idx+1}) {text}")
        
        while True:
            ans = input("پاسخ شما (۱/۲/۳/۴): ").strip()
            if ans in ['1', '2', '3', '4']:
                score = q['options'][int(ans) - 1][1]
                answers.append(score)
                break
            else:
                print("لطفاً یکی از گزینه‌های ۱/۲/۳/۴ را وارد کنید.")
        print()
    
    return answers

if __name__ == "__main__":
    # تست پرسشنامه
    answers = display_questionnaire()
    result = calculate_risk_profile(answers)
    print(f"نتیجه ارزیابی:")
    print(f"  امتیاز خام: {result['raw_score']}/44")
    print(f"  امتیاز نرمال‌شده: {result['normalized_score']:.1f}/100")
    print(f"  پروفایل ریسک: {result['profile']}")


def display_questionnaire_streamlit():
    """
    نسخه Streamlit از پرسشنامه
    برمی‌گرداند: (answers, risk_profile_result)
    """
    import streamlit as st
    
    answers = []
    
    st.markdown("### 📋 پرسشنامه ارزیابی ریسک‌پذیری")
    st.markdown("لطفاً به سوالات زیر پاسخ دهید:")
    
    for i, q in enumerate(QUESTIONS):
        st.write(f"**{i+1}. {q['question']}**")
        
        # ایجاد گزینه‌ها
        options_text = [opt[0] for opt in q['options']]
        selected = st.radio(
            f"پاسخ سوال {i+1}",
            options=options_text,
            key=f"q_{i}",
            index=None,
            horizontal=False
        )
        
        if selected:
            # یافتن امتیاز پاسخ انتخاب شده
            score = next(opt[1] for opt in q['options'] if opt[0] == selected)
            answers.append(score)
        else:
            st.warning("لطفاً یک گزینه انتخاب کنید.")
            return None, None
    
    # محاسبه نتیجه
    if len(answers) == len(QUESTIONS):
        result = calculate_risk_profile(answers)
        return answers, result
    else:
        return None, None