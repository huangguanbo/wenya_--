"""
文芽 - 合规模型
"""
from datetime import datetime, timedelta
from app import db


def _default_expires_at():
    """合规日志默认过期时间：6 个月后"""
    return datetime.utcnow() + timedelta(days=180)


class ComplianceLog(db.Model):
    """
    合规日志表 - 全程留痕
    所有 AI 交互、用户操作、审核记录保存不少于 6 个月
    """
    __tablename__ = 'compliance_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 日志类型
    log_type = db.Column(db.String(32), nullable=False, index=True)
    # ai_interaction: AI 交互
    # user_action: 用户操作
    # content_review: 内容审核
    # guardian_consent: 监护人同意
    # data_export: 数据导出
    # privacy_action: 隐私操作
    
    # 关联对象
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    related_id = db.Column(db.Integer, nullable=True)  # 相关对象 ID（作文 ID、会话 ID 等）
    related_type = db.Column(db.String(32), nullable=True)  # 相关对象类型
    
    # 操作详情
    action = db.Column(db.String(64), nullable=False)
    details = db.Column(db.JSON, nullable=True)  # 详细数据（结构化存储）
    
    # 合规审查
    is_sensitive = db.Column(db.Boolean, default=False)  # 是否涉及敏感内容
    review_status = db.Column(db.String(32), default='none')
    # none: 无需审核
    # pending: 待审核
    # approved: 已通过
    # flagged: 已标记
    
    # IP 和设备信息（用于安全审计）
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    # 时间戳（用于 6 个月保存期限计算）
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    expires_at = db.Column(db.DateTime, default=_default_expires_at, index=True)  # 过期时间（默认 6 个月）
    
    # 索引
    __table_args__ = (
        db.Index('idx_compliance_type_created', 'log_type', 'created_at'),
    )
    
    def to_dict(self):
        return {
            'log_type': self.log_type,
            'user_id': self.user_id,
            'related_id': self.related_id,
            'related_type': self.related_type,
            'action': self.action,
            'details': self.details,
            'is_sensitive': self.is_sensitive,
            'review_status': self.review_status,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    def __repr__(self):
        return f'<ComplianceLog {self.log_type} {self.action}>'


class AlgorithmLog(db.Model):
    """
    算法备案日志表 - AI 算法透明度
    记录 AI 算法决策过程，用于网信办年度合规审计
    """
    __tablename__ = 'algorithm_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 算法类型
    algorithm_type = db.Column(db.String(64), nullable=False)
    # writing_score: 作文评分算法
    # ranking_calculation: 排行榜计算算法
    # content_filter: 内容过滤算法
    # ai_response: AI 回复生成算法
    
    # 输入数据（脱敏）
    input_summary = db.Column(db.JSON, nullable=True)  # 输入摘要（不包含完整内容）
    input_hash = db.Column(db.String(64), nullable=True)  # 输入数据哈希（用于追溯）
    
    # 输出结果
    output_summary = db.Column(db.JSON, nullable=True)  # 输出摘要
    confidence_score = db.Column(db.Float, nullable=True)  # 置信度
    
    # 算法版本（用于追溯和回滚）
    algorithm_version = db.Column(db.String(32), nullable=False)
    model_version = db.Column(db.String(64), nullable=True)  # AI 模型版本
    
    # 决策因子（可解释性）
    decision_factors = db.Column(db.JSON, nullable=True)  # 关键决策因子
    
    # 异常情况
    is_anomaly = db.Column(db.Boolean, default=False)
    anomaly_reason = db.Column(db.String(255), nullable=True)
    
    # 人工干预
    is_human_reviewed = db.Column(db.Boolean, default=False)
    human_reviewer = db.Column(db.String(64), nullable=True)
    human_review_result = db.Column(db.String(32), nullable=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 索引（便于审计查询）
    __table_args__ = (
        db.Index('idx_algorithm_type_created', 'algorithm_type', 'created_at'),
    )
    
    def to_dict(self):
        return {
            'algorithm_type': self.algorithm_type,
            'input_summary': self.input_summary,
            'output_summary': self.output_summary,
            'confidence_score': round(self.confidence_score, 2) if self.confidence_score else None,
            'algorithm_version': self.algorithm_version,
            'model_version': self.model_version,
            'decision_factors': self.decision_factors,
            'is_anomaly': self.is_anomaly,
            'is_human_reviewed': self.is_human_reviewed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AlgorithmLog {self.algorithm_type}>'
