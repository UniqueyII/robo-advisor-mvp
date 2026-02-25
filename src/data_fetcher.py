# src/data_fetcher.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

# Asset symbols for Yahoo Finance
SYMBOLS = [
    {'name': 'Gold', 'symbol': 'GLD'},      # Gold ETF
    {'name': 'Silver', 'symbol': 'SLV'},    # Silver ETF
    {'name': 'Bitcoin', 'symbol': 'BTC-USD'},
    {'name': 'Ethereum', 'symbol': 'ETH-USD'}
]

def get_usd_to_toman_rate():
    """Get USD to Toman exchange rate"""
    return 700000  # Updated rate - you can make this dynamic if needed

def fetch_asset_data(symbol, years=3, progress_callback=None):
    """
    Fetch real asset data from Yahoo Finance
    
    Parameters:
    -----------
    symbol : str
        Yahoo Finance symbol (e.g., 'GLD', 'BTC-USD')
    years : int
        Number of years of historical data
    progress_callback : callable
        Optional callback for progress updates
    
    Returns:
    --------
    pd.Series : Close prices with datetime index, or None if failed
    """
    try:
        if progress_callback:
            progress_callback(f"📥 Downloading {symbol}...")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years*365)
        
        # Download data using yfinance
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date, interval='1d')
        
        if data.empty:
            print(f"    ⚠️ No data received for {symbol}")
            return None
        
        # Extract Close prices
        close_prices = data['Close']
        
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
    Fetch all asset data and combine into DataFrame
    
    Parameters:
    -----------
    years : int
        Number of years of historical data
    progress_callback : callable
        Optional callback for progress updates
    
    Returns:
    --------
    pd.DataFrame : Price data for all assets in Toman, or None if failed
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
    
    # Create DataFrame
    print("\n🔨 Creating DataFrame...")
    df = pd.DataFrame(data_dict)
    
    # Remove rows with any missing data
    initial_rows = len(df)
    df = df.dropna()
    final_rows = len(df)
    
    if df.empty:
        print("❌ DataFrame is empty after removing NaN values!")
        return None
    
    print(f"  Initial rows: {initial_rows}")
    print(f"  Final rows: {final_rows} (removed {initial_rows - final_rows} rows with missing data)")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Date range: {df.index[0].date()} to {df.index[-1].date()}")
    
    # Convert to Toman
    usd_rate = get_usd_to_toman_rate()
    print(f"\n💰 Converting to Toman (rate: {usd_rate:,.0f} Toman/USD)...")
    
    for col in df.columns:
        df[col] = df[col] * usd_rate
    
    print(f"\n✅ DataFrame ready: {df.shape}")
    print(f"   Assets: {', '.join(df.columns)}")
    
    # Display current prices
    print("\n💵 Current Prices (Toman):")
    for asset in df.columns:
        price = df[asset].iloc[-1]
        print(f"   {asset}: {price:,.0f} Toman")
    
    return df

def create_sample_data():
    """
    Create sample data for testing purposes
    Only used as fallback when real data cannot be fetched
    """
    print("\n" + "="*60)
    print("🔄 CREATING SAMPLE DATA (FALLBACK)")
    print("="*60)
    
    # Generate 3 years of trading days
    date_range = pd.date_range(end=datetime.now(), periods=252*3, freq='B')
    
    # Asset parameters based on historical characteristics
    params = {
        'Gold': {'start_price': 1800, 'mean_return': 0.0002, 'volatility': 0.01},
        'Silver': {'start_price': 22, 'mean_return': 0.0003, 'volatility': 0.015},
        'Bitcoin': {'start_price': 30000, 'mean_return': 0.0015, 'volatility': 0.04},
        'Ethereum': {'start_price': 2000, 'mean_return': 0.0012, 'volatility': 0.035}
    }
    
    usd_rate = get_usd_to_toman_rate()
    np.random.seed(42)
    df = pd.DataFrame(index=date_range)
    
    for asset, param in params.items():
        n_days = len(date_range)
        # Generate realistic price movements using Geometric Brownian Motion
        returns = np.random.normal(param['mean_return'], param['volatility'], n_days)
        prices = param['start_price'] * np.exp(np.cumsum(returns))
        df[asset] = prices * usd_rate
    
    print(f"✅ Sample data created for {len(df)} days")
    print(f"   Assets: {', '.join(df.columns)}")
    print(f"   Date range: {df.index[0].date()} to {df.index[-1].date()}")
    
    return df

