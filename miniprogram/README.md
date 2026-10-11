# 文芽 - 微信小程序

## 项目简介

"文芽"微信小程序版本，面向 6-18 岁未成年人的 AI 辅助写作练习应用。

## 快速开始

### 1. 安装微信开发者工具

下载地址：https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html

### 2. 导入项目

1. 打开微信开发者工具
2. 选择"导入项目"
3. 选择 `miniprogram` 目录
4. 填写 AppID（测试可选"测试号"）

### 3. 配置后端 API

在 `utils/config.js` 中修改 API 地址：

```javascript
module.exports = {
  API_BASE_URL: 'https://your-backend.com/api',
  // ...
}
```

### 4. 后端 CORS 配置

确保 Flask 后端允许小程序域名访问：

```python
# config.py
CORS_ORIGINS = 'https://servicewechat.com,your-backend.com'
```

## 项目结构

```
miniprogram/
├── app.js                 # 小程序入口
├── app.json               # 小程序配置
├── app.wxss               # 全局样式
├── sitemap.json           # 索引配置
├── project.config.json    # 项目配置
├── utils/
│   ├── api.js            # API 请求封装（已集成日志）
│   ├── auth.js           # 认证工具
│   ├── config.js         # 配置常量
│   ├── util.js           # 通用工具函数
│   └── logger.js         # 运行日志工具（新增）
├── pages/
│   ├── index/            # 首页
│   ├── writing/          # 写作页
│   ├── ranking/          # 排行榜
│   ├── community/        # 社区
│   ├── profile/          # 个人中心
│   ├── login/            # 登录
│   ├── register/         # 注册
│   ├── writing-detail/   # 作文详情
│   ├── settings/         # 设置
│   └── logs/             # 运行日志（新增）
├── images/               # 图片资源
└── README.md             # 项目说明
```

## 核心功能

- ✅ 微信登录 + 手机号验证
- ✅ AI 写作指导
- ✅ 七维度评分
- ✅ 成长曲线图表
- ✅ 排行榜
- ✅ 作品社区
- ✅ 监护人验证
- ✅ 运行日志记录（新增）

## 运行日志功能

小程序已集成运行日志记录功能，仅记录错误和警告级别的日志。

### 查看日志
1. 进入"我的"页面
2. 点击"运行日志"菜单项（仅开发模式可见）
3. 查看日志列表和详细信息

### 日志级别
- **error**: API 请求失败、未处理的异常
- **warning**: API 业务错误、登录态过期

### 导出日志
用户可通过"导出"按钮将日志复制到剪贴板，便于反馈给开发者。

详细说明请参考 `LOGGER_GUIDE.md`

## 开发注意事项

1. **网络请求**：必须在微信公众平台配置合法域名
2. **登录流程**：使用微信登录 + 后端 JWT 认证
3. **内容安全**：调用微信内容安全 API
4. **图表渲染**：使用 echarts-for-weixin
5. **日志记录**：仅记录错误和警告，避免日志过多影响性能

## 部署上线

1. 在微信公众平台提交审核
2. 选择"教育 - 在线教育"类目
3. 提供未成年人保护相关说明
4. 配置生产环境 API 地址
5. 关闭 DEBUG 模式（`config.DEBUG = false`）

## 文档导航

- `README.md` - 项目说明（本文件）
- `DEVELOPMENT_GUIDE.md` - 完整开发指南
- `API_ADAPTER.md` - 后端 API 适配指南
- `CONVERSION_SUMMARY.md` - 转换总结
- `LOGGER_GUIDE.md` - 运行日志功能说明

## 技术支持

如有问题，请联系：support@wenya.com
