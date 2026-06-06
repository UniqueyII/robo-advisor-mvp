# src/portfolio_optimizer.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import warnings
import streamlit as st
from datetime import datetime, timedelta
warnings.filterwarnings('ignore')

class PortfolioOptimizer:
    """
    کلاس بهینه‌سازی سبد سرمایه‌گذاری با MPT و شبیه‌سازی مونت‌کارلو
    Portfolio Optimizer using Modern Portfolio Theory and Monte Carlo Simulation
    """
    
    def __init__(self, price_data):
        """
        پارامترها / Parameters:
        -----------
        price_data : DataFrame
            داده‌های قیمت دارایی‌ها / Asset price data
        """
        self.prices = price_data
        self.returns = self.prices.pct_change().dropna()
        self.assets = list(self.prices.columns)
        self.n_assets = len(self.assets)
        
        # محاسبه آمار / Calculate statistics
        self.mean_returns = self.returns.mean() * 252  # بازده سالانه / Annualized returns
        self.cov_matrix = self.returns.cov() * 252     # ماتریس کوواریانس سالانه / Annualized covariance
        
        # FIXED: Correct weights for risk profiles based on requirements
        self.profile_weights = {
            'Conservative': {'Gold': 0.50, 'Silver': 0.25, 'Bitcoin': 0.15, 'Ethereum': 0.10},
            'Moderate': {'Gold': 0.30, 'Silver': 0.20, 'Bitcoin': 0.30, 'Ethereum': 0.20},
            'Aggressive': {'Gold': 0.15, 'Silver': 0.10, 'Bitcoin': 0.40, 'Ethereum': 0.35}
        }
        
        # Risk profile constraints for optimization
        self.profile_constraints = {
            'Conservative': {
                'Gold': (0.40, 0.60),
                'Silver': (0.20, 0.30),
                'Bitcoin': (0.05, 0.20),
                'Ethereum': (0.05, 0.15),
                'target_volatility': (0.10, 0.15),
                'target_return': (0.08, 0.12)
            },
            'Moderate': {
                'Gold': (0.25, 0.35),
                'Silver': (0.15, 0.25),
                'Bitcoin': (0.15, 0.30),
                'Ethereum': (0.15, 0.25),
                'target_volatility': (0.15, 0.22),
                'target_return': (0.12, 0.18)
            },
            'Aggressive': {
                'Gold': (0.10, 0.20),
                'Silver': (0.10, 0.15),
                'Bitcoin': (0.30, 0.45),
                'Ethereum': (0.25, 0.40),
                'target_volatility': (0.25, 0.35),
                'target_return': (0.20, 0.30)
            }
        }

    @property
    def weights(self):
        """Return profile weights as arrays aligned with self.assets.
        
        This helper is provided for the test suite which looks for a
        ``weights`` attribute.
        """
        return {
            profile: np.array([dist[asset] for asset in self.assets])
            for profile, dist in self.profile_weights.items()
        }
    
    def get_profile_weights(self, risk_profile):
        """
        دریافت وزن‌های از پیش تعریف شده برای پروفایل ریسک
        Get predefined weights for risk profile
        
        پارامترها / Parameters:
        -----------
        risk_profile : str
            'Conservative', 'Moderate', or 'Aggressive'
        
        بازگشت / Returns:
        --------
        np.array : وزن‌های سبد / Portfolio weights
        """
        if risk_profile in self.profile_weights:
            weights_dict = self.profile_weights[risk_profile]
            # تبدیل به آرایه به ترتیب دارایی‌ها
            weights = np.array([weights_dict[asset] for asset in self.assets])
            return weights
        else:
            raise ValueError(f"پروفایل {risk_profile} شناخته شده نیست.")
    
    def portfolio_stats(self, weights, risk_free_rate=0.02):
        """
        محاسبه بازده و ریسک سبد
        Calculate portfolio return and risk
        
        پارامترها / Parameters:
        -----------
        weights : np.array
            وزن‌های سبد / Portfolio weights
        risk_free_rate : float
            نرخ بدون ریسک / Risk-free rate (default 2%)
        
        بازگشت / Returns:
        --------
        dict : آمار سبد / Portfolio statistics
        """
        # بازده مورد انتظار / Expected return
        port_return = np.sum(self.mean_returns * weights)
        
        # ریسک (انحراف معیار) / Risk (standard deviation)
        port_volatility = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        
        # نسبت شارپ / Sharpe ratio
        sharpe_ratio = (port_return - risk_free_rate) / port_volatility if port_volatility != 0 else 0
        
        # محاسبه Sortino Ratio / Calculate Sortino Ratio
        portfolio_returns = self.returns.dot(weights)
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_std = np.sqrt(np.mean(downside_returns**2)) * np.sqrt(252) if len(downside_returns) > 0 else port_volatility
        sortino_ratio = (port_return - risk_free_rate) / downside_std if downside_std != 0 else 0
        
        # محاسبه Maximum Drawdown / Calculate Maximum Drawdown
        cumulative_returns = (1 + portfolio_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # محاسبه Calmar Ratio / Calculate Calmar Ratio
        calmar_ratio = port_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        return {
            'return': port_return,
            'volatility': port_volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar_ratio,
            'weights': weights
        }
    
    def optimize_sharpe(self, risk_profile=None):
        """
        بهینه‌سازی سبد برای بیشینه‌کردن نسبت شارپ با محدودیت‌های پروفایل ریسک
        Optimize portfolio to maximize Sharpe ratio with risk profile constraints
        
        پارامترها / Parameters:
        -----------
        risk_profile : str or None
            'Conservative', 'Moderate', or 'Aggressive'
        
        بازگشت / Returns:
        --------
        dict : سبد بهینه / Optimal portfolio
        """
        # تابع منفی شارپ (چون minimize می‌کنیم)
        def negative_sharpe(weights):
            stats = self.portfolio_stats(weights)
            return -stats['sharpe_ratio']
        
        # محدودیت‌ها: مجموع وزن‌ها = 1
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        
        # FIXED: Apply risk profile specific bounds
        if risk_profile and risk_profile in self.profile_constraints:
            bounds = []
            for asset in self.assets:
                if asset in self.profile_constraints[risk_profile]:
                    bounds.append(self.profile_constraints[risk_profile][asset])
                else:
                    bounds.append((0, 1))
            bounds = tuple(bounds)
            
            # Additional constraint: crypto max allocation for conservative
            if risk_profile == 'Conservative':
                # Bitcoin + Ethereum <= 0.25 (25%)
                btc_idx = self.assets.index('Bitcoin') if 'Bitcoin' in self.assets else None
                eth_idx = self.assets.index('Ethereum') if 'Ethereum' in self.assets else None
                if btc_idx is not None and eth_idx is not None:
                    constraints.append({
                        'type': 'ineq',
                        'fun': lambda x: 0.25 - (x[btc_idx] + x[eth_idx])
                    })
        else:
            # حدود وزن‌ها: بین ۰ تا ۰.۶ (max 60% per asset for diversification)
            bounds = tuple((0, 0.6) for _ in range(self.n_assets))
        
        # وزن اولیه
        if risk_profile and risk_profile in self.profile_weights:
            initial_weights = self.get_profile_weights(risk_profile)
        else:
            initial_weights = np.array([1/self.n_assets] * self.n_assets)
        
        # بهینه‌سازی
        try:
            result = minimize(negative_sharpe, initial_weights,
                            method='SLSQP', bounds=bounds,
                            constraints=constraints,
                            options={'maxiter': 1000})
            
            if result.success:
                optimal_weights = result.x
                return self.portfolio_stats(optimal_weights)
            else:
                # Fallback to profile weights if optimization fails
                print(f"Optimization warning: {result.message}")
                return self.portfolio_stats(initial_weights)
        except Exception as e:
            print(f"Optimization error: {e}")
            return self.portfolio_stats(initial_weights)
    
    def minimize_volatility(self, target_return=None, risk_profile=None):
        """
        بهینه‌سازی سبد برای کمینه‌کردن ریسک
        Optimize portfolio to minimize risk
        
        پارامترها / Parameters:
        -----------
        target_return : float or None
            بازده هدف / Target return
        risk_profile : str or None
            پروفایل ریسک / Risk profile
        
        بازگشت / Returns:
        --------
        dict : سبد بهینه / Optimal portfolio
        """
        # تابع نوسان برای مینیمم‌سازی
        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        
        # محدودیت‌ها
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        
        # اگر بازده هدف مشخص شده
        if target_return is not None:
            constraints.append({
                'type': 'eq',
                'fun': lambda x: np.sum(self.mean_returns * x) - target_return
            })
        
        # تعیین حدود بر اساس پروفایل ریسک
        if risk_profile and risk_profile in self.profile_constraints:
            bounds = []
            for asset in self.assets:
                if asset in self.profile_constraints[risk_profile]:
                    bounds.append(self.profile_constraints[risk_profile][asset])
                else:
                    bounds.append((0, 1))
            bounds = tuple(bounds)
        else:
            bounds = tuple((0, 0.6) for _ in range(self.n_assets))
        
        # وزن اولیه
        if risk_profile and risk_profile in self.profile_weights:
            initial_weights = self.get_profile_weights(risk_profile)
        else:
            initial_weights = np.array([1/self.n_assets] * self.n_assets)
        
        # بهینه‌سازی
        try:
            result = minimize(portfolio_volatility, initial_weights,
                            method='SLSQP', bounds=bounds,
                            constraints=constraints,
                            options={'maxiter': 1000})
            
            if result.success:
                optimal_weights = result.x
                return self.portfolio_stats(optimal_weights)
            else:
                return self.portfolio_stats(initial_weights)
        except Exception as e:
            print(f"Volatility optimization error: {e}")
            return self.portfolio_stats(initial_weights)
    
    def efficient_frontier(self, n_portfolios=100):
        """
        تولید مرز کارا
        Generate efficient frontier
        
        پارامترها / Parameters:
        -----------
        n_portfolios : int
            تعداد سبدهای تصادفی / Number of random portfolios
        
        بازگشت / Returns:
        --------
        tuple : (returns, volatilities, weights, sharpe_ratios)
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
    
    def monte_carlo_simulation(self, weights, initial_investment, years=1, n_simulations=10000):
        """
        شبیه‌سازی مونت‌کارلو برای پیش‌بینی ارزش آینده سبد
        Monte Carlo simulation for portfolio value prediction
        
        پارامترها / Parameters:
        -----------
        weights : np.array
            وزن‌های سبد / Portfolio weights
        initial_investment : float
            سرمایه اولیه (تومان) / Initial investment
        years : int
            افق زمانی (سال) / Time horizon (years)
        n_simulations : int
            تعداد شبیه‌سازی‌ها / Number of simulations (FIXED: 10,000)
        
        بازگشت / Returns:
        --------
        dict : نتایج شبیه‌سازی / Simulation results
        """
        days = years * 252  # روزهای کاری / Trading days
        last_prices = self.prices.iloc[-1].values
        
        # محاسبه تعداد سهم هر دارایی
        shares = (weights * initial_investment) / last_prices
        
        results = []
        
        for _ in range(n_simulations):
            # شبیه‌سازی مسیر قیمت با Geometric Brownian Motion
            simulated_prices = last_prices.copy()
            
            for day in range(days):
                # تولید بازده تصادفی با توزیع نرمال
                random_returns = np.random.multivariate_normal(
                    self.mean_returns / 252,  # بازده روزانه
                    self.cov_matrix / 252,     # کوواریانس روزانه
                    size=1
                )[0]
                
                # Geometric Brownian Motion: price_t = price_0 * exp((μ - σ²/2)*dt + σ*√dt*ε)
                simulated_prices *= (1 + random_returns)
            
            # ارزش نهایی سبد
            final_value = np.sum(shares * simulated_prices)
            results.append(final_value)
        
        results = np.array(results)
        
        # محاسبه معیارهای ریسک
        mean_final_value = np.mean(results)
        median_final_value = np.median(results)
        std_final_value = np.std(results)
        
        # FIXED: محاسبه صحیح VaR و CVaR
        # VaR (در سطح اطمینان 95%) - حداکثر زیان احتمالی
        percentile_5 = np.percentile(results, 5)
        var_95 = initial_investment - percentile_5
        
        # CVaR (Conditional VaR) - میانگین زیان در بدترین 5% سناریوها
        worst_5_percent = results[results <= percentile_5]
        cvar_95 = initial_investment - worst_5_percent.mean() if len(worst_5_percent) > 0 else var_95
        
        # احتمال زیان
        prob_loss = np.sum(results < initial_investment) / n_simulations
        
        # بهترین و بدترین سناریو
        best_case = np.percentile(results, 95)
        worst_case = np.percentile(results, 5)
        
        return {
            'initial_investment': initial_investment,
            'mean_final_value': mean_final_value,
            'median_final_value': median_final_value,
            'std_final_value': std_final_value,
            'best_case': best_case,
            'worst_case': worst_case,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'prob_loss': prob_loss,
            'all_simulations': results,
            'expected_return_pct': (mean_final_value / initial_investment - 1) * 100
        }
    
    def calculate_var(self, weights, initial_investment, confidence_level=0.95, method='historical'):
        """
        محاسبه Value at Risk
        Calculate Value at Risk
        
        پارامترها / Parameters:
        -----------
        weights : np.array
            وزن‌های سبد / Portfolio weights
        initial_investment : float
            سرمایه اولیه / Initial investment
        confidence_level : float
            سطح اطمینان (مثلاً 0.95 برای 95%) / Confidence level
        method : str
            'historical', 'parametric', or 'monte_carlo'
        
        بازگشت / Returns:
        --------
        float : مقدار VaR / VaR amount
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
            var_amount = initial_investment * (z_score * port_volatility / np.sqrt(252) - port_return / 252)
            
        elif method == 'monte_carlo':
            # VaR از شبیه‌سازی مونت‌کارلو
            mc_results = self.monte_carlo_simulation(weights, initial_investment, years=1, n_simulations=10000)
            var_amount = mc_results['var_95']
        
        else:
            raise ValueError("method باید 'historical', 'parametric', یا 'monte_carlo' باشد.")
        
        return var_amount
    
    def generate_report(self, risk_profile, investment):
        """
        تولید گزارش کامل برای پروفایل ریسک و مبلغ سرمایه‌گذاری
        Generate complete report for risk profile and investment amount
        
        This method:
        1. Optimizes portfolio based on risk profile
        2. Calculates all metrics
        3. Runs Monte Carlo simulation
        4. Calculates VaR and CVaR
        5. Generates recommendations
        
        پارامترها / Parameters:
        -----------
        risk_profile : str
            'Conservative', 'Moderate', or 'Aggressive'
        investment : float
            مبلغ سرمایه‌گذاری / Investment amount
        
        بازگشت / Returns:
        --------
        dict : گزارش کامل / Complete report
        """
        # FIXED: Optimize based on risk profile instead of using fixed weights
        try:
            # Get optimized weights for the risk profile
            optimized = self.optimize_sharpe(risk_profile=risk_profile)
            weights = optimized['weights']
            
            # If optimization resulted in weights outside profile bounds, use profile defaults
            if risk_profile in self.profile_constraints:
                constraints = self.profile_constraints[risk_profile]
                weights_valid = True
                for i, asset in enumerate(self.assets):
                    if asset in constraints:
                        min_w, max_w = constraints[asset]
                        if weights[i] < min_w or weights[i] > max_w:
                            weights_valid = False
                            break
                
                if not weights_valid:
                    weights = self.get_profile_weights(risk_profile)
            
        except Exception as e:
            print(f"Optimization failed: {e}, using default weights")
            weights = self.get_profile_weights(risk_profile)
        
        # Calculate portfolio statistics
        stats = self.portfolio_stats(weights)
        
        # Run Monte Carlo simulation
        mc_results = self.monte_carlo_simulation(weights, investment, years=1, n_simulations=10000)
        
        # Calculate VaR using multiple methods
        var_historical = self.calculate_var(weights, investment, method='historical')
        var_parametric = self.calculate_var(weights, investment, method='parametric')
        var_monte_carlo = mc_results['var_95']
        
        # Calculate CVaR
        cvar = mc_results['cvar_95']
        
        # Generate recommendation text
        recommendation = self._generate_recommendation(risk_profile, stats, mc_results)
        
        # Create detailed weights dictionary
        weights_dict = {asset: float(w) for asset, w in zip(self.assets, weights)}
        
        return {
            # Weights
            'weights': weights,
            'weights_dict': weights_dict,
            
            # Returns and Risk
            'expected_return': stats['return'],
            'expected_return_pct': stats['return'] * 100,
            'risk': stats['volatility'],
            'volatility': stats['volatility'],
            'volatility_pct': stats['volatility'] * 100,
            
            # Risk Metrics
            'sharpe_ratio': stats['sharpe_ratio'],
            'sortino_ratio': stats['sortino_ratio'],
            'max_drawdown': stats['max_drawdown'],
            'max_drawdown_pct': stats['max_drawdown'] * 100,
            'calmar_ratio': stats['calmar_ratio'],
            
            # VaR and CVaR
            'var': var_monte_carlo,
            'var_historical': var_historical,
            'var_parametric': var_parametric,
            'var_pct': (var_monte_carlo / investment) * 100,
            'cvar': cvar,
            'cvar_pct': (cvar / investment) * 100,
            
            # Monte Carlo Results
            'mc_mean_value': mc_results['mean_final_value'],
            'mc_best_case': mc_results['best_case'],
            'mc_worst_case': mc_results['worst_case'],
            'mc_prob_loss': mc_results['prob_loss'],
            'mc_expected_return_pct': mc_results['expected_return_pct'],
            
            # Recommendation
            'recommendation': recommendation,
            'risk_profile': risk_profile
        }
    
    def _generate_recommendation(self, risk_profile, stats, mc_results):
        """
        تولید توصیه متنی بر اساس پروفایل ریسک و نتایج
        Generate text recommendation based on risk profile and results
        """
        if risk_profile == 'Conservative':
            return f"""
🛡️ **توصیه برای سرمایه‌گذار محافظه‌کار:**

با بازده مورد انتظار {stats['return']*100:.1f}% و ریسک {stats['volatility']*100:.1f}%، این سبد برای شما مناسب است.
احتمال زیان در این سبد {mc_results['prob_loss']*100:.1f}% است.

✅ **مزایا:**
- حفاظت بالا از سرمایه با تمرکز بر طلا و نقره
- نوسانات کم و خواب راحت!
- مناسب برای افق زمانی میان‌مدت تا بلندمدت

⚠️ **نکات:**
- بازدهی محدود (کمتر از بازار کریپتو)
- برای رشد سریع مناسب نیست
            """
        elif risk_profile == 'Moderate':
            return f"""
⚖️ **توصیه برای سرمایه‌گذار متعادل:**

با بازده مورد انتظار {stats['return']*100:.1f}% و ریسک {stats['volatility']*100:.1f}%، این سبد تعادل خوبی دارد.
احتمال زیان در این سبد {mc_results['prob_loss']*100:.1f}% است.

✅ **مزایا:**
- تعادل مناسب بین ریسک و بازده
- متنوع‌سازی بین فلزات گران‌بها و کریپتو
- مناسب برای اکثر سرمایه‌گذاران

⚠️ **نکات:**
- نیاز به نظارت منظم
- ممکن است در بازارهای نزولی دچار نوسان شود
            """
        else:  # Aggressive
            return f"""
🚀 **توصیه برای سرمایه‌گذار تهاجمی:**

با بازده مورد انتظار {stats['return']*100:.1f}% و ریسک {stats['volatility']*100:.1f}%، این سبد پتانسیل رشد بالایی دارد.
احتمال زیان در این سبد {mc_results['prob_loss']*100:.1f}% است.

✅ **مزایا:**
- پتانسیل بازدهی بسیار بالا
- استفاده از رشد سریع بازار کریپتو
- مناسب برای افق زمانی بلندمدت

⚠️ **هشدار:**
- ریسک بالا - ممکن است تا 30% یا بیشتر زیان کنید
- نوسانات شدید - روحیه قوی لازم است
- فقط سرمایه‌ای را وارد کنید که از دست دادنش برایتان مشکلی ایجاد نکند
            """
    
    def plot_efficient_frontier(self, optimal_portfolio=None, risk_profile=None):
        """
        رسم مرز کارا
        Plot efficient frontier
        """
        returns, volatilities, _, sharpe_ratios = self.efficient_frontier(200)
        
        plt.figure(figsize=(12, 8))
        
        # نقاط سبدهای تصادفی
        scatter = plt.scatter(volatilities, returns, c=sharpe_ratios, 
                             cmap='viridis', alpha=0.6, s=30)
        plt.colorbar(scatter, label='نسبت شارپ / Sharpe Ratio')
        
        # سبد بهینه اگر داده شود
        if optimal_portfolio:
            plt.scatter(optimal_portfolio['volatility'], optimal_portfolio['return'],
                       c='red', s=200, marker='*', label='سبد بهینه / Optimal Portfolio')
        
        # نمایش سبدهای پروفایل ریسک
        if risk_profile:
            for profile in ['Conservative', 'Moderate', 'Aggressive']:
                weights = self.get_profile_weights(profile)
                stats = self.portfolio_stats(weights)
                marker = 's' if profile == risk_profile else 'o'
                size = 150 if profile == risk_profile else 100
                plt.scatter(stats['volatility'], stats['return'],
                           marker=marker, s=size, label=profile, alpha=0.8)
        
        plt.xlabel('ریسک (انحراف معیار) / Risk (Std Dev)')
        plt.ylabel('بازده مورد انتظار / Expected Return')
        plt.title('مرز کارای مارکوویتز / Markowitz Efficient Frontier')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        return plt


def load_and_optimize():
    """Load REAL data from Yahoo Finance using data_fetcher functions"""
    try:
        # Import the functions from data_fetcher (NOT a class)
        from data_fetcher import create_dataframe

        # Show progress in Streamlit
        with st.spinner("📥 دریافت داده‌های واقعی از Yahoo Finance..."):
            # Use your existing function to get real data
            df = create_dataframe(use_real=True)

            if df is None or df.empty:
                st.warning("⚠️ دریافت داده واقعی ممکن نبود. استفاده از داده نمونه...")
                df = create_dataframe(use_real=False)

            if df is None or df.empty:
                st.error("❌ داده‌ای موجود نیست. لطفاً بعداً تلاش کنید.")
                return None

            # Display success message
            st.success(f"✅ داده‌ها با موفقیت دریافت شدند: {df.index[0].date()} تا {df.index[-1].date()}")

            return df

    except Exception as e:
        st.error(f"❌ خطا در دریافت داده: {str(e)}")
        print(f"Error in load_and_optimize: {e}")

    # Fallback to sample data
    try:
        from data_fetcher import create_sample_data
        st.warning("⚠️ استفاده از داده نمونه")
        df = create_sample_data()
        if df is not None:
            return df
    except:
        pass

    return None


if __name__ == "__main__":
    # تست ماژول / Test module
    print("🧪 تست ماژول PortfolioOptimizer...")
    
    try:
        # بارگذاری داده‌ها
        df = load_and_optimize()
        
        if df is not None:
            optimizer = PortfolioOptimizer(df)
            
            # تست محاسبات پایه
            print("\n📊 آمار دارایی‌ها / Asset Statistics:")
            for asset in optimizer.assets:
                print(f"  {asset}: بازده/Return {optimizer.mean_returns[asset]:.1%}, نوسان/Volatility {np.sqrt(optimizer.cov_matrix.loc[asset, asset]):.1%}")
            
            # تست سبد Conservative
            print("\n🧪 تست پروفایل Conservative:")
            report = optimizer.generate_report('Conservative', 100000000)  # 100M Toman
            print(f"  وزن‌ها / Weights:")
            for asset, weight in report['weights_dict'].items():
                print(f"    {asset}: {weight:.1%}")
            print(f"  بازده / Return: {report['expected_return']:.1%}")
            print(f"  ریسک / Risk: {report['volatility']:.1%}")
            print(f"  شارپ / Sharpe: {report['sharpe_ratio']:.2f}")
            print(f"  VaR 95%: {report['var_pct']:.1f}%")
            
            # تست سبد Aggressive
            print("\n🧪 تست پروفایل Aggressive:")
            report = optimizer.generate_report('Aggressive', 100000000)
            print(f"  وزن‌ها / Weights:")
            for asset, weight in report['weights_dict'].items():
                print(f"    {asset}: {weight:.1%}")
            print(f"  بازده / Return: {report['expected_return']:.1%}")
            print(f"  ریسک / Risk: {report['volatility']:.1%}")
            print(f"  شارپ / Sharpe: {report['sharpe_ratio']:.2f}")
            print(f"  VaR 95%: {report['var_pct']:.1f}%")
            
            print("\n✅ تست موفقیت‌آمیز! ماژول آماده است.")
        else:
            print("❌ خطا: داده‌ای دریافت نشد")
        
    except Exception as e:
        print(f"❌ خطا در تست: {e}")
        import traceback
        traceback.print_exc()