def create_dataframe(use_real=True, years=3, progress_callback=None):
    """
    Main function to get price data
    
    Parameters:
    -----------
    use_real : bool
        If True, fetch real data from Yahoo Finance
        If False, generate sample data
    years : int
        Number of years of historical data
    progress_callback : callable
        Optional callback for progress updates
    
    Returns:
    --------
    pd.DataFrame : Price data in Toman
    """
    if use_real:
        df = fetch_all_assets(years, progress_callback)
        if df is not None and not df.empty and len(df) >= 252:
            return df
        else:
            print("\n⚠️ Real data fetch failed or insufficient, using sample data as fallback")
            return create_sample_data()
    else:
        return create_sample_data()

def save_data(df, filename='market_data.csv'):
    """Save data to CSV file"""
    data_dir = 'data/processed'
    os.makedirs(data_dir, exist_ok=True)
    
    filepath = os.path.join(data_dir, filename)
    df.to_csv(filepath)
    print(f"💾 Data saved to {filepath}")
    return filepath

def load_data(filename='market_data.csv'):
    """Load data from CSV file"""
    filepath = os.path.join('data/processed', filename)
    if os.path.exists(filepath):
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        print(f"📂 Data loaded from {filepath}")
        return df
    else:
        print(f"⚠️ File {filepath} not found.")
        return None

def display_data_info(df):
    """Display comprehensive data information"""
    if df is None or df.empty:
        print("❌ No data available!")
        return
    
    print("\n" + "="*60)
    print("📊 DATA SUMMARY")
    print("="*60)
    
    print(f"\n📅 Date Range: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"📈 Number of Days: {len(df)}")
    print(f"📊 Assets: {', '.join(df.columns)}")
    
    print("\n💰 Current Prices (Toman):")
    for asset in df.columns:
        price = df[asset].iloc[-1]
        change = (df[asset].iloc[-1] / df[asset].iloc[0] - 1) * 100
        print(f"  {asset}: {price:,.0f} Toman ({change:+.1f}% over period)")
    
    print("\n📊 First 3 rows:")
    print(df.head(3))
    
    print("\n📊 Last 3 rows:")
    print(df.tail(3))
    
    # Calculate and display returns statistics
    returns = df.pct_change().dropna()
    print("\n📉 Daily Returns Statistics:")
    print(f"{'Asset':<12} {'Mean':<12} {'Std Dev':<12} {'Min':<12} {'Max':<12}")
    print("-" * 60)
    for asset in returns.columns:
        mean = returns[asset].mean() * 100
        std = returns[asset].std() * 100
        min_ret = returns[asset].min() * 100
        max_ret = returns[asset].max() * 100
        print(f"{asset:<12} {mean:>10.3f}% {std:>10.3f}% {min_ret:>10.1f}% {max_ret:>10.1f}%")
    
    # Annualized statistics
    print("\n📈 Annualized Statistics (252 trading days):")
    print(f"{'Asset':<12} {'Return':<12} {'Volatility':<12}")
    print("-" * 36)
    for asset in df.columns:
        annual_return = returns[asset].mean() * 252 * 100
        annual_vol = returns[asset].std() * np.sqrt(252) * 100
        print(f"{asset:<12} {annual_return:>10.1f}% {annual_vol:>10.1f}%")

def validate_data(df):
    """
    Validate that data is suitable for portfolio optimization
    
    Returns:
    --------
    tuple : (is_valid, error_message)
    """
    if df is None:
        return False, "Data is None"
    
    if df.empty:
        return False, "Data is empty"
    
    if len(df) < 252:
        return False, f"Insufficient data: {len(df)} days (need at least 252)"
    
    if len(df.columns) < 2:
        return False, f"Insufficient assets: {len(df.columns)} (need at least 2)"
    
    # Check for NaN values
    if df.isnull().any().any():
        return False, "Data contains NaN values"
    
    # Check for negative values
    if (df < 0).any().any():
        return False, "Data contains negative values"
    
    # Check for zero variance
    for col in df.columns:
        if df[col].std() == 0:
            return False, f"Asset {col} has zero variance"
    
    return True, "Data is valid"

if __name__ == "__main__":
    print("🚀 Starting data fetcher test...")
    print("="*60)
    
    # Test fetching real data
    df = create_dataframe(use_real=True, years=3)
    
    if df is not None and not df.empty:
        # Validate data
        is_valid, message = validate_data(df)
        print(f"\n✅ Validation: {message}")
        
        if is_valid:
            # Display info
            display_data_info(df)
            
            # Save data
            save_data(df, 'market_data.csv')
            
            print("\n🎉 Data is ready for portfolio optimization!")
        else:
            print(f"\n❌ Validation failed: {message}")
    else:
        print("\n❌ Failed to create dataframe")
