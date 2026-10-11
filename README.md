# 文芽 - 未成年人 AI 写作练习平台

## 项目简介

"文芽"是一个面向 6-18 岁未成年人的 AI 辅助写作练习网页端应用。核心功能包括：

- 🤖 **专属 AI 写作教练**：基于三层记忆架构，提供个性化写作指导
- 📊 **七维度评分系统**：任务、主题、内容、结构、语言、文体、思维
- 📈 **成长排行榜**：综合榜、进步榜、维度榜，避免焦虑的设计
- 📚 **作品社区**：公开展示与交流，分级审核机制
- 🔒 **合规保护**：监护人验证、内容安全过滤、全程留痕

## 技术栈

### 后端
- **框架**: Flask 3.0
- **数据库**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **认证**: Flask-Login
- **限流**: Flask-Limiter
- **AI 集成**: OpenAI 兼容 API

### 前端
- **框架**: Vue 3 + Vite
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **UI**: Tailwind CSS
- **图表**: ECharts 5
- **HTTP**: Axios

## 项目结构

```
wenya/
├── app.py                 # Flask 应用入口
├── config.py              # 配置模块
├── requirements.txt       # Python 依赖
├── models/                # 数据模型
│   ├── __init__.py
│   ├── user.py           # 用户、监护人、用户画像
│   ├── writing.py        # 作文、草稿、评分
│   ├── ai_memory.py      # AI 记忆、会话
│   ├── ranking.py        # 排行榜记录
│   ├── community.py      # 社区作品、评论
│   └── compliance.py     # 合规日志、算法日志
├── routes/               # 路由蓝图
│   ├── auth.py           # 认证路由
│   ├── api.py            # 通用 API
│   ├── writing.py        # 写作路由
│   ├── ranking.py        # 排行榜路由
│   └── community.py      # 社区路由
├── services/             # 业务服务
│   ├── ai_service.py     # AI 评分、对话服务
│   └── content_safe.py   # 内容安全过滤
└── frontend/             # Vue 3 前端
    ├── src/
    │   ├── main.js
    │   ├── App.vue
    │   ├── api.js
    │   ├── router.js
    │   ├── stores/
    │   ├── views/
    │   └── styles/
    ├── package.json
    └── vite.config.js
```

## 快速开始

### 1. 环境准备

```bash
# Python 3.9+
# Node.js 18+
# PostgreSQL 14+
```

### 2. 后端安装

```bash
cd wenya

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 配置数据库、AI API 密钥等

# 初始化数据库
flask db upgrade

# 启动开发服务器
python app.py
```

### 3. 前端安装

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:3000

## 核心功能说明

### AI 评分系统

七维度评分体系，根据学段自动调整权重：

| 维度 | 小学 | 初中 | 高中 |
|------|------|------|------|
| 任务完成 | 15% | 10% | 10% |
| 主题立意 | 10% | 15% | 20% |
| 内容充实 | 20% | 20% | 20% |
| 结构逻辑 | 15% | 15% | 15% |
| 语言表达 | 25% | 20% | 15% |
| 文体规范 | 10% | 10% | 10% |
| 思维深度 | 5%  | 10% | 10% |

### 三层记忆架构

1. **L1 写作画像层**：学段、优势/弱势、偏好等长期记忆
2. **L2 写作知识库层**：素材、范文、修改历史
3. **L3 会话上下文层**：当前任务的对话历史

### 合规保护机制

- ✅ 监护人手机短信验证
- ✅ AI 输出内容安全过滤
- ✅ 作品分级展示（小学仅同年级可见）
- ✅ 全程日志留痕（6 个月）
- ✅ 算法备案透明化

## 环境变量

```bash
# .env.example

# Flask
SECRET_KEY=your-secret-key
FLASK_ENV=development

# 数据库
DATABASE_URL=postgresql://postgres:password@localhost:5432/wenya

# AI
AI_API_BASE=https://api.openai.com/v1
AI_API_KEY=your-api-key
AI_MODEL=gpt-4

# 内容安全
CONTENT_SAFE_API_KEY=your-bce-api-key
CONTENT_SAFE_ENABLED=false

# 合规公示
ICP_NUMBER=京 ICP 备 XXXXXXXX 号
ALGORITHM_NUMBER=算法备案编号
```

## API 文档

### 认证
- `POST /api/auth/register` - 注册（需监护人验证）
- `POST /api/auth/login` - 登录
- `POST /api/auth/logout` - 登出
- `GET /api/auth/me` - 获取当前用户

### 写作
- `POST /api/writing` - 创建作文
- `GET /api/writing/:id` - 获取作文详情
- `PUT /api/writing/:id` - 更新作文
- `POST /api/writing/:id/submit` - 提交评分
- `POST /api/writing/:id/ai-chat` - AI 对话

### 排行榜
- `GET /api/ranking/overall` - 综合榜
- `GET /api/ranking/progress` - 进步榜
- `GET /api/ranking/dimension/:dim` - 维度榜
- `GET /api/ranking/my-growth-curve` - 成长曲线
- `POST /api/ranking/toggle-visibility` - 退出排行榜

### 社区
- `GET /api/community/works` - 作品列表
- `GET /api/community/works/:id` - 作品详情
- `POST /api/community/works/:id/like` - 点赞
- `POST /api/community/works/:id/comment` - 评论

## 合规说明

### ICP 备案
网站上线前需在工信部完成 ICP 备案，备案编号需公示于页脚。

### 算法备案
根据《生成式人工智能服务管理暂行办法》，需在网信办完成：
1. 深度合成服务算法备案
2. 大模型上线备案

### 未成年人保护
- 不满 14 周岁需监护人明确同意
- 同意记录保存至年满 14 周岁后 3 年
- 提供一键退出排行榜功能
- 小学阶段作品不公开排名

## 开发团队

最小团队配置（4 人）：
- 全栈开发（1-2 人）
- AI/Prompt 工程（1 人）
- UI/UX 设计（1 人）
- 产品/合规（1 人）

## 许可证

MIT License

## 参考资料

- 《中小学生成式人工智能使用指南（2025 年版）》
- 《人工智能拟人化互动服务管理暂行办法》
- 《生成式人工智能服务管理暂行办法》
- 《未成年人网络保护条例》
