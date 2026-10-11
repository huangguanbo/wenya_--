# 🎨 文芽精美 UI 界面使用说明

## 📁 文件位置

主界面文件：`frontend/dashboard.html`

## 🚀 快速预览

### 方式 1：直接打开（推荐）
直接在浏览器中打开文件：
```bash
open frontend/dashboard.html
```

### 方式 2：HTTP 服务器
```bash
# 已启动服务器，访问：
http://localhost:8080/frontend/dashboard.html
```

### 方式 3：Python 内置服务器
```bash
cd frontend
python -m http.server 3000
# 访问 http://localhost:3000/dashboard.html
```

## 🎯 功能说明

### 1. 仪表盘 (Dashboard)
- **统计卡片**：显示总交互次数、记忆片段数、作文数量、平均评分
- **成长曲线图**：展示写作能力随时间的变化趋势
- **七维度雷达图**：可视化各项能力分布
- **最近记忆**：快速查看最新的记忆片段

### 2. 记忆管理 (Memory Management)
- **搜索功能**：按关键词搜索记忆内容
- **类别过滤**：按写作画像/交互记录/知识库/反馈筛选
- **记忆列表**：显示所有记忆片段，带重要性评分
- **类别分布**：饼图展示各类别占比
- **管理操作**：清空记忆片段/画像/全部

### 3. AI 对话 (AI Chat)
- **聊天界面**：气泡式对话 UI
- **快速提问**：预设常见问题一键提问
- **记忆增强**：显示当前记忆状态
- **清空对话**：一键清除对话历史

### 4. 设置 (Settings)
- **AI 提供商**：选择 OpenAI/Claude/通义千问等
- **API Key**：配置你的 API 密钥
- **模型名称**：自定义模型（如 gpt-4o）
- **功能开关**：启用/禁用记忆和缓存

## 🎨 设计特色

### 配色方案
- **主色**：紫色到蓝色渐变 (#667eea → #764ba2)
- **成功**：绿色 (#10b981)
- **警告**：黄色 (#f59e0b)
- **危险**：红色 (#ef4444)

### 视觉效果
- ✨ **毛玻璃效果**：半透明卡片带背景模糊
- 🌊 **渐变背景**：现代感十足的渐变色
- 🎭 **悬停动画**：卡片上浮效果
- 📱 **响应式设计**：完美适配各种屏幕
- 🎪 **加载动画**：旋转加载器
- 💬 **聊天气泡**：用户/AI 不同样式

### 交互体验
- 🍞 **Toast 通知**：底部弹出提示
- 📊 **ECharts 图表**：专业的数据可视化
- ⚡ **快速切换**：无刷新视图切换
- 🔍 **实时搜索**：即时过滤结果

## 📱 响应式断点

- **手机**：< 640px
- **平板**：640px - 1024px
- **桌面**：> 1024px

## 🔗 API 端点

界面已集成以下 API：

```javascript
GET  /api/memory/stats          // 获取统计数据
GET  /api/memory/profile        // 获取用户画像
GET  /api/memory/fragments      // 检索记忆片段
POST /api/memory/clear          // 清空记忆
POST /api/writing/ai-chat       // AI 对话
```

## 🛠️ 自定义修改

### 修改配色
编辑 `tailwind.config` 中的颜色配置：
```javascript
colors: {
  primary: { /* 修改主色 */ },
  success: '#10b981',  // 修改成功色
}
```

### 修改渐变
编辑 `.gradient-bg` 类：
```css
.gradient-bg {
  background: linear-gradient(135deg, #你的颜色 1, #你的颜色 2);
}
```

### 添加新视图
1. 在 HTML 中添加新视图区块：
```html
<div id="new-view" class="view-section hidden">
  <!-- 内容 -->
</div>
```

2. 在导航栏添加按钮：
```html
<button onclick="switchView('new')" class="nav-btn">
  新视图
</button>
```

## 📊 图表配置

### 成长曲线图
位于 `renderGrowthChart()` 函数，可修改：
- X 轴数据（月份）
- Y 轴范围（分数范围）
- 系列数据（分数数组）

### 雷达图
位于 `renderRadarChart()` 函数，可修改：
- 维度名称（indicator）
- 分数数据（value 数组）

## 🎯 使用技巧

### 快捷键
- **Enter**：在搜索框/聊天框发送
- **Esc**：关闭 Toast（未来功能）

### 数据刷新
- 切换视图时自动刷新数据
- 手动刷新页面获取最新数据

### 本地存储
设置会保存在 `localStorage`：
- `ai_provider`：AI 提供商
- `ai_model`：模型名称
- `ai_memory`：记忆开关
- `ai_cache`：缓存开关

## 🐛 故障排查

### 图表不显示
检查 ECharts CDN 是否可访问，或改用本地文件。

### API 调用失败
确认后端服务已启动，检查浏览器控制台错误。

### 样式异常
检查 Tailwind CDN 是否加载成功。

## 📝 更新日志

### v1.0 (2026-10-04)
- ✨ 初始版本发布
- 🎨 精美 UI 设计
- 📊 数据可视化图表
- 💬 AI 对话界面
- 🧠 记忆管理功能
- ⚙️ 设置面板

## 🎓 学习资源

- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [ECharts 文档](https://echarts.apache.org/zh/index.html)
- [Font Awesome 图标](https://fontawesome.com/icons)

---

**享受这个精美的 UI 界面吧！** 🎉
