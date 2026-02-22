# src/portfolio_optimizer.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class PortfolioOptimizer:
    """
    کلاس بهینه‌سازی سبد سرمایه‌گذاری با MPT و شبیه‌سازی مونت‌کارلو
    """
    
    def __init__(self, price_data):
        """
        پارامترها:
        -----------
        price_data : DataFrame
            داده‌های قیمت دارایی‌ها
        """
        self.prices = price_data
        self.returns = self.prices.pct_change().dropna()
        self.assets = list(self.prices.columns)
        self.n_assets = len(self.assets)
        
        # محاسبه آمار
        self.mean_returns = self.returns.mean() * 252  # بازده سالانه
        self.cov_matrix = self.returns.cov() * 252     # ماتریس کوواریانس سالانه
        
        # وزن‌های پیش‌فرض برای پروفایل‌های مختلف
        self.profile_weights = {
            'Conservative': {'Gold': 0.4, 'Silver': 0.3, 'Bitcoin': 0.2, 'Ethereum': 0.1},
            'Moderate': {'Gold': 0.3, 'Silver': 0.2, 'Bitcoin': 0.3, 'Ethereum': 0.2},
            'Aggressive': {'Gold': 0.1, 'Silver': 0.1, 'Bitcoin': 0.5, 'Ethereum': 0.3}
        }
    
    def get_profile_weights(self, risk_profile):
        """
        دریافت وزن‌های از پیش تعریف شده برای پروفایل ریسک
        
        پارامترها:
        -----------
        risk_profile : str
            'Conservative', 'Moderate', یا 'Aggressive'
        
        بازگشت:
        --------
        np.array : وزن‌های سبد
        """
        if risk_profile in self.profile_weights:
            weights_dict = self.profile_weights[risk_profile]
            # تبدیل به آرایه به ترتیب دارایی‌ها
            weights = np.array([weights_dict[asset] for asset in self.assets])
            return weights
        else:
            raise ValueError(f"پروفایل {risk_profile} شناخته شده نیست.")
    
    def portfolio_stats(self, weights):
        """
        محاسبه بازده و ریسک سبد
        
        پارامترها:
        -----------
        weights : np.array
            وزن‌های سبد
        
        بازگشت:
        --------
        dict : آمار سبد
        """
        # بازده مورد انتظار
        port_return = np.sum(self.mean_returns * weights)
        
        # ریسک (انحراف معیار)
        port_volatility = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        
        # نسبت شارپ (فرض نرخ بدون ریسک = 0.05 یا 5%)
        risk_free_rate = 0.05
        sharpe_ratio = (port_return - risk_free_rate) / port_volatility if port_volatility != 0 else 0
        
        return {
            'return': port_return,
            'volatility': port_volatility,
            'sharpe_ratio': sharpe_ratio,
            'weights': weights
        }
    
    def optimize_sharpe(self, risk_profile=None):
        """
        بهینه‌سازی سبد برای بیشینه‌کردن نسبت شارپ (کارای مارکوویتز)
        
        پارامترها:
        -----------
        risk_profile : str یا None
            اگر مشخص باشد، از وزن‌های اولیه آن پروفایل استفاده می‌کند
        
        بازگشت:
        --------
        dict : سبد بهینه
        """
        # تابع منفی شارپ (چون minimize می‌کنیم)
        def negative_sharpe(weights):
            stats = self.portfolio_stats(weights)
            return -stats['sharpe_ratio']
        
        # محدودیت‌ها: مجموع وزن‌ها = 1
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        
        # حدود وزن‌ها: بین ۰ تا ۱
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        
        # وزن اولیه
        if risk_profile and risk_profile in self.profile_weights:
            initial_weights = self.get_profile_weights(risk_profile)
        else:
            initial_weights = np.array([1/self.n_assets] * self.n_assets)  # وزن مساوی
        
        # بهینه‌سازی
        result = minimize(negative_sharpe, initial_weights,
                         method='SLSQP', bounds=bounds,
                         constraints=constraints)
        
        if result.success:
            optimal_weights = result.x
            return self.portfolio_stats(optimal_weights)
        else:
            raise RuntimeError("بهینه‌سازی ناموفق بود.")
    
    def efficient_frontier(self, n_portfolios=100):
        """
        تولید مرز کارا
        
        پارامترها:
        -----------
        n_portfolios : int
            تعداد سبدهای تصادفی برای تولید مرز کارا
        
        بازگشت:
        --------
        tuple : (بازده‌ها, ریسک‌ها, وزن‌ها, شارپ‌ها)
        """
        returns = []
        volatilities = []
        sharpe_ratios = []
        all_weights = []
        
        for _ in range(n_portfolios):
            # تولید وزن‌های تصادفی
            weights = np.random.random(self.n_assets)
            weights /= np.sum(weights)
            
            stats = self.portfolio_stats(weights)
            
            returns.append(stats['return'])
            volatilities.append(stats['volatility'])
            sharpe_ratios.append(stats['sharpe_ratio'])
            all_weights.append(weights)
        
        return np.array(returns), np.array(volatilities), np.array(all_weights), np.array(sharpe_ratios)
    
    def monte_carlo_simulation(self, weights, initial_investment, years=1, n_simulations=1000):
        """
        شبیه‌سازی مونت‌کارلو برای پیش‌بینی ارزش آینده سبد
        
        پارامترها:
        -----------
        weights : np.array
            وزن‌های سبد
        initial_investment : float
            سرمایه اولیه (تومان)
        years : int
            افق زمانی (سال)
        n_simulations : int
            تعداد شبیه‌سازی‌ها
        
        بازگشت:
        --------
        dict : نتایج شبیه‌سازی
        """
        days = years * 252  # روزهای کاری
        last_prices = self.prices.iloc[-1].values
        
        # محاسبه تعداد سهم هر دارایی
        shares = (weights * initial_investment) / last_prices
        
        results = []
        
        for _ in range(n_simulations):
            # شبیه‌سازی مسیر قیمت
            simulated_prices = last_prices.copy()
            
            for day in range(days):
                # تولید بازده تصادفی با توزیع نرمال
                random_returns = np.random.multivariate_normal(
                    self.mean_returns / 252,  # بازده روزانه
                    self.cov_matrix / 252,     # کوواریانس روزانه
                    size=1
                )[0]
                
                simulated_prices *= (1 + random_returns)
            
            # ارزش نهایی سبد
            final_value = np.sum(shares * simulated_prices)
            results.append(final_value)
        
        results = np.array(results)
        
        # محاسبه معیارهای ریسک
        mean_final_value = np.mean(results)
        median_final_value = np.median(results)
        std_final_value = np.std(results)
        
        # محاسبه VaR (در سطح اطمینان 95%)
        var_95 = initial_investment - np.percentile(results, 5)
        cvar_95 = initial_investment - results[results <= np.percentile(results, 5)].mean()
        
        # احتمال زیان
        prob_loss = np.sum(results < initial_investment) / n_simulations
        
        return {
            'initial_investment': initial_investment,
            'mean_final_value': mean_final_value,
            'median_final_value': median_final_value,
            'std_final_value': std_final_value,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'prob_loss': prob_loss,
            'all_simulations': results,
            'expected_return_pct': (mean_final_value / initial_investment - 1) * 100
        }
    
    def calculate_var(self, weights, initial_investment, confidence_level=0.95, method='historical'):
        """
        محاسبه Value at Risk
        
        پارامترها:
        -----------
        weights : np.array
            وزن‌های سبد
        initial_investment : float
            سرمایه اولیه
        confidence_level : float
            سطح اطمینان (مثلاً 0.95 برای 95%)
        method : str
            'historical' یا 'parametric'
        
        بازگشت:
        --------
        float : مقدار VaR
        """
        if method == 'historical':
            # VaR تاریخی
            portfolio_returns = self.returns.dot(weights)
            var = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
            var_amount = -var * initial_investment
            
        elif method == 'parametric':
            # VaR پارامتریک (فرض توزیع نرمال)
            port_return = np.sum(self.mean_returns * weights)
            port_volatility = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
            
            from scipy.stats import norm
            z_score = norm.ppf(1 - confidence_level)
            var_amount = initial_investment * (z_score * port_volatility - port_return)
        
        else:
            raise ValueError("method باید 'historical' یا 'parametric' باشد.")
        
        return var_amount
    
    def generate_report(self, risk_profile, investment_amount):
        """
        تولید گزارش کامل برای یک پروفایل ریسک
        
        پارامترها:
        -----------
        risk_profile : str
            پروفایل ریسک
        investment_amount : float
            مبلغ سرمایه‌گذاری (تومان)
        
        بازگشت:
        --------
        dict : گزارش کامل
        """
        print(f"📊 تولید گزارش برای پروفایل: {risk_profile}")
        print(f"💰 سرمایه: {investment_amount:,.0f} تومان")
        
        # ۱. وزن‌های پروفایل
        profile_weights = self.get_profile_weights(risk_profile)
        profile_stats = self.portfolio_stats(profile_weights)
        
        # ۲. سبد بهینه (شارپ ماکسیمم)
        print("\n🔍 در حال بهینه‌سازی سبد...")
        optimal_portfolio = self.optimize_sharpe(risk_profile)
        
        # ۳. شبیه‌سازی مونت‌کارلو (۱ سال)
        print("🎲 در حال شبیه‌سازی مونت‌کارلو...")
        mc_results = self.monte_carlo_simulation(
            optimal_portfolio['weights'],
            investment_amount,
            years=1,
            n_simulations=2000
        )
        
        # ۴. محاسبه VaR
        var_historical = self.calculate_var(
            optimal_portfolio['weights'],
            investment_amount,
            method='historical'
        )
        
        var_parametric = self.calculate_var(
            optimal_portfolio['weights'],
            investment_amount,
            method='parametric'
        )
        
        # ۵. گردآوری گزارش
        report = {
            'risk_profile': risk_profile,
            'investment_amount': investment_amount,
            
            'profile_portfolio': {
                'weights': dict(zip(self.assets, profile_weights)),
                'stats': profile_stats
            },
            
            'optimal_portfolio': {
                'weights': dict(zip(self.assets, optimal_portfolio['weights'])),
                'stats': optimal_portfolio
            },
            
            'monte_carlo': mc_results,
            
            'risk_metrics': {
                'var_historical': var_historical,
                'var_parametric': var_parametric,
                'expected_shortfall': mc_results['cvar_95']
            },
            
            'recommendation': self.generate_recommendation(
                risk_profile,
                optimal_portfolio,
                mc_results
            )
        }
        
        print(f"✅ گزارش برای {risk_profile} آماده است!")
        return report
    
    def generate_recommendation(self, risk_profile, optimal_portfolio, mc_results):
        """
        تولید توصیه سرمایه‌گذاری
        """
        expected_return = mc_results['expected_return_pct']
        prob_loss = mc_results['prob_loss']
        var = mc_results['var_95']
        
        if risk_profile == 'Conservative':
            if prob_loss > 0.1:
                rec = "ریسک بالا برای پروفایل محافظه‌کار. پیشنهاد می‌شود سهم طلا افزایش یابد."
            else:
                rec = "سبد مناسب برای پروفایل محافظه‌کار. تعادل خوبی بین ریسک و بازده دارد."
        
        elif risk_profile == 'Moderate':
            if expected_return > 20:
                rec = "بازده مورد انتظار عالی! این سبد برای سرمایه‌گذاران متعادل ایده‌آل است."
            else:
                rec = "سبد متعادل با ریسک کنترل‌شده. مناسب برای اهداف میان‌مدت."
        
        else:  # Aggressive
            if expected_return > 30:
                rec = "بازده بالقوه بسیار بالا! مناسب برای سرمایه‌گذاران ریسک‌پذیر با افق بلندمدت."
            else:
                rec = "سبد تهاجمی با تمرکز بر رمزارزها. نوسان بالا اما پتانسیل رشد عالی."
        
        return {
            'text': rec,
            'expected_return': expected_return,
            'risk_level': 'Low' if risk_profile == 'Conservative' else 
                         'Medium' if risk_profile == 'Moderate' else 'High',
            'suggested_horizon': 'کوتاه‌مدت (۱-۲ سال)' if risk_profile == 'Conservative' else
                               'میان‌مدت (۳-۵ سال)' if risk_profile == 'Moderate' else
                               'بلندمدت (۵+ سال)'
        }
    
    def plot_efficient_frontier(self, optimal_portfolio=None):
        """
        رسم مرز کارا
        """
        returns, volatilities, _, sharpe_ratios = self.efficient_frontier(200)
        
        plt.figure(figsize=(12, 8))
        
        # نقاط سبدهای تصادفی
        scatter = plt.scatter(volatilities, returns, c=sharpe_ratios, 
                             cmap='viridis', alpha=0.6, s=30)
        plt.colorbar(scatter, label='نسبت شارپ')
        
        # سبد بهینه اگر داده شود
        if optimal_portfolio:
            plt.scatter(optimal_portfolio['volatility'], optimal_portfolio['return'],
                       c='red', s=200, marker='*', label='سبد بهینه')
        
        plt.xlabel('ریسک (انحراف معیار)')
        plt.ylabel('بازده مورد انتظار')
        plt.title('مرز کارای مارکوویتز')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        return plt

