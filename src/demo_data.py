"""
演示数据模块 - 提供模拟的股票数据用于演示
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List

class DemoDataProvider:
    """演示数据提供器"""
    
    def __init__(self):
        self.demo_stocks = {
            '600519.SH': {
                'name': '贵州茅台',
                'ts_code': '600519.SH',
                'area': '贵州',
                'industry': '白酒',
                'market': '主板',
                'list_date': '20010827'
            },
            '000001.SZ': {
                'name': '平安银行',
                'ts_code': '000001.SZ',
                'area': '广东',
                'industry': '银行',
                'market': '主板',
                'list_date': '19910403'
            },
            '000002.SZ': {
                'name': '万科A',
                'ts_code': '000002.SZ',
                'area': '广东',
                'industry': '房地产',
                'market': '主板',
                'list_date': '19910129'
            },
            '000858.SZ': {
                'name': '五粮液',
                'ts_code': '000858.SZ',
                'area': '四川',
                'industry': '白酒',
                'market': '主板',
                'list_date': '19980427'
            },
            '002415.SZ': {
                'name': '海康威视',
                'ts_code': '002415.SZ',
                'area': '浙江',
                'industry': '电子',
                'market': '中小板',
                'list_date': '20100528'
            }
        }
    
    def get_stock_basic(self, ts_code: str) -> Dict:
        """获取股票基本信息"""
        return self.demo_stocks.get(ts_code, {
            'name': f'演示股票{ts_code}',
            'ts_code': ts_code,
            'area': '演示地区',
            'industry': '演示行业',
            'market': '演示市场',
            'list_date': '20200101'
        })
    
    def get_daily_data(self, ts_code: str, start_date: str, end_date: str = None) -> pd.DataFrame:
        """生成模拟的日线数据"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        # 生成日期范围
        start_dt = datetime.strptime(start_date, '%Y%m%d')
        end_dt = datetime.strptime(end_date, '%Y%m%d')
        date_range = pd.date_range(start=start_dt, end=end_dt, freq='D')
        
        # 过滤掉周末
        date_range = date_range[date_range.weekday < 5]
        
        # 生成模拟价格数据
        np.random.seed(hash(ts_code) % 1000)  # 使用股票代码作为随机种子
        
        base_price = 50 + np.random.randint(0, 200)  # 基础价格
        prices = []
        
        for i, date in enumerate(date_range):
            # 模拟价格波动
            if i == 0:
                price = base_price
            else:
                change = np.random.normal(0, 0.02)  # 2%的标准差
                price = prices[-1] * (1 + change)
            
            prices.append(price)
        
        # 创建DataFrame
        df = pd.DataFrame({
            'ts_code': ts_code,
            'trade_date': [d.strftime('%Y%m%d') for d in date_range],
            'open': [p * (1 + np.random.normal(0, 0.01)) for p in prices],
            'high': [p * (1 + abs(np.random.normal(0, 0.015))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.015))) for p in prices],
            'close': prices,
            'vol': np.random.randint(1000000, 10000000, len(prices)),
            'amount': np.random.randint(10000000, 100000000, len(prices)),
            'pe': np.random.uniform(10, 50, len(prices)),
            'pb': np.random.uniform(1, 10, len(prices)),
            'ps': np.random.uniform(1, 20, len(prices)),
            'total_mv': np.random.uniform(1000000000, 10000000000, len(prices)),
            'circ_mv': np.random.uniform(500000000, 5000000000, len(prices)),
            'turnover_rate': np.random.uniform(0.5, 5, len(prices))
        })
        
        return df
    
    def get_financial_data(self, ts_code: str, start_date: str, end_date: str = None) -> Dict:
        """生成模拟的财务数据"""
        # 模拟财务指标数据
        fina_data = []
        for i in range(8):  # 最近8个季度
            fina_data.append({
                'ts_code': ts_code,
                'end_date': f'202{4-i//4}0{3-i%4+1}31',
                'roe': np.random.uniform(8, 25),
                'grossprofit_margin': np.random.uniform(20, 60),
                'netprofit_margin': np.random.uniform(5, 30),
                'roa': np.random.uniform(3, 15),
                'equity_multiplier': np.random.uniform(1.5, 4),
                'debt_to_equity': np.random.uniform(0.1, 0.8),
                'pe': np.random.uniform(10, 50),
                'pb': np.random.uniform(1, 10),
                'tr_yoy': np.random.uniform(-20, 50),
                'netprofit_yoy': np.random.uniform(-30, 60)
            })
        
        # 模拟利润表数据
        income_data = []
        for i in range(6):
            income_data.append({
                'ts_code': ts_code,
                'end_date': f'202{4-i//4}0{3-i%4+1}31',
                'revenue': np.random.uniform(1000000000, 10000000000),
                'n_income': np.random.uniform(100000000, 2000000000),
                'yoy_revenue': np.random.uniform(-20, 50),
                'yoy_netprofit': np.random.uniform(-30, 60)
            })
        
        # 模拟现金流量表数据
        cashflow_data = []
        for i in range(6):
            cashflow_data.append({
                'ts_code': ts_code,
                'end_date': f'202{4-i//4}0{3-i%4+1}31',
                'n_cashflow_act': np.random.uniform(500000000, 3000000000)
            })
        
        # 模拟资产负债表数据
        balance_data = []
        for i in range(6):
            balance_data.append({
                'ts_code': ts_code,
                'end_date': f'202{4-i//4}0{3-i%4+1}31',
                'total_assets': np.random.uniform(50000000000, 500000000000),
                'total_liab': np.random.uniform(20000000000, 300000000000),
                'total_cur_assets': np.random.uniform(20000000000, 200000000000),
                'total_cur_liab': np.random.uniform(10000000000, 150000000000)
            })
        
        return {
            'fina': pd.DataFrame(fina_data),
            'income': pd.DataFrame(income_data),
            'cashflow': pd.DataFrame(cashflow_data),
            'balance': pd.DataFrame(balance_data)
        }
    
    def get_forecast_data(self, ts_code: str, start_date: str, end_date: str = None) -> pd.DataFrame:
        """生成模拟的业绩预告数据"""
        forecast_types = ['预增', '略增', '扭亏', '续盈', '预减', '略减', '首亏', '续亏']
        
        forecast_data = []
        for i in range(3):  # 最近3个预告
            forecast_data.append({
                'ts_code': ts_code,
                'ann_date': f'202{4-i//4}0{3-i%4+1}15',
                'type': np.random.choice(forecast_types),
                'p_change_min': np.random.uniform(-50, 100),
                'p_change_max': np.random.uniform(-30, 150)
            })
        
        return pd.DataFrame(forecast_data)
    
    def get_latest_quote(self, ts_code: str) -> Dict:
        """获取最新行情数据"""
        # 生成最新的模拟行情
        base_price = 50 + np.random.randint(0, 200)
        
        return {
            'ts_code': ts_code,
            'trade_date': datetime.now().strftime('%Y%m%d'),
            'open': base_price * (1 + np.random.normal(0, 0.01)),
            'high': base_price * (1 + abs(np.random.normal(0, 0.015))),
            'low': base_price * (1 - abs(np.random.normal(0, 0.015))),
            'close': base_price,
            'vol': np.random.randint(1000000, 10000000),
            'amount': np.random.randint(10000000, 100000000),
            'pe': np.random.uniform(10, 50),
            'pb': np.random.uniform(1, 10),
            'ps': np.random.uniform(1, 20),
            'total_mv': np.random.uniform(1000000000, 10000000000),
            'circ_mv': np.random.uniform(500000000, 5000000000),
            'turnover_rate': np.random.uniform(0.5, 5)
        }

# 全局演示数据提供器实例
demo_data_provider = DemoDataProvider()
