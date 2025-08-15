import os
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd

load_dotenv()

from .config import OPENAI_API_KEY, OPENAI_MODEL

# 设置 OpenAI API
# openai.api_key = OPENAI_API_KEY # This line is removed as per the new_code

class AIAnalyzer:
    """AI分析器"""
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
    
    def generate_analysis_report(self, analysis_results: Dict) -> str:
        """生成AI分析报告"""
        try:
            # 构建提示词
            prompt = self._build_prompt(analysis_results)
            
            # 调用 OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """你是一位资深的股票分析师和投资顾问，拥有丰富的A股市场分析经验。你的分析将直接影响投资者的决策，因此必须基于所有可用的TuShare数据进行全面、深入的分析。

你的核心职责：
1. **全面数据分析师**：深入分析所有TuShare提供的财务数据、市场指标、估值数据
2. **专业投资顾问**：基于数据分析提供明确的投资建议和操作指导
3. **风险控制专家**：识别潜在风险并给出具体的风险提示
4. **市场洞察专家**：结合行业趋势和市场环境进行分析

分析要求：
1. **数据驱动**：所有结论必须基于提供的TuShare数据，不能凭空臆测
2. **全面分析**：必须分析所有维度的数据（质量、增长、估值、动量、风险）
3. **语言风格**：使用通俗易懂的白话，让普通投资者都能理解
4. **结构清晰**：严格按照以下5个章节结构：
   - 公司概况
   - 投资亮点
   - 主要风险
   - 建议投资者：
   - 投资建议

特别要求：
1. **投资建议必须明确**：给出明确的买入/卖出/持有建议，说明具体理由
2. **基于数据说话**：所有结论都要有数据支撑
3. **风险提示具体**：明确指出具体的风险点和影响
4. **操作指导详细**：给出具体的操作建议，如买入时机、止损位等

