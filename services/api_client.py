"""
文芽 - 通用 API 客户端服务
支持多种 AI 模型接入，提供统一的调用接口
"""
import json
import time
import hashlib
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)


class APIClientError(Exception):
    """API 客户端异常"""
    def __init__(self, message: str, status_code: int = None, retry_after: int = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.retry_after = retry_after


class CacheEntry:
    """缓存条目"""
    def __init__(self, key: str, value: Any, ttl: int):
        self.key = key
        self.value = value
        self.created_at = datetime.utcnow()
        self.ttl = ttl  # 秒

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.created_at + timedelta(seconds=self.ttl)


class APIClient:
    """
    通用 API 客户端
    支持：OpenAI, Claude, 通义千问，DeepSeek 等
    功能：缓存、重试、降级、限流
    """

    # 支持的模型提供商
    PROVIDERS = {
        'openai': {
            'base_url': 'https://api.openai.com/v1',
            'auth_header': 'Authorization',
            'auth_format': 'Bearer {api_key}',
            'chat_endpoint': '/chat/completions',
            'response_path': 'choices[0].message.content'
        },
        'claude': {
            'base_url': 'https://api.anthropic.com/v1',
            'auth_header': 'x-api-key',
            'auth_format': '{api_key}',
            'chat_endpoint': '/messages',
            'response_path': 'content[0].text',
            'extra_headers': {
                'anthropic-version': '2023-06-01'
            }
        },
        'aliyun': {
            'base_url': 'https://dashscope.aliyuncs.com/api/v1',
            'auth_header': 'Authorization',
            'auth_format': 'Bearer {api_key}',
            'chat_endpoint': '/services/aigc/text-generation/generation',
            'response_path': 'output.text'
        },
        'deepseek': {
            'base_url': 'https://api.deepseek.com/v1',
            'auth_header': 'Authorization',
            'auth_format': 'Bearer {api_key}',
            'chat_endpoint': '/chat/completions',
            'response_path': 'choices[0].message.content'
        },
        'moonshot': {
            'base_url': 'https://api.moonshot.cn/v1',
            'auth_header': 'Authorization',
            'auth_format': 'Bearer {api_key}',
            'chat_endpoint': '/chat/completions',
            'response_path': 'choices[0].message.content'
        }
    }

    def __init__(self, provider: str = 'openai', api_key: str = None, 
                 base_url: str = None, model: str = None,
                 cache_enabled: bool = True, cache_ttl: int = 3600):
        """
        初始化 API 客户端
        
        Args:
            provider: 模型提供商 (openai/claude/aliyun/deepseek/moonshot)
            api_key: API 密钥
            base_url: 自定义 API 地址（可选）
            model: 模型名称
            cache_enabled: 是否启用缓存
            cache_ttl: 缓存过期时间（秒）
        """
        if provider not in self.PROVIDERS:
            raise ValueError(f"不支持的模型提供商：{provider}")

        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url or self.PROVIDERS[provider]['base_url']
        self.model = model or self._get_default_model(provider)
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        self.cache: Dict[str, CacheEntry] = {}
        
        # 统计信息
        self.stats = {
            'total_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0,
            'retries': 0
        }

    def _get_default_model(self, provider: str) -> str:
        """获取提供商的默认模型"""
        default_models = {
            'openai': 'gpt-4o',
            'claude': 'claude-3-sonnet-20240229',
            'aliyun': 'qwen-max',
            'deepseek': 'deepseek-chat',
            'moonshot': 'moonshot-v1-8k'
        }
        return default_models.get(provider, 'gpt-4')

    def _generate_cache_key(self, messages: List[Dict], **kwargs) -> str:
        """生成缓存键"""
        key_data = json.dumps({
            'provider': self.provider,
            'model': self.model,
            'messages': messages,
            'kwargs': kwargs
        }, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        if not self.cache_enabled:
            return None
        
        entry = self.cache.get(key)
        if entry and not entry.is_expired():
            self.stats['cache_hits'] += 1
            return entry.value
        
        if entry:
            del self.cache[key]  # 清理过期缓存
        
        self.stats['cache_misses'] += 1
        return None

    def _set_cache(self, key: str, value: Any):
        """设置缓存"""
        if not self.cache_enabled:
            return
        
        self.cache[key] = CacheEntry(key, value, self.cache_ttl)
        
        # 清理过期缓存（每 10 次调用清理一次）
        if self.stats['total_calls'] % 10 == 0:
            expired_keys = [k for k, v in self.cache.items() if v.is_expired()]
            for k in expired_keys:
                del self.cache[k]

    def chat(self, messages: List[Dict], **kwargs) -> Dict:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            **kwargs: 额外参数 (temperature, max_tokens, etc.)
        
        Returns:
            Dict: {
                'content': str,
                'usage': Dict,
                'model': str,
                'provider': str,
                'cached': bool
            }
        """
        self.stats['total_calls'] += 1
        
        # 检查缓存
        cache_key = self._generate_cache_key(messages, **kwargs)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            cached_result['cached'] = True
            return cached_result

        # 构建请求
        headers, payload = self._build_request(messages, **kwargs)
        
        # 发送请求（带重试）
        max_retries = kwargs.get('max_retries', 3)
        retry_delay = kwargs.get('retry_delay', 1.0)
        
        for attempt in range(max_retries):
            try:
                response = self._send_request(headers, payload)
                
                # 解析响应
                result = self._parse_response(response)
                
                # 缓存结果
                self._set_cache(cache_key, result)
                
                result['cached'] = False
                return result

            except APIClientError as e:
                self.stats['errors'] += 1
                
                # 判断是否可重试
                if e.status_code and e.status_code not in [400, 401, 403]:
                    if attempt < max_retries - 1:
                        self.stats['retries'] += 1
                        wait_time = retry_delay * (2 ** attempt)
                        if e.retry_after:
                            wait_time = max(wait_time, e.retry_after)
                        logger.warning(f"API 调用失败，{wait_time}s 后重试 (attempt {attempt + 1}/{max_retries}): {e.message}")
                        time.sleep(wait_time)
                        continue
                
                logger.error(f"API 调用失败：{e.message}")
                raise

        raise APIClientError("API 调用失败，已达最大重试次数")

    def _build_request(self, messages: List[Dict], **kwargs) -> tuple:
        """构建请求头和负载"""
        provider_config = self.PROVIDERS[self.provider]
        
        # 构建请求头
        headers = {
            'Content-Type': 'application/json',
            provider_config['auth_header']: provider_config['auth_format'].format(api_key=self.api_key)
        }
        
        # 添加额外请求头
        if 'extra_headers' in provider_config:
            headers.update(provider_config['extra_headers'])
        
        # 构建请求体（不同提供商格式不同）
        if self.provider == 'openai' or self.provider == 'deepseek' or self.provider == 'moonshot':
            payload = {
                'model': self.model,
                'messages': messages,
                'temperature': kwargs.get('temperature', 0.7),
                'max_tokens': kwargs.get('max_tokens', 2000)
            }
        elif self.provider == 'claude':
            # Claude 使用不同的格式
            system_message = next((m for m in messages if m['role'] == 'system'), None)
            user_messages = [m for m in messages if m['role'] != 'system']
            
            payload = {
                'model': self.model,
                'messages': user_messages,
                'max_tokens': kwargs.get('max_tokens', 2000),
                'temperature': kwargs.get('temperature', 0.7)
            }
            
            if system_message:
                payload['system'] = system_message['content']
                
        elif self.provider == 'aliyun':
            # 阿里云通义千问格式
            payload = {
                'model': self.model,
                'input': {
                    'messages': messages
                },
                'parameters': {
                    'temperature': kwargs.get('temperature', 0.7),
                    'max_tokens': kwargs.get('max_tokens', 2000)
                }
            }
        
        return headers, payload

    def _send_request(self, headers: Dict, payload: Dict) -> Dict:
        """发送 HTTP 请求"""
        try:
            import requests
            
            provider_config = self.PROVIDERS[self.provider]
            url = self.base_url.rstrip('/') + provider_config['chat_endpoint']
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                retry_after = None
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 5))
                
                raise APIClientError(
                    f"API 请求失败：{error_data.get('error', {}).get('message', '未知错误')}",
                    status_code=response.status_code,
                    retry_after=retry_after
                )
            
            return response.json()
            
        except ImportError:
            raise APIClientError("requests 库未安装，请运行：pip install requests")
        except requests.Timeout:
            raise APIClientError("API 请求超时")
        except requests.ConnectionError:
            raise APIClientError("API 连接失败")

    def _parse_response(self, response: Dict) -> Dict:
        """解析响应"""
        provider_config = self.PROVIDERS[self.provider]
        
        try:
            if self.provider == 'openai' or self.provider == 'deepseek' or self.provider == 'moonshot':
                content = response['choices'][0]['message']['content']
                usage = response.get('usage', {})
            elif self.provider == 'claude':
                content = response['content'][0]['text']
                usage = {
                    'prompt_tokens': response.get('usage', {}).get('input_tokens', 0),
                    'completion_tokens': response.get('usage', {}).get('output_tokens', 0)
                }
            elif self.provider == 'aliyun':
                content = response['output']['text']
                usage = response.get('usage', {})
            else:
                content = ''
                usage = {}
            
            return {
                'content': content,
                'usage': usage,
                'model': self.model,
                'provider': self.provider
            }
            
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"解析 API 响应失败：{e}, response={response}")
            raise APIClientError(f"API 响应格式异常：{str(e)}")

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'cache_size': len(self.cache),
            'provider': self.provider,
            'model': self.model
        }

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        logger.info("API 缓存已清空")


# 装饰器：带降级的 API 调用
def fallback_on_error(fallback_value):
    """
    装饰器：API 调用失败时返回降级值
    
    Usage:
        @fallback_on_error({'content': '默认回复', 'fallback': True})
        def call_api(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except APIClientError as e:
                logger.warning(f"API 调用失败，使用降级值：{e.message}")
                return fallback_value
        return wrapper
    return decorator
