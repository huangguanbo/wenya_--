"""
文芽 - 统一响应格式工具
"""
from flask import jsonify


def success_response(data=None, message='success', status_code=200):
    """成功响应"""
    response = {'code': 0, 'message': message}
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code


def error_response(error, message=None, status_code=400):
    """错误响应"""
    response = {'code': 1, 'error': error}
    if message:
        response['message'] = message
    return jsonify(response), status_code


def paginated_response(items, pagination, message='success'):
    """分页响应"""
    return jsonify({
        'code': 0,
        'message': message,
        'data': items,
        'pagination': {
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })
