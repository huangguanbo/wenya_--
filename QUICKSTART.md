# 文芽项目快速开始指南

## 📋 项目概述

**文芽** 是一个面向 6-18 岁未成年人的 AI 辅助写作练习网页端应用，完全免费，纯公共教育工具属性。

### 核心特色

1. **专属 AI 写作教练** - 基于三层记忆架构，提供个性化指导
2. **七维度评分系统** - 任务、主题、内容、结构、语言、文体、思维
3. **防焦虑排行榜** - 只展示进步和前 50%，保护学生自尊心
4. **合规保护机制** - 监护人验证、内容过滤、全程留痕

## 🚀 快速启动（5 分钟）

### 前置要求

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+

### 步骤 1：克隆项目

```bash
cd /path/to/wenya
```

### 步骤 2：配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库和 AI API 密钥
```

### 步骤 3：安装依赖并启动

```bash
# 方式一：使用启动脚本
chmod +x setup.sh
./setup.sh

# 方式二：手动安装
# 后端
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py

# 前端
cd frontend
npm install
```

### 步骤 4：启动服务

```bash
# 终端 1：启动后端（端口 5000）
source venv/bin/activate
python app.py

# 终端 2：启动前端（端口 3000）
cd frontend
npm run dev
```

访问 http://localhost:3000

## 📁 文件结构

```
wenya/
├── app.py                 # Flask 应用入口
├── config.py              # 配置管理
├── init_db.py             # 数据库初始化
├── requirements.txt       # Python 依赖
├── .env.example          # 环境变量示例
├── setup.sh              # 启动脚本
│
├── models/               # 数据模型
│   ├── user.py          # 用户、监护人、画像
│   ├── writing.py       # 作文、草稿、评分
│   ├── ai_memory.py     # AI 记忆、会话
│   ├── ranking.py       # 排行榜
│   ├── community.py     # 社区作品
│   └── compliance.py    # 合规日志
│
├── routes/               # API 路由
│   ├── auth.py          # 认证
│   ├── writing.py       # 写作
│   ├── ranking.py       # 排行榜
│   └── community.py     # 社区
│
├── services/             # 业务服务
│   ├── ai_service.py    # AI 评分/对话
│   └── content_safe.py  # 内容安全
│
└── frontend/             # Vue 3 前端
    ├── src/
    │   ├── views/       # 页面组件
    │   ├── stores/      # 状态管理
    │   └── styles/      # 样式
    └── package.json
```

## 🔑 核心功能演示

### 1. 用户注册

```bash
POST /api/auth/register
{
  "username": "xiaoming",
  "password": "password123",
  "grade": 5,
  "birth_date": "2015-01-01",
  "guardian_name": "小明爸爸",
  "guardian_phone": "13800138000",
  "guardian_relationship": "父子",
  "guardian_verification_code": "123456"
}
```

### 2. 创建作文

```bash
POST /api/writing
Headers: Cookie: session=xxx
{
  "title": "我的梦想",
  "prompt": "请描述你的梦想",
  "content": "每个人都有一个梦想..."
}
```

### 3. AI 对话

```bash
POST /api/writing/1/ai-chat
{
  "message": "帮我看看这个开头怎么写更好",
  "session_type": "writing_guidance"
}
```

### 4. 提交评分

```bash
POST /api/writing/1/submit
# 返回七维度评分和 AI 评语
```

### 5. 查看排行榜

```bash
GET /api/ranking/overall?grade=5
# 返回同年级综合排行榜（前 50%）
```

## 🎨 前端页面

| 路由 | 页面 | 功能 |
|------|------|------|
| `/` | 首页 | 数据统计、成长曲线、快速入口 |
| `/login` | 登录 | 用户登录 |
| `/register` | 注册 | 用户注册 + 监护人验证 |
| `/writing` | 写作 | AI 对话 + 富文本编辑器 |
| `/writings` | 作文列表 | 查看历史作文 |
| `/ranking` | 排行榜 | 综合榜/进步榜/维度榜 |
| `/community` | 社区 | 作品广场 |
| `/profile` | 个人中心 | 写作画像、统计 |
| `/settings` | 设置 | 隐私、监护人、合规 |

## 🛡️ 合规特性

### 监护人验证

```python
# 注册时必须提供监护人信息
# 通过短信验证码验证监护人同意
# 同意记录保存至年满 14 周岁后 3 年
```

### 内容安全

```python
# 所有用户输入和 AI 输出都经过内容安全过滤
# 敏感词检测 + 第三方 API 审核
# 不合规内容自动替换为安全回复
```

### 数据保护

```python
# 所有操作记录 ComplianceLog（6 个月）
# AI 决策记录 AlgorithmLog（永久）
# 支持一键导出供网信办审计
```

## 📊 API 接口

### 认证
- `POST /api/auth/register` - 注册
- `POST /api/auth/login` - 登录
- `POST /api/auth/logout` - 登出
- `GET /api/auth/me` - 获取当前用户

### 写作
- `POST /api/writing` - 创建作文
- `GET /api/writing/:id` - 获取作文
- `PUT /api/writing/:id` - 更新作文
- `POST /api/writing/:id/submit` - 提交评分
- `POST /api/writing/:id/ai-chat` - AI 对话

### 排行榜
- `GET /api/ranking/overall` - 综合榜
- `GET /api/ranking/progress` - 进步榜
- `GET /api/ranking/dimension/:dim` - 维度榜
- `GET /api/ranking/my-growth-curve` - 成长曲线

### 社区
- `GET /api/community/works` - 作品列表
- `GET /api/community/works/:id` - 作品详情
- `POST /api/community/works/:id/like` - 点赞
- `POST /api/community/works/:id/comment` - 评论

## 🐛 常见问题

### Q: 数据库连接失败？
```bash
# 检查 PostgreSQL 是否运行
pg_isready

# 创建数据库
createdb wenya
```

### Q: AI API 无法调用？
```bash
# 检查 .env 配置
# AI_API_KEY=your-key-here
# AI_API_BASE=https://api.openai.com/v1
```

### Q: 前端无法访问后端？
```bash
# 检查 vite.config.js 代理配置
# proxy: { '/api': 'http://localhost:5000' }
```

## 📝 下一步

1. **配置 AI 服务** - 在 `.env` 中配置真实的 AI API 密钥
2. **配置内容安全** - 申请百度/阿里内容安全 API
3. **配置短信服务** - 申请阿里云/腾讯云短信服务
4. **申请合规资质** - ICP 备案、算法备案
5. **部署上线** - 参考 ARCHITECTURE.md 部署文档

## 📚 文档

- [README.md](README.md) - 项目说明
- [ARCHITECTURE.md](ARCHITECTURE.md) - 技术架构
- [.env.example](.env.example) - 环境变量说明

## 🎯 MVP 范围

一个月开发周期的 MVP 功能：
- ✅ 用户注册登录（含监护人验证）
- ✅ 写作工作台（AI 对话 + 编辑器）
- ✅ AI 评分系统（七维度）
- ✅ 综合排行榜
- ✅ 个人数据中心
- ⏸️ 社区功能（简化版）
- ⏸️ 进步排行榜（延后）

## 💡 提示

- 开发环境使用 `FLASK_ENV=development` 开启调试模式
- 前端使用 `npm run dev` 开启热重载
- 数据库变更使用 `python init_db.py` 重新初始化
- API 测试推荐使用 Postman 或 Insomnia
