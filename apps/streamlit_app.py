import os
import sys
from datetime import datetime, timedelta
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from dotenv import load_dotenv
import pandas as pd
import re

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# 添加错误处理
try:
    from src.analysis import analyze_stock, analyze_with_ai
    from src.report import build_pdf
    from src.data import DataFetcher
except Exception as e:
    st.error(f"❌ 模块导入失败: {e}")
    st.info("请确保所有依赖包已正确安装")
    st.stop()

load_dotenv()

# 页面配置
st.set_page_config(
    page_title="IF YOU HAVE NOTHING TO DO", 
    layout="wide",
    initial_sidebar_state="expanded"
)



def get_investment_recommendation(composite_score: float, subscores: dict) -> tuple:
    """
    根据综合评分和各维度评分生成投资建议
    返回: (建议类型, 建议文本, 颜色)
    """
    # 基础建议基于综合评分
    if composite_score >= 0.7:
        base_recommendation = "看涨"
        color = "success"
    elif composite_score >= 0.4:
        base_recommendation = "稳定"
        color = "info"
    else:
        base_recommendation = "看跌"
        color = "error"
    
    # 分析各维度表现
    strong_points = []
    weak_points = []
    
    category_names = {
        'quality': '质量',
        'growth': '增长', 
        'valuation': '估值',
        'momentum': '动量',
        'risk': '风险'
    }
    
    for category, score in subscores.items():
        # 处理None值
        if score is None:
            score = 0
        
        category_name = category_names.get(category, category)
        if score >= 0.7:
            strong_points.append(category_name)
        elif score < 0.4:
            weak_points.append(category_name)
    
    # 生成详细建议文本
    if base_recommendation == "看涨":
        if strong_points:
            recommendation_text = f"强烈推荐买入！该股票在{', '.join(strong_points)}方面表现优异"
        else:
            recommendation_text = "建议买入，综合评分良好"
    elif base_recommendation == "稳定":
        if strong_points and weak_points:
            recommendation_text = f"建议持有，{', '.join(strong_points)}表现良好，但{', '.join(weak_points)}需要关注"
        elif strong_points:
            recommendation_text = f"建议持有，{', '.join(strong_points)}方面表现稳定"
        else:
            recommendation_text = "建议观望，各项指标表现一般"
    else:  # 看跌
        if weak_points:
            recommendation_text = f"建议回避，{', '.join(weak_points)}方面存在风险"
        else:
            recommendation_text = "建议回避，综合评分较低"
    
    return base_recommendation, recommendation_text, color

def normalize_stock_code(code: str) -> str:
    """标准化股票代码格式"""
    # 移除所有空格和特殊字符
    code = re.sub(r'[^\w]', '', code.upper())
    
    # 如果是6位数字，添加后缀
    if len(code) == 6:
        if code.startswith('6'):
            return f"{code}.SH"
        elif code.startswith('0') or code.startswith('3'):
            return f"{code}.SZ"
        else:
            return f"{code}.SH"  # 默认上海
    
    return code

def get_indicator_explanation(indicator: str) -> str:
    """获取指标解释"""
    explanations = {
        'pe_ratio': '市盈率：股价与每股收益的比率，反映投资回收期',
        'pb_ratio': '市净率：股价与每股净资产的比率，反映资产价值',
        'turnover': '换手率：股票交易活跃程度，反映市场关注度'
    }
    return explanations.get(indicator, '')

