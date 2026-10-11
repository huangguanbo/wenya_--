# 快速参考卡 - API 调用和记忆增强

## 环境变量配置

```bash
# 选择 AI 提供商
AI_PROVIDER=openai          # openai/claude/aliyun/deepseek/moonshot

# API 配置
AI_API_BASE=https://api.openai.com/v1
AI_API_KEY=sk-xxx
AI_MODEL=gpt-4o

# 功能开关
AI_ENABLE_MEMORY=true       # 增强记忆
AI_ENABLE_CACHE=true        # API 缓存
```

## 提供商配置速查

| 提供商 | AI_PROVIDER | AI_API_BASE | 默认模型 |
|--------|-------------|-------------|---------|
| OpenAI | `openai` | `https://api.openai.com/v1` | gpt-4o |
| Claude | `claude` | `https://api.anthropic.com/v1` | claude-3-sonnet-20240229 |
| 通义千问 | `aliyun` | `https://dashscope.aliyuncs.com/api/v1` | qwen-max |
| DeepSeek | `deepseek` | `https://api.deepseek.com/v1` | deepseek-chat |
| 月之暗面 | `moonshot` | `https://api.moonshot.cn/v1` | moonshot-v1-8k |

## Python 使用示例

### API 客户端
```python
from services.api_client import APIClient

client = APIClient(
    provider='openai',
    api_key='sk-xxx',
    model='gpt-4o'
)

result = client.chat(
    messages=[{"role": "user", "content": "你好"}],
    temperature=0.7
)

print(result['content'])
print(f"缓存：{result['cached']}")
```

### 记忆服务
```python
from services.memory_service import MemoryService

memory = MemoryService()

# 添加记忆
memory.add_fragment(
    user_id=1,
    content="学生擅长记叙文",
    category='writing_profile',
    interaction_type='guidance'
)

# 检索记忆
fragments = memory.retrieve(
    user_id=1,
    query="写作优势",
    top_k=5
)

# 聚合摘要
summary = memory.aggregate_memories(
    user_id=1,
    time_range_days=30
)
```

### AI 服务（带记忆增强）
```python
from services.ai_service import AIService

ai = AIService(
    provider='openai',
    enable_memory=True,
    enable_cache=True
)

response = ai.chat(
    message="老师，我作文结构不清晰",
    writing_context=writing,
    user_profile=user_profile
)

print(response['content'])
print(response['model_info'])
```

## API 端点速查

```bash
# 记忆画像
GET  /api/memory/profile
PUT  /api/memory/profile

# 记忆片段
GET  /api/memory/fragments?q=关键词&category=writing_profile&top_k=10
DELETE /api/memory/fragments/<id>

# 记忆聚合
GET  /api/memory/aggregate?days=30

# 交互上下文
GET  /api/memory/context?q=作文结构&writing_id=123

# 统计信息
GET  /api/memory/stats

# 清空记忆
POST /api/memory/clear
{
  "type": "fragments"
}
```

## 代码片段

### 降级处理
```python
from services.api_client import fallback_on_error

@fallback_on_error({'content': '默认回复', 'fallback': True})
def call_ai():
    return client.chat(messages=[...])
```

### 查看统计
```python
# API 客户端统计
stats = client.get_stats()
# {'total_calls': 10, 'cache_hits': 3, 'cache_misses': 7, ...}

# 记忆服务统计
stats = memory.get_stats()
# {'total_users': 5, 'total_fragments': 120, ...}
```

### 清空缓存
```python
client.clear_cache()
```

## 依赖安装

```bash
# 基础依赖
pip install -r requirements.txt

# 向量检索（可选）
pip install sentence-transformers torch
```

## 测试

```bash
# 运行测试
python test_api_memory.py

# 预期输出
所有测试通过！✓
```

## 常见问题

**Q: 如何切换模型提供商？**
A: 修改 `.env` 中的 `AI_PROVIDER`，重启应用

**Q: 缓存多久过期？**
A: 默认 1 小时，可在 `APIClient` 中设置 `cache_ttl`

**Q: 如何关闭记忆功能？**
A: 设置 `AI_ENABLE_MEMORY=false` 或初始化时传 `enable_memory=False`

**Q: 向量检索怎么用？**
A: 安装 `sentence-transformers`，初始化时传 `vector_store_enabled=True`

**Q: 记忆重要性如何计算？**
A: 基于内容长度、交互类型、用户反馈，随时间自动衰减

## 调试技巧

```python
# 查看 API 调用统计
print(client.get_stats())

# 查看缓存大小
print(f"缓存条目数：{len(client.cache)}")

# 查看记忆片段
fragments = memory.memory_fragments[user_id]
for f in fragments:
    print(f"{f.content[:50]}... (重要性：{f.importance:.2f})")

# 强制清理过期缓存
expired = [k for k, v in client.cache.items() if v.is_expired()]
for k in expired:
    del client.cache[k]
```

## 性能基准

| 场景 | 无缓存 | 有缓存 |
|------|--------|--------|
| 响应时间 | 1-3s | 0.1-0.3s |
| API 成本 | 100% | 50-70% |

| 检索方式 | 速度 | 准确度 |
|---------|------|--------|
| 关键词 | 快 | 中 |
| 向量 | 中 | 高 |

## 文件清单

```
services/
├── api_client.py       # API 客户端（新增）
├── memory_service.py   # 记忆服务（新增）
└── ai_service.py       # AI 服务（已更新）

routes/
└── memory.py           # 记忆路由（新增）

根目录
├── config.py           # 配置（已更新）
├── .env.example        # 环境示例（已更新）
├── requirements.txt    # 依赖（已更新）
├── app.py              # 应用入口（已更新）
├── test_api_memory.py  # 测试（新增）
├── API_MEMORY_GUIDE.md # 详细指南（新增）
└── UPDATE_SUMMARY.md   # 更新总结（新增）
```

## 联系支持

遇到问题？
1. 查看 `API_MEMORY_GUIDE.md` 详细文档
2. 运行 `python test_api_memory.py` 诊断
3. 检查日志中的错误信息