报告格式：
- 使用 ## 作为章节标题
- 使用 ** 标记重要信息
- 段落之间用空行分隔
- 总长度控制在800-1200字之间
- 严格按照要求的章节标题格式
- 所有内容必须基于TuShare数据分析得出"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            ai_text = response.choices[0].message.content.strip()
            
            # 检查AI响应是否足够详细
            if len(ai_text) < 200:
                return self._generate_fallback_analysis(analysis_results)
            
            # 解析AI分析结果，生成新的评分
            ai_scores = self._parse_ai_scores(ai_text, analysis_results)
            
            # 将AI评分添加到分析结果中
            analysis_results['ai_scores'] = ai_scores
            
            return ai_text
            
        except Exception as e:
            print(f"AI分析生成失败: {e}")
            return self._generate_fallback_analysis(analysis_results)
    
    def _build_prompt(self, analysis_results: Dict) -> str:
        """构建提示词"""
        meta = analysis_results.get('meta', {})
        company_name = meta.get('name', f'股票{meta.get("ts_code", "未知")}')
        ts_code = meta.get('ts_code', '未知')
        industry = meta.get('industry', '未知行业')
        
        subscores = analysis_results.get('subscores', {})
        composite_score = analysis_results.get('composite', 0)
        view = analysis_results.get('view', '中性')
        
        evidence = analysis_results.get('evidence', {})
        
        prompt = f"""
请为以下股票生成一份基于TuShare数据的全面分析报告。你的分析将直接影响投资决策，因此必须基于所有可用数据进行深入分析。

**基本信息**
- 公司名称：{company_name}
- 股票代码：{ts_code}
- 所属行业：{industry}

**综合评分**
- 综合评分：{composite_score:.2f}/1.00
- 投资建议：{view}

**各维度评分**
- 质量评分：{subscores.get('quality', 0):.2f}/1.00
- 增长评分：{subscores.get('growth', 0):.2f}/1.00
- 估值评分：{subscores.get('valuation', 0):.2f}/1.00
- 动量评分：{subscores.get('momentum', 0):.2f}/1.00
- 风险评分：{subscores.get('risk', 0):.2f}/1.00

**TuShare数据指标（请基于这些数据进行分析）**
{self._format_evidence_data(evidence)}

**分析要求：**
请生成一份包含以下章节的详细报告，所有内容必须基于上述TuShare数据分析得出：

## 公司概况
- 基于公司基本信息和行业背景进行分析
- 结合财务数据评估公司基本面

## 投资亮点
- 基于各维度评分和财务指标识别投资价值
- 突出公司的竞争优势和发展潜力

## 主要风险
- 基于风险评分和具体数据指标识别风险点
- 分析数据限制和不确定性

## 建议投资者：
- 针对不同类型投资者的具体建议
- 基于风险承受能力给出策略指导

## 投资建议
- **必须给出明确的买入/卖出/持有建议**
- 基于所有TuShare数据分析得出最终决策
- 提供具体的操作指导（如买入时机、止损位等）

**特别强调：**
1. 所有结论必须基于提供的TuShare数据，不能凭空臆测
2. 投资建议必须明确具体，不能模棱两可
3. 必须分析所有维度的数据（质量、增长、估值、动量、风险）
4. 如果数据缺失，请明确说明并基于现有数据进行分析
5. 给出可操作的具体建议"""
        
        return prompt
    
    def _format_evidence_data(self, evidence: Dict) -> str:
        """格式化证据数据"""
        if not evidence:
            return "数据不足，无法提供详细分析。"
        
        formatted_data = []
        
        # 最新行情
        last_quote = evidence.get('last_quote', {})
        if last_quote:
            formatted_data.append(f"最新收盘价：¥{last_quote.get('close', 'N/A')}")
            formatted_data.append(f"市盈率(PE)：{last_quote.get('pe', 'N/A')}")
            formatted_data.append(f"市净率(PB)：{last_quote.get('pb', 'N/A')}")
            formatted_data.append(f"换手率：{last_quote.get('turnover_rate', 'N/A')}%")
        
        # 质量指标
        quality = evidence.get('quality', {})
        if quality:
            formatted_data.append(f"ROE：{quality.get('roe', 'N/A')}%")
            formatted_data.append(f"毛利率：{quality.get('gross_margin', 'N/A')}%")
            formatted_data.append(f"净利率：{quality.get('net_margin', 'N/A')}%")
        
        # 增长指标
        growth = evidence.get('growth', {})
        if growth:
            formatted_data.append(f"营收增长率：{growth.get('revenue_growth', 'N/A')}%")
            formatted_data.append(f"净利润增长率：{growth.get('profit_growth', 'N/A')}%")
        
        # 估值指标
        valuation = evidence.get('valuation', {})
        if valuation:
            formatted_data.append(f"PEG：{valuation.get('peg', 'N/A')}")
        
        # 动量指标
        momentum = evidence.get('momentum', {})
        if momentum:
            formatted_data.append(f"近3月收益率：{momentum.get('return_3m', 'N/A')}%")
            formatted_data.append(f"近6月收益率：{momentum.get('return_6m', 'N/A')}%")
        
        # 风险指标（使用文字描述）
        risk = evidence.get('risk', {})
        if risk:
            # 使用文字描述而不是数值
            volatility_text = risk.get('volatility_text', '数据不足')
            max_drawdown_text = risk.get('max_drawdown_text', '数据不足')
            var_95_text = risk.get('var_95_text', '数据不足')
            sharpe_ratio_text = risk.get('sharpe_ratio_text', '数据不足')
            
            formatted_data.append(f"波动性：{volatility_text}")
            formatted_data.append(f"最大回撤：{max_drawdown_text}")
            formatted_data.append(f"风险水平：{var_95_text}")
            formatted_data.append(f"收益风险比：{sharpe_ratio_text}")
        
        if formatted_data:
            return "\n".join(formatted_data)
        else:
            return "数据不足，无法提供详细分析。"
    
    def _generate_fallback_analysis(self, analysis_results: Dict) -> str:
        """生成备用分析报告"""
        meta = analysis_results.get('meta', {})
        company_name = meta.get('name', f'股票{meta.get("ts_code", "未知")}')
        ts_code = meta.get('ts_code', '未知')
        composite_score = analysis_results.get('composite', 0)
        view = analysis_results.get('view', '中性')
        subscores = analysis_results.get('subscores', {})
        
        investment_advice = self._get_investment_advice(composite_score)
        
        report = f"""## 公司概况

**{company_name}（{ts_code}）** 是一家上市公司，基于当前的分析数据，我们对其投资价值进行了综合评估。

## 投资亮点

根据五维度评分体系，该股票的综合评分为 **{composite_score:.2f}/1.00**，投资建议为 **{view}**。

**各维度表现：**
- 质量维度：{subscores.get('quality', 0):.2f}/1.00
- 增长维度：{subscores.get('growth', 0):.2f}/1.00  
- 估值维度：{subscores.get('valuation', 0):.2f}/1.00
- 动量维度：{subscores.get('momentum', 0):.2f}/1.00
- 风险维度：{subscores.get('risk', 0):.2f}/1.00

## 主要风险

由于数据获取限制，部分财务指标可能不完整。建议投资者：
1. 进一步了解公司的具体业务模式
2. 关注行业政策变化
3. 注意市场整体风险

## 建议投资者：

当前分析基于有限的数据，建议投资者：
- 查看公司最新财报
- 关注行业对比数据
- 结合宏观经济环境
- 控制投资仓位，分散风险

## 投资建议

{investment_advice}

**风险提示：** 本分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。"""
        
        return report
    
    def _parse_ai_scores(self, ai_text: str, analysis_results: Dict) -> Dict:
        """解析AI分析结果，生成新的评分"""
        # 基于AI分析内容生成评分
        scores = {
            'quality': 0.5,
            'growth': 0.5,
            'valuation': 0.5,
            'momentum': 0.5,
            'risk': 0.5
        }
        
        # 根据AI分析内容调整评分 - 更精确的解析
        ai_text_lower = ai_text.lower()
        
        # 质量维度评分
        if any(word in ai_text_lower for word in ["优秀", "卓越", "领先", "强劲", "稳健"]):
            scores['quality'] = 0.8
        elif any(word in ai_text_lower for word in ["良好", "稳定", "健康", "合理"]):
            scores['quality'] = 0.7
        elif any(word in ai_text_lower for word in ["一般", "中等", "普通"]):
            scores['quality'] = 0.5
        elif any(word in ai_text_lower for word in ["较差", "薄弱", "问题", "风险"]):
            scores['quality'] = 0.3
        
        # 增长维度评分
        if any(word in ai_text_lower for word in ["高速增长", "快速增长", "强劲增长", "高增长"]):
            scores['growth'] = 0.9
        elif any(word in ai_text_lower for word in ["稳定增长", "持续增长", "稳步增长"]):
            scores['growth'] = 0.7
        elif any(word in ai_text_lower for word in ["缓慢增长", "增长放缓", "增长有限"]):
            scores['growth'] = 0.5
        elif any(word in ai_text_lower for word in ["负增长", "下滑", "下降", "衰退"]):
            scores['growth'] = 0.2
        
        # 估值维度评分
        if any(word in ai_text_lower for word in ["低估", "便宜", "价值洼地", "投资价值"]):
            scores['valuation'] = 0.8
        elif any(word in ai_text_lower for word in ["合理", "适中", "正常", "公允"]):
            scores['valuation'] = 0.6
        elif any(word in ai_text_lower for word in ["偏高", "较贵", "溢价"]):
            scores['valuation'] = 0.4
        elif any(word in ai_text_lower for word in ["高估", "泡沫", "过度", "昂贵"]):
            scores['valuation'] = 0.2
        
        # 动量维度评分（基于投资建议）
        if any(word in ai_text_lower for word in ["买入", "推荐", "积极", "看好"]):
            scores['momentum'] = 0.8
        elif any(word in ai_text_lower for word in ["持有", "观望", "中性", "谨慎"]):
            scores['momentum'] = 0.5
        elif any(word in ai_text_lower for word in ["卖出", "回避", "看空", "不推荐"]):
            scores['momentum'] = 0.2
        
        # 风险维度评分
        if any(word in ai_text_lower for word in ["低风险", "风险较小", "相对安全"]):
            scores['risk'] = 0.8
        elif any(word in ai_text_lower for word in ["中等风险", "风险适中", "一般风险"]):
            scores['risk'] = 0.5
        elif any(word in ai_text_lower for word in ["高风险", "风险较大", "不确定性"]):
            scores['risk'] = 0.2
        
        # 计算综合评分
        weights = {
            'quality': 0.25,
            'growth': 0.25,
            'valuation': 0.20,
            'momentum': 0.15,
            'risk': 0.15
        }
        
        composite_score = sum(scores[key] * weights[key] for key in scores.keys())
        
        return {
            'subscores': scores,
            'composite': composite_score
        }
    
    def _get_investment_advice(self, composite_score: float) -> str:
        """根据综合评分生成投资建议"""
        if composite_score >= 0.7:
            return "该股票综合表现优秀，可以考虑适当配置。建议关注公司基本面变化，适时调整仓位。"
        elif composite_score >= 0.5:
            return "该股票表现中等，建议谨慎投资。可以少量配置，但需要密切关注风险。"
        elif composite_score >= 0.3:
            return "该股票表现一般，建议观望为主。如需投资，建议严格控制仓位。"
        else:
            return "该股票综合评分较低，建议暂时回避。如需投资，需要充分了解风险。"

# 全局AI分析器实例
ai_analyzer = AIAnalyzer()

def generate_ai_response(prompt: str) -> str:
    """生成AI回复的通用函数"""
    try:
        analyzer = AIAnalyzer()
        
        # 调用 OpenAI API
        response = analyzer.client.chat.completions.create(
            model=analyzer.model,
            messages=[
                {
                    "role": "system",
                    "content": """你是一位专业的股票分析师和投资顾问。请基于提供的分析结果，用通俗易懂的语言回答用户问题。

回答要求：
1. 语言通俗易懂，避免专业术语
2. 基于提供的分析数据回答
3. 回答要准确、专业、有帮助
4. 如果问题超出分析范围，请说明并提供建议"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        ai_text = response.choices[0].message.content.strip()
        return ai_text
        
    except Exception as e:
        print(f"AI回复生成失败: {e}")
        return f"抱歉，AI回复生成失败：{str(e)}。请检查OpenAI API配置。"
