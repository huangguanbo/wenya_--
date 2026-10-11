"""
文芽 - AI 服务模块
负责与大模型交互，实现写作评分和对话功能
"""
import json
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime

from .api_client import APIClient, APIClientError, fallback_on_error
from .memory_service import MemoryService

logger = logging.getLogger(__name__)


class AIService:
    """
    AI 写作教练服务（增强版）
    功能：
    1. 多模型支持（OpenAI/Claude/通义千问/DeepSeek/月之暗面）
    2. 增强的记忆能力（向量检索、记忆聚合）
    3. 缓存和降级策略
    """

    def __init__(self, api_base=None, api_key=None, model=None, provider=None,
                 enable_memory: bool = True, enable_cache: bool = True):
        from flask import current_app

        # API 配置
        self.provider = provider or current_app.config.get('AI_PROVIDER', 'openai')
        self.api_base = api_base or current_app.config.get('AI_API_BASE')
        self.api_key = api_key or current_app.config.get('AI_API_KEY')
        self.model = model or current_app.config.get('AI_MODEL', 'gpt-4')
        self.max_tokens = current_app.config.get('AI_MAX_TOKENS', 2000)
        self.temperature = current_app.config.get('AI_TEMPERATURE', 0.7)
        
        # 初始化 API 客户端（支持多模型）
        self.api_client = APIClient(
            provider=self.provider,
            api_key=self.api_key,
            base_url=self.api_base,
            model=self.model,
            cache_enabled=enable_cache,
            cache_ttl=3600  # 1 小时缓存
        )
        
        # 初始化记忆服务
        self.enable_memory = enable_memory
        self.memory_service = MemoryService() if enable_memory else None
    
    def _get_headers(self):
        """获取请求头"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def _build_system_prompt(self, session_type='writing_guidance'):
        """
        构建系统级 Prompt
        设定 AI 的"人格"边界：写作教练/引导者
        """
        base_prompt = """你是一位专业的 AI 写作教练，专门为 6-18 岁未成年人提供写作指导。

【角色定位】
- 你是一位温和专业的写作教练，不是聊天伙伴
- 你的职责是引导学生提高写作能力，而不是提供情感陪伴
- 你专注于写作技巧、结构、表达等方面的指导

【交互原则】
1. 使用鼓励性但专业的语言，避免过度情感化表达
2. 聚焦写作本身，温和拒绝与写作无关的闲聊
3. 采用启发式提问，引导学生自己思考，而非直接给出答案
4. 根据学生的年级调整语言难度和指导深度
5. 明确指出自己是 AI 写作教练，不伪装成人类

【安全边界】
- 不讨论敏感政治、宗教、暴力、色情等内容
- 不提供可能误导学生的价值观建议
- 如遇不当内容，温和地引导回写作主题

请始终保持专业、温和、聚焦写作的教练风格。"""
        
        return base_prompt
    
    def _build_scoring_prompt(self, writing, user_profile=None):
        """
        构建作文评分 Prompt
        七维度评分体系
        """
        grade = writing.author.grade if writing.author else 6
        grade_level = "小学" if grade <= 6 else "初中" if grade <= 9 else "高中"
        
        prompt = f"""你是一位专业的中小学语文作文评分专家。请根据以下评分标准对这篇{grade_level}作文进行评分。

【作文信息】
题目：{writing.title}
字数：{writing.word_count}
年级：{grade}年级

【作文内容】
{writing.content}

【评分维度】（每个维度 0-100 分）
1. 任务完成：是否理解并完成了写作要求
2. 主题立意：中心思想是否明确、深刻
3. 内容充实：材料是否丰富、具体、有说服力
4. 结构逻辑：段落安排是否合理、层次是否清晰
5. 语言表达：用词是否准确、语句是否通顺、修辞是否恰当
6. 文体规范：是否符合所选文体的基本特征
7. 思维深度：思考是否有深度、有独到见解

【{grade_level}评分权重参考】
"""
        
        if grade <= 6:
            prompt += """
小学阶段权重：
- 任务完成：15%
- 主题立意：10%
- 内容充实：20%
- 结构逻辑：15%
- 语言表达：25%
- 文体规范：10%
- 思维深度：5%
"""
        elif grade <= 9:
            prompt += """
初中阶段权重：
- 任务完成：10%
- 主题立意：15%
- 内容充实：20%
- 结构逻辑：15%
- 语言表达：20%
- 文体规范：10%
- 思维深度：10%
"""
        else:
            prompt += """
高中阶段权重：
- 任务完成：10%
- 主题立意：20%
- 内容充实：20%
- 结构逻辑：15%
- 语言表达：15%
- 文体规范：10%
- 思维深度：10%
"""
        
        prompt += """
