"""
文芽 - 辅助工具函数
"""
import re
import random
import string
from flask import request


def count_words(text):
    """
    统计字数（中文按字，英文按词）
    """
    if not text:
        return 0
    chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', text))
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    return chinese_chars + english_words


def get_client_ip():
    """获取客户端真实 IP（处理反向代理）"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    if request.headers.get('X-Real-IP'):
        return request.headers['X-Real-IP']
    return request.remote_addr


def generate_random_string(length=16):
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def calculate_percentile(scores, value):
    """
    计算百分位
    """
    if not scores:
        return 0
    sorted_scores = sorted(scores)
    count = sum(1 for s in sorted_scores if s <= value)
    return round((count / len(sorted_scores)) * 100, 1)
