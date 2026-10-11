"""
文芽 - 认证路由
"""
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random
import string

from app import db, limiter
from models.user import User, Guardian, UserProfile
from models.ai_memory import AIMemory
from models.writing import Writing
from models.compliance import ComplianceLog
from utils.validators import (
    validate_username, validate_password, validate_phone, validate_grade
)
from utils.response import success_response, error_response
from utils.helpers import get_client_ip

auth_bp = Blueprint('auth', __name__)

# 临时存储验证码（生产环境应使用 Redis）
verification_codes = {}

CODE_EXPIRE_MINUTES = 5


def generate_verification_code(length=6):
    """生成验证码"""
    return ''.join(random.choices(string.digits, k=length))


def cleanup_expired_codes():
    """清理过期验证码"""
    now = datetime.utcnow()
    expired_keys = [k for k, v in verification_codes.items() if v['expires_at'] < now]
    for k in expired_keys:
        del verification_codes[k]


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per hour")
def register():
    """用户注册（需监护人同意验证）"""
    data = request.get_json()
    if not data:
        return error_response('Invalid request', status_code=400)

    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    grade = data.get('grade')
    birth_date_str = data.get('birth_date')

    guardian_name = (data.get('guardian_name') or '').strip()
    guardian_phone = (data.get('guardian_phone') or '').strip()
    guardian_relationship = data.get('guardian_relationship') or ''
    guardian_verification_code = data.get('guardian_verification_code') or ''

    # 字段校验
    ok, msg = validate_username(username)
    if not ok:
        return error_response(msg, status_code=400)

    ok, msg = validate_password(password)
    if not ok:
        return error_response(msg, status_code=400)

    ok, msg = validate_grade(grade)
    if not ok:
        return error_response(msg, status_code=400)

    ok, msg = validate_phone(guardian_phone)
    if not ok:
        return error_response(msg, status_code=400)

    if not guardian_name:
        return error_response('监护人姓名不能为空', status_code=400)

    if User.query.filter_by(username=username).first():
        return error_response('用户名已存在', status_code=409)

    # 解析出生日期
    birth_date = None
    if birth_date_str:
        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        except ValueError:
            return error_response('出生日期格式无效', status_code=400)

    # 清理过期验证码
    cleanup_expired_codes()

    # 验证监护人验证码
    guardian_key = f"guardian:{guardian_phone}"
    stored = verification_codes.get(guardian_key)
    if not stored:
        return error_response('验证码未发送或已过期，请重新获取', status_code=400)

    if stored['expires_at'] < datetime.utcnow():
        del verification_codes[guardian_key]
        return error_response('验证码已过期，请重新获取', status_code=400)

    if guardian_verification_code != stored['code']:
        return error_response('验证码错误', status_code=400)

    # 创建监护人
    guardian = Guardian(
        name=guardian_name,
        phone=guardian_phone,
        relationship=guardian_relationship,
        is_verified=True,
        verified_at=datetime.utcnow(),
        verification_method='sms',
        consent_given_at=datetime.utcnow(),
        consent_expires_at=datetime.utcnow() + timedelta(days=365 * 3)
    )
    db.session.add(guardian)
    db.session.flush()

    # 创建用户
    user = User(
        username=username,
        grade=grade,
        birth_date=birth_date,
        is_guardian_verified=True,
        guardian_id=guardian.id
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    # 创建用户画像 & AI 记忆
    profile = UserProfile(user_id=user.id)
    ai_memory = AIMemory(user_id=user.id)
    db.session.add(profile)
    db.session.add(ai_memory)

    # 合规日志
    compliance_log = ComplianceLog(
        log_type='guardian_consent',
        user_id=user.id,
        action='guardian_verification_completed',
        details={'guardian_name': guardian_name, 'guardian_phone': guardian_phone},
        ip_address=get_client_ip()
    )
    db.session.add(compliance_log)

    db.session.commit()

    # 清理验证码
    del verification_codes[guardian_key]

    login_user(user)

    return success_response({'user': user.to_dict()}, message='注册成功', status_code=201)


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per hour")
def login():
    """用户登录"""
    data = request.get_json()
    if not data:
        return error_response('Invalid request', status_code=400)

    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return error_response('用户名和密码不能为空', status_code=400)

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return error_response('用户名或密码错误', status_code=401)

    if not user.is_active:
        return error_response('账号已被停用', status_code=403)

    user.last_login_at = datetime.utcnow()
    db.session.commit()

    login_user(user, remember=bool(data.get('remember', False)))

    compliance_log = ComplianceLog(
        log_type='user_action',
        user_id=user.id,
        action='user_login',
        details={'username': username},
        ip_address=get_client_ip()
    )
    db.session.add(compliance_log)
    db.session.commit()

    return success_response({'user': user.to_dict()}, message='登录成功')


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """用户登出"""
    compliance_log = ComplianceLog(
        log_type='user_action',
        user_id=current_user.id,
        action='user_logout',
        ip_address=get_client_ip()
    )
    db.session.add(compliance_log)
    db.session.commit()

    logout_user()
    return success_response(message='已退出登录')


@auth_bp.route('/change-password', methods=['POST'])
@login_required
@limiter.limit("10 per hour")
def change_password():
    """修改密码"""
    data = request.get_json()
    if not data:
        return error_response('Invalid request', status_code=400)

    old_password = data.get('old_password') or ''
    new_password = data.get('new_password') or ''

    if not current_user.check_password(old_password):
        return error_response('原密码错误', status_code=400)

    ok, msg = validate_password(new_password)
    if not ok:
        return error_response(msg, status_code=400)

    if old_password == new_password:
        return error_response('新密码不能与原密码相同', status_code=400)

    current_user.set_password(new_password)
    db.session.commit()

    compliance_log = ComplianceLog(
        log_type='user_action',
        user_id=current_user.id,
        action='password_change',
        ip_address=get_client_ip()
    )
    db.session.add(compliance_log)
    db.session.commit()

    return success_response(message='密码修改成功')


@auth_bp.route('/profile', methods=['GET', 'PUT'])
@login_required
def profile():
    """获取/更新用户资料"""
    if request.method == 'GET':
        return success_response({
            'user': current_user.to_dict(),
            'profile': current_user.profile.to_dict() if current_user.profile else None
        })

    # PUT - 更新资料
    data = request.get_json()
    if not data:
        return error_response('Invalid request', status_code=400)

    allowed_fields = ['nickname', 'avatar', 'bio']
    for field in allowed_fields:
        if field in data:
            value = data[field]
            if isinstance(value, str) and len(value) > 500:
                return error_response(f'{field} 内容过长', status_code=400)
            setattr(current_user, field, value)

    if 'grade' in data:
        ok, msg = validate_grade(data['grade'])
        if not ok:
            return error_response(msg, status_code=400)
        current_user.grade = data['grade']

    db.session.commit()
    return success_response({'user': current_user.to_dict()}, message='资料更新成功')


@auth_bp.route('/export-data', methods=['POST'])
@login_required
@limiter.limit("3 per day")
def export_data():
    """导出用户数据（合规要求：数据可携带权）"""
    writings = Writing.query.filter_by(user_id=current_user.id).all()
    profile = current_user.profile

    export = {
        'user': current_user.to_dict(),
        'profile': profile.to_dict() if profile else None,
        'writings': [w.to_dict(include_content=True, include_scores=True) for w in writings],
        'exported_at': datetime.utcnow().isoformat()
    }

    compliance_log = ComplianceLog(
        log_type='compliance',
        user_id=current_user.id,
        action='data_export',
        ip_address=get_client_ip()
    )
    db.session.add(compliance_log)
    db.session.commit()

    return success_response(export, message='数据导出成功')


@auth_bp.route('/send-guardian-code', methods=['POST'])
@limiter.limit("3 per hour")
def send_guardian_code():
    """发送监护人验证码"""
    data = request.get_json()
    if not data:
        return error_response('Invalid request', status_code=400)

    phone = (data.get('phone') or '').strip()

    ok, msg = validate_phone(phone)
    if not ok:
        return error_response(msg, status_code=400)

    # 清理过期验证码
    cleanup_expired_codes()

    code = generate_verification_code()

    verification_codes[f"guardian:{phone}"] = {
        'code': code,
        'expires_at': datetime.utcnow() + timedelta(minutes=CODE_EXPIRE_MINUTES)
    }

    current_app.logger.info(f"监护人验证码 [{phone}]: {code}")

    compliance_log = ComplianceLog(
        log_type='guardian_consent',
        action='verification_code_sent',
        details={'phone': phone},
        ip_address=get_client_ip()
    )
    db.session.add(compliance_log)
    db.session.commit()

    return success_response(message='验证码已发送')


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """获取当前用户信息"""
    return success_response({
        'user': current_user.to_dict(),
        'profile': current_user.profile.to_dict() if current_user.profile else None
    })