【输出格式】
请严格按照以下 JSON 格式输出评分结果，不要输出其他内容：
{
    "task_score": 85,
    "theme_score": 78,
    "content_score": 82,
    "structure_score": 80,
    "language_score": 85,
    "genre_score": 75,
    "thinking_score": 70,
    "weights": {
        "task": 0.15,
        "theme": 0.10,
        "content": 0.20,
        "structure": 0.15,
        "language": 0.25,
        "genre": 0.10,
        "thinking": 0.05
    },
    "ai_comment": "总体评语，100-200 字",
    "ai_suggestions": ["建议 1", "建议 2", "建议 3"],
    "confidence": 0.85,
    "decision_factors": ["语言流畅", "结构清晰", "立意一般"]
}

注意：confidence 是你对评分的置信度（0-1），如果作文明显偏离正常水平或存在异常，请降低置信度。
"""
        
        return prompt
    
    def score_writing(self, writing) -> Dict:
        """
        对作文进行 AI 评分
        返回七维度评分结果
        """
        grade = writing.author.grade if writing.author else 6
        try:
            # 构建评分 prompt
            prompt = self._build_scoring_prompt(writing)
            
            # 调用大模型
            response = self._call_llm(
                messages=[
                    {"role": "system", "content": "你是一位专业的中小学语文作文评分专家，只输出 JSON，不要输出任何解释性文字。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3  # 评分需要更稳定
            )
            
            # 解析 JSON 响应（可能包含 markdown 代码块）
            response = response.strip()
            if response.startswith('```'):
                lines = response.split('\n')
                response = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
                response = response.strip()
            
            result = json.loads(response)
            
            # 验证并补全必要字段
            score_fields = ['task_score', 'theme_score', 'content_score',
                           'structure_score', 'language_score', 'genre_score', 'thinking_score']
            for field in score_fields:
                val = result.get(field)
                if not isinstance(val, (int, float)):
                    result[field] = 75
                else:
                    result[field] = max(0, min(100, float(val)))
            
            if not isinstance(result.get('ai_comment'), str):
                result['ai_comment'] = ''
            if not isinstance(result.get('ai_suggestions'), list):
                result['ai_suggestions'] = []
            if not isinstance(result.get('confidence'), (int, float)):
                result['confidence'] = 0.8
            else:
                result['confidence'] = max(0.0, min(1.0, float(result['confidence'])))
            if not isinstance(result.get('decision_factors'), list):
                result['decision_factors'] = []
            
            # 设置默认权重
            if 'weights' not in result or not isinstance(result['weights'], dict):
                result['weights'] = self._get_default_weights(grade)
            
            # 标记是否需要人工复审
            scores = [result[f] for f in score_fields]
            avg_score = sum(scores) / len(scores)
            # 任一维度分数与均分差异过大，或置信度过低
            needs_review = (
                result['confidence'] < 0.6 or
                any(abs(s - avg_score) > 30 for s in scores) or
                avg_score < 20 or avg_score > 98
            )
            result['needs_human_review'] = needs_review
            
            return result
            
        except Exception as e:
            logger.error(f"AI scoring failed: {str(e)}")
            # 返回默认分数（避免系统崩溃）
            return {
                'task_score': 75,
                'theme_score': 75,
                'content_score': 75,
                'structure_score': 75,
                'language_score': 75,
                'genre_score': 75,
                'thinking_score': 75,
                'weights': self._get_default_weights(grade),
                'ai_comment': 'AI 评分暂时不可用，请稍后重试。',
                'ai_suggestions': [],
                'confidence': 0.0,
                'needs_human_review': True,
                'decision_factors': []
            }
    
    def chat(self, message: str, writing_context=None, user_profile=None, 
             memory=None, history: List = None, session_type: str = 'writing_guidance') -> Dict:
        """
        AI 对话辅导
        支持审题、素材启发、逐段引导等场景
        """
        try:
            # 构建对话上下文
            messages = [
                {"role": "system", "content": self._build_system_prompt(session_type)}
            ]
            
            # 添加用户画像信息
            if user_profile:
                profile_info = f"学生信息：{user_profile.user.grade if user_profile.user else '未知'}年级，"
                if user_profile.strength_tags:
                    profile_info += f"优势：{', '.join(user_profile.strength_tags)}，"
                if user_profile.weakness_tags:
                    profile_info += f"需改进：{', '.join(user_profile.weakness_tags)}"
                messages.append({"role": "system", "content": profile_info})
            
            # 添加写作上下文
            if writing_context:
                context_info = f"""当前写作任务：
