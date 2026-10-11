#!/bin/bash

# 文芽 - 开发环境启动脚本

echo "🌱 文芽 - 未成年人 AI 写作练习平台"
echo "=================================="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 Python 3，请先安装"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 需要 Node.js，请先安装"
    exit 1
fi

# 检查 PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️  未检测到 PostgreSQL，请确保已安装并运行"
fi

echo ""
echo "📦 正在安装后端依赖..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "📦 正在安装前端依赖..."
cd frontend
npm install
cd ..

echo ""
echo "🗄️  正在初始化数据库..."
python init_db.py

echo ""
echo "✅ 安装完成！"
echo ""
echo "启动方式："
echo "  后端：source venv/bin/activate && python app.py"
echo "  前端：cd frontend && npm run dev"
echo ""
echo "访问地址：http://localhost:3000"
