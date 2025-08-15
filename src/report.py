import io
import math
from typing import Dict, Any
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib
matplotlib.use('Agg')
import numpy as np
from io import BytesIO
from datetime import datetime
from typing import Dict, List
import os

def _radar_chart_png(scores: Dict[str, float]) -> bytes:
    labels = ["quality","growth","valuation","momentum","risk"]
    vals = [scores.get(k, float("nan")) for k in labels]
    import numpy as np
    arr = np.array([0 if (v is None or math.isnan(v)) else v for v in vals], dtype=float)
    if np.nanstd(arr) == 0:
        scaled = np.zeros_like(arr)
    else:
        scaled = (arr - np.nanmin(arr)) / (np.nanmax(arr) - np.nanmin(arr) + 1e-9)
    N = len(labels)
    angles = np.linspace(0, 2*math.pi, N, endpoint=False).tolist()
    scaled = np.concatenate((scaled, [scaled[0]]))
    angles += [angles[0]]

    fig = plt.figure(figsize=(4,4), dpi=150)
    ax = plt.subplot(111, polar=True)
    ax.plot(angles, scaled)
    ax.fill(angles, scaled, alpha=0.25)
    ax.set_thetagrids([a*180/math.pi for a in angles[:-1]], labels)
    ax.set_ylim(0, 1)
    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format="png")
    plt.close(fig)
    return buf.getvalue()

def _bars_png(scores: Dict[str, float]) -> bytes:
    labels = list(scores.keys())
    vals = [scores[k] for k in labels]
    fig = plt.figure(figsize=(5,3), dpi=150)
    ax = plt.subplot(111)
    ax.bar(labels, vals)
    ax.set_ylabel("z-score")
    ax.tick_params(axis='x', rotation=15)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    return buf.getvalue()

