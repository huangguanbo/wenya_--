# 文芽 Flask 服务前端 API 功能文档

> 基于当前后端代码（`routes/*.py` + `app.py`）整理。
> 适用于前端联调与接口接入，不包含数据库内部实现细节。

## 1. 基础信息

- 服务入口：`app.py`
- API 前缀：
  - 认证：`/api/auth`
  - 通用：`/api`
  - 写作：`/api/writing`
  - 排行榜：`/api/ranking`
  - 社区：`/api/community`
  - AI 记忆：`/api/memory`
- 认证方式：`Flask-Login` 会话认证（登录后依赖 Cookie，会话接口需携带凭据）
- CORS：`/api/*` 开启跨域并支持携带凭据（`supports_credentials=True`）

---

## 2. 统一响应格式

### 2.1 成功响应（`success_response`）

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

- `code=0` 表示成功
- `data` 字段按接口返回

### 2.2 错误响应（`error_response`）

```json
{
  "code": 1,
  "error": "错误摘要",
  "message": "可选详细信息"
}
```

### 2.3 分页响应（`paginated_response`）

```json
{
  "code": 0,
  "message": "success",
  "data": [],
  "pagination": {
    "total": 100,
    "pages": 10,
    "current_page": 1,
    "per_page": 10,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## 3. 鉴权与全局错误码说明

- 需要登录的接口使用 `@login_required`
- 未登录访问：`401`
- 无权限：`403`
- 资源不存在：`404`
- 请求过于频繁：`429`
- 服务内部异常：`500`

常见业务状态码：

- `400` 参数校验失败
- `401` 用户名/密码错误或未认证
- `403` 账号停用 / 内容安全拦截 / 操作无权限
- `404` 资源不存在
- `409` 资源冲突（如重复发布、重复举报、并发重复提交）
- `503` 外部 AI 服务不可用或未开通

---

## 4. 认证模块（`/api/auth`）

## 4.1 登录

- **POST** `/api/auth/login`
- 认证：否
- 限流：`10 per hour`
- 请求体：

```json
{
  "username": "student01",
  "password": "Passw0rd123",
  "remember": true
}
```

- 成功：返回 `user`，并建立会话。

## 4.2 登出

- **POST** `/api/auth/logout`
- 认证：是
- 成功：清除登录态。

## 4.3 修改密码

- **POST** `/api/auth/change-password`
- 认证：是
- 限流：`10 per hour`
- 请求体：

```json
{
  "old_password": "old",
  "new_password": "new"
}
```

## 4.4 获取/更新个人资料

- **GET** `/api/auth/profile`
  - 认证：是
  - 返回：`user`、`profile`、`guardian`（手机号脱敏）

- **PUT** `/api/auth/profile`
  - 认证：是
  - 可更新字段：
    - `nickname`（最长 32，且会做内容安全检查）
    - `show_in_ranking`（布尔）
    - `show_works_publicly`（布尔）
    - `grade`

## 4.5 导出个人数据

- **POST** `/api/auth/export-data`
- 认证：是
- 限流：`3 per day`
- 返回：用户信息、画像、全部作文（含内容和评分）、导出时间。

## 4.6 获取当前用户信息

- **GET** `/api/auth/me`
- 认证：是
- 返回：`user` + `profile`

---

## 5. 通用模块（`/api`）

## 5.1 健康检查

- **GET** `/api/health`
- 认证：否
- 返回：`status=ok`

## 5.2 用户写作统计

- **GET** `/api/stats`
- 认证：是
- 返回：
  - `total_writings`
  - `scored_writings`
  - `average_score`
  - `best_score`
  - `profile`

## 5.3 AI 配置状态

- **GET** `/api/ai/status`
- 认证：是
- 返回（不含密钥）：
  - `scoring.configured/mock_mode/provider/model`
  - `chat.configured/mock_mode`

## 5.4 合规信息

- **GET** `/api/compliance/info`
- 认证：否
- 返回：ICP 备案号、算法备案号、隐私政策/服务条款地址

## 5.5 通知列表

- **GET** `/api/notifications`
- 认证：是
- 返回：`notifications[]`、`unread_count`

## 5.6 写作挑战

- **GET** `/api/challenges`
- 认证：否（允许匿名）
- 返回：挑战列表（题目、描述、体裁、字数范围、难度）

- **GET** `/api/challenges/{challenge_id}`
- 认证：否（允许匿名）
- 返回：单个挑战详情

## 5.7 素材库

- **GET** `/api/materials`
- 认证：否（允许匿名）
- 查询参数：
  - `category`：`quote|idiom|example`
- 返回：
  - 指定分类时：该分类素材
  - 不指定时：全部分类及素材

---

## 6. 写作模块（`/api/writing`）

## 6.1 创建作文

- **POST** `/api/writing`
- 认证：是
- 请求体：

```json
{
  "title": "我的题目",
  "prompt": "写作要求",
  "content": "作文正文"
}
```

- 约束：
  - `title` 必填，<=200 字
  - `content` 必填，且进行内容安全检查
- 成功：创建 `writing` 和初始 `draft(version=1)`，返回 `writing`

## 6.2 获取作文详情

- **GET** `/api/writing/{writing_id}`
- 认证：是
- 返回：`writing`（含内容、评分）+ `community_work`（若已发布）

## 6.3 更新作文

- **PUT** `/api/writing/{writing_id}`
- 认证：是
- 仅 `status=draft` 可修改
- 可更新：`title`、`content`
- 更新 `content` 时会新增草稿版本并做内容安全检查

## 6.4 删除作文（软删除）

- **DELETE** `/api/writing/{writing_id}`
- 认证：是

## 6.5 提交评分

- **POST** `/api/writing/{writing_id}/submit`
- 认证：是
- 限流：`3 per minute`
- 约束：
  - 仅草稿可提交
  - 最少字数 `100`
- 成功：
  - 生成七维评分 + 总分
  - 更新作文为已提交/已评分
  - 返回 `writing`（含评分）与 `is_mock`
- 可能错误：
  - `503`：评分服务未配置或暂不可用
  - `409`：并发下重复提交冲突

## 6.6 自动保存草稿

- **POST** `/api/writing/{writing_id}/draft`
- 认证：是
- 限流：`30 per minute`
- 请求体示例：

```json
{
  "title": "可选",
  "prompt": "可选",
  "content": "最新内容"
}
```

- 返回：`version`、`writing`

## 6.7 草稿历史

- **GET** `/api/writing/{writing_id}/drafts`
- 认证：是
- 返回：最近最多 50 个草稿版本（版本号、字数、时间）

## 6.8 AI 写作对话历史

- **GET** `/api/writing/{writing_id}/ai-chat`
- 认证：是
- 返回：`messages[]`（role/content/timestamp）

## 6.9 AI 写作对话

- **POST** `/api/writing/{writing_id}/ai-chat`
- 认证：是
- 限流：`20 per minute`
- 请求体：

```json
{
  "message": "请帮我优化开头段落",
  "session_type": "writing_guidance"
}
```

- 返回：
  - `response`
  - `conversation_id`
  - `is_mock`
- 说明：
  - 用户输入会做内容安全检查
  - AI 输出也会做二次安全过滤（必要时替换为安全回复）

## 6.10 作文列表

- **GET** `/api/writing`
- 认证：是
- 查询参数：
  - `page` 默认 1
  - `per_page` 默认 10，最大 100
  - `status` 默认 `all`
- 返回：分页数据（每项为作文摘要 + 评分）

---

## 7. 排行榜模块（`/api/ranking`）

## 7.1 综合榜（同年级）

- **GET** `/api/ranking/overall`
- 认证：是
- 参数：
  - `grade`（可选，默认当前用户年级）
- 返回：
  - `rankings`
  - `user_rank`
  - `total_participants`
  - `grade`
  - `rank_type=overall`

## 7.2 进步榜

- **GET** `/api/ranking/progress`
- 认证：是
- 参数：
  - `grade`（可选，默认当前用户年级）
  - `days`（默认 30）
- 返回：
  - `rankings`
  - `user_rank`
  - `period_days`
  - `rank_type=progress`

## 7.3 维度榜

- **GET** `/api/ranking/dimension/{dimension}`
- 认证：是
- `dimension` 可选：
  - `theme`
  - `content`
  - `structure`
  - `language`
  - `creativity`（映射思维维度）
- 参数：
  - `grade`（可选，默认当前用户年级）
- 返回：
  - `rankings`
  - `user_rank`
  - `dimension`
  - `rank_type=dimension`

## 7.4 个人成长曲线（私密）

- **GET** `/api/ranking/my-growth-curve`
- 认证：是
- 参数：`days`（默认 90）
- 返回：
  - `growth_data.average_score[]`
  - `growth_data.percentile[]`
  - `growth_data.writing_count[]`
  - `is_private=true`

## 7.5 排行榜可见性开关

- **POST** `/api/ranking/toggle-visibility`
- 认证：是
- 请求体：

```json
{
  "show": true
}
```

- 返回：`show_in_ranking`

---

## 8. 社区模块（`/api/community`）

## 8.1 社区作品列表

- **GET** `/api/community/works`
- 认证：否
- 查询参数：
  - 分页：`page`（默认 1）, `per_page`（默认 12）
  - 筛选：`grade`, `school_stage`, `genre`, `tag`, `q`, `featured`
- 说明：
  - 仅返回 `review_status=approved` 且作者允许公开展示的作品
  - 返回数据已做隐私脱敏（匿名作者信息）

## 8.2 作品详情

- **GET** `/api/community/works/{work_id}`
- 认证：否（登录时会返回更多状态）
- 返回：
  - `work`
  - 包含 `is_mine`, `is_liked`, `review_status` 等状态

## 8.3 点赞/取消点赞

- **POST** `/api/community/works/{work_id}/like`
- 认证：是
- 行为：同一接口切换点赞状态
- 返回：`like_count`, `is_liked`

## 8.4 评论作品

- **POST** `/api/community/works/{work_id}/comment`
- 认证：是
- 请求体：

```json
{
  "content": "评论内容",
  "parent_id": 123
}
```

- 约束：
  - `content` 必填，<=500 字
  - 可选 `parent_id`（回复某条评论）
- 返回：创建后的 `comment`

## 8.5 获取评论列表

- **GET** `/api/community/works/{work_id}/comments`
- 认证：否
- 返回：`comments[]`（含 `author_name`、`is_mine`）

## 8.6 删除评论

- **DELETE** `/api/community/works/{work_id}/comments/{comment_id}`
- 认证：是
- 仅评论作者可删除

## 8.7 举报作品

- **POST** `/api/community/works/{work_id}/report`
- 认证：是
- 限流：`5 per hour`
- 请求体：

```json
{
  "reason": "spam",
  "description": "可选，最多 500 字"
}
```

- 约束：
  - 不能举报自己的作品
  - 同一用户对同一作品仅可举报一次
- 返回：`report_id`、`reason`、`reason_label`

## 8.8 获取我的举报状态

- **GET** `/api/community/works/{work_id}/report`
- 认证：是
- 返回：`report`（未举报时为 `null`）

## 8.9 发布作文到社区

- **POST** `/api/community/publish/{writing_id}`
- 认证：是
- 前置条件：
  - 作文已评分（`is_scored=true`）
  - 该作文未发布过
- 请求体：

```json
{
  "tags": ["记叙", "成长"],
  "genre": "记叙文"
}
```

- 返回：`work`
- 说明：
  - 受 `COMMUNITY_AUTO_APPROVE` 配置影响：
    - 开启：直接 `approved` 并公开
    - 关闭：`pending`，需审核后公开

## 8.10 精选作品

- **GET** `/api/community/featured`
- 认证：否
- 参数：`page`（默认 1）, `per_page`（默认 6）
- 返回：精选作品分页

---

## 9. AI 记忆模块（`/api/memory`）

> 全部需要登录

## 9.1 获取记忆画像

- **GET** `/api/memory/profile`
- 返回：
  - `profile`
  - `knowledge_base`
  - `stats`（交互次数/最近交互时间/版本）

## 9.2 更新记忆画像

- **PUT** `/api/memory/profile`
- 请求体：

```json
{
  "writing_profile": {},
  "knowledge_base": {}
}
```

- 行为：对已有画像/知识库做合并更新。

## 9.3 检索记忆片段

- **GET** `/api/memory/fragments`
- 参数：
  - `q`（查询词）
  - `category`
  - `top_k`（默认 10，最大 50）
  - `min_importance`（默认 0.3）
- 返回：`fragments[]`, `count`, `query`

## 9.4 删除记忆片段

- **DELETE** `/api/memory/fragments/{fragment_id}`

## 9.5 记忆聚合摘要

- **GET** `/api/memory/aggregate`
- 参数：
  - `category`
  - `days`（默认 30）
- 返回：`summary`, `time_range_days`

## 9.6 获取交互上下文

- **GET** `/api/memory/context`
- 参数：
  - `q`
  - `writing_id`
- 返回：`context`

## 9.7 记忆统计

- **GET** `/api/memory/stats`
- 返回：
  - `system_stats`
  - `user_stats`

## 9.8 清空记忆

- **POST** `/api/memory/clear`
- 请求体：

```json
{
  "type": "all"
}
```

- `type` 可选：`all | fragments | profile`

---

## 10. 前端接入建议（基于现有实现）

1. **统一处理 `code` 字段**：`code=0` 成功，`code=1` 失败。
2. **会话接口必须携带 Cookie**：跨域时前端需开启 `withCredentials=true`。
3. **实现 401 统一跳转登录**，403/429/503 做明确提示。
4. **分页接口统一读取 `pagination`**，不要自行推断。
5. **写作与社区接口涉及内容安全拦截**，前端需要展示后端返回的具体错误文案。
6. **排行榜、社区均有"可见性/审核状态"逻辑**，前端要按状态展示，不应默认"提交即公开"。
