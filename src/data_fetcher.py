# src/data_fetcher.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import yfinance as yf

# نمادهای جایگزین - فقط از نمادهای ساده استفاده می‌کنیم
SYMBOLS = [
    {'name': 'Gold', 'symbols': ['GLD']},
    {'name': 'Silver', 'symbols': ['SLV']},
    {'name': 'Bitcoin', 'symbols': ['BTC-USD']},
    {'name': 'Ethereum', 'symbols': ['ETH-USD']}
]

def get_usd_to_toman_rate():
    """نرخ دلار به تومان"""
    return 160000

def fetch_asset_simple(symbol, years=3):
    """دریافت ساده داده با yfinance - حتماً Series برگرداند"""
    try:
        print(f"    دانلود {symbol}...")
        # Removed show_errors and progress to ensure compatibility
        data = yf.download(symbol, period=f'{years}y')
        
        if data.empty:
            print(f"    ⚠️ داده {symbol} خالی است")
            return None
        
        # Taking the 'Close' column
        if 'Close' in data.columns:
            close_data = data['Close']
            
            # Check if it's a Series or a MultiIndex DataFrame (happens in newer yfinance versions)
            if isinstance(close_data, pd.DataFrame):
                return close_data.iloc[:, 0]
            return close_data
        else:
            print(f"    ⚠️ ستون Close در {symbol} نیست")
            return None
            
    except Exception as e:
        print(f"    ❌ خطا: {str(e)}")
        return None

def create_real_data_simple():
    """دریافت ساده داده واقعی"""
    print("📥 دریافت داده‌های واقعی...")
    
    data_dict = {}
    successful = 0
    
    for asset in SYMBOLS:
        asset_name = asset['name']
        symbol = asset['symbols'][0]
        
        print(f"\n  {asset_name} ({symbol}):")
        prices = fetch_asset_simple(symbol)
        
        if prices is not None and isinstance(prices, pd.Series) and len(prices) > 100:
            data_dict[asset_name] = prices
            successful += 1
            
            # نمایش آخرین قیمت
            last_price = float(prices.iloc[-1])
            print(f"    آخرین قیمت: ${last_price:,.2f}")
            print(f"    تعداد روزها: {len(prices)}")
        else:
            print(f"    ❌ دریافت نشد یا داده ناکافی")
    
    print(f"\n📊 نتیجه: {successful}/4 دارایی دریافت شدند")
    
    if successful < 2:
        print("⚠️ حداقل ۲ دارایی نیاز است")
        return None
    
    # ایجاد DataFrame
    print("\n🔨 ایجاد DataFrame...")
    df = pd.DataFrame(data_dict)
    
    # حذف سطرهای خالی
    initial_rows = len(df)
    df = df.dropna()
    final_rows = len(df)
    
    if df.empty:
        print("❌ DataFrame خالی است!")
        return None
    
    print(f"  سطرهای اولیه: {initial_rows}")
    print(f"  سطرهای نهایی: {final_rows}")
    print(f"  ستون‌ها: {list(df.columns)}")
    
    # تبدیل به تومان
    usd_rate = get_usd_to_toman_rate()
    print(f"💰 تبدیل به تومان (نرخ: {usd_rate:,.0f})...")
    
    for col in df.columns:
        df[col] = df[col] * usd_rate
    
    print(f"\n✅ DataFrame ساخته شد: {df.shape}")
    return df

def create_sample_data():
    """ایجاد داده نمونه"""
    print("🔄 ایجاد داده‌های نمونه...")
    
    date_range = pd.date_range(end=datetime.now(), periods=365*3, freq='B')
    
    params = {
        'Gold': {'start_price': 1800, 'mean_return': 0.0001, 'volatility': 0.01},
        'Silver': {'start_price': 22, 'mean_return': 0.0002, 'volatility': 0.015},
        'Bitcoin': {'start_price': 30000, 'mean_return': 0.001, 'volatility': 0.03},
        'Ethereum': {'start_price': 2000, 'mean_return': 0.0008, 'volatility': 0.025}
    }
    
    usd_rate = get_usd_to_toman_rate()
    np.random.seed(42)
    df = pd.DataFrame(index=date_range)
    
    for asset, param in params.items():
        n_days = len(date_range)
        returns = np.random.normal(param['mean_return'], param['volatility'], n_days)
        prices = param['start_price'] * np.exp(np.cumsum(returns))
        df[asset] = prices * usd_rate
    
    print(f"✅ داده‌های نمونه برای {len(df)} روز ایجاد شدند.")
    return df

def create_dataframe(use_real=True):
    """دریافت داده‌ها"""
    if use_real:
        df = create_real_data_simple()
        if df is not None and not df.empty:
            return df
        else:
            print("\n⚠️ استفاده از داده‌های نمونه")
            return create_sample_data()
    else:
        return create_sample_data()

def save_data(df, filename='market_data.csv'):
    """ذخیره داده‌ها"""
    data_dir = 'data/processed'
    os.makedirs(data_dir, exist_ok=True)
    
    filepath = os.path.join(data_dir, filename)
    df.to_csv(filepath)
    print(f"💾 ذخیره در {filepath}")
    return filepath

def load_data(filename='market_data.csv'):
    """بارگذاری داده‌ها"""
    filepath = os.path.join('data/processed', filename)
    if os.path.exists(filepath):
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        print(f"📂 بارگذاری از {filepath}")
        return df
    else:
        print(f"⚠️ فایل {filepath} یافت نشد.")
        return None

def display_data_info(df):
    """نمایش اطلاعات داده‌ها"""
    if df is None or df.empty:
        print("❌ داده‌ای موجود نیست!")
        return
    
    print("\n" + "="*60)
    print("📊 خلاصه داده‌ها")
    print("="*60)
    
    print(f"\n📅 بازه زمانی: {df.index[0].date()} تا {df.index[-1].date()}")
    print(f"📈 تعداد روزها: {len(df)}")
    
    print("\n💰 قیمت‌های فعلی (تومان):")
    for asset in df.columns:
        price = df[asset].iloc[-1]
        print(f"  {asset}: {price:,.0f} تومان")
    
    print("\n📊 ۳ ردیف اول:")
    print(df.head(3))
    
    print("\n📈 ۳ ردیف آخر:")
    print(df.tail(3))
    
    # بازده روزانه
    returns = df.pct_change().dropna()
    print("\n📉 بازده روزانه:")
    print(f"{'دارایی':<10} {'میانگین':<10} {'نوسان':<10}")
    print("-" * 30)
    for asset in returns.columns:
        mean = returns[asset].mean() * 100
        std = returns[asset].std() * 100
        print(f"{asset:<10} {mean:.3f}٪    {std:.3f}٪")

if __name__ == "__main__":
    print("🚀 شروع...")
    df = create_dataframe(use_real=True)
    
    if df is not None and not df.empty:
        display_data_info(df)
        save_data(df, 'market_data.csv')
        print("\n🎉 داده‌ها آماده هستند!")
    else:
        print("❌ مشکل در دریافت داده.")