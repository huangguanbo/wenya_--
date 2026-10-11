"""
文芽 - AI 记忆模型（三层记忆架构）
"""
from datetime import datetime
from app import db


class AIMemory(db.Model):
    """
    AI 专属记忆表 - 三层记忆架构
    每个用户一条记录，存储结构化的长期记忆
    """
    __tablename__ = 'ai_memories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # L1·写作画像层（长期记忆）
    # 记录学段、优势/弱势文体、常错类型、修辞偏好等结构化信息
    writing_profile = db.Column(db.JSON, default=lambda: {
        'school_stage': None,        # 学段：elementary/middle/high
        'grade': None,               # 年级
        'strength_genres': [],       # 优势文体
        'weakness_genres': [],       # 弱势文体
        'common_errors': [],         # 常错类型
        'rhetoric_preferences': [],  # 修辞偏好
        'writing_style': [],         # 写作风格标签
        'improvement_areas': []      # 需要改进的领域
    })
    
    # L2·写作知识库层（领域记忆）
    # 存储素材积累、范文学习、修改历史
    knowledge_base = db.Column(db.JSON, default=lambda: {
        'favorite_materials': [],    # 常用素材
        'learned_examples': [],      # 学习过的范文 ID
        'revision_history': [],      # 重要修改历史摘要
        'accumulated_phrases': [],   # 积累的好词好句
        'topic_clusters': []         # 写过的主题聚类
    })
    
    # 记忆更新元数据
    last_interaction_at = db.Column(db.DateTime, nullable=True)
    total_interactions = db.Column(db.Integer, default=0)
    memory_version = db.Column(db.String(32), default='v1.0')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    conversations = db.relationship('AIConversation', backref='memory', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'writing_profile': self.writing_profile,
            'knowledge_base': self.knowledge_base,
            'last_interaction_at': self.last_interaction_at.isoformat() if self.last_interaction_at else None,
            'total_interactions': self.total_interactions,
            'memory_version': self.memory_version
        }
    
    def __repr__(self):
        return f'<AIMemory user_{self.user_id}>'


class AIConversation(db.Model):
    """
    AI 会话记录表 - L3 会话上下文层（短期记忆）
    保存当前写作任务的对话历史，确保辅导逻辑连贯
    """
    __tablename__ = 'ai_conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    memory_id = db.Column(db.Integer, db.ForeignKey('ai_memories.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    writing_id = db.Column(db.Integer, db.ForeignKey('writings.id'), nullable=True)
    
    # 会话类型
    session_type = db.Column(db.String(32), default='writing_guidance')
    # writing_guidance: 写作指导
    # brainstorming: 头脑风暴
    # revision: 修改建议
    # scoring: 评分解释
    
    # 对话内容
    messages = db.Column(db.JSON, default=list)  # 对话历史 [{role, content, timestamp}]
    
    # 上下文摘要（用于长期记忆更新）
    summary = db.Column(db.Text, nullable=True)
    key_points = db.Column(db.JSON, default=list)  # 关键点提取
    
    # 合规审查
    is_filtered = db.Column(db.Boolean, default=False)  # 是否被内容安全过滤
    filter_reason = db.Column(db.String(255), nullable=True)
    
    # 状态
    is_completed = db.Column(db.Boolean, default=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_type': self.session_type,
            'messages': self.messages,
            'summary': self.summary,
            'key_points': self.key_points,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AIConversation {self.id}>'
