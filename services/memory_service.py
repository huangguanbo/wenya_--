"""
文芽 - 增强记忆服务
支持向量检索、记忆聚合、长期记忆持久化
"""
import json
import hashlib
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class MemoryFragment:
    """记忆片段"""
    id: str
    user_id: int
    content: str
    category: str  # writing_profile, knowledge, interaction, feedback
    importance: float  # 0-1，重要性评分
    embedding: Optional[List[float]] = None  # 向量表示（可选）
    metadata: Optional[Dict] = None
    created_at: datetime = None
    accessed_at: datetime = None
    access_count: int = 0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.accessed_at is None:
            self.accessed_at = self.created_at
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'category': self.category,
            'importance': self.importance,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'accessed_at': self.accessed_at.isoformat() if self.accessed_at else None,
            'access_count': self.access_count
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryFragment':
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            content=data['content'],
            category=data['category'],
            importance=data['importance'],
            embedding=data.get('embedding'),
            metadata=data.get('metadata'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            accessed_at=datetime.fromisoformat(data['accessed_at']) if data.get('accessed_at') else None,
            access_count=data.get('access_count', 0)
        )


class MemoryService:
    """
    增强记忆服务
    功能：
    1. 记忆片段化存储
    2. 重要性评分与衰减
    3. 相似记忆检索（支持向量检索）
    4. 记忆聚合与摘要
    5. 长期记忆持久化
    """

    def __init__(self, db_session=None, vector_store_enabled: bool = False):
        """
        初始化记忆服务
        
        Args:
            db_session: 数据库会话
            vector_store_enabled: 是否启用向量检索（需要额外依赖）
        """
        self.db_session = db_session
        self.vector_store_enabled = vector_store_enabled
        self.memory_fragments: Dict[int, List[MemoryFragment]] = {}  # user_id -> fragments
        self.importance_decay_factor = 0.95  # 重要性衰减因子
        self.max_fragments_per_user = 1000  # 每用户最大记忆片段数
        
        # 向量编码器（可选）
        self.encoder = None
        if vector_store_enabled:
            self._init_vector_encoder()

    def _init_vector_encoder(self):
        """初始化向量编码器"""
        try:
            # 尝试使用 sentence-transformers
            from sentence_transformers import SentenceTransformer
            self.encoder = SentenceTransformer('paraphrase-MiniLM-L6-v2')
            logger.info("向量编码器初始化成功")
        except ImportError:
            logger.warning("sentence-transformers 未安装，向量检索功能不可用")
            self.vector_store_enabled = False
        except Exception as e:
            logger.warning(f"向量编码器初始化失败：{e}")
            self.vector_store_enabled = False

    def _generate_fragment_id(self, user_id: int, content: str) -> str:
        """生成记忆片段 ID"""
        timestamp = datetime.utcnow().isoformat()
        key = f"{user_id}:{content}:{timestamp}"
        return hashlib.md5(key.encode()).hexdigest()

    def _calculate_importance(self, content: str, interaction_type: str, 
                             user_feedback: float = None) -> float:
        """
        计算记忆重要性
        
        因素：
        - 内容长度和复杂度
        - 交互类型（评分>指导>闲聊）
        - 用户反馈（如果有）
        """
        # 基础重要性（基于内容长度）
        length_score = min(1.0, len(content) / 500) * 0.3
        
        # 交互类型权重
        type_weights = {
            'scoring': 1.0,      # 评分最重要
            'revision': 0.8,     # 修改建议
            'guidance': 0.6,     # 写作指导
            'brainstorming': 0.5, # 头脑风暴
            'chat': 0.3          # 普通对话
        }
        type_score = type_weights.get(interaction_type, 0.3) * 0.4
        
        # 用户反馈（如果有）
        feedback_score = user_feedback if user_feedback else 0.5
        feedback_score *= 0.3
        
        importance = length_score + type_score + feedback_score
        return min(1.0, max(0.0, importance))

    def add_fragment(self, user_id: int, content: str, category: str,
                    interaction_type: str = 'chat', user_feedback: float = None,
                    metadata: Dict = None) -> MemoryFragment:
        """
        添加记忆片段
        
        Args:
            user_id: 用户 ID
            content: 记忆内容
            category: 类别
            interaction_type: 交互类型
            user_feedback: 用户反馈（0-1）
            metadata: 额外元数据
        
        Returns:
            MemoryFragment: 创建的记忆片段
        """
        importance = self._calculate_importance(content, interaction_type, user_feedback)
        
        fragment = MemoryFragment(
            id=self._generate_fragment_id(user_id, content),
            user_id=user_id,
            content=content,
            category=category,
            importance=importance,
            metadata=metadata or {}
        )
        
        # 生成向量表示（如果启用）
        if self.vector_store_enabled and self.encoder:
            try:
                embedding = self.encoder.encode(content).tolist()
                fragment.embedding = embedding
            except Exception as e:
                logger.warning(f"生成向量表示失败：{e}")
        
        # 存储到内存
        if user_id not in self.memory_fragments:
            self.memory_fragments[user_id] = []
        
        self.memory_fragments[user_id].append(fragment)
        
        # 清理过期记忆（保持最大数量）
        self._prune_fragments(user_id)
        
        # 异步持久化到数据库（如果有 db_session）
        if self.db_session:
            self._persist_to_db(fragment)
        
        logger.info(f"添加记忆片段：user_id={user_id}, category={category}, importance={importance:.2f}")
        return fragment

    def _persist_to_db(self, fragment: MemoryFragment):
        """持久化到数据库"""
        try:
            from models.ai_memory import MemoryFragmentDB
            
            db_fragment = MemoryFragmentDB(
                id=fragment.id,
                user_id=fragment.user_id,
                content=fragment.content,
                category=fragment.category,
                importance=fragment.importance,
                embedding=fragment.embedding,
                metadata=fragment.metadata,
                created_at=fragment.created_at,
                accessed_at=fragment.accessed_at,
                access_count=fragment.access_count
            )
            self.db_session.add(db_fragment)
            self.db_session.commit()
        except Exception as e:
            logger.error(f"持久化记忆片段失败：{e}")
            self.db_session.rollback()

    def _prune_fragments(self, user_id: int):
        """清理低重要性记忆"""
        if user_id not in self.memory_fragments:
            return
        
        fragments = self.memory_fragments[user_id]
        
        # 应用重要性衰减
        for fragment in fragments:
            days_old = (datetime.utcnow() - fragment.created_at).days
            fragment.importance *= (self.importance_decay_factor ** days_old)
        
        # 按重要性排序
        fragments.sort(key=lambda f: f.importance, reverse=True)
        
        # 保留 Top N
        if len(fragments) > self.max_fragments_per_user:
            removed = fragments[self.max_fragments_per_user:]
            self.memory_fragments[user_id] = fragments[:self.max_fragments_per_user]
            logger.info(f"清理 {len(removed)} 个低重要性记忆片段")

    def retrieve(self, user_id: int, query: str, top_k: int = 5,
                category: str = None, min_importance: float = 0.3) -> List[MemoryFragment]:
        """
        检索相关记忆
        
        Args:
            user_id: 用户 ID
            query: 查询文本
            top_k: 返回数量
            category: 类别过滤
            min_importance: 最低重要性阈值
        
        Returns:
            List[MemoryFragment]: 相关记忆片段
        """
        if user_id not in self.memory_fragments:
            return []
        
        fragments = self.memory_fragments[user_id]
        
        # 过滤
        filtered = [
            f for f in fragments
            if f.importance >= min_importance
            and (category is None or f.category == category)
        ]
        
        # 排序策略
        if self.vector_store_enabled and self.encoder and fragments[0].embedding:
            # 向量相似度检索
            try:
                query_embedding = self.encoder.encode(query).tolist()
                for fragment in filtered:
                    similarity = self._cosine_similarity(query_embedding, fragment.embedding)
                    fragment.metadata['similarity'] = similarity
                
                filtered.sort(key=lambda f: f.metadata.get('similarity', 0), reverse=True)
            except Exception as e:
                logger.warning(f"向量检索失败，回退到关键词匹配：{e}")
                filtered = self._keyword_match(filtered, query, top_k)
        else:
            # 关键词匹配
            filtered = self._keyword_match(filtered, query, top_k)
        
        # 更新访问统计
        for fragment in filtered[:top_k]:
            fragment.accessed_at = datetime.utcnow()
            fragment.access_count += 1
        
        return filtered[:top_k]

    def _keyword_match(self, fragments: List[MemoryFragment], query: str, top_k: int) -> List[MemoryFragment]:
        """关键词匹配"""
        query_words = set(query.lower().split())
        
        def score(fragment: str) -> float:
            content_words = set(fragment.content.lower().split())
            overlap = len(query_words & content_words)
            return overlap / (len(query_words) + 1)
        
        fragments.sort(key=score, reverse=True)
        return fragments[:top_k]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)

    def aggregate_memories(self, user_id: int, category: str = None,
                          time_range_days: int = 30) -> Dict:
        """
        聚合记忆生成摘要
        
        Args:
            user_id: 用户 ID
            category: 类别
            time_range_days: 时间范围（天）
        
        Returns:
            Dict: 聚合摘要
        """
        if user_id not in self.memory_fragments:
            return {}
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)
        fragments = [
            f for f in self.memory_fragments[user_id]
            if f.created_at >= cutoff_date
            and (category is None or f.category == category)
        ]
        
        if not fragments:
            return {}
        
        # 按类别分组
        by_category = {}
        for fragment in fragments:
            if fragment.category not in by_category:
                by_category[fragment.category] = []
            by_category[fragment.category].append(fragment)
        
        # 生成摘要
        summary = {
            'total_fragments': len(fragments),
            'time_range_days': time_range_days,
            'categories': {}
        }
        
        for cat, frags in by_category.items():
            # 提取高频词
            word_freq = self._extract_frequent_words([f.content for f in frags])
            
            summary['categories'][cat] = {
                'count': len(frags),
                'avg_importance': sum(f.importance for f in frags) / len(frags),
                'top_keywords': word_freq[:10],
                'recent_content': [f.content[:100] for f in sorted(frags, key=lambda x: x.created_at, reverse=True)[:3]]
            }
        
        return summary

    def _extract_frequent_words(self, texts: List[str], top_n: int = 20) -> List[str]:
        """提取高频词"""
        import re
        from collections import Counter
        
        # 中文分词（简单实现）
        words = []
        for text in texts:
            # 提取中文词汇（简单按字符分割）
            chinese_chars = re.findall(r'[\u4e00-\u9fff]+', text)
            words.extend(''.join(chinese_chars))
            
            # 提取英文单词
            english_words = re.findall(r'\b[a-zA-Z]+\b', text)
            words.extend(english_words)
        
        # 统计词频
        word_counts = Counter(words)
        return [word for word, count in word_counts.most_common(top_n)]

    def update_memory_profile(self, user_id: int, new_profile: Dict) -> Dict:
        """
        更新用户记忆画像
        
        Args:
            user_id: 用户 ID
            new_profile: 新画像数据
        
        Returns:
            Dict: 更新后的画像
        """
        # 获取现有画像
        existing = self.retrieve(user_id, "写作画像", category='writing_profile', top_k=1)
        
        if existing:
            # 合并画像
            merged = {**existing[0].metadata, **new_profile}
            self.add_fragment(
                user_id=user_id,
                content=f"写作画像更新：{json.dumps(new_profile, ensure_ascii=False)}",
                category='writing_profile',
                interaction_type='guidance',
                metadata=merged
            )
            return merged
        else:
            # 新建画像
            self.add_fragment(
                user_id=user_id,
                content=f"初始写作画像：{json.dumps(new_profile, ensure_ascii=False)}",
                category='writing_profile',
                interaction_type='guidance',
                metadata=new_profile
            )
            return new_profile

    def get_context_for_interaction(self, user_id: int, current_query: str,
                                   writing_context: Dict = None) -> Dict:
        """
        为当前交互生成上下文
        
        Args:
            user_id: 用户 ID
            current_query: 当前查询
            writing_context: 写作上下文
        
        Returns:
            Dict: 上下文信息
        """
        context = {
            'user_profile': None,
            'relevant_memories': [],
            'writing_history': [],
            'feedback_history': []
        }
        
        # 获取用户画像
        profile_memories = self.retrieve(user_id, "写作画像", category='writing_profile', top_k=1)
        if profile_memories:
            context['user_profile'] = profile_memories[0].metadata
        
        # 获取相关记忆
        relevant = self.retrieve(user_id, current_query, top_k=5, min_importance=0.4)
        context['relevant_memories'] = [
            {'content': f.content, 'category': f.category, 'importance': f.importance}
            for f in relevant
        ]
        
        # 获取写作历史
        writing_history = self.retrieve(user_id, "作文", category='knowledge', top_k=3)
        context['writing_history'] = [
            {'content': f.content[:200], 'metadata': f.metadata}
            for f in writing_history
        ]
        
        # 获取反馈历史
        feedback = self.retrieve(user_id, "反馈", category='feedback', top_k=3)
        context['feedback_history'] = [
            {'content': f.content, 'importance': f.importance}
            for f in feedback
        ]
        
        return context

    def get_stats(self) -> Dict:
        """获取统计信息"""
        total_fragments = sum(len(frags) for frags in self.memory_fragments.values())
        
        return {
            'total_users': len(self.memory_fragments),
            'total_fragments': total_fragments,
            'vector_store_enabled': self.vector_store_enabled,
            'avg_fragments_per_user': total_fragments / max(1, len(self.memory_fragments))
        }


# 数据库模型（可选，用于持久化）
def create_memory_fragment_model(db):
    """创建记忆片段数据库模型"""
    from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
    from sqlalchemy.ext.declarative import declarative_base
    
    Base = declarative_base()
    
    class MemoryFragmentDB(Base):
        __tablename__ = 'memory_fragments'
        
        id = Column(String(64), primary_key=True)
        user_id = Column(Integer, nullable=False, index=True)
        content = Column(Text, nullable=False)
        category = Column(String(64), nullable=False, index=True)
        importance = Column(Float, default=0.5)
        embedding = Column(JSON, nullable=True)  # 向量表示
        metadata = Column(JSON, default=dict)
        created_at = Column(DateTime, nullable=True)
        accessed_at = Column(DateTime, nullable=True)
        access_count = Column(Integer, default=0)
    
    return MemoryFragmentDB
