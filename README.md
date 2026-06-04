# 🤖 Robo-Advisor MVP - مشاور سرمایه‌گذاری هوشمند

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.24%2B-red)
![Finance](https://img.shields.io/badge/Finance-Quant-orange)
![GitHub](https://img.shields.io/badge/GitHub-Repository-brightgreen)
[![Tests](https://github.com/UniqueyII/robo-advisor-mvp/actions/workflows/tests.yml/badge.svg)](https://github.com/UniqueyII/robo-advisor-mvp/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/UniqueyII/robo-advisor-mvp/branch/main/graph/badge.svg)](https://codecov.io/gh/UniqueyII/robo-advisor-mvp)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.24+-red.svg)](https://streamlit.io/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://robo-advisor-mvp.streamlit.app)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Tests](https://github.com/UniqueyII/robo-advisor-mvp/actions/workflows/tests.yml/badge.svg)
## 🌟 پروژه نمونه کار حرفه‌ای

یک سیستم مشاوره سرمایه‌گذاری خودکار که با استفاده از تکنیک‌های پیشرفته مالی، سبد سرمایه‌گذاری بهینه را پیشنهاد می‌دهد.

### ✨ ویژگی‌های کلیدی

- 🧠 **ارزیابی هوشمند ریسک**: پرسشنامه ۱۱ سواله با الگوریتم نرمال‌سازی
- 📊 **مدل‌های مالی پیشرفته**: 
  - Modern Portfolio Theory (MPT)
  - شبیه‌سازی مونت‌کارلو
  - Value at Risk (VaR) و Expected Shortfall
- 💰 **پشتیبانی چند ارزی**: نمایش همزمان تومان و دلار
- 🎯 **دارایی‌های متنوع**: طلا، نقره، ارزهای دیجیتال، بورس ایران
- 🖥️ **داشبورد تعاملی**: رابط کاربری با Streamlit در ۶ صفحه

### 🏗️ معماری فنی
robo-advisor-mvp/
├── src/ # کدهای اصلی
│ ├── risk_profile.py # ارزیابی ریسک
│ ├── data_fetcher.py # دریافت داده‌های بازار
│ ├── portfolio_optimizer.py # مدل‌های مالی
│ └── dashboard.py # رابط کاربری
├── data/ # داده‌های بازار
├── notebooks/ # تحلیل‌های اولیه
├── tests/ # تست‌های واحد
└── docs/ # مستندات


### 🚀 اجرای پروژ
- "http://192.168.1.104:8501" لینک سایت پروؤه

#### ۱. پیش‌نیازها
- Python 3.9 یا بالاتر
- pip (مدیریت بسته‌های پایتون)

#### ۲. نصب وابستگی‌ها
```bash
# ایجاد محیط مجازی
python -m venv venv

# فعال‌سازی محیط (در ویندوز)
venv\Scripts\activate

# نصب پکیج‌ها
pip install -r requirements.txt

# دریافت داده‌ها
python src/data_fetcher.py

# اجرای داشبورد
streamlit run src/dashboard.py
# سپس مرورگر باز می‌شود و می‌توانید از http://localhost:8501 استفاده کنید


## 🚀 شروع سریع

### پیش‌نیازها
*   Python 3.9 یا بالاتر
*   pip (مدیر بسته پایتون)
*   [Git](https://git-scm.com/) (برای کلون کردن)

### نصب و راه‌اندازی
1.  **کلون کردن ریپازیتوری و رفتن به دایرکتوری پروژه:**
    ```bash
    git clone https://github.com/UniqueyII/robo-advisor-mvp.git
    cd robo-advisor-mvp
    ```
2.  **ایجاد و فعال‌سازی محیط مجازی (توصیه می‌شود):**
    ```bash
    python -m venv venv
    # در ویندوز:
    venv\Scripts\activate
    # در مک/لینوکس:
    source venv/bin/activate
    ```
3.  **نصب وابستگی‌ها:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **دریافت داده‌های بازار (اختیاری - اگر فایل داده از قبل موجود نیست):**
    ```bash
    python src/data_fetcher.py
    ```
5.  **راه‌اندازی اپلیکیشن داشبورد:**
    ```bash
    streamlit run src/dashboard.py
    ```
6.  مرورگر شما به طور خودکار باز می‌شود و اپلیکیشن در `http://192.168.1.104:8501' در دسترس خواهد بود.

## 📸 گالری تصاویر
<img width="1879" height="1079" alt="image" src="https://github.com/user-attachments/assets/fc41bd80-7e9d-4b0c-9666-e59929a9d65e" />

<img width="1878" height="1073" alt="image" src="https://github.com/user-attachments/assets/5ab1c480-2b66-408a-8f0a-b68537a2434a" />

<img width="1914" height="1008" alt="image" src="https://github.com/user-attachments/assets/edad21c8-b5b7-4ecb-843f-7908a5011075" />

| صفحه پرسشنامه ریسک | پیشنهاد پرتفولیو |
| :---: | :---: |
| ![صفحه پرسشنامه](https://via.placeholder.com/400x250/3E8ACC/FFFFFF?text=Risk+Questionnaire+Page) | ![صفحه نتایج](https://via.placeholder.com/400x250/2E7D32/FFFFFF?text=Portfolio+Recommendation) |
| *توضیح مختصر تصویر ۱* | *توضیح مختصر تصویر ۲* |

## 🧩 چالش‌های فنی و راه‌حل‌ها
| چالش | راه‌حل پیاده‌سازی شده |
| :--- | :--- |
| **یکپارچه‌سازی داده‌های بازار ایران** | استفاده از ترکیب [کتابخانه/API/وب‌اسکرپینگ] برای دریافت داده‌های بورس تهران. |
| **محاسبات سنگین شبیه‌سازی مونت‌کارلو** | بهینه‌سازی با کتابخانه NumPy (بردارسازی) و پیاده‌سازی Caching برای نتایج. |
| **مدیریت وضعیت (State) در Streamlit** | استفاده از `st.session_state` برای حفظ داده کاربر بین صفحات مختلف داشبورد. |
| **نمایش دو واحد پولی (تومان/دلار)** | ایجاد یک Toggle در UI و تبدیل نرخ واقعی با تابع helper. |

## 🛠️ تکنولوژی‌های استفاده شده
*   **زبان اصلی**: ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white)
*   **فریم‌ورک وب/داشبورد**: ![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
*   **پردازش داده و محاسبات**: ![Pandas](https://img.shields.io/badge/-Pandas-150458?logo=pandas&logoColor=white) ![NumPy](https://img.shields.io/badge/-NumPy-013243?logo=numpy&logoColor=white) ![SciPy](https://img.shields.io/badge/-SciPy-8CAAE6?logo=scipy&logoColor=white)
*   **مصورسازی داده**: ![Plotly](https://img.shields.io/badge/-Plotly-3F4F75?logo=plotly&logoColor=white) ![Matplotlib](https://img.shields.io/badge/-Matplotlib-11557C?logo=python&logoColor=white)
*   **دریافت داده مالی**: ![yfinance](https://img.shields.io/badge/-yfinance-00A86B?logo=yahoo&logoColor=white)

## 📈 مهارت‌های نمایش داده شده
این پروژه به طور عملی دانش و مهارت‌های زیر را نشان می‌دهد:
1.  **برنامه‌نویسی و معماری نرم‌افزار**: طراحی ماژولار، اصول کدنویسی تمیز (SOLID/DRY)، مدیریت وابستگی.
2.  **مهندسی و تحلیل داده مالی**: کار با APIهای مالی، پاک‌سازی و پردازش سری‌های زمانی، مدیریت نرخ ارز.
3.  **مالی کمی (Quantitative Finance)**: پیاده‌سازی عملی مدل‌های MPT، شبیه‌سازی مونت‌کارلو، معیارهای ریسک (VaR/CVaR).
4.  **توسعه اپلیکیشن تعاملی**: ساخت رابط کاربری با Streamlit، مدیریت state، طراحی UX.
5.  **مدیریت پروژه حرفه‌ای**: کنترل نسخه با Git، مستندسازی، بسته‌بندی و ارائه پروژه.

---

## 🌍 English Version

# 🤖 Robo-Advisor MVP: Intelligent Investment Portfolio Optimizer

## 📖 Project Overview
An automated investment advisory system (Robo-Advisor) that uses quantitative finance techniques to suggest an optimized investment portfolio based on a user's risk profile. This project is a complete Minimum Viable Product (MVP) showcasing modular architecture, advanced financial models, and an interactive dashboard.

## ✨ Key Features
- **🧠 Intelligent Risk Assessment**: An 11-question risk questionnaire with score normalization.
- **📊 Advanced Financial Models**:
  - Modern Portfolio Theory (MPT) and Efficient Frontier.
  - Monte Carlo simulation for forecasting.
  - Value at Risk (VaR) and Conditional Value at Risk (CVaR) calculation.
- **💰 Multi-Currency Support**: Display results in both Iranian Toman and US Dollar.
- **🌐 Diverse Assets**: Coverage of Gold, Silver, Cryptocurrencies, and [Iranian assets such as Tehran Stock Exchange equities].
- **🖥️ Interactive Dashboard**: A 6-page user interface built with Streamlit.

## 🏗️ Project Architecture
*(Same as above, in English if preferred)*

## 🚀 Quick Start
*(Same installation steps as above)*

## 📸 Screenshot Gallery
*(Add your own screenshots later)*

## 🧩 Technical Challenges & Solutions
| Challenge | Implemented Solution |
| :--- | :--- |
| **Integrating Iranian Market Data** | Using a combination of [Library/API/Web Scraping] to fetch Tehran Stock Exchange data. |
| **Heavy Monte Carlo Simulation Computations** | Optimized with NumPy vectorization and implemented Caching for results. |
| **Managing State in Streamlit** | Utilized `st.session_state` to persist user data across different dashboard pages. |
| **Displaying Dual Currency (Toman/USD)** | Created a UI toggle and real-time rate conversion using a helper function. |

## 🛠️ Technology Stack
*(Same badges as above)*

## 📈 Demonstrated Skills
This project practically demonstrates the following knowledge and skills:
1.  **Software Programming & Architecture**: Modular design, clean code principles (SOLID/DRY), dependency management.
2.  **Financial Data Engineering & Analysis**: Working with financial APIs, cleaning and processing time-series data, and handling exchange rates.
3.  **Quantitative Finance**: Practical implementation of MPT models, Monte Carlo simulation, risk metrics (VaR/CVaR).
4.  **Interactive Application Development**: Building UI with Streamlit, state management, and UX design.
5.  **Professional Project Management**: Version control with Git, documentation, packaging, and project presentation.

## 👨‍💻 Developer
**[Your Name]**  
- 📧 Email: [Your Email]  
- 💼 LinkedIn: [Your LinkedIn Profile URL]  
- 🐙 GitHub: [Your GitHub Profile URL]

## 📄 License
Distributed under the MIT License. See `LICENSE` file for more information.

---

# 