def build_pdf(analysis_result: Dict, ai_text: str, output_path: str):
    """生成PDF报告 - 现代化设计"""
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []
    
    # 注册中文字体
    try:
        # 使用ReportLab内置的中文字体支持
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        chinese_font_registered = True
        print("✅ 中文字体注册成功")
    except Exception as e:
        print(f"中文字体注册失败: {e}")
        chinese_font_registered = False
    
    # 获取样式并设置中文字体
    styles = getSampleStyleSheet()

    # 创建支持中文的样式
    font_name = 'STSong-Light' if chinese_font_registered else 'Helvetica'
    
    # 主标题样式 - 红色主题
    title_style = ParagraphStyle(
        'ChineseTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=20,
        spaceAfter=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#dc3545'),
        spaceBefore=10
    )
    
    # 章节标题样式
    heading_style = ParagraphStyle(
        'ChineseHeading',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=16,
        spaceAfter=10,
        spaceBefore=15,
        textColor=colors.HexColor('#dc3545'),
        borderWidth=1,
        borderColor=colors.HexColor('#dc3545'),
        borderPadding=8,
        borderRadius=5,
        backColor=colors.HexColor('#f8f9fa')
    )
    
    # 子标题样式
    subheading_style = ParagraphStyle(
        'ChineseSubheading',
        parent=styles['Heading3'],
        fontName=font_name,
        fontSize=12,
        spaceAfter=6,
        spaceBefore=10,
        textColor=colors.HexColor('#6c757d'),
        borderLeftWidth=3,
        borderLeftColor=colors.HexColor('#dc3545'),
        leftIndent=10
    )
    
    # 正文样式
    normal_style = ParagraphStyle(
        'ChineseNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        spaceAfter=6,
        textColor=colors.HexColor('#212529')
    )
    
    # 强调样式
    emphasis_style = ParagraphStyle(
        'ChineseEmphasis',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        spaceAfter=6,
        textColor=colors.HexColor('#dc3545'),
        backColor=colors.HexColor('#f8f9fa'),
        borderWidth=1,
        borderColor=colors.HexColor('#e9ecef'),
        borderPadding=5,
        borderRadius=3
    )
    
    # 标题 - 现代化设计
    meta = analysis_result.get('meta', {})
    company_name = meta.get('name', '未知公司')
    ts_code = meta.get('ts_code', '')
    
    # 添加装饰性边框
    story.append(Spacer(1, 10))
    
    # 主标题
    title = Paragraph(f"{company_name}（{ts_code}）投资分析报告", title_style)
    story.append(title)
    
    # 装饰性分隔线
    story.append(Paragraph('<hr width="80%" color="#dc3545" thickness="2"/>', normal_style))
    story.append(Spacer(1, 10))
    
    # 报告信息
    report_info = f"分析时间：{analysis_result.get('asof', '')}"
    story.append(Paragraph(report_info, emphasis_style))
    story.append(Spacer(1, 15))
    
    # 投资建议 - 从AI文本中提取
    if ai_text and "## 投资建议" in ai_text:
        investment_advice_start = ai_text.find("## 投资建议")
        next_section_start = ai_text.find("##", investment_advice_start + 1)
        if next_section_start == -1:
            investment_advice_text = ai_text[investment_advice_start:]
        else:
            investment_advice_text = ai_text[investment_advice_start:next_section_start]
        
        # 提取建议内容
        lines = investment_advice_text.split('\n')
        advice_lines = []
        for line in lines:
            line = line.strip()
            if line and line != "## 投资建议":
                advice_lines.append(line)
        
        advice_content = ' '.join(advice_lines)
        if advice_content:
            story.append(Paragraph(f"投资建议: {advice_content}", heading_style))
            story.append(Spacer(1, 12))
    
    # 五维度综合评分
    story.append(Paragraph("五维度综合评分", heading_style))
    story.append(Spacer(1, 6))
    
    # 使用AI评分（如果可用）
    if 'ai_scores' in analysis_result:
        ai_scores = analysis_result.get('ai_scores', {})
        subscores = ai_scores.get('subscores', {})
        composite_score = ai_scores.get('composite', 0)
    else:
        subscores = analysis_result.get('subscores', {})
        composite_score = analysis_result.get('composite', 0)
    
    # 综合评分
    story.append(Paragraph(f"综合评分: {composite_score:.2f}", normal_style))
    story.append(Spacer(1, 6))
    
    # 各维度评分
    if subscores:
        story.append(Paragraph("各维度评分（基于AI分析）：", normal_style))
        story.append(Spacer(1, 6))
        
        score_data = []
        score_data.append(['维度', '评分'])
        for category, score in subscores.items():
            category_name = {
                'quality': '质量',
                'growth': '增长',
                'valuation': '估值',
                'momentum': '动量',
                'risk': '风险'
            }.get(category, category)
            score_data.append([category_name, f"{score:.2f}"])
        
        score_table = Table(score_data, colWidths=[2*inch, 1*inch])
        score_table.setStyle(TableStyle([
            # 表头样式
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc3545')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            # 数据行样式
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('FONTNAME', (0, 1), (-1, -1), font_name),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            # 边框样式
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
            # 圆角效果（通过边框实现）
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#dc3545')),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 12))
    
    # 市场快照
    story.append(Paragraph("市场快照", heading_style))
    story.append(Spacer(1, 6))
    
    # 公司基本信息
    industry = meta.get('industry', 'N/A')
    area = meta.get('area', 'N/A')
    story.append(Paragraph(f"所属行业: {industry}", normal_style))
    story.append(Paragraph(f"所属地区: {area}", normal_style))
    story.append(Spacer(1, 6))
    
    # 最新行情数据
    latest_quote = analysis_result.get('evidence', {}).get('last_quote', {})
    
    # 收盘价
    close_price = latest_quote.get('close', 'N/A')
    if close_price is not None and close_price != 'N/A':
        story.append(Paragraph(f"收盘价: ¥{close_price:.2f}", normal_style))
    else:
        story.append(Paragraph("收盘价: N/A", normal_style))
    
    # PE比率
    pe_ratio = latest_quote.get('pe', 'N/A')
    if pe_ratio is not None and pe_ratio != 'N/A':
        story.append(Paragraph(f"PE: {pe_ratio:.2f}", normal_style))
    else:
        story.append(Paragraph("PE: N/A", normal_style))
    
    # PB比率
    pb_ratio = latest_quote.get('pb', 'N/A')
    if pb_ratio is not None and pb_ratio != 'N/A':
        story.append(Paragraph(f"PB: {pb_ratio:.2f}", normal_style))
    else:
        story.append(Paragraph("PB: N/A", normal_style))
    
    # 换手率
    turnover = latest_quote.get('turnover_rate', 'N/A')
    if turnover is not None and turnover != 'N/A':
        story.append(Paragraph(f"换手率: {turnover:.2f}%", normal_style))
    else:
        story.append(Paragraph("换手率: N/A", normal_style))
    
    story.append(Spacer(1, 12))
    
    # 雷达图
    try:
        radar_chart = create_radar_chart(subscores)
        story.append(Paragraph("五维度评分雷达图", heading_style))
        story.append(Spacer(1, 6))
        story.append(radar_chart)
        story.append(Spacer(1, 12))
    except Exception as e:
        print(f"生成雷达图失败: {e}")
        # 如果雷达图生成失败，添加错误提示
        story.append(Paragraph("雷达图生成失败", normal_style))
        story.append(Spacer(1, 12))
    
    # 详细分析数据
    story.append(Paragraph("详细分析数据", heading_style))
    story.append(Spacer(1, 8))
    
    evidence = analysis_result.get('evidence', {})
    
    # 质量指标分析
    quality = evidence.get('quality', {})
    if quality:
        story.append(Paragraph("质量指标分析:", subheading_style))
        quality_text = []
        if quality.get('roe') is not None:
            quality_text.append(f"ROE: {quality['roe']:.2f}%")
        if quality.get('gross_margin') is not None:
            quality_text.append(f"毛利率: {quality['gross_margin']:.2f}%")
        if quality.get('net_margin') is not None:
            quality_text.append(f"净利率: {quality['net_margin']:.2f}%")
        if quality.get('debt_to_assets') is not None:
            quality_text.append(f"资产负债率: {quality['debt_to_assets']:.2f}%")
        if quality.get('equity_multiplier') is not None:
            quality_text.append(f"权益乘数: {quality['equity_multiplier']:.2f}")
        
        if quality_text:
            story.append(Paragraph(" | ".join(quality_text), emphasis_style))
        story.append(Spacer(1, 8))
    
    # 增长指标分析
    growth = evidence.get('growth', {})
    if growth:
        story.append(Paragraph("增长指标分析:", subheading_style))
        growth_text = []
        if growth.get('revenue_yoy') is not None:
            growth_text.append(f"营收同比增长: {growth['revenue_yoy']:.2f}%")
        if growth.get('profit_yoy') is not None:
            growth_text.append(f"净利润同比增长: {growth['profit_yoy']:.2f}%")
        if growth.get('revenue_qoq') is not None:
            growth_text.append(f"营收环比增长: {growth['revenue_qoq']:.2f}%")
        if growth.get('profit_qoq') is not None:
            growth_text.append(f"净利润环比增长: {growth['profit_qoq']:.2f}%")
        
        if growth_text:
            story.append(Paragraph(" | ".join(growth_text), emphasis_style))
        story.append(Spacer(1, 8))
    
    # 估值指标分析
    valuation = evidence.get('valuation', {})
    if valuation:
        story.append(Paragraph("估值指标分析:", subheading_style))
        valuation_text = []
        if valuation.get('pe') is not None:
            valuation_text.append(f"PE: {valuation['pe']:.2f}")
        if valuation.get('pb') is not None:
            valuation_text.append(f"PB: {valuation['pb']:.2f}")
        if valuation.get('peg') is not None:
            valuation_text.append(f"PEG: {valuation['peg']:.2f}")
        if valuation.get('ps') is not None:
            valuation_text.append(f"PS: {valuation['ps']:.2f}")
        
        if valuation_text:
            story.append(Paragraph(" | ".join(valuation_text), emphasis_style))
        story.append(Spacer(1, 8))
    
    # 动量指标分析
    momentum = evidence.get('momentum', {})
    if momentum:
        story.append(Paragraph("动量指标分析:", subheading_style))
        momentum_text = []
        if momentum.get('rsi') is not None:
            momentum_text.append(f"RSI: {momentum['rsi']:.2f}")
        if momentum.get('macd') is not None:
            momentum_text.append(f"MACD: {momentum['macd']:.2f}")
        if momentum.get('bollinger_position') is not None:
            momentum_text.append(f"布林带位置: {momentum['bollinger_position']:.2f}")
        
        if momentum_text:
            story.append(Paragraph(" | ".join(momentum_text), emphasis_style))
        story.append(Spacer(1, 8))
    
    # 风险指标分析
    risk = evidence.get('risk', {})
    if risk:
        story.append(Paragraph("风险指标分析:", subheading_style))
        risk_text = []
        if risk.get('volatility') is not None:
            risk_text.append(f"波动率: {risk['volatility']:.2f}%")
        if risk.get('max_drawdown') is not None:
            risk_text.append(f"最大回撤: {risk['max_drawdown']:.2f}%")
        if risk.get('var_95') is not None:
            risk_text.append(f"VaR(95%): {risk['var_95']:.2f}%")
        if risk.get('sharpe_ratio') is not None:
            risk_text.append(f"夏普比率: {risk['sharpe_ratio']:.2f}")
        
        if risk_text:
            story.append(Paragraph(" | ".join(risk_text), emphasis_style))
        story.append(Spacer(1, 15))
    
    # AI分析报告
    if ai_text and ai_text != "AI分析暂时不可用，请稍后重试。":
        story.append(Paragraph("AI深度分析", heading_style))
        story.append(Spacer(1, 6))
        
        # 将AI文本分段
        ai_paragraphs = ai_text.split('\n\n')
        for para in ai_paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), normal_style))
                story.append(Spacer(1, 6))
    
    # 免责声明
    disclaimer = """
免责声明：
本报告基于公开数据生成，仅供研究学习使用，不构成投资建议。投资有风险，入市需谨慎。
"""
    story.append(Spacer(1, 12))
    story.append(Paragraph(disclaimer, normal_style))
    
    # 生成PDF
    doc.build(story)

def create_radar_chart(subscores: Dict) -> Image:
    """创建雷达图"""
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['PingFang SC', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans', 'Helvetica']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 准备数据
    categories = ['质量', '增长', '估值', '动量', '风险']
    values = [
        subscores.get('quality', 0),
        subscores.get('growth', 0),
        subscores.get('valuation', 0),
        subscores.get('momentum', 0),
        subscores.get('risk', 0)
    ]
    
    # 创建雷达图
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
    
    # 计算角度
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    values += values[:1]  # 闭合图形
    angles += angles[:1]
    
    # 绘制雷达图
    ax.plot(angles, values, 'o-', linewidth=2, label='评分')
    ax.fill(angles, values, alpha=0.25)
    
    # 设置标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(-1, 1)
    ax.set_yticks([-1, -0.5, 0, 0.5, 1])
    ax.set_yticklabels(['-1', '-0.5', '0', '0.5', '1'])
    ax.grid(True)
    
    plt.title('五维度评分雷达图', size=16, y=1.1)
    plt.tight_layout()
    
    # 保存到内存
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    # 创建ReportLab图片对象
    img = Image(img_buffer)
    img.drawHeight = 4*inch
    img.drawWidth = 4*inch
    
    return img
