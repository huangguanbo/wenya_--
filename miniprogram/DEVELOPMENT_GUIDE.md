# 文芽 - 微信小程序开发指南

## 项目结构

```
miniprogram/
├── app.js                    # 小程序入口文件
├── app.json                  # 小程序配置文件
├── app.wxss                  # 全局样式文件
├── project.config.json       # 微信开发者工具项目配置
├── sitemap.json              # 索引配置
├── utils/                    # 工具模块
│   ├── api.js               # API 请求封装
│   ├── auth.js              # 认证工具
│   ├── config.js            # 配置常量
│   └── util.js              # 通用工具函数
├── pages/                    # 页面目录
│   ├── index/               # 首页
│   ├── writing/             # 写作页
│   ├── ranking/             # 排行榜
│   ├── community/           # 社区
│   ├── profile/             # 个人中心
│   ├── login/               # 登录
│   ├── register/            # 注册
│   ├── writing-detail/      # 作文详情
│   └── settings/            # 设置
├── components/               # 自定义组件（待扩展）
└── images/                   # 图片资源
```

## 快速开始

### 1. 安装微信开发者工具

下载地址：https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html

### 2. 导入项目

1. 打开微信开发者工具
2. 选择"导入项目"
3. 选择 `miniprogram` 目录
4. 填写 AppID（测试可选择"测试号"）

### 3. 准备图标资源

参考 `images/README.md` 准备 TabBar 图标文件。

### 4. 配置后端 API

编辑 `utils/config.js`：

```javascript
module.exports = {
  // 开发环境（本地）
  API_BASE_URL: 'http://192.168.1.100:5000/api',
  
  // 生产环境
  // API_BASE_URL: 'https://api.wenya.com/api',
  
  TIMEOUT: 30000,
  DEBUG: true
}
```

### 5. 配置微信公众平台

#### 5.1 配置服务器域名

登录 [微信公众平台](https://mp.weixin.qq.com/) → 开发 → 开发管理 → 开发设置 → 服务器域名

添加以下域名：
- `request` 合法域名：`https://api.wenya.com`

#### 5.2 配置业务域名（如需 H5 嵌套）

如有 H5 页面嵌套需求，需配置业务域名。

### 6. 后端 CORS 配置

确保 Flask 后端允许小程序访问：

```python
# config.py
CORS_ORIGINS = 'https://servicewechat.com,your-backend.com'
```

## 核心功能说明

### 登录认证

小程序采用微信登录 + 后端 JWT 认证：

1. **微信一键登录**: 调用 `wx.login()` 获取 code，发送到后端换取 token
2. **手机号登录**: 输入手机号 + 验证码登录
3. **注册**: 需监护人手机号验证

### API 调用

所有 API 请求通过 `utils/api.js` 统一封装：

```javascript
const api = require('../../utils/api')

// GET 请求
const res = await api.get('/writing')

// POST 请求
const res = await api.post('/writing', { title, content })
```

### 状态管理

使用 `app.globalData` 存储全局状态：

```javascript
const app = getApp()

// 获取用户信息
const user = app.globalData.user

// 获取 token
const token = app.globalData.token
```

## 页面说明

### 首页 (index)
- 欢迎信息
- 统计数据展示
- 快速入口
- 成长曲线
- 最近作品

### 写作页 (writing)
- 标题和编辑器
- 自动保存草稿
- AI 对话面板
- 提交评分

### 排行榜 (ranking)
- 综合榜
- 进步榜
- 维度榜
- 我的排名

### 社区 (community)
- 作品列表
- 筛选排序
- 点赞互动

### 个人中心 (profile)
- 用户信息
- 统计数据
- 功能菜单
- 设置入口

## 开发注意事项

### 1. 网络请求
- 必须在微信公众平台配置合法域名
- 开发期间可在开发者工具中勾选"不校验合法域名"
- 请求超时时间设置为 30 秒

### 2. 登录流程
```
用户打开小程序 → 检查本地 token → 有效则直接登录
                              ↓ 无效
                        调用 wx.login() → 获取 code
                              ↓
                        发送到后端 /auth/wx-login
                              ↓
                        获取 token 和用户信息
                              ↓
                        存储到本地和 globalData
```

### 3. 内容安全

小程序内用户生成内容需调用微信内容安全 API：

```javascript
// 文本内容安全检测
wx.security.msgSecurityCheck({
  content: '待检测内容',
  success: (res) => {
    if (res.result === 1) {
      // 内容正常
    } else {
      // 内容违规
    }
  }
})
```

### 4. 图表渲染

如需使用 ECharts，需引入 [echarts-for-weixin](https://github.com/ecomfe/echarts-for-weixin)：

```bash
# 下载 echarts-for-weixin 到 components 目录
```

### 5. 分享功能

```javascript
// 在页面中定义
onShareAppMessage() {
  return {
    title: '文芽 - 来看看我的作文',
    path: '/pages/writing-detail/writing-detail?id=123'
  }
}

// 触发分享
wx.showShareMenu({
  withShareTicket: true
})
```

## 调试技巧

### 1. 开启调试模式

在 `utils/config.js` 中设置 `DEBUG: true`，会输出详细日志。

### 2. 使用真机调试

在开发者工具中点击"真机调试"，扫码在手机上测试。

### 3. 性能分析

使用开发者工具的"性能面板"分析：
- 页面渲染时间
- 网络请求耗时
- 内存占用

### 4. 常见错误排查

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 网络请求失败 | 域名未配置 | 在 MP 后台配置服务器域名 |
| 登录态过期 | token 失效 | 清除本地存储，重新登录 |
| 页面未找到 | 路径错误 | 检查 app.json 中页面路径 |
| 样式不生效 | WXSS 语法错误 | 检查选择器和单位 |

## 部署上线

### 1. 代码上传

在微信开发者工具中点击"上传"，填写版本号和备注。

### 2. 提交审核

登录微信公众平台 → 版本管理 → 提交审核

### 3. 选择类目

选择"教育 - 在线教育"类目，需提供：
- 《增值电信业务经营许可证》
- 未成年人保护相关说明

### 4. 发布上线

审核通过后，在后台点击"发布"。

## 扩展开发

### 添加新页面

1. 在 `pages/` 目录创建页面文件夹
2. 在 `app.json` 的 `pages` 数组中添加路径
3. 创建 `.wxml`, `.js`, `.wxss`, `.json` 四个文件

### 添加自定义组件

1. 在 `components/` 目录创建组件
2. 在页面的 `.json` 中引入组件
3. 在 `.wxml` 中使用组件

### 添加云开发

如需使用微信云开发：
1. 在 `app.json` 中添加 `"cloud": true`
2. 在 `app.js` 中调用 `wx.cloud.init()`
3. 使用云函数和云数据库

## 参考资料

- [微信小程序官方文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
- [微信开放社区](https://developers.weixin.qq.com/community/)
- [小程序设计指南](https://developers.weixin.qq.com/miniprogram/design/)

## 技术支持

如有问题，请联系：support@wenya.com
