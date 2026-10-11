"""
文芽 - 社区模型
"""
from datetime import datetime
from app import db


class CommunityWork(db.Model):
    """
    社区作品表 - 公开展示的作文
    """
    __tablename__ = 'community_works'
    
    id = db.Column(db.Integer, primary_key=True)
    writing_id = db.Column(db.Integer, db.ForeignKey('writings.id'), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # 作品信息（冗余存储，便于查询）
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    word_count = db.Column(db.Integer, default=0)
    
    # 作者信息（冗余存储）
    author_grade = db.Column(db.Integer, nullable=False)  # 作者年级
    author_school_stage = db.Column(db.String(32), nullable=False)  # 学段
    
    # 评分信息
    overall_score = db.Column(db.Float, nullable=True)
    dimension_scores = db.Column(db.JSON, nullable=True)  # 维度得分
    
    # 互动统计
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    
    # 审核状态（社区作品需要更严格的审核）
    review_status = db.Column(db.String(32), default='pending')
    # pending: 待审核
    # approved: 已通过
    # rejected: 已拒绝
    # needs_revision: 需修改
    
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewed_by = db.Column(db.String(64), nullable=True)
    rejection_reason = db.Column(db.String(255), nullable=True)
    
    # 标签和分类
    tags = db.Column(db.JSON, default=list)  # 作品标签
    genre = db.Column(db.String(64), nullable=True)  # 文体
    
    # 状态
    is_featured = db.Column(db.Boolean, default=False)  # 是否精选
    is_deleted = db.Column(db.Boolean, default=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    likes = db.relationship('WorkLike', backref='work', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('WorkComment', backref='work', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_content=True):
        result = {
            'id': self.id,
            'writing_id': self.writing_id,
            'user_id': self.user_id,
            'title': self.title,
            'word_count': self.word_count,
            'author_grade': self.author_grade,
            'author_school_stage': self.author_school_stage,
            'overall_score': round(self.overall_score, 1) if self.overall_score else None,
            'dimension_scores': self.dimension_scores,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'view_count': self.view_count,
            'tags': self.tags,
            'genre': self.genre,
            'is_featured': self.is_featured,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_content:
            result['content'] = self.content
        
        return result
    
    def __repr__(self):
        return f'<CommunityWork {self.title}>'


class WorkLike(db.Model):
    """作品点赞表"""
    __tablename__ = 'work_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    work_id = db.Column(db.Integer, db.ForeignKey('community_works.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 防止重复点赞
    __table_args__ = (
        db.UniqueConstraint('work_id', 'user_id', name='unique_work_user_like'),
    )
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WorkLike work_{self.work_id} user_{self.user_id}>'


class WorkComment(db.Model):
    """作品评论表"""
    __tablename__ = 'work_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    work_id = db.Column(db.Integer, db.ForeignKey('community_works.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('work_comments.id'), nullable=True)  # 父评论 ID（回复功能）
    
    content = db.Column(db.Text, nullable=False)
    
    # 审核
    is_approved = db.Column(db.Boolean, default=True)  # 默认通过，敏感词触发审核
    is_deleted = db.Column(db.Boolean, default=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    replies = db.relationship('WorkComment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'work_id': self.work_id,
            'user_id': self.user_id,
            'content': self.content,
            'parent_id': self.parent_id,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<WorkComment {self.id}>'
