"""
文芽 - 排行榜模型
"""
from datetime import datetime, timedelta
from app import db


class RankingRecord(db.Model):
    """
    排行榜记录表 - 实时排行榜数据
    存储当前有效的排行榜记录
    """
    __tablename__ = 'ranking_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    grade = db.Column(db.Integer, nullable=False, index=True)  # 年级用于同年级排行
    
    # 排行类型
    rank_type = db.Column(db.String(32), nullable=False)
    # overall: 综合排行（同年级主榜）
    # progress: 进步排行
    # theme: 立意维度榜
    # content: 内容维度榜
    # structure: 结构维度榜
    # language: 语言维度榜
    # creativity: 创意维度榜
    
    # 排行数据
    score = db.Column(db.Float, nullable=False)  # 用于排行的分数
    percentile = db.Column(db.Float, nullable=True)  # 百分位（如 62 表示超过 62% 的人）
    rank_position = db.Column(db.Integer, nullable=True)  # 排名位置
    
    # 统计周期
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)
    is_hidden = db.Column(db.Boolean, default=False)  # 是否隐藏（用户退出排行或分数过低）
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'rank_type': self.rank_type,
            'score': round(self.score, 1),
            'percentile': round(self.percentile, 1) if self.percentile else None,
            'rank_position': self.rank_position,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'is_hidden': self.is_hidden
        }
    
    def __repr__(self):
        return f'<RankingRecord user_{self.user_id} {self.rank_type}>'


class RankingHistory(db.Model):
    """
    排行榜历史表 - 成长曲线数据
    存储历史排行记录，用于生成个人成长曲线
    """
    __tablename__ = 'ranking_histories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    grade = db.Column(db.Integer, nullable=False)
    
    # 数据类型
    data_type = db.Column(db.String(32), nullable=False)
    # average_score: 平均分时
    # percentile: 百分位
    # rank_position: 排名
    # writing_count: 写作数量
    
    # 数据值
    value = db.Column(db.Float, nullable=False)
    
    # 时间维度
    recorded_date = db.Column(db.Date, nullable=False, index=True)  # 按日期聚合
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'data_type': self.data_type,
            'value': round(self.value, 2),
            'recorded_date': self.recorded_date.isoformat() if self.recorded_date else None
        }
    
    def __repr__(self):
        return f'<RankingHistory user_{self.user_id} {self.data_type}>'
