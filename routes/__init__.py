"""
文芽 - 路由模块
"""
from routes.auth import auth_bp
from routes.api import api_bp
from routes.writing import writing_bp
from routes.ranking import ranking_bp
from routes.community import community_bp

__all__ = [
    'auth_bp',
    'api_bp',
    'writing_bp',
    'ranking_bp',
    'community_bp'
]
