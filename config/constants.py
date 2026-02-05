# config/constants.py

# نرخ تبدیل دلار به تومان (می‌توانی به‌روز کنی)
USD_TO_TOMAN = 160000

# وزن دارایی‌ها برای سبدهای مختلف
PORTFOLIO_WEIGHTS = {
    'Conservative': {'Gold': 0.4, 'Silver': 0.3, 'Bitcoin': 0.2, 'Ethereum': 0.1},
    'Moderate': {'Gold': 0.3, 'Silver': 0.2, 'Bitcoin': 0.3, 'Ethereum': 0.2},
    'Aggressive': {'Gold': 0.1, 'Silver': 0.1, 'Bitcoin': 0.5, 'Ethereum': 0.3}
}