def format_quality_data(data: dict) -> str:
    """格式化质量数据为可读文本"""
    if not data:
        return ""
    
    text_parts = []
    
    # ROE
    roe = data.get('roe', 0)
    if roe is not None and not pd.isna(roe):
        if roe >= 15:
            level = "优秀"
        elif roe >= 10:
            level = "良好"
        elif roe >= 5:
            level = "一般"
        else:
            level = "较差"
        text_parts.append(f"净资产收益率(ROE): {roe:.2f}% ({level})")
    
    # ROA
    roa = data.get('roa', 0)
    if roa is not None and not pd.isna(roa):
        if roa >= 8:
            level = "优秀"
        elif roa >= 5:
            level = "良好"
        elif roa >= 2:
            level = "一般"
        else:
            level = "较差"
        text_parts.append(f"总资产收益率(ROA): {roa:.2f}% ({level})")
    
    # 资产负债率
    debt_ratio = data.get('debt_ratio', 0)
    if debt_ratio is not None and not pd.isna(debt_ratio):
        if debt_ratio <= 30:
            level = "优秀"
        elif debt_ratio <= 50:
            level = "良好"
        elif debt_ratio <= 70:
            level = "一般"
        else:
            level = "较高"
        text_parts.append(f"资产负债率: {debt_ratio:.2f}% ({level})")
    
    # 权益乘数
    equity_multiplier = data.get('equity_multiplier', 0)
    if equity_multiplier is not None and not pd.isna(equity_multiplier):
        if equity_multiplier <= 1.5:
            level = "保守"
        elif equity_multiplier <= 2.5:
            level = "适中"
        else:
            level = "激进"
        text_parts.append(f"权益乘数: {equity_multiplier:.2f} ({level})")
    
    return "\n\n".join(text_parts)

def format_growth_data(data: dict) -> str:
    """格式化增长数据为可读文本"""
    if not data:
        return ""
    
    text_parts = []
    
    # 营收增长率
    revenue_growth = data.get('revenue_growth', 0)
    if revenue_growth is not None and not pd.isna(revenue_growth):
        if revenue_growth >= 20:
            level = "高速增长"
        elif revenue_growth >= 10:
            level = "稳定增长"
        elif revenue_growth >= 0:
            level = "缓慢增长"
        else:
            level = "负增长"
        text_parts.append(f"营收增长率: {revenue_growth:.2f}% ({level})")
    
    # 净利润增长率
    profit_growth = data.get('profit_growth', 0)
    if profit_growth is not None and not pd.isna(profit_growth):
        if profit_growth >= 25:
            level = "高速增长"
        elif profit_growth >= 15:
            level = "稳定增长"
        elif profit_growth >= 0:
            level = "缓慢增长"
        else:
            level = "负增长"
        text_parts.append(f"净利润增长率: {profit_growth:.2f}% ({level})")
    
    # 净资产增长率
    equity_growth = data.get('equity_growth', 0)
    if equity_growth is not None and not pd.isna(equity_growth):
        if equity_growth >= 15:
            level = "高速增长"
        elif equity_growth >= 8:
            level = "稳定增长"
        elif equity_growth >= 0:
            level = "缓慢增长"
        else:
            level = "负增长"
        text_parts.append(f"净资产增长率: {equity_growth:.2f}% ({level})")
    
    return "\n\n".join(text_parts)

def format_valuation_data(data: dict) -> str:
    """格式化估值数据为可读文本"""
    if not data:
        return ""
    
    text_parts = []
    
    # P/E
    pe = data.get('pe', 0)
    if pe is not None and not pd.isna(pe):
        if pe <= 15:
            level = "低估"
        elif pe <= 25:
            level = "合理"
        elif pe <= 40:
            level = "偏高"
        else:
            level = "高估"
        text_parts.append(f"市盈率(P/E): {pe:.2f} ({level})")
    
    # P/B
    pb = data.get('pb', 0)
    if pb is not None and not pd.isna(pb):
        if pb <= 1.5:
            level = "低估"
        elif pb <= 3:
            level = "合理"
        elif pb <= 5:
            level = "偏高"
        else:
            level = "高估"
        text_parts.append(f"市净率(P/B): {pb:.2f} ({level})")
    
    # P/S
    ps = data.get('ps', 0)
    if ps is not None and not pd.isna(ps):
        if ps <= 2:
            level = "低估"
        elif ps <= 5:
            level = "合理"
        elif ps <= 10:
            level = "偏高"
        else:
            level = "高估"
        text_parts.append(f"市销率(P/S): {ps:.2f} ({level})")
    
    # PEG
    peg = data.get('peg', 0)
    if peg is not None and not pd.isna(peg):
        if peg <= 1:
            level = "低估"
        elif peg <= 1.5:
            level = "合理"
        else:
            level = "高估"
        text_parts.append(f"PEG比率: {peg:.2f} ({level})")
    
    return "\n\n".join(text_parts)

