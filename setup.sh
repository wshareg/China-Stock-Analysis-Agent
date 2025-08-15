#!/bin/bash

# 股票分析工具 - 安全设置脚本
echo "🔒 股票分析工具 - 安全配置"
echo "================================"

# 检查是否已有 .env 文件
if [ -f ".env" ]; then
    echo "⚠️  发现现有的 .env 文件"
    read -p "是否要备份并重新创建？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
        echo "✅ 已备份到 .env.backup.$(date +%Y%m%d_%H%M%S)"
    else
        echo "❌ 取消操作"
        exit 1
    fi
fi

# 复制示例文件
if [ ! -f ".env.example" ]; then
    echo "❌ 未找到 .env.example 文件"
    exit 1
fi

cp .env.example .env
echo "✅ 已创建 .env 文件"

# 提示用户配置
echo ""
echo "📝 请按照以下步骤配置您的 API 密钥："
echo ""
echo "1. 编辑 .env 文件："
echo "   nano .env"
echo "   或"
echo "   code .env"
echo ""
echo "2. 替换以下占位符："
echo "   - TUSHARE_TOKEN=your_actual_tushare_token_here"
echo "   - OPENAI_API_KEY=your_actual_openai_api_key_here"
echo ""
echo "3. 保存文件并退出编辑器"
echo ""
echo "🔗 获取 API 密钥："
echo "   - TuShare Pro: https://tushare.pro/"
echo "   - OpenAI: https://platform.openai.com/"
echo ""

# 检查 .gitignore
if grep -q "\.env" .gitignore; then
    echo "✅ .env 文件已在 .gitignore 中"
else
    echo "⚠️  警告：.env 文件可能没有被 .gitignore 忽略"
fi

echo ""
echo "🎯 配置完成后，运行以下命令启动应用："
echo "   streamlit run apps/streamlit_app.py"
echo ""
echo "📖 更多安全信息请查看 SECURITY.md"
