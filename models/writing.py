"""
文芽 - 写作模型
"""
from datetime import datetime
from app import db


class Writing(db.Model):
    """作文表"""
    __tablename__ = 'writings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # 题目信息
    title = db.Column(db.String(200), nullable=False)
    prompt = db.Column(db.Text, nullable=True)  # 写作提示/要求
    
    # 内容
    content = db.Column(db.Text, nullable=False)  # 正文
    word_count = db.Column(db.Integer, default=0)  # 字数
    
    # 评分
    overall_score = db.Column(db.Float, nullable=True)  # 总分
    is_scored = db.Column(db.Boolean, default=False)  # 是否已评分
    
    # 状态
    status = db.Column(db.String(32), default='draft')  # draft:草稿，submitted:已提交，published:已发布
    is_public = db.Column(db.Boolean, default=False)  # 是否公开到社区
    is_deleted = db.Column(db.Boolean, default=False)
    
    # 审核
    review_status = db.Column(db.String(32), default='pending')  # pending:待审核，approved:通过，rejected:拒绝
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewed_by = db.Column(db.String(64), nullable=True)  # 审核人/AI
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = db.Column(db.DateTime, nullable=True, index=True)
    published_at = db.Column(db.DateTime, nullable=True)
    
    # 索引
    __table_args__ = (
        db.Index('idx_writing_user_status', 'user_id', 'status'),
        db.Index('idx_writing_user_created', 'user_id', 'created_at'),
    )
    
    # 关联
    scores = db.relationship('WritingScore', backref='writing', uselist=False, cascade='all, delete-orphan')
    drafts = db.relationship('WritingDraft', backref='writing', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_content=True, include_scores=True):
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'author': self.author.to_dict() if hasattr(self, 'author') else None,
            'title': self.title,
            'prompt': self.prompt,
            'word_count': self.word_count,
            'overall_score': round(self.overall_score, 1) if self.overall_score else None,
            'is_scored': self.is_scored,
            'status': self.status,
            'is_public': self.is_public,
            'review_status': self.review_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_content:
            result['content'] = self.content
        
        if include_scores and self.scores:
            result['scores'] = self.scores.to_dict()
        
        return result
    
    def __repr__(self):
        return f'<Writing {self.title}>'


class WritingDraft(db.Model):
    """作文草稿表 - 自动保存"""
    __tablename__ = 'writing_drafts'
    
    id = db.Column(db.Integer, primary_key=True)
    writing_id = db.Column(db.Integer, db.ForeignKey('writings.id'), nullable=False, index=True)
    
    # 草稿内容
    content = db.Column(db.Text, nullable=False)
    word_count = db.Column(db.Integer, default=0)
    
    # 版本
    version = db.Column(db.Integer, default=1)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WritingDraft {self.writing_id} v{self.version}>'


class WritingScore(db.Model):
    """作文评分表 - 七维度评分体系"""
    __tablename__ = 'writing_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    writing_id = db.Column(db.Integer, db.ForeignKey('writings.id'), unique=True, nullable=False)
    
    # 七大维度评分 (1-100)
    task_score = db.Column(db.Integer, nullable=True)      # 任务完成
    theme_score = db.Column(db.Integer, nullable=True)     # 主题立意
    content_score = db.Column(db.Integer, nullable=True)   # 内容充实
    structure_score = db.Column(db.Integer, nullable=True) # 结构逻辑
    language_score = db.Column(db.Integer, nullable=True)  # 语言表达
    genre_score = db.Column(db.Integer, nullable=True)     # 文体规范
    thinking_score = db.Column(db.Integer, nullable=True)  # 思维深度
    
    # 权重（根据学段动态调整）
    weights = db.Column(db.JSON, nullable=True)
    
    # AI 评语
    ai_comment = db.Column(db.Text, nullable=True)  # 总体评语
    ai_suggestions = db.Column(db.JSON, nullable=True)  # 改进建议列表
    
    # 评分可信度
    confidence = db.Column(db.Float, default=0.0)  # AI 评分置信度 0-1
    needs_human_review = db.Column(db.Boolean, default=False)  # 是否需要人工复审
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def calculate_overall(self):
        """计算总分"""
        scores = [
            self.task_score, self.theme_score, self.content_score,
            self.structure_score, self.language_score, self.genre_score,
            self.thinking_score
        ]
        if any(s is None for s in scores):
            return 0
        
        # 默认权重（可被学段权重覆盖）
        default_weights = {
            'task': 0.10,
            'theme': 0.15,
            'content': 0.20,
            'structure': 0.15,
            'language': 0.20,
            'genre': 0.10,
            'thinking': 0.10
        }
        
        weights = self.weights or default_weights
        
        total = (
            self.task_score * weights.get('task', 0.10) +
            self.theme_score * weights.get('theme', 0.15) +
            self.content_score * weights.get('content', 0.20) +
            self.structure_score * weights.get('structure', 0.15) +
            self.language_score * weights.get('language', 0.20) +
            self.genre_score * weights.get('genre', 0.10) +
            self.thinking_score * weights.get('thinking', 0.10)
        )
        
        return round(total, 1)
    
    def to_dict(self):
        return {
            'task_score': self.task_score,
            'theme_score': self.theme_score,
            'content_score': self.content_score,
            'structure_score': self.structure_score,
            'language_score': self.language_score,
            'genre_score': self.genre_score,
            'thinking_score': self.thinking_score,
            'overall_score': self.calculate_overall(),
            'weights': self.weights,
            'ai_comment': self.ai_comment,
            'ai_suggestions': self.ai_suggestions,
            'confidence': round(self.confidence, 2),
            'needs_human_review': self.needs_human_review,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<WritingScore {self.writing_id}>'
