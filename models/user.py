"""
文芽 - 用户模型
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # 用户信息
    nickname = db.Column(db.String(64), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    grade = db.Column(db.Integer, nullable=True)  # 1-12 年级
    birth_date = db.Column(db.Date, nullable=True)  # 用于计算年龄和年级
    
    # 监护人验证
    is_guardian_verified = db.Column(db.Boolean, default=False)
    guardian_id = db.Column(db.Integer, db.ForeignKey('guardians.id'), nullable=True)
    
    # 隐私设置
    show_in_ranking = db.Column(db.Boolean, default=True)  # 是否显示在排行榜
    show_works_publicly = db.Column(db.Boolean, default=True)  # 是否公开展示作品
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, nullable=True)
    
    # 关联
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    guardian = db.relationship('Guardian', backref='users', uselist=False)
    writings = db.relationship('Writing', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    ai_memory = db.relationship('AIMemory', backref='user', uselist=False, cascade='all, delete-orphan')
    community_works = db.relationship('CommunityWork', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_age(self):
        """获取年龄"""
        if not self.birth_date:
            return None
        today = datetime.today().date()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age
    
    def get_school_stage(self):
        """获取学段"""
        if not self.grade:
            return None
        if 1 <= self.grade <= 6:
            return 'elementary'  # 小学
        elif 7 <= self.grade <= 9:
            return 'middle'  # 初中
        elif 10 <= self.grade <= 12:
            return 'high'  # 高中
        return None
    
    def to_dict(self):
        """转换为字典（不包含敏感信息）"""
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'avatar_url': self.avatar_url,
            'grade': self.grade,
            'school_stage': self.get_school_stage(),
            'is_guardian_verified': self.is_guardian_verified,
            'show_in_ranking': self.show_in_ranking,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class Guardian(db.Model):
    """监护人表"""
    __tablename__ = 'guardians'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True)
    relationship = db.Column(db.String(32), nullable=False)  # 父子/母子/父女/母女等
    
    # 验证信息
    is_verified = db.Column(db.Boolean, default=False)
    verified_at = db.Column(db.DateTime, nullable=True)
    verification_method = db.Column(db.String(32), nullable=True)  # sms/email
    
    # 同意记录（根据法律要求保存至未成年人年满 14 周岁后 3 年）
    consent_given_at = db.Column(db.DateTime, nullable=False)
    consent_expires_at = db.Column(db.DateTime, nullable=True)  # 年满 14 周岁后 3 年
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'relationship': self.relationship,
            'is_verified': self.is_verified,
            'consent_given_at': self.consent_given_at.isoformat() if self.consent_given_at else None
        }
    
    def __repr__(self):
        return f'<Guardian {self.name}>'


class UserProfile(db.Model):
    """用户画像表 - 存储写作能力标签"""
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # 写作能力标签
    strength_tags = db.Column(db.JSON, default=list)  # 优势标签
    weakness_tags = db.Column(db.JSON, default=list)  # 弱势标签
    preferred_genres = db.Column(db.JSON, default=list)  # 偏好文体
    
    # 统计数据
    total_writings = db.Column(db.Integer, default=0)  # 总写作数
    average_score = db.Column(db.Float, default=0.0)  # 平均分
    consecutive_days = db.Column(db.Integer, default=0)  # 连续写作天数
    best_score = db.Column(db.Float, default=0.0)  # 最高分
    
    # 维度得分（雷达图数据）
    dimension_scores = db.Column(db.JSON, default=lambda: {
        'theme': 0,      # 立意
        'content': 0,    # 内容
        'structure': 0,  # 结构
        'language': 0,   # 语言
        'creativity': 0  # 创意
    })
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'strength_tags': self.strength_tags,
            'weakness_tags': self.weakness_tags,
            'preferred_genres': self.preferred_genres,
            'total_writings': self.total_writings,
            'average_score': round(self.average_score, 1),
            'consecutive_days': self.consecutive_days,
            'best_score': round(self.best_score, 1),
            'dimension_scores': self.dimension_scores
        }
    
    def __repr__(self):
        return f'<UserProfile {self.user_id}>'
