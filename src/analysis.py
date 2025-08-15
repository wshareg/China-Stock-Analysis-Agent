import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .data import data_fetcher
from .indicators import indicator_calculator
from .ai import ai_analyzer
from .config import SCORE_WEIGHTS

def analyze_stock(ts_code: str, start_date: str = '20180101') -> Dict:
    """分析单只股票"""
    try:
        # 1. 获取数据
        stock_data = _fetch_stock_data(ts_code, start_date)
        
        # 2. 计算指标
        indicators = _calculate_all_indicators(stock_data)
        
        # 3. 计算评分
        scores = _calculate_scores(indicators)
        
        # 4. 生成投资观点
        view = _generate_investment_view(scores['composite'])
        
        # 5. 构建结果
        result = {
            'meta': stock_data['basic'],
            'composite': scores['composite'],
            'subscores': scores['subscores'],
            'view': view,
            'evidence': indicators,
            'asof': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return result
        
    except Exception as e:
        print(f"分析股票失败: {e}")
        return _create_error_result(ts_code, str(e))

def analyze_with_ai(ts_code: str, start_date: str = '20180101') -> Dict:
    """带AI分析的股票分析"""
    try:
        # 1. 基础分析
        result = analyze_stock(ts_code, start_date)
        
        # 2. AI分析
        if result.get('meta', {}).get('name'):  # 确保有基本数据
            ai_text = ai_analyzer.generate_analysis_report(result)
            result['ai_text'] = ai_text
        
        return result
        
    except Exception as e:
        print(f"AI分析失败: {e}")
        return analyze_stock(ts_code, start_date)  # 返回基础分析结果

def _fetch_stock_data(ts_code: str, start_date: str) -> Dict:
    """获取股票数据"""
    data = {}
    
    # 基本信息
    data['basic'] = data_fetcher.get_stock_basic(ts_code)
    
    # 日线数据
    data['daily'] = data_fetcher.get_daily_data(ts_code, start_date)
    
    # 财务数据
    data['financial'] = data_fetcher.get_financial_data(ts_code, start_date)
    
    # 业绩预告
    data['forecast'] = data_fetcher.get_forecast_data(ts_code, start_date)
    
    # 行业数据
    data['industry'] = data_fetcher.get_industry_data(ts_code)
    
    # 最新行情
    data['latest_quote'] = data_fetcher.get_latest_quote(ts_code)
    
    return data

def _calculate_all_indicators(stock_data: Dict) -> Dict:
    """计算所有指标"""
    indicators = {}
    
    # 质量指标
    indicators['quality'] = indicator_calculator.calculate_quality_indicators(
        stock_data['financial']
    )
    
    # 增长指标
    indicators['growth'] = indicator_calculator.calculate_growth_indicators(
        stock_data['financial']
    )
    
    # 估值指标
    indicators['valuation'] = indicator_calculator.calculate_valuation_indicators(
        stock_data['financial'],
        stock_data['latest_quote']
    )
    
    # 动量指标
    indicators['momentum'] = indicator_calculator.calculate_momentum_indicators(
        stock_data['daily']
    )
    
    # 风险指标
    indicators['risk'] = indicator_calculator.calculate_risk_indicators(
        stock_data['daily'],
        stock_data['financial']
    )
    
    # 最新行情 - 确保数据正确传递
    indicators['last_quote'] = stock_data.get('latest_quote', {})
    
    return indicators

def _calculate_scores(indicators: Dict) -> Dict:
    """计算评分"""
    scores = {}
    
    # 计算各维度评分
    for category in ['quality', 'growth', 'valuation', 'momentum', 'risk']:
        category_indicators = indicators.get(category, {})
        scores[category] = indicator_calculator.calculate_z_scores(
            category_indicators, category
        )
    
    # 计算综合评分
    composite_score = 0
    total_weight = 0
    
    for category, weight in SCORE_WEIGHTS.items():
        if category in scores:
            composite_score += scores[category] * weight
            total_weight += weight
    
    if total_weight > 0:
        composite_score = composite_score / total_weight
    
    return {
        'subscores': scores,
        'composite': composite_score
    }

def _generate_investment_view(composite_score: float) -> str:
    """生成投资观点"""
    if composite_score >= 0.7:
        return "强烈推荐买入"
    elif composite_score >= 0.2:
        return "建议买入"
    elif composite_score >= -0.2:
        return "建议观望"
    elif composite_score >= -0.7:
        return "建议谨慎"
    else:
        return "建议回避"

def _create_error_result(ts_code: str, error_msg: str) -> Dict:
    """创建错误结果"""
    return {
        'meta': {'ts_code': ts_code, 'name': '分析失败'},
        'composite': 0,
        'subscores': {
            'quality': 0,
            'growth': 0,
            'valuation': 0,
            'momentum': 0,
            'risk': 0
        },
        'view': '分析失败',
        'evidence': {
            'quality': {},
            'growth': {},
            'valuation': {},
            'momentum': {},
            'risk': {},
            'last_quote': {}
        },
        'asof': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'error': error_msg
    }
