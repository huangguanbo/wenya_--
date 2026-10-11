"""
文芽 - 配置模块
"""
import os
from datetime import timedelta


class Config:
    """基础配置"""
    # 安全
    SECRET_KEY = os.environ.get('SECRET_KEY', 'wenya-dev-secret-key-change-in-prod')
    
    # 数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'postgresql://postgres:postgres@localhost:5432/wenya'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # 会话
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # 上传
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # AI
    AI_API_BASE = os.environ.get('AI_API_BASE', 'https://api.openai.com/v1')
    AI_API_KEY = os.environ.get('AI_API_KEY', '')
    AI_MODEL = os.environ.get('AI_MODEL', 'gpt-4')
    AI_MAX_TOKENS = 2000
    AI_TEMPERATURE = 0.7
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'openai')  # openai/claude/aliyun/deepseek/moonshot
    AI_ENABLE_MEMORY = os.environ.get('AI_ENABLE_MEMORY', 'true').lower() == 'true'
    AI_ENABLE_CACHE = os.environ.get('AI_ENABLE_CACHE', 'true').lower() == 'true'
    
    # 内容安全
    CONTENT_SAFE_API_KEY = os.environ.get('CONTENT_SAFE_API_KEY', '')
    CONTENT_SAFE_ENABLED = os.environ.get('CONTENT_SAFE_ENABLED', 'false').lower() == 'true'
    
    # 限流
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    
    # 日志
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # 合规
    ICP_NUMBER = os.environ.get('ICP_NUMBER', '')  # ICP 备案号
    ALGORITHM_NUMBER = os.environ.get('ALGORITHM_NUMBER', '')  # 算法备案号
    
    # 前端
    VITE_API_URL = os.environ.get('VITE_API_URL', 'http://localhost:5000/api')


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
