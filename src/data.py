import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

from .config import TUSHARE_TOKEN
from .demo_data import demo_data_provider

# 初始化 TuShare
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

class DataFetcher:
    """数据获取类"""
    
    def __init__(self, demo_mode=False):
        self.pro = pro
        self.demo_mode = demo_mode
    
    def get_stock_basic(self, ts_code: str) -> Dict:
        """获取股票基本信息"""
        if self.demo_mode:
            return demo_data_provider.get_stock_basic(ts_code)
        
        try:
            df = self.pro.stock_basic(ts_code=ts_code, fields='ts_code,name,area,industry,market,list_date')
            if df.empty:
                return {}
            return df.iloc[0].to_dict()
        except Exception as e:
            print(f"获取股票基本信息失败: {e}")
            return {}
    
    def get_daily_data(self, ts_code: str, start_date: str, end_date: str = None) -> pd.DataFrame:
        """获取日线数据"""
        if self.demo_mode:
            return demo_data_provider.get_daily_data(ts_code, start_date, end_date)
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        try:
            df = self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            df = df.sort_values('trade_date')
            return df
        except Exception as e:
            print(f"获取日线数据失败: {e}")
            return pd.DataFrame()
    
    def get_financial_data(self, ts_code: str, start_date: str, end_date: str = None) -> Dict:
        """获取财务数据"""
        if self.demo_mode:
            return demo_data_provider.get_financial_data(ts_code, start_date, end_date)
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        try:
            # 获取财务指标
            fina = self.pro.fina_indicator(ts_code=ts_code, start_date=start_date, end_date=end_date)
            
            # 获取利润表
            income = self.pro.income(ts_code=ts_code, start_date=start_date, end_date=end_date)
            
            # 获取资产负债表
            balance = self.pro.balancesheet(ts_code=ts_code, start_date=start_date, end_date=end_date)
            
            # 获取现金流量表
            cashflow = self.pro.cashflow(ts_code=ts_code, start_date=start_date, end_date=end_date)
            
            return {
                'fina': fina,
                'income': income,
                'balance': balance,
                'cashflow': cashflow
            }
        except Exception as e:
            print(f"获取财务数据失败: {e}")
            return {}
    
    def get_forecast_data(self, ts_code: str, start_date: str, end_date: str = None) -> pd.DataFrame:
        """获取业绩预告数据"""
        if self.demo_mode:
            return demo_data_provider.get_forecast_data(ts_code, start_date, end_date)
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        try:
            df = self.pro.forecast(ts_code=ts_code, start_date=start_date, end_date=end_date)
            return df
        except Exception as e:
            print(f"获取业绩预告数据失败: {e}")
            return pd.DataFrame()
    
    def get_industry_data(self, ts_code: str) -> Dict:
        """获取行业数据"""
        if self.demo_mode:
            stock_info = self.get_stock_basic(ts_code)
            return {
                'industry': stock_info.get('industry', '演示行业'),
                'industry_name': stock_info.get('industry', '演示行业')
            }
        
        try:
            # 获取股票所属行业
            stock_info = self.get_stock_basic(ts_code)
            industry = stock_info.get('industry', '')
            
            if not industry:
                return {}
            
            # 获取行业指数数据（这里简化处理，实际可能需要更复杂的逻辑）
            return {
                'industry': industry,
                'industry_name': industry
            }
        except Exception as e:
            print(f"获取行业数据失败: {e}")
            return {}
    
    def get_latest_quote(self, ts_code: str) -> Dict:
        """获取最新行情（包含估值指标）"""
        if self.demo_mode:
            return demo_data_provider.get_latest_quote(ts_code)
        
        try:
            # 获取最新交易日
            today = datetime.now().strftime('%Y%m%d')
            
            # 获取日线数据（包含估值指标）
            df = self.pro.daily_basic(ts_code=ts_code, start_date=today, end_date=today, 
                                    fields='ts_code,trade_date,close,pe,pb,ps,total_mv,circ_mv,turnover_rate')
            
            if df.empty:
                # 如果今天没有数据，获取最近的数据
                df = self.pro.daily_basic(ts_code=ts_code, limit=1,
                                        fields='ts_code,trade_date,close,pe,pb,ps,total_mv,circ_mv,turnover_rate')
            
            if not df.empty:
                return df.iloc[0].to_dict()
            
            # 如果还是没有数据，尝试获取基础日线数据
            df_daily = self.pro.daily(ts_code=ts_code, limit=1)
            if not df_daily.empty:
                return df_daily.iloc[0].to_dict()
            
            return {}
        except Exception as e:
            print(f"获取最新行情失败: {e}")
            return {}

# 全局数据获取器实例（默认使用真实 API）
data_fetcher = DataFetcher(demo_mode=False)
