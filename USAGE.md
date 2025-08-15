# A股价值分析器使用说明

## 🚀 快速开始

### 1. 环境准备

确保您已经安装了 Python 3.8+ 并激活了虚拟环境：

```bash
# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量模板并配置您的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入您的 API 密钥：

```env
TUSHARE_TOKEN=您的_tushare_pro_token
OPENAI_API_KEY=您的_openai_api_key
OPENAI_MODEL=gpt-4o
```

### 3. 启动应用

```bash
streamlit run apps/streamlit_app.py
```

应用将在 http://localhost:8501 启动。

## 📊 功能说明

### 主要功能

1. **多维度量化分析**
   - 质量（ROE、毛利率、净利率等）
   - 增长（营收/净利润同比增长）
   - 估值（PE、PB、PEG等）
   - 动量（3/6/12个月收益率）
   - 风险（波动率、最大回撤等）

2. **AI 深度分析**
   - 基于量化结果生成结构化研报
   - 包含8个分析维度
   - 提供投资建议和操作策略

3. **可视化报告**
   - 雷达图展示五维评分
   - 一键导出 PDF 报告

### 使用步骤

1. **输入股票代码**
   - 格式：`600519.SH`（上海）、`000001.SZ`（深圳）
   - 支持 A 股全市场

2. **设置分析参数**
   - 起始日期：默认为 2018年1月1日
   - 启用 AI 分析：勾选后生成深度研报

3. **查看分析结果**
   - 综合评分和投资建议
   - 各维度详细指标
   - AI 分析报告（如启用）

4. **导出报告**
   - 点击"导出 PDF 报告"下载完整分析报告

## 🔧 技术架构

### 核心模块

- `src/config.py` - 配置管理
- `src/data.py` - 数据获取（TuShare API）
- `src/indicators.py` - 指标计算
- `src/analysis.py` - 分析逻辑
- `src/ai.py` - AI 分析（OpenAI API）
- `src/report.py` - 报告生成

### 数据来源

- **TuShare Pro**：股票基础数据、财务数据、行情数据
- **OpenAI API**：AI 分析报告生成

## ⚠️ 注意事项

### API 权限

1. **TuShare Pro**
   - 需要注册 TuShare Pro 账户
   - 获取 API Token
   - 确保有足够的数据访问权限

2. **OpenAI API**
   - 需要 OpenAI 账户和 API Key
   - 建议使用 GPT-4o 模型以获得最佳效果

### 使用限制

- 本工具仅供研究学习使用
- 不构成投资建议
- 请遵守相关 API 的使用条款

## 🐛 常见问题

### Q: TuShare API 权限不足怎么办？
A: 请检查您的 TuShare Pro 账户权限，确保有足够的数据访问额度。

### Q: AI 分析失败怎么办？
A: 检查 OpenAI API Key 是否正确配置，确保账户有足够的余额。

### Q: 如何获取更多股票数据？
A: 升级 TuShare Pro 账户或联系客服获取更高权限。

### Q: 报告生成失败怎么办？
A: 确保已安装所有依赖包，特别是 matplotlib 和 reportlab。

## 📞 技术支持

如有问题，请检查：
1. 环境变量配置是否正确
2. 网络连接是否正常
3. API 密钥是否有效
4. 依赖包是否完整安装

---

**免责声明**：本工具仅供学术研究和技术交流使用，不构成任何投资建议。投资有风险，入市需谨慎。
