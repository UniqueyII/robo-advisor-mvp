import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Asset symbols for Yahoo Finance - استفاده از قیمت اونس برای طلا و نقره
SYMBOLS = [
    {'name': 'Gold', 'symbol': 'GC=F'},     # Gold futures (per ounce)
    {'name': 'Silver', 'symbol': 'SI=F'},   # Silver futures (per ounce)
    {'name': 'Bitcoin', 'symbol': 'BTC-USD'},
    {'name': 'Ethereum', 'symbol': 'ETH-USD'},
]

def get_usd_to_toman_rate():
    """Get USD to Toman exchange rate (approximate)"""
    return 700000  # 700,000 Toman per USD

def fetch_asset_data(symbol, years=3, progress_callback=None):
    """
    Fetch real asset data from Yahoo Finance.
    Returns a pandas Series of close prices, or None if failed.
    """
    try:
        if progress_callback:
            progress_callback(f"📥 Downloading {symbol}...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years*365)
        
        # استفاده از yf.download (پایدارتر)
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)
        
        # اگر خالی بود، روش دوم: Ticker.history
        if data.empty:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
        
        if data.empty:
            print(f"    ⚠️ No data for {symbol}")
            return None
        
        close_prices = data['Close'].squeeze()
        close_prices = close_prices.dropna()
        
        if len(close_prices) < 100:
            print(f"    ⚠️ Insufficient data for {symbol} (only {len(close_prices)} days)")
            return None
        
        print(f"    ✅ {symbol}: {len(close_prices)} days, Last price: ${close_prices.iloc[-1]:,.2f}")
        return close_prices
        
    except Exception as e:
        print(f"    ❌ Error fetching {symbol}: {str(e)}")
        return None

def fetch_all_assets(years=3, progress_callback=None):
    """
    Fetch all asset data and combine into DataFrame with aligned indices.
    """
    print("="*60)
    print("📥 FETCHING REAL DATA FROM YAHOO FINANCE")
    print("="*60)
    
    data_dict = {}
    successful = 0
    
    for asset_info in SYMBOLS:
        asset_name = asset_info['name']
        symbol = asset_info['symbol']
        
        print(f"\n{asset_name} ({symbol}):")
        prices = fetch_asset_data(symbol, years, progress_callback)
        
        if prices is not None and isinstance(prices, pd.Series) and len(prices) > 100:
            data_dict[asset_name] = prices
            successful += 1
        else:
            print(f"    ❌ Failed to fetch {asset_name}")
    
    print(f"\n📊 Result: {successful}/{len(SYMBOLS)} assets fetched successfully")
    
    if successful < 2:
        print("⚠️ Need at least 2 assets for portfolio optimization")
        return None
    
    # همسان‌سازی ایندکس‌ها (روزهای مشترک)
    print("\n🔄 Aligning date indices...")
    
    common_index = None
    for name, series in data_dict.items():
        if common_index is None:
            common_index = series.index
        else:
            common_index = common_index.intersection(series.index)
    
    print(f"  Common dates: {len(common_index)} days")
    
    # محدود کردن همه سری‌ها به ایندکس مشترک
    aligned_data = {}
    for name, series in data_dict.items():
        aligned_data[name] = series.loc[common_index]
    
    # ساخت DataFrame
    print("\n🔨 Creating DataFrame...")
    df = pd.DataFrame(aligned_data)
    
    if df.isnull().any().any():
        print("⚠️ Still found NaN values, dropping rows...")
        df = df.dropna()
    
    if df.empty:
        print("❌ DataFrame is empty after alignment!")
        return None
    
    print(f"  Rows: {len(df)}, Columns: {list(df.columns)}")
    print(f"  Date range: {df.index[0].date()} to {df.index[-1].date()}")
    
    # تبدیل به تومان
    usd_rate = get_usd_to_toman_rate()
    print(f"\n💰 Converting to Toman (rate: {usd_rate:,.0f} Toman/USD)...")
    for col in df.columns:
        df[col] = df[col] * usd_rate
    
    print(f"\n✅ DataFrame ready: {df.shape}")
    print("💵 Current Prices (Toman per ounce for Gold/Silver):")
    for asset in df.columns:
        price = df[asset].iloc[-1]
        print(f"   {asset}: {price:,.0f} Toman")
    
    return df