def format_momentum_data(data: dict) -> str:
    """格式化动量数据为可读文本"""
    if not data:
        return ""
    
    text_parts = []
    
    # 动量评分
    momentum_score = data.get('momentum_score', 0)
    if momentum_score is not None and not pd.isna(momentum_score):
        if momentum_score >= 0.7:
            level = "强势"
        elif momentum_score >= 0.4:
            level = "中性"
        else:
            level = "弱势"
        text_parts.append(f"动量评分: {momentum_score:.2f} ({level})")
    
    # 相对强度
    relative_strength = data.get('relative_strength', 0)
    if relative_strength is not None and not pd.isna(relative_strength):
        if relative_strength >= 1.2:
            level = "强于大盘"
        elif relative_strength >= 0.8:
            level = "与大盘相当"
        else:
            level = "弱于大盘"
        text_parts.append(f"相对强度: {relative_strength:.2f} ({level})")
    
    # 波动率
    volatility = data.get('volatility', 0)
    if volatility is not None and not pd.isna(volatility):
        if volatility <= 20:
            level = "低波动"
        elif volatility <= 35:
            level = "中等波动"
        else:
            level = "高波动"
        text_parts.append(f"波动率: {volatility:.2f}% ({level})")
    
    return "\n\n".join(text_parts)

def format_risk_data(data: dict) -> str:
    """格式化风险数据为可读文本"""
    if not data:
        return ""
    
    text_parts = []
    
    # 波动率
    volatility = data.get('volatility', 0)
    if volatility is not None and not pd.isna(volatility):
        if volatility <= 20:
            level = "低风险"
        elif volatility <= 35:
            level = "中等风险"
        else:
            level = "高风险"
        text_parts.append(f"波动率: {volatility:.2f}% ({level})")
    
    # 最大回撤
    max_drawdown = data.get('max_drawdown', 0)
    if max_drawdown is not None and not pd.isna(max_drawdown):
        if abs(max_drawdown) <= 10:
            level = "低风险"
        elif abs(max_drawdown) <= 25:
            level = "中等风险"
        else:
            level = "高风险"
        text_parts.append(f"最大回撤: {max_drawdown:.2f}% ({level})")
    
    # VaR (Value at Risk)
    var_95 = data.get('var_95', 0)
    if var_95 is not None and not pd.isna(var_95):
        if abs(var_95) <= 2:
            level = "低风险"
        elif abs(var_95) <= 5:
            level = "中等风险"
        else:
            level = "高风险"
        text_parts.append(f"风险价值(VaR): {var_95:.2f}% ({level})")
    
    # 夏普比率
    sharpe_ratio = data.get('sharpe_ratio', 0)
    if sharpe_ratio is not None and not pd.isna(sharpe_ratio):
        if sharpe_ratio >= 1:
            level = "优秀"
        elif sharpe_ratio >= 0.5:
            level = "良好"
        elif sharpe_ratio >= 0:
            level = "一般"
        else:
            level = "较差"
        text_parts.append(f"夏普比率: {sharpe_ratio:.4f} ({level})")
    
    return "\n\n".join(text_parts)

def create_spider_chart(subscores: dict) -> go.Figure:
    """创建蜘蛛图"""
    categories = {
        'quality': '质量',
        'growth': '增长',
        'valuation': '估值',
        'momentum': '动量',
        'risk': '风险'
    }
    
    # 准备数据
    cat_names = []
    values = []
    
    for key, name in categories.items():
        value = subscores.get(key, 0)
        if value is None:
            value = 0
        cat_names.append(name)
        values.append(value)
    
    # 创建蜘蛛图
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=cat_names,
        fill='toself',
        name='评分',
        line_color='rgb(32, 201, 151)',
        fillcolor='rgba(32, 201, 151, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=False,
        title="五维度综合评分",
        font=dict(size=14)
    )
    
    return fig