# تابع کمکی برای استفاده سریع
def load_and_optimize():
    """Load REAL data from Yahoo Finance and run optimization"""
    try:
        # Define assets to fetch
        assets = {
            'Gold': 'GC=F',
            'Silver': 'SI=F',
            'Bitcoin': 'BTC-USD',
            'Ethereum': 'ETH-USD'
        }
        
        # Fetch real data from Yahoo Finance
        from data_fetcher import DataFetcher
        fetcher = DataFetcher()
        
        # Get last 2 years of daily data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        data = {}
        for i, (name, symbol) in enumerate(assets.items()):
            status_text.text(f"Fetching {name} data from Yahoo Finance...")
            df = fetcher.get_historical_data(symbol, '1d', start_date, end_date)
            if df is not None and not df.empty:
                data[name] = df['Close']
            progress_bar.progress((i + 1) / len(assets))
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Create DataFrame with all assets
        df = pd.DataFrame(data)
        
        # Drop any rows with missing data
        df = df.dropna()
        
        if df.empty:
            st.error("❌ Could not fetch data from Yahoo Finance. Please try again later.")
            return None
            
        # Show success message with date range
        st.success(f"✅ Fetched real data from {df.index[0].date()} to {df.index[-1].date()}")
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error fetching real data: {str(e)}")
        print(f"Error in load_and_optimize: {e}")
        return None

if __name__ == "__main__":
    # تست ماژول
    print("🧪 تست ماژول PortfolioOptimizer...")
    
    try:
        # بارگذاری داده‌ها
        optimizer = load_and_optimize()
        
        # تست محاسبات پایه
        print("\n📊 آمار دارایی‌ها:")
        for asset in optimizer.assets:
            print(f"  {asset}: بازده {optimizer.mean_returns[asset]:.1%}, نوسان {np.sqrt(optimizer.cov_matrix.loc[asset, asset]):.1%}")
        
        # تست سبد Conservative
        print("\n🧪 تست پروفایل Conservative:")
        weights = optimizer.get_profile_weights('Conservative')
        stats = optimizer.portfolio_stats(weights)
        print(f"  بازده: {stats['return']:.1%}")
        print(f"  ریسک: {stats['volatility']:.1%}")
        print(f"  شارپ: {stats['sharpe_ratio']:.2f}")
        
        print("\n✅ تست موفقیت‌آمیز! ماژول آماده است.")
        
    except Exception as e:
        print(f"❌ خطا در تست: {e}")