题目：{writing_context.title}
要求：{writing_context.prompt or '无特定要求'}
已写内容：{writing_context.content[:500]}...
"""
                messages.append({"role": "system", "content": context_info})
            
            # 添加历史对话
            if history:
                for msg in history[-10:]:  # 最多 10 条历史
                    messages.append(msg)
            
            # 添加当前消息
            messages.append({"role": "user", "content": message})

            # 使用增强记忆检索上下文（如果启用）
            context_enhanced_message = message
            if self.enable_memory and self.memory_service:
                # 检索相关记忆
                context = self.memory_service.get_context_for_interaction(
                    user_id=user_profile.user.id if user_profile and user_profile.user else 0,
                    current_query=message,
                    writing_context={
                        'title': writing_context.title,
                        'content': writing_context.content[:500]
                    } if writing_context else None
                )
                
                # 注入相关记忆到上下文
                if context.get('relevant_memories'):
                    memory_context = "\n【相关记忆】\n"
                    for mem in context['relevant_memories'][:3]:
                        memory_context += f"- {mem['content']}\n"
                    messages.insert(-1, {"role": "system", "content": memory_context})
                
                # 记录对话到记忆
                self.memory_service.add_fragment(
                    user_id=user_profile.user.id if user_profile and user_profile.user else 0,
                    content=f"用户提问：{message[:200]}",
                    category='interaction',
                    interaction_type=session_type,
                    metadata={'session_type': session_type, 'writing_id': writing_context.id if writing_context else None}
                )

            # 调用大模型（使用新的 API 客户端）
            try:
                result = self.api_client.chat(
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                response = result['content']
                
                # 记录 AI 响应到记忆
                if self.enable_memory and self.memory_service:
                    self.memory_service.add_fragment(
                        user_id=user_profile.user.id if user_profile and user_profile.user else 0,
                        content=f"AI 回复：{response[:200]}",
                        category='interaction',
                        interaction_type=session_type,
                        metadata={'model': self.model, 'provider': self.provider}
                    )

            except APIClientError as e:
                logger.error(f"API 调用失败：{e.message}")
                response = self._mock_response(messages)

            # 提取关键点（用于记忆更新）
            key_points = self._extract_key_points(message, response, session_type)

            return {
                'content': response,
                'session_type': session_type,
                'key_points': key_points,
                'summary': f"{session_type} - {message[:50]}...",
                'is_filtered': False,
                'model_info': {
                    'provider': self.provider,
                    'model': self.model,
                    'cached': result.get('cached', False) if 'result' in locals() else False
                }
            }

        except Exception as e:
            logger.error(f"AI chat failed: {str(e)}")
            return {
                'content': 'AI 教练暂时不可用，请稍后再试。',
                'session_type': session_type,
                'key_points': [],
                'summary': '',
                'is_filtered': False
            }
    
    def _call_llm(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """
        调用大模型 API（使用新的 API 客户端）
        支持多模型、缓存、重试、降级
        """
        try:
            result = self.api_client.chat(
                messages=messages,
                temperature=temperature,
                max_tokens=self.max_tokens
            )
            return result['content']
        except APIClientError as e:
            logger.error(f"API 调用失败：{e.message}")
            return self._mock_response(messages)

    def _mock_response(self, messages: List[Dict]) -> str:
        """模拟响应（开发测试用）"""
        last_message = messages[-1]['content'] if messages else ""

        if "评分" in last_message or "分数" in last_message:
            import random
            base = random.randint(70, 90)
            return json.dumps({
                "task_score": base,
                "theme_score": base - 5,
                "content_score": base - 3,
                "structure_score": base - 7,
                "language_score": base,
                "genre_score": base - 5,
                "thinking_score": base - 10,
                "weights": {"task": 0.1, "theme": 0.15, "content": 0.2, "structure": 0.15, "language": 0.2, "genre": 0.1, "thinking": 0.1},
                "ai_comment": "这是一篇不错的作文，主题明确，语言流畅。建议在内容充实和思维深度方面继续努力。",
                "ai_suggestions": ["可以增加一些具体的例子来支撑观点", "尝试使用更多样的修辞手法", "深入思考问题背后的原因"],
                "confidence": 0.85,
                "decision_factors": ["语言流畅", "结构完整", "立意清晰"]
            }, ensure_ascii=False)

        return "这是一个很好的写作问题。让我们一步步思考：首先，明确你要表达的核心观点是什么？其次，考虑如何用具体的例子来支撑这个观点。最后，注意段落之间的过渡要自然。你有什么具体的写作困难吗？"
    
    def _get_default_weights(self, grade: int) -> Dict:
        """获取默认权重"""
        if grade <= 6:
            return {"task": 0.15, "theme": 0.10, "content": 0.20, "structure": 0.15, "language": 0.25, "genre": 0.10, "thinking": 0.05}
        elif grade <= 9:
            return {"task": 0.10, "theme": 0.15, "content": 0.20, "structure": 0.15, "language": 0.20, "genre": 0.10, "thinking": 0.10}
        else:
            return {"task": 0.10, "theme": 0.20, "content": 0.20, "structure": 0.15, "language": 0.15, "genre": 0.10, "thinking": 0.10}
    
    def _extract_key_points(self, user_msg: str, ai_response: str, session_type: str) -> List[str]:
        """提取对话关键点（用于记忆更新）"""
        # 简化实现，实际可用 NLP 提取
        key_points = []
        
        if session_type == 'writing_guidance':
            key_points.append(f"写作指导：{user_msg[:30]}")
        elif session_type == 'brainstorming':
            key_points.append(f"头脑风暴：{user_msg[:30]}")
        elif session_type == 'revision':
            key_points.append(f"修改建议：{user_msg[:30]}")
        
        return key_points
