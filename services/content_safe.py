"""
文芽 - 内容安全服务模块
负责 AI 输出和用户上传内容的合规过滤
"""
import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


SENSITIVE_WORDS: List[str] = [
    "违法", "毒品", "赌博", "色情", "淫秽", "诈骗", "贿赂", "贪污",
    "恐怖", "爆炸", "杀人", "自杀", "自残", "暴力", "虐待", "强奸",
    "邪教", "迷信", "传销", "走私", "洗钱", "贩毒", "卖淫", "嫖娼",
    "抢劫", "盗窃", "欺诈", "诽谤", "侮辱", "歧视", "仇恨",
    "fuck", "shit", "bitch", "dick", "pussy", "cunt", "asshole"
]

SAFE_RESPONSE = '抱歉，我需要专注于写作指导。让我们继续讨论你的作文吧。'

_sensitive_compiled = [re.compile(re.escape(w), re.IGNORECASE) for w in SENSITIVE_WORDS]


class ContentSafeService:
    """内容安全审核服务"""

    def __init__(self, api_key=None, enabled=None, min_length=10, max_length=100000):
        try:
            from flask import current_app
            has_app = current_app and current_app.config
        except (RuntimeError, ImportError):
            has_app = False

        if has_app:
            self.api_key = api_key or current_app.config.get('CONTENT_SAFE_API_KEY')
            self.enabled = enabled if enabled is not None else current_app.config.get('CONTENT_SAFE_ENABLED', False)
        else:
            self.api_key = api_key
            self.enabled = enabled if enabled is not None else False
        self.min_length = min_length
        self.max_length = max_length

    def check_content(self, content: str) -> Dict:
        """
        检查内容安全性
        返回：{'is_safe': bool, 'reason': str or None, 'hit_word': str or None}
        """
        if not content:
            return {'is_safe': True, 'reason': None, 'hit_word': None}

        try:
            # 1. 敏感词检测（始终启用本地词库，保证基础合规）
            hit = self._check_sensitive_words(content)
            if hit:
                return {
                    'is_safe': False,
                    'reason': f'包含不当内容',
                    'hit_word': hit
                }

            # 2. 长度检测
            if len(content) < self.min_length:
                return {
                    'is_safe': False,
                    'reason': '内容过短',
                    'hit_word': None
                }

            if len(content) > self.max_length:
                return {
                    'is_safe': False,
                    'reason': '内容过长',
                    'hit_word': None
                }

            # 3. 拟人化检查（检测是否在诱导 AI 扮演非写作教练角色）
            if self._check_anthropomorphic(content):
                return {
                    'is_safe': False,
                    'reason': '请专注于写作练习相关的交流',
                    'hit_word': None
                }

            # 4. 第三方内容安全 API（可选，未启用时跳过）
            if self.enabled and self.api_key:
                api_result = self._call_safe_api(content)
                if not api_result['is_safe']:
                    return api_result

            return {'is_safe': True, 'reason': None, 'hit_word': None}

        except Exception as e:
            logger.error(f"Content safety check failed: {str(e)}")
            return {'is_safe': True, 'reason': None, 'hit_word': None}

    def _check_sensitive_words(self, content: str) -> Optional[str]:
        """检测敏感词"""
        for pattern in _sensitive_compiled:
            match = pattern.search(content)
            if match:
                return match.group()
        return None

    def _check_anthropomorphic(self, content: str) -> bool:
        """
        检测拟人化倾向：
        学生要求 AI 扮演非写作教练角色（如"你是真人吗"、"你叫什么名字"、"你扮演XXX"）
        轻度问题仅警告，严重时拒绝回答
        """
        patterns = [
            r'你是(真人|人|猫|狗|机器人|女朋友|男朋友|妈妈|爸爸)',
            r'你(叫|名字)(什么|叫啥)',
            r'(扮演|假装|模拟)(你是|一下).{0,20}(不是|非).{0,10}(写作|作文|老师|教练)',
            r'(不要|别)当(写作|作文)(老师|教练|助手)',
        ]
        for p in patterns:
            if re.search(p, content):
                return True
        return False

    def _call_safe_api(self, content: str) -> Dict:
        """调用第三方内容安全 API（预留接口）"""
        try:
            return {'is_safe': True, 'reason': None, 'hit_word': None}
        except Exception as e:
            logger.error(f"Third-party safe API call failed: {str(e)}")
            return {'is_safe': True, 'reason': None, 'hit_word': None}

    def filter_ai_response(self, content: str) -> Dict:
        """
        过滤 AI 回复
        如果包含不当内容，替换为安全回复（不检查长度，短回复属正常）
        """
        if not content:
            return {'filtered': False, 'content': content, 'reason': None}

        hit = self._check_sensitive_words(content)
        if hit:
            return {
                'filtered': True,
                'content': SAFE_RESPONSE,
                'reason': f'包含不当内容'
            }

        if self._check_anthropomorphic(content):
            return {
                'filtered': True,
                'content': SAFE_RESPONSE,
                'reason': '请专注于写作练习相关的交流'
            }

        return {
            'filtered': False,
            'content': content,
            'reason': None
        }

    def check_user_info(self, nickname: str, avatar_url: str = None) -> Dict:
        """检查用户信息（昵称、头像）"""
        if nickname:
            result = self._check_sensitive_words(nickname)
            if result:
                return {
                    'is_safe': False,
                    'reason': '昵称包含不当内容',
                    'hit_word': result
                }
            if len(nickname) > 20:
                return {
                    'is_safe': False,
                    'reason': '昵称长度不能超过 20 个字符',
                    'hit_word': None
                }

        if avatar_url:
            if not avatar_url.startswith(('http://', 'https://', '/')):
                return {
                    'is_safe': False,
                    'reason': '无效的头像链接',
                    'hit_word': None
                }

        return {'is_safe': True, 'reason': None, 'hit_word': None}


# 模块级便捷函数，供路由层直接使用
_default_service = None


def _get_service() -> ContentSafeService:
    global _default_service
    if _default_service is None:
        try:
            _default_service = ContentSafeService()
        except Exception:
            _default_service = ContentSafeService(enabled=False)
    return _default_service


def content_safety_check(content: str) -> Dict:
    """便捷函数：检查内容安全性"""
    return _get_service().check_content(content)


def filter_ai_response(content: str) -> Dict:
    """便捷函数：过滤 AI 回复"""
    return _get_service().filter_ai_response(content)
