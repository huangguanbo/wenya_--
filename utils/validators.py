"""
文芽 - 输入校验工具
"""
import re


def validate_username(username):
    """
    校验用户名
    规则：3-32 位，字母、数字、下划线、中文
    """
    if not username:
        return False, '用户名不能为空'
    if len(username) < 3:
        return False, '用户名至少 3 个字符'
    if len(username) > 32:
        return False, '用户名最多 32 个字符'
    if not re.match(r'^[\w\u4e00-\u9fa5]+$', username):
        return False, '用户名只能包含字母、数字、下划线和中文'
    return True, None


def validate_password(password):
    """
    校验密码强度
    规则：至少 8 位，包含字母和数字
    """
    if not password:
        return False, '密码不能为空'
    if len(password) < 8:
        return False, '密码至少 8 个字符'
    if not re.search(r'[a-zA-Z]', password):
        return False, '密码必须包含字母'
    if not re.search(r'[0-9]', password):
        return False, '密码必须包含数字'
    return True, None


def validate_phone(phone):
    """
    校验手机号（中国大陆）
    """
    if not phone:
        return False, '手机号不能为空'
    if not re.match(r'^1[3-9]\d{9}$', phone):
        return False, '请输入有效的 11 位手机号'
    return True, None


def validate_grade(grade):
    """
    校验年级（1-12）
    """
    try:
        grade = int(grade)
    except (TypeError, ValueError):
        return False, '年级必须为数字'
    if grade < 1 or grade > 12:
        return False, '年级必须在 1-12 之间'
    return True, None


def validate_content_length(content, min_len=10, max_len=100000):
    """
    校验内容长度
    """
    if not content:
        return False, '内容不能为空'
    if len(content) < min_len:
        return False, f'内容至少 {min_len} 个字符'
    if len(content) > max_len:
        return False, f'内容最多 {max_len} 个字符'
    return True, None
