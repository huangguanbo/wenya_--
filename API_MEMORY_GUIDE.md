# API 调用和增强记忆功能使用指南

## 新增功能概述

本次更新为文芽项目添加了以下核心功能：

1. **多模型 API 调用支持** - 支持 OpenAI、Claude、通义千问、DeepSeek、月之暗面等多种 AI 模型
2. **增强记忆能力** - 向量检索、记忆聚合、长期记忆持久化
3. **缓存和降级策略** - API 调用缓存、失败降级、自动重试

## 文件结构

```
wenya/
├── services/
│   ├── api_client.py       # 通用 API 客户端（新增）
│   ├── memory_service.py   # 增强记忆服务（新增）
│   └── ai_service.py       # AI 服务（已更新）
├── routes/
│   └── memory.py           # 记忆管理路由（新增）
├── config.py               # 配置模块（已更新）
├── .env.example            # 环境变量示例（已更新）
└── requirements.txt        # 依赖文件（已更新）
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

如需启用向量检索功能（可选）：
```bash
pip install sentence-transformers torch
```

### 2. 配置环境变量

编辑 `.env` 文件：

```bash
# 选择 AI 提供商
AI_PROVIDER=openai          # openai/claude/aliyun/deepseek/moonshot
AI_API_KEY=your-api-key
AI_MODEL=gpt-4

# 或者使用其他提供商
# AI_PROVIDER=aliyun       # 阿里云通义千问
# AI_API_BASE=https://dashscope.aliyuncs.com/api/v1
# AI_MODEL=qwen-max

# 增强功能开关
AI_ENABLE_MEMORY=true       # 启用增强记忆
AI_ENABLE_CACHE=true        # 启用 API 缓存
```

### 3. 使用多模型 API

```python
from services.api_client import APIClient

# 使用 OpenAI
client = APIClient(
    provider='openai',
    api_key='sk-xxx',
    model='gpt-4o'
)

# 使用阿里云通义千问
client = APIClient(
    provider='aliyun',
    api_key='your-key',
    model='qwen-max'
)

# 发送请求
result = client.chat(
    messages=[
        {"role": "user", "content": "你好，请帮我修改这篇作文"}
    ],
    temperature=0.7
)

print(result['content'])
print(f"缓存命中：{result['cached']}")
```

### 4. 使用增强记忆

```python
from services.memory_service import MemoryService

# 初始化记忆服务
memory = MemoryService(vector_store_enabled=True)

# 添加记忆片段
memory.add_fragment(
    user_id=1,
    content="学生擅长记叙文写作，但在议论文方面需要加强",
    category='writing_profile',
    interaction_type='guidance',
    metadata={'grade': 8, 'strength': '记叙文'}
)

# 检索相关记忆
fragments = memory.retrieve(
    user_id=1,
    query="写作优势",
    top_k=5,
    min_importance=0.4
)

# 聚合记忆生成摘要
summary = memory.aggregate_memories(
    user_id=1,
    time_range_days=30
)
print(summary)
```

### 5. 在 AI 对话中使用增强记忆

```python
from services.ai_service import AIService

# 初始化 AI 服务（带记忆增强）
ai_service = AIService(
    provider='openai',
    api_key='sk-xxx',
    model='gpt-4o',
    enable_memory=True,
    enable_cache=True
)

# 对话（自动使用记忆增强）
response = ai_service.chat(
    message="老师，我觉得我的作文结构不够清晰",
    writing_context=writing,
    user_profile=user_profile,
    session_type='writing_guidance'
)

# 响应中包含模型信息
print(response['content'])
print(response['model_info'])  # 提供商、模型、是否缓存
```

## API 端点

### 记忆管理 API

```bash
# 获取用户记忆画像
GET /api/memory/profile

# 更新用户记忆画像
PUT /api/memory/profile
{
  "writing_profile": {
    "school_stage": "middle",
    "grade": 8,
    "strength_genres": ["记叙文", "散文"],
    "weakness_genres": ["议论文"]
  }
}

