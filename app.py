"""
文芽 - Flask 应用入口
应用工厂模式，统一初始化扩展、蓝图、错误处理
"""
import os
import logging
from datetime import datetime, timedelta

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

from config import config

db = SQLAlchemy()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)


def create_app(config_name=None):
    """应用工厂函数"""
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    # 安全头
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    CORS(app, supports_credentials=True, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', '*').split(','),
            "supports_credentials": True
        }
    })

    # Flask-Login 配置
    login_manager.login_view = 'auth.login'
    login_manager.session_protection = 'strong'

    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({'error': 'Authentication required'}), 401

    # 日志配置
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 注册蓝图
    from routes.auth import auth_bp
    from routes.api import api_bp
    from routes.writing import writing_bp
    from routes.ranking import ranking_bp
    from routes.community import community_bp
    from routes.memory import memory_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(writing_bp, url_prefix='/api/writing')
    app.register_blueprint(ranking_bp, url_prefix='/api/ranking')
    app.register_blueprint(community_bp, url_prefix='/api/community')
    app.register_blueprint(memory_bp, url_prefix='/api/memory')

    # 全局错误处理
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'message': str(error.description) if hasattr(error, 'description') else None}), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({'error': 'Unauthorized'}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(429)
    def ratelimit_handler(error):
        return jsonify({'error': 'Too many requests', 'message': '请求过于频繁，请稍后再试'}), 429

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.exception('Internal server error')
        return jsonify({'error': 'Internal server error'}), 500

    # 请求日志
    @app.before_request
    def log_request():
        if request.path.startswith('/api/'):
            app.logger.debug(f'{request.method} {request.path} from {request.remote_addr}')

    # 创建数据库表（开发环境）
    with app.app_context():
        if app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite'):
            db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
