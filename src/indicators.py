import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats
from datetime import datetime, timedelta

class IndicatorCalculator:
    """指标计算器"""
    
    def __init__(self):
        pass
    
    def _convert_risk_to_text(self, risk_indicators: Dict) -> Dict:
        """将风险指标数值转换为文字描述"""
        text_indicators = {}
        
        # 波动率转换为文字
        volatility = risk_indicators.get('volatility')
        if pd.notna(volatility):
            if volatility < 15:
                text_indicators['volatility_text'] = "低波动"
            elif volatility < 30:
                text_indicators['volatility_text'] = "中等波动"
            elif volatility < 50:
                text_indicators['volatility_text'] = "高波动"
            else:
                text_indicators['volatility_text'] = "极高波动"
        else:
            text_indicators['volatility_text'] = "数据不足"
        
        # 最大回撤转换为文字
        max_drawdown = risk_indicators.get('max_drawdown')
        if pd.notna(max_drawdown):
            if max_drawdown > -10:
                text_indicators['max_drawdown_text'] = "回撤较小"
            elif max_drawdown > -25:
                text_indicators['max_drawdown_text'] = "回撤中等"
            elif max_drawdown > -40:
                text_indicators['max_drawdown_text'] = "回撤较大"
            else:
                text_indicators['max_drawdown_text'] = "回撤极大"
        else:
            text_indicators['max_drawdown_text'] = "数据不足"
        
        # VaR转换为文字
        var_95 = risk_indicators.get('var_95')
        if pd.notna(var_95):
            if var_95 > -2:
                text_indicators['var_95_text'] = "风险较低"
            elif var_95 > -5:
                text_indicators['var_95_text'] = "风险中等"
            elif var_95 > -10:
                text_indicators['var_95_text'] = "风险较高"
            else:
                text_indicators['var_95_text'] = "风险极高"
        else:
            text_indicators['var_95_text'] = "数据不足"
        
        # 夏普比率转换为文字
        sharpe_ratio = risk_indicators.get('sharpe_ratio')
        if pd.notna(sharpe_ratio):
            if sharpe_ratio > 1:
                text_indicators['sharpe_ratio_text'] = "收益风险比优秀"
            elif sharpe_ratio > 0.5:
                text_indicators['sharpe_ratio_text'] = "收益风险比良好"
            elif sharpe_ratio > 0:
                text_indicators['sharpe_ratio_text'] = "收益风险比一般"
            else:
                text_indicators['sharpe_ratio_text'] = "收益风险比较差"
        else:
            text_indicators['sharpe_ratio_text'] = "数据不足"
        
        return text_indicators
    
    def calculate_quality_indicators(self, financial_data: Dict) -> Dict:
        """计算质量指标"""
        quality = {}
        
        try:
            # 获取财务指标数据
            fina = financial_data.get('fina', pd.DataFrame())
            if not fina.empty:
                latest = fina.iloc[0]
                
                # ROE
                quality['roe'] = latest.get('roe', np.nan)
                
                # 毛利率
                quality['gross_margin'] = latest.get('grossprofit_margin', np.nan)
                
                # 净利率
                quality['net_margin'] = latest.get('netprofit_margin', np.nan)
                
                # ROA
                quality['roa'] = latest.get('roa', np.nan)
                
                # 权益乘数 - 通过 assets_to_eqt 计算
                assets_to_eqt = latest.get('assets_to_eqt', np.nan)
                if pd.notna(assets_to_eqt):
                    quality['equity_multiplier'] = assets_to_eqt
                else:
                    # 备用计算方法：通过 debt_to_assets 计算
                    debt_to_assets = latest.get('debt_to_assets', np.nan)
                    if pd.notna(debt_to_assets) and debt_to_assets > 0:
                        quality['equity_multiplier'] = 1 / (1 - debt_to_assets / 100)
                    else:
                        quality['equity_multiplier'] = np.nan
            
            # 获取现金流量数据
            cashflow = financial_data.get('cashflow', pd.DataFrame())
            if not cashflow.empty:
                latest_cf = cashflow.iloc[0]
                
                # 经营活动现金流量
                quality['operating_cf'] = latest_cf.get('n_cashflow_act', np.nan)
            
        except Exception as e:
            print(f"计算质量指标失败: {e}")
        
        return quality
    
    def calculate_growth_indicators(self, financial_data: Dict) -> Dict:
        """计算增长指标"""
        growth = {}
        
        try:
            # 获取财务指标数据
            fina = financial_data.get('fina', pd.DataFrame())
            if not fina.empty:
                latest = fina.iloc[0]
                
                # 营收同比增长
                growth['revenue_yoy'] = latest.get('tr_yoy', np.nan)
                
                # 净利润同比增长
                growth['profit_yoy'] = latest.get('netprofit_yoy', np.nan)
            
            # 获取利润表数据
            income = financial_data.get('income', pd.DataFrame())
            if not income.empty:
                latest_income = income.iloc[0]
                
                # 营收
                growth['revenue'] = latest_income.get('revenue', np.nan)
                
                # 净利润
                growth['net_income'] = latest_income.get('n_income', np.nan)
                
                # 营收同比增长
                if pd.isna(growth.get('revenue_yoy')):
                    growth['revenue_yoy'] = latest_income.get('yoy_revenue', np.nan)
                
                # 净利润同比增长
                if pd.isna(growth.get('profit_yoy')):
                    growth['profit_yoy'] = latest_income.get('yoy_netprofit', np.nan)
            
            # 获取业绩预告数据
            forecast = financial_data.get('forecast', pd.DataFrame())
            if not forecast.empty:
                latest_forecast = forecast.iloc[0]
                
                # 预告类型
                growth['forecast_type'] = latest_forecast.get('type', '')
                
                # 预告变动幅度
                growth['forecast_change_min'] = latest_forecast.get('p_change_min', np.nan)
                growth['forecast_change_max'] = latest_forecast.get('p_change_max', np.nan)
            
        except Exception as e:
            print(f"计算增长指标失败: {e}")
        
        return growth
    
    def calculate_valuation_indicators(self, financial_data: Dict, latest_quote: Dict) -> Dict:
        """计算估值指标"""
        valuation = {}
        
        try:
            # 从最新行情获取估值指标
            if latest_quote:
                valuation['pe'] = latest_quote.get('pe', np.nan)
                valuation['pb'] = latest_quote.get('pb', np.nan)
                valuation['ps'] = latest_quote.get('ps', np.nan)
                valuation['total_mv'] = latest_quote.get('total_mv', np.nan)
                valuation['circ_mv'] = latest_quote.get('circ_mv', np.nan)
                valuation['close'] = latest_quote.get('close', np.nan)
                valuation['turnover_rate'] = latest_quote.get('turnover_rate', np.nan)
            
            # 从财务数据获取增长数据用于PEG计算
            fina = financial_data.get('fina', pd.DataFrame())
            if not fina.empty:
                latest = fina.iloc[0]
                profit_yoy = latest.get('netprofit_yoy', np.nan)
                
                # 计算PEG
                if pd.notna(valuation.get('pe')) and pd.notna(profit_yoy) and profit_yoy > 0:
                    valuation['peg'] = valuation['pe'] / profit_yoy
                
                # 获取更多财务指标用于估值
                valuation['roe'] = latest.get('roe', np.nan)
                valuation['roa'] = latest.get('roa', np.nan)
                valuation['gross_margin'] = latest.get('grossprofit_margin', np.nan)
                valuation['net_margin'] = latest.get('netprofit_margin', np.nan)
            
            # 从利润表获取数据
            income = financial_data.get('income', pd.DataFrame())
            if not income.empty:
                latest_income = income.iloc[0]
                revenue = latest_income.get('revenue', np.nan)
                net_income = latest_income.get('n_income', np.nan)
                
                # 计算P/S和P/E
                if pd.notna(valuation.get('close')) and pd.notna(revenue) and revenue > 0:
                    # 这里需要获取总股本，暂时使用市值估算
                    if pd.notna(valuation.get('total_mv')) and valuation['total_mv'] > 0:
                        shares = valuation['total_mv'] / valuation['close']
                        revenue_per_share = revenue / shares
                        if revenue_per_share > 0:
                            valuation['ps_calculated'] = valuation['close'] / revenue_per_share
                
                if pd.notna(valuation.get('close')) and pd.notna(net_income) and net_income > 0:
                    if pd.notna(valuation.get('total_mv')) and valuation['total_mv'] > 0:
                        shares = valuation['total_mv'] / valuation['close']
                        eps = net_income / shares
                        if eps > 0:
                            valuation['pe_calculated'] = valuation['close'] / eps
            
            # 从资产负债表获取数据
            balance = financial_data.get('balance', pd.DataFrame())
            if not balance.empty:
                latest_balance = balance.iloc[0]
                total_assets = latest_balance.get('total_assets', np.nan)
                total_equity = latest_balance.get('total_hldr_eqy_exc_min_int', np.nan)
                
                # 计算P/B
                if pd.notna(valuation.get('close')) and pd.notna(total_equity) and total_equity > 0:
                    if pd.notna(valuation.get('total_mv')) and valuation['total_mv'] > 0:
                        shares = valuation['total_mv'] / valuation['close']
                        bps = total_equity / shares
                        if bps > 0:
                            valuation['pb_calculated'] = valuation['close'] / bps
            
        except Exception as e:
            print(f"计算估值指标失败: {e}")
        
        return valuation
    
    def calculate_momentum_indicators(self, daily_data: pd.DataFrame) -> Dict:
        """计算动量指标"""
        momentum = {}
        
        try:
            if not daily_data.empty:
                # 按日期排序
                daily_data = daily_data.sort_values('trade_date')
                
                # 计算各期间收益率
                periods = [3, 6, 12]
                for period in periods:
                    if len(daily_data) >= period:
                        start_price = daily_data.iloc[-period]['close']
                        end_price = daily_data.iloc[-1]['close']
                        returns = (end_price - start_price) / start_price * 100
                        momentum[f'return_{period}m'] = returns
                
                # 计算12-1动量（12个月收益率减去1个月收益率）
                if 'return_12m' in momentum and 'return_1m' in momentum:
                    momentum['momentum_12_1'] = momentum['return_12m'] - momentum['return_1m']
                elif 'return_12m' in momentum:
                    momentum['momentum_12_1'] = momentum['return_12m']
                
                # 计算相对强弱指标（RSI）
                if len(daily_data) >= 14:
                    daily_data['price_change'] = daily_data['close'].diff()
                    gains = daily_data['price_change'].where(daily_data['price_change'] > 0, 0)
                    losses = -daily_data['price_change'].where(daily_data['price_change'] < 0, 0)
                    
                    avg_gain = gains.rolling(window=14).mean().iloc[-1]
                    avg_loss = losses.rolling(window=14).mean().iloc[-1]
                    
                    if avg_loss != 0:
                        rs = avg_gain / avg_loss
                        momentum['rsi'] = 100 - (100 / (1 + rs))
                    else:
                        momentum['rsi'] = 100
            
        except Exception as e:
            print(f"计算动量指标失败: {e}")
        
        return momentum
    
    def calculate_risk_indicators(self, daily_data: pd.DataFrame, financial_data: Dict) -> Dict:
        """计算风险指标"""
        risk = {}
        
        try:
            if not daily_data.empty:
                # 计算收益率
                daily_data = daily_data.sort_values('trade_date')
                daily_data['returns'] = daily_data['close'].pct_change()
                returns = daily_data['returns'].dropna()
                
                if len(returns) > 0:
                    # 波动率（年化）
                    volatility = returns.std() * np.sqrt(252) * 100
                    risk['volatility'] = volatility
                    
                    # 最大回撤
                    cumulative_returns = (1 + returns).cumprod()
                    rolling_max = cumulative_returns.expanding().max()
                    drawdown = (cumulative_returns - rolling_max) / rolling_max
                    max_drawdown = drawdown.min() * 100
                    risk['max_drawdown'] = max_drawdown
                    
                    # VaR (95% 置信度)
                    var_95 = np.percentile(returns, 5) * 100
                    risk['var_95'] = var_95
                    
                    # 夏普比率（简化版，假设无风险利率为3%）
                    if volatility > 0:
                        risk['sharpe_ratio'] = (returns.mean() * 252 - 0.03) / volatility
                    else:
                        risk['sharpe_ratio'] = np.nan
                
                # 将数值转换为文字描述
                text_indicators = self._convert_risk_to_text(risk)
                risk.update(text_indicators)
            
            # 财务风险指标
            fina = financial_data.get('fina', pd.DataFrame())
            if not fina.empty:
                latest = fina.iloc[0]
                
                # 资产负债率
                risk['debt_ratio'] = latest.get('debt_to_assets', np.nan)
                
                # 流动比率
                risk['current_ratio'] = latest.get('current_ratio', np.nan)
                
                # 速动比率
                risk['quick_ratio'] = latest.get('quick_ratio', np.nan)
                
        except Exception as e:
            print(f"计算风险指标失败: {e}")
        
        return risk
    
    def calculate_z_scores(self, indicators: Dict, category: str) -> float:
        """计算Z分数"""
        try:
            # 这里使用简化的评分方法
            # 实际应用中需要基于历史数据或行业数据计算标准化分数
            
            if category == 'quality':
                scores = []
                if pd.notna(indicators.get('roe')):
                    scores.append(min(indicators['roe'] / 20, 1))  # ROE > 20% 得满分
                if pd.notna(indicators.get('gross_margin')):
                    scores.append(min(indicators['gross_margin'] / 50, 1))  # 毛利率 > 50% 得满分
                if pd.notna(indicators.get('net_margin')):
                    scores.append(min(indicators['net_margin'] / 20, 1))  # 净利率 > 20% 得满分
                
                return np.mean(scores) if scores else 0
            
            elif category == 'growth':
                scores = []
                if pd.notna(indicators.get('revenue_yoy')):
                    scores.append(min(indicators['revenue_yoy'] / 30, 1))  # 营收增长 > 30% 得满分
                if pd.notna(indicators.get('profit_yoy')):
                    scores.append(min(indicators['profit_yoy'] / 30, 1))  # 利润增长 > 30% 得满分
                
                return np.mean(scores) if scores else 0
            
            elif category == 'valuation':
                scores = []
                if pd.notna(indicators.get('pe')):
                    pe_score = max(0, 1 - indicators['pe'] / 50)  # PE < 50 得满分
                    scores.append(pe_score)
                if pd.notna(indicators.get('pb')):
                    pb_score = max(0, 1 - indicators['pb'] / 10)  # PB < 10 得满分
                    scores.append(pb_score)
                if pd.notna(indicators.get('peg')):
                    peg_score = max(0, 1 - indicators['peg'] / 2)  # PEG < 2 得满分
                    scores.append(peg_score)
                
                return np.mean(scores) if scores else 0
            
            elif category == 'momentum':
                scores = []
                if pd.notna(indicators.get('return_12m')):
                    momentum_score = min(max(indicators['return_12m'] / 50, -1), 1)  # 12个月收益率
                    scores.append(momentum_score)
                
                return np.mean(scores) if scores else 0
            
            elif category == 'risk':
                scores = []
                if pd.notna(indicators.get('volatility')):
                    vol_score = max(0, 1 - indicators['volatility'] / 50)  # 波动率 < 50% 得满分
                    scores.append(vol_score)
                if pd.notna(indicators.get('max_drawdown')):
                    dd_score = max(0, 1 + indicators['max_drawdown'] / 50)  # 最大回撤 > -50% 得满分
                    scores.append(dd_score)
                
                return np.mean(scores) if scores else 0
            
            return 0
            
        except Exception as e:
            print(f"计算Z分数失败: {e}")
            return 0

# 全局指标计算器实例
indicator_calculator = IndicatorCalculator()