# 检索记忆片段
GET /api/memory/fragments?q=写作优势&category=writing_profile&top_k=10

# 聚合记忆摘要
GET /api/memory/aggregate?days=30

# 获取交互上下文
GET /api/memory/context?q=作文结构&writing_id=123

# 获取统计信息
GET /api/memory/stats

# 清空记忆
POST /api/memory/clear
{
  "type": "fragments"  # all/fragments/profile
}
```

## 支持的 AI 模型提供商

| 提供商 | 配置示例 | 默认模型 |
|--------|---------|---------|
| OpenAI | `AI_PROVIDER=openai` | gpt-4o |
| Claude | `AI_PROVIDER=claude` | claude-3-sonnet-20240229 |
| 阿里云 | `AI_PROVIDER=aliyun` | qwen-max |
| DeepSeek | `AI_PROVIDER=deepseek` | deepseek-chat |
| 月之暗面 | `AI_PROVIDER=moonshot` | moonshot-v1-8k |

## 高级功能

### 1. API 调用缓存

```python
client = APIClient(
    provider='openai',
    cache_enabled=True,
    cache_ttl=3600  # 1 小时
)

# 相同请求会自动返回缓存结果
result1 = client.chat(messages=[...])
result2 = client.chat(messages=[...])  # 缓存命中

print(client.get_stats())
# {
#   'total_calls': 2,
#   'cache_hits': 1,
#   'cache_misses': 1,
#   'cache_size': 1
# }
```

### 2. 向量检索（需要安装 sentence-transformers）

```python
# 启用向量检索
memory = MemoryService(vector_store_enabled=True)

# 自动计算向量相似度
fragments = memory.retrieve(
    user_id=1,
    query="如何提高写作水平",  # 语义相似即可匹配
    top_k=5
)
```

### 3. 记忆重要性衰减

记忆片段的重要性会随时间自动衰减：
- 新记忆：重要性 = 初始评分
- 30 天后：重要性 = 初始评分 × 0.95^30 ≈ 21%
- 低重要性记忆会被自动清理

### 4. 降级策略

```python
from services.api_client import fallback_on_error

@fallback_on_error({'content': '默认回复', 'fallback': True})
def call_ai_api():
    return client.chat(messages=[...])
```

## 性能优化建议

1. **启用缓存** - 减少重复 API 调用
2. **使用向量检索** - 提高记忆检索准确性
3. **定期清理记忆** - 避免内存占用过高
4. **选择合适的模型** - 根据场景选择性价比最优的模型

## 故障排查

### API 调用失败

```python
try:
    result = client.chat(messages=[...])
except APIClientError as e:
    print(f"错误：{e.message}")
    print(f"状态码：{e.status_code}")
    print(f"重试等待：{e.retry_after}s")
```

### 记忆服务不可用

```python
ai_service = AIService(enable_memory=False)  # 禁用记忆
```

## 迁移指南

### 从旧版本迁移

旧代码：
```python
from openai import OpenAI
client = OpenAI(base_url=..., api_key=...)
```

新代码：
```python
from services.api_client import APIClient
client = APIClient(provider='openai', api_key=...)
result = client.chat(messages=[...])
```

### 保持向后兼容

`ai_service.py` 保留了原有的接口，现有代码无需修改即可使用新功能。

## 安全注意事项

1. **API 密钥管理** - 不要将密钥提交到版本控制
2. **内容过滤** - AI 输出仍需经过内容安全检查
3. **记忆隐私** - 用户记忆数据需加密存储（生产环境）
4. **限流保护** - 已集成 Flask-Limiter，避免滥用

## 下一步计划

- [ ] 支持更多 AI 模型提供商
- [ ] 实现记忆的数据库持久化
- [ ] 添加记忆可视化工具
- [ ] 支持自定义 Prompt 模板
- [ ] 实现多轮对话优化