def display_analysis_results(res, stock_code, normalized_code, start_date_str, end_date_str):
    """显示分析结果"""
    # 基本信息
    company_name = res.get("meta", {}).get('name', '未知公司')
    ts_code_display = normalized_code
    
    # 使用卡片样式显示标题
    st.markdown(f"""
    <div class="metric-container">
        <h2 style="color: #dc3545; margin-bottom: 0.5rem;">{company_name}（{ts_code_display}）分析报告</h2>
        <p style="color: #6c757d; margin: 0;">分析时间范围：{start_date_str} 至 {end_date_str}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 投资建议 - 基于AI分析结果
    if 'ai_report' in st.session_state:
        # 从AI报告中提取投资建议
        ai_report = st.session_state.ai_report
        if "## 投资建议" in ai_report:
            # 提取投资建议部分
            investment_advice_start = ai_report.find("## 投资建议")
            # 找到下一个章节的开始位置
            next_section_start = ai_report.find("##", investment_advice_start + 1)
            if next_section_start == -1:
                # 如果没有下一个章节，取到结尾
                investment_advice_text = ai_report[investment_advice_start:]
            else:
                investment_advice_text = ai_report[investment_advice_start:next_section_start]
            
            # 提取建议内容（去掉标题和多余的空行）
            lines = investment_advice_text.split('\n')
            advice_lines = []
            for line in lines:
                line = line.strip()
                if line and line != "## 投资建议":
                    advice_lines.append(line)
            
            advice_content = ' '.join(advice_lines)
            
            if advice_content:
                # 根据建议内容判断颜色
                if "买入" in advice_content or "推荐" in advice_content:
                    st.success(f"投资建议: {advice_content}")
                elif "回避" in advice_content or "谨慎" in advice_content or "观望" in advice_content:
                    st.warning(f"投资建议: {advice_content}")
                else:
                    st.info(f"投资建议: {advice_content}")
            else:
                st.info("投资建议: 等待AI分析完成...")
        else:
            # 如果AI报告中没有投资建议，显示默认建议
            st.info("投资建议: 等待AI分析完成...")
    else:
        # 如果还没有AI报告，显示等待信息
        st.info("投资建议: 分析中...")
    
    # 五维度综合评分和市场快照 - 基于AI分析结果
    st.subheader("五维度综合评分")
    
    # 创建两列布局：左侧显示蜘蛛图，右侧显示市场快照
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        # 蜘蛛图显示 - 基于AI分析结果
        if 'ai_report' in st.session_state and 'ai_scores' in res:
            # 使用AI生成的评分
            ai_scores = res.get('ai_scores', {})
            subscores = ai_scores.get('subscores', {})
            composite_score = ai_scores.get('composite', 0)
            
            if subscores:
                spider_fig = create_spider_chart(subscores)
                st.plotly_chart(spider_fig, use_container_width=True, key="spider_chart_main")
                
                # 综合评分
                st.metric("综合评分", f"{composite_score:.2f}")
                
                # 各维度评分
                st.write("**各维度评分（基于AI分析）：**")
                for category, score in subscores.items():
                    if score is None:
                        score = 0
                    
                    category_name = {
                        'quality': '质量',
                        'growth': '增长', 
                        'valuation': '估值',
                        'momentum': '动量',
                        'risk': '风险'
                    }.get(category, category)
                    
                    # 根据分数设置颜色
                    if score >= 0.7:
                        color = "🟢"
                    elif score >= 0.4:
                        color = "🟡"
                    else:
                        color = "🔴"
                    
                    st.write(f"{color} {category_name}: {score:.2f}")
        else:
            # 如果还没有AI分析结果，只显示等待信息，不显示任何临时评分
            st.info("等待AI分析完成，所有评分和图表将基于AI分析结果生成...")
    
    with right_col:
        # 市场快照 - 基于AI分析结果
        st.info("**最新行情快照**")
        
        # 公司基本信息 - 基于TuShare数据
        industry = res.get("meta", {}).get('industry', 'N/A')
        if industry is None:
            industry = 'N/A'
        st.write(f"所属行业: {industry}")
        
        # 从AI报告中提取公司概况信息
        if 'ai_report' in st.session_state:
            ai_report = st.session_state.ai_report
            if "## 公司概况" in ai_report:
                # 提取公司概况部分
                company_overview_start = ai_report.find("## 公司概况")
                next_section_start = ai_report.find("##", company_overview_start + 1)
                if next_section_start == -1:
                    company_overview_text = ai_report[company_overview_start:]
                else:
                    company_overview_text = ai_report[company_overview_start:next_section_start]
                
                # 提取概况内容（去掉标题）
                lines = company_overview_text.split('\n')
                overview_lines = []
                for line in lines:
                    line = line.strip()
                    if line and line != "## 公司概况":
                        overview_lines.append(line)
                
                if overview_lines:
                    overview_content = ' '.join(overview_lines[:3])  # 只显示前3句话
                    st.write(f"**公司概况**: {overview_content}")
        
        # 地区信息
        area = res.get("meta", {}).get('area', 'N/A')
        if area is None:
            area = 'N/A'
        st.write(f"所属地区: {area}")
        
        # 最新行情数据
        latest_quote = res.get('evidence', {}).get('last_quote', {})
        
        # 收盘价
        close_price = latest_quote.get('close', 'N/A')
        if close_price is not None and not pd.isna(close_price):
            st.write(f"收盘价: ¥{close_price:.2f}")
        else:
            st.write("收盘价: N/A")
        
        # PE比率
        pe_ratio = latest_quote.get('pe', 'N/A')
        if pe_ratio is not None and not pd.isna(pe_ratio):
            st.write(f"PE: {pe_ratio:.2f}")
        else:
            st.write("PE: N/A")
        
        # PB比率
        pb_ratio = latest_quote.get('pb', 'N/A')
        if pb_ratio is not None and not pd.isna(pb_ratio):
            st.write(f"PB: {pb_ratio:.2f}")
        else:
            st.write("PB: N/A")
        
        # 换手率
        turnover = latest_quote.get('turnover_rate', 'N/A')
        if turnover is not None and not pd.isna(turnover):
            st.write(f"换手率: {turnover:.2f}%")
        else:
            st.write("换手率: N/A")
    
    # 详细分析数据
    st.subheader("详细分析数据")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["质量", "增长", "估值", "动量", "风险"])
    
    with tab1:
        quality_data = res.get('evidence', {}).get('quality', {})
        formatted_quality = format_quality_data(quality_data)
        if formatted_quality:
            st.write("**质量指标分析:**")
            st.write(formatted_quality)
        else:
            st.json(quality_data)
    
    with tab2:
        growth_data = res.get('evidence', {}).get('growth', {})
        formatted_growth = format_growth_data(growth_data)
        if formatted_growth:
            st.write("**增长指标分析:**")
            st.write(formatted_growth)
        else:
            st.json(growth_data)
    
    with tab3:
        valuation_data = res.get('evidence', {}).get('valuation', {})
        formatted_valuation = format_valuation_data(valuation_data)
        if formatted_valuation:
            st.write("**估值指标分析:**")
            st.write(formatted_valuation)
        else:
            st.json(valuation_data)
    
    with tab4:
        momentum_data = res.get('evidence', {}).get('momentum', {})
        formatted_momentum = format_momentum_data(momentum_data)
        if formatted_momentum:
            st.write("**动量指标分析:**")
            st.write(formatted_momentum)
        else:
            st.json(momentum_data)
    
    with tab5:
        risk_data = res.get('evidence', {}).get('risk', {})
        formatted_risk = format_risk_data(risk_data)
        if formatted_risk:
            st.write("**风险指标分析:**")
            st.write(formatted_risk)
        else:
            st.json(risk_data)
    
    # 检查是否已有AI报告
    if 'ai_report' in st.session_state:
        st.markdown(st.session_state.ai_report)
        

    
    # 如果没有AI报告，自动生成
    elif 'analysis_result' in st.session_state and 'ai_report' not in st.session_state:
        with st.spinner("🤖 AI正在分析所有数据并生成投资建议..."):
            try:
                # 直接调用AI分析器生成报告
                from src.ai import ai_analyzer
                ai_report = ai_analyzer.generate_analysis_report(res)
                
                # 保存AI报告到session state
                st.session_state.ai_report = ai_report
                
                st.success("✅ AI分析完成！所有投资建议已基于AI分析结果更新")
                st.rerun()  # 重新运行以显示基于AI的所有内容
                
            except Exception as e:
                st.error(f"❌ AI分析生成失败: {str(e)}")
                st.info("请检查OpenAI API配置")
    

    
    # PDF导出
    st.subheader("报告导出")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("生成PDF报告"):
            with st.spinner("正在生成PDF报告..."):
                try:
                    # 生成PDF
                    from src.report import build_pdf
                    import tempfile
                    import os
                    
                    # 创建临时文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        temp_path = tmp_file.name
                    
                    # 获取AI报告文本
                    ai_text = st.session_state.get('ai_report', 'AI分析报告暂不可用')
                    
                    # 生成PDF
                    build_pdf(res, ai_text, temp_path)
                    
                    # 读取PDF数据
                    with open(temp_path, 'rb') as f:
                        pdf_data = f.read()
                    
                    # 删除临时文件
                    os.unlink(temp_path)
                    
                    # 保存到session state
                    st.session_state.pdf_data = pdf_data
                    st.session_state.pdf_filename = f"{company_name}_{ts_code_display}_分析报告.pdf"
                    
                    st.success("✅ PDF报告生成成功！")
                    
                except Exception as e:
                    st.error(f"❌ PDF生成失败: {str(e)}")
    
    with col2:
        # 下载PDF按钮
        if 'pdf_data' in st.session_state and 'pdf_filename' in st.session_state:
            st.download_button(
                label="下载PDF报告",
                data=st.session_state.pdf_data,
                file_name=st.session_state.pdf_filename,
                mime="application/pdf"
            )

# 自定义CSS样式 - 全新布局设计
st.markdown("""
<style>
    /* 重置所有默认样式 */
    * {
        box-sizing: border-box !important;
    }
    
    /* 页面整体布局 */
    .main {
        margin-left: 0 !important;
        width: 100% !important;
        max-width: none !important;
        padding: 0 !important;
    }
    
    /* 主内容容器 */
    .main .block-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
        padding: 1rem !important;
        margin: 0 !important;
        width: 100% !important;
        max-width: none !important;
    }
    
    /* 侧边栏样式 - 使用flexbox布局 */
    [data-testid="stSidebar"] {
        width: 25% !important;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
        position: relative !important;
        float: left !important;
        height: auto !important;
        min-height: 100vh !important;
        overflow-y: auto !important;
        border-right: 2px solid #dee2e6 !important;
    }
    
    /* 主内容区域 */
    .main .block-container {
        width: 75% !important;
        float: right !important;
        margin-left: 0 !important;
        padding: 2rem !important;
    }
    
    /* 清除浮动 */
    .main::after {
        content: "" !important;
        display: table !important;
        clear: both !important;
    }
    
    /* 标题样式 */
    .main-title {
        font-size: 2.5rem !important;
        font-weight: bold !important;
        background: linear-gradient(135deg, #dc3545 0%, #c82333 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin-bottom: 1rem !important;
        text-align: center !important;
    }
    
    /* 侧边栏内容样式 */
    [data-testid="stSidebar"] .stMarkdown {
        padding: 1rem !important;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #dc3545 !important;
        text-align: center !important;
        margin-bottom: 1.5rem !important;
        font-size: 1.5rem !important;
    }
    
    /* 输入框样式 */
    .stTextInput > div > div > input {
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #dc3545 !important;
        box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1) !important;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #212529 0%, #343a40 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 15px rgba(33, 37, 41, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin: 0.5rem 0 !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #343a40 0%, #495057 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(33, 37, 41, 0.4) !important;
    }
    
    /* 重新分析按钮样式 */
    [data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #6c757d 0%, #868e96 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 15px rgba(108, 117, 125, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin: 0.5rem 0 !important;
    }
    
    [data-testid="baseButton-secondary"]:hover {
        background: linear-gradient(135deg, #868e96 0%, #adb5bd 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(108, 117, 125, 0.4) !important;
    }
    
    /* 卡片样式 */
    .metric-container {
        background: white !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid #e9ecef !important;
        margin: 1rem 0 !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }
    
    /* 文本内容样式 */
    p, div, span {
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        white-space: normal !important;
        max-width: 100% !important;
    }
    
    /* 成功消息样式 */
    .stSuccess {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%) !important;
        border: 2px solid #28a745 !important;
        border-radius: 10px !important;
    }
    
    /* 警告消息样式 */
    .stWarning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%) !important;
        border: 2px solid #ffc107 !important;
        border-radius: 10px !important;
    }
    
    /* 错误消息样式 */
    .stError {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%) !important;
        border: 2px solid #dc3545 !important;
        border-radius: 10px !important;
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
    }
    
    /* 确保所有内容都能完整显示 */
    .main .block-container > div,
    .main .block-container > section,
    .main .block-container > article {
        margin: 0 !important;
        width: 100% !important;
        max-width: none !important;
        padding: 0 !important;
        overflow: visible !important;
    }
    
    /* 图表容器样式 */
    .stPlotlyChart {
        width: 100% !important;
        max-width: none !important;
        overflow: visible !important;
    }
    
    /* 表格样式 */
    .stDataFrame {
        width: 100% !important;
        max-width: none !important;
        overflow-x: auto !important;
    }
    
    /* 卡片样式 */
    .metric-container {
        background: white !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid #e9ecef !important;
        margin: 1rem 0 !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }
    
    /* 文本内容样式 */
    .main .block-container p, .main .block-container div {
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        white-space: normal !important;
        max-width: 100% !important;
    }
    
    /* 成功消息样式 */
    .stSuccess {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%) !important;
        border: 2px solid #28a745 !important;
        border-radius: 10px !important;
    }
    
    /* 警告消息样式 */
    .stWarning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%) !important;
        border: 2px solid #ffc107 !important;
        border-radius: 10px !important;
    }
    
    /* 错误消息样式 */
    .stError {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%) !important;
        border: 2px solid #dc3545 !important;
        border-radius: 10px !important;
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
    }
    
    /* 重新分析按钮样式 - 灰色 */
    [data-testid="stSidebar"] [data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #6c757d 0%, #868e96 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 15px rgba(108, 117, 125, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin: 0 auto !important;
        display: block !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        position: relative !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="baseButton-secondary"]:hover {
        background: linear-gradient(135deg, #868e96 0%, #adb5bd 100%) !important;
        transform: translateX(-50%) translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(108, 117, 125, 0.4) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white !important;
        border-radius: 8px 8px 0 0 !important;
        border: 2px solid #e9ecef !important;
        border-bottom: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: #dc3545 !important;
        color: white !important;
        border-color: #dc3545 !important;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    # 主标题 - 红色渐变设计
    st.markdown('<h1 class="main-title">IF YOU HAVE NOTHING TO DO</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6c757d; font-size: 0.9rem; text-align: center; margin-bottom: 1rem;">公司价值分析工具 - 仅供研究学习，不构成投资建议</p>', unsafe_allow_html=True)
    
    # 装饰性分隔线
    st.markdown('<div style="height: 3px; background: linear-gradient(90deg, #dc3545, #c82333, #dc3545); border-radius: 2px; margin: 1rem 0;"></div>', unsafe_allow_html=True)
    
    # 分析设置标题
    st.markdown('<h3 style="color: #dc3545; text-align: center; margin-bottom: 1.5rem;">分析设置</h3>', unsafe_allow_html=True)
    
    # 股票代码输入
    stock_code = st.text_input("股票代码", placeholder="例如：600519")
    
    # 日期选择
    end_date = st.date_input(
        "结束日期",
        value=datetime.now().date(),
        max_value=datetime.now().date()
    )
    
    start_date = st.date_input(
        "开始日期",
        value=(datetime.now() - timedelta(days=365)).date(),
        max_value=end_date
    )
    
    # 分析按钮
    run = st.button("开始分析", type="primary")
    
    # 重新分析按钮
    if st.button("重新分析", key="reanalyze_button"):
        # 清除session state
        if 'analysis_result' in st.session_state:
            del st.session_state.analysis_result
        if 'analysis_meta' in st.session_state:
            del st.session_state.analysis_meta
        if 'pdf_data' in st.session_state:
            del st.session_state.pdf_data
        if 'pdf_filename' in st.session_state:
            del st.session_state.pdf_filename
        if 'ai_report' in st.session_state:
            del st.session_state.ai_report
        if 'analysis_key' in st.session_state:
            del st.session_state.analysis_key
        st.rerun()

# 主内容区域
if run and stock_code:
    # 标准化股票代码
    normalized_code = normalize_stock_code(stock_code)
    
    # 检查是否是新的股票代码（与之前分析的不同）
    current_analysis_key = f"{normalized_code}_{start_date.strftime('%Y%m%d')}"
    previous_analysis_key = st.session_state.get('analysis_key', '')
    
    if current_analysis_key != previous_analysis_key:
        # 如果是新的股票代码，清除之前的分析结果
        if 'analysis_result' in st.session_state:
            del st.session_state.analysis_result
        if 'analysis_meta' in st.session_state:
            del st.session_state.analysis_meta
        if 'ai_report' in st.session_state:
            del st.session_state.ai_report
        if 'pdf_data' in st.session_state:
            del st.session_state.pdf_data
        if 'pdf_filename' in st.session_state:
            del st.session_state.pdf_filename
    
    # 检查是否已有AI分析结果
    if 'ai_report' in st.session_state and st.session_state.get('analysis_result') is not None:
        # 如果已有AI分析结果，显示完整分析
        res = st.session_state.analysis_result
        display_analysis_results(res, stock_code, normalized_code, start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d'))
    else:
        # 如果还没有AI分析结果，只显示加载信息，不显示任何临时分析结果
        with st.spinner("🔍 正在分析股票数据..."):
            try:
                # 执行分析
                res = analyze_stock(normalized_code, start_date.strftime('%Y%m%d'))
                
                # 保存分析结果到session state
                st.session_state.analysis_result = res
                st.session_state.analysis_meta = {
                    'stock_code': stock_code,
                    'normalized_code': normalized_code,
                    'start_date': start_date.strftime('%Y%m%d'),
                    'end_date': end_date.strftime('%Y%m%d')
                }
                st.session_state.analysis_key = current_analysis_key
                
                # 自动生成AI分析
                with st.spinner("🤖 AI正在分析所有数据并生成投资建议..."):
                    try:
                        from src.ai import ai_analyzer
                        ai_report = ai_analyzer.generate_analysis_report(res)
                        st.session_state.ai_report = ai_report
                        st.success("✅ AI分析完成！所有分析结果已生成")
                        st.rerun()  # 重新运行以显示完整分析
                    except Exception as e:
                        st.error(f"❌ AI分析生成失败: {str(e)}")
                        st.info("请检查OpenAI API配置")
                        # AI分析失败时，清除分析结果，不显示任何临时数据
                        if 'analysis_result' in st.session_state:
                            del st.session_state.analysis_result
                        if 'analysis_meta' in st.session_state:
                            del st.session_state.analysis_meta
                
            except Exception as e:
                st.error(f"❌ 分析过程中出现错误: {str(e)}")
                st.info("请检查股票代码是否正确，或稍后重试")

elif st.session_state.get('analysis_result') is not None and 'ai_report' in st.session_state:
    # 显示保存的分析结果
    res = st.session_state.analysis_result
    meta = st.session_state.analysis_meta
    
    display_analysis_results(
        res, 
        meta['stock_code'], 
        meta['normalized_code'], 
        meta['start_date'], 
        meta['end_date']
    )
