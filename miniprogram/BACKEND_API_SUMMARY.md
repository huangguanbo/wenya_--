# 微信小程序前端后端 API 调用汇总

> 统计范围：`miniprogram/` 目录下前端源码（页面 + `utils`）  
> 统计口径：仅包含实际发起网络请求的后端 API；不含页面跳转 URL。  
> 基础地址：`API_BASE_URL`（见 `miniprogram/utils/config.js`，默认示例值为 `https://your-backend.com/api`）。

---

## 1) 认证与账号

| 方法 | 接口（相对 `API_BASE_URL`） | 典型完整路径示例 | 主要调用位置 | 用途 | 主要请求参数 |
|---|---|---|---|---|---|
| POST | `/auth/wx-login` | `/api/auth/wx-login` | `pages/login/login.js`、`utils/auth.js` | 微信登录换取业务 token | `code` |
| POST | `/auth/send-code` | `/api/auth/send-code` | `pages/login/login.js`、`pages/register/register.js` | 发送手机验证码 | `phone` |
| POST | `/auth/login` | `/api/auth/login` | `pages/login/login.js`、`utils/auth.js` | 手机号 + 验证码登录 | `phone`、`verification_code` |
| POST | `/auth/register` | `/api/auth/register` | `pages/register/register.js`、`utils/auth.js` | 注册账号（含监护人信息） | `username`、`nickname`、`grade`、`guardian`（含 `phone`、`verification_code`）等 |

---

## 2) 首页与用户统计

| 方法 | 接口（相对 `API_BASE_URL`） | 典型完整路径示例 | 主要调用位置 | 用途 | 主要请求参数 |
|---|---|---|---|---|---|
| GET | `/stats` | `/api/stats` | `pages/index/index.js`、`pages/profile/profile.js` | 获取用户统计信息（总写作数、均分等） | 无 |
| GET | `/ranking/my-growth-curve` | `/api/ranking/my-growth-curve` | `pages/index/index.js` | 首页成长曲线 | `days`（示例：`30`） |

---

## 3) 写作相关

| 方法 | 接口（相对 `API_BASE_URL`） | 典型完整路径示例 | 主要调用位置 | 用途 | 主要请求参数 |
|---|---|---|---|---|---|
| GET | `/writing` | `/api/writing` | `pages/index/index.js` | 获取最近作品列表 | `page`、`per_page` |
| POST | `/writing` | `/api/writing` | `pages/writing/writing.js` | 创建作文草稿 | `title`、`content` |
| GET | `/writing/{id}` | `/api/writing/123` | `pages/writing/writing.js`、`pages/writing-detail/writing-detail.js` | 获取作文详情 | 路径参数 `id` |
| POST | `/writing/{id}/draft` | `/api/writing/123/draft` | `pages/writing/writing.js` | 保存草稿 | `title`、`content` |
| POST | `/writing/{id}/submit` | `/api/writing/123/submit` | `pages/writing/writing.js` | 提交评分 | `title`、`content` |
| POST | `/writing/{id}/ai-chat` | `/api/writing/123/ai-chat` | `pages/writing/writing.js` | AI 写作辅导对话 | `message`、`session_type` |

---

## 4) 社区相关

| 方法 | 接口（相对 `API_BASE_URL`） | 典型完整路径示例 | 主要调用位置 | 用途 | 主要请求参数 |
|---|---|---|---|---|---|
| GET | `/community/works` | `/api/community/works` | `pages/community/community.js` | 社区作品列表 | `page`、`per_page`、`grade`、`sort` |
| GET | `/community/works/{id}` | `/api/community/works/123` | `pages/writing-detail/writing-detail.js` | 社区作品详情 | 路径参数 `id` |
| POST | `/community/works/{id}/like` | `/api/community/works/123/like` | `pages/community/community.js` | 点赞 | 路径参数 `id` |
| POST | `/community/works/{id}/unlike` | `/api/community/works/123/unlike` | `pages/community/community.js` | 取消点赞 | 路径参数 `id` |

---

## 5) 排行榜相关

| 方法 | 接口（相对 `API_BASE_URL`） | 典型完整路径示例 | 主要调用位置 | 用途 | 主要请求参数 |
|---|---|---|---|---|---|
| GET | `/ranking/overall` | `/api/ranking/overall` | `pages/ranking/ranking.js` | 综合排行榜 | 无 |
| GET | `/ranking/progress` | `/api/ranking/progress` | `pages/ranking/ranking.js` | 进步榜 | 无 |
| GET | `/ranking/dimension/{dimension}` | `/api/ranking/dimension/theme` | `pages/ranking/ranking.js` | 分维度排行榜 | 路径参数 `dimension`（如 `theme`、`content` 等） |
| GET | `/ranking/my-rank` | `/api/ranking/my-rank` | `pages/ranking/ranking.js` | 我的排名 | 无 |

---

## 6) 反馈与运维

| 方法 | 接口（相对 `API_BASE_URL`） | 典型完整路径示例 | 主要调用位置 | 用途 | 主要请求参数 |
|---|---|---|---|---|---|
| POST | `/feedback` | `/api/feedback` | `pages/settings/settings.js` | 提交用户反馈 | `content`、`contact` |

---

## 7) 日志上报（条件触发）

> 来源：`miniprogram/utils/logger.js` 中直接 `wx.request`。  
> 当前 `ENABLE_REPORT = false`，默认不会发出该请求；仅在开启日志上报时触发。

| 方法 | 请求 URL 代码拼接方式 | 主要调用位置 | 触发条件 | 请求体 |
|---|---|---|---|---|
| POST | `config.API_BASE_URL + '/api/log/upload'` | `reportLog`、`reportLogs` | `ENABLE_REPORT=true` 且满足对应调用逻辑 | `logs`（单条或批量） |

---

## 8) 通用请求封装说明

- 统一封装文件：`miniprogram/utils/api.js`
- 支持方法：`GET`、`POST`、`PUT`、`DELETE`、`uploadFile`
- 鉴权头：`Authorization`（从本地 `token` 读取）
- 超时配置：`config.TIMEOUT`（默认 `30000ms`）
- `uploadFile` 为通用能力，当前页面代码中**未发现实际调用**。

