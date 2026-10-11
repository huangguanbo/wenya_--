"""
文芽 - API 客户端和记忆服务测试脚本
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_api_client():
    """测试 API 客户端"""
    print("\n=== 测试 API 客户端 ===")
    
    from services.api_client import APIClient, APIClientError
    
    # 测试 1: 创建客户端（不实际调用）
    try:
        client = APIClient(
            provider='openai',
            api_key='test-key',
            model='gpt-4o',
            cache_enabled=True
        )
        print("✓ API 客户端创建成功")
        print(f"  提供商：{client.provider}")
        print(f"  模型：{client.model}")
        print(f"  缓存：{client.cache_enabled}")
    except Exception as e:
        print(f"✗ API 客户端创建失败：{e}")
        return False
    
    # 测试 2: 测试缓存功能
    try:
        cache_key = client._generate_cache_key([{"role": "user", "content": "test"}])
        client._set_cache(cache_key, {"content": "test response"})
        cached = client._get_from_cache(cache_key)
        
        if cached and cached['content'] == "test response":
            print("✓ 缓存功能正常")
        else:
            print("✗ 缓存功能异常")
            return False
    except Exception as e:
        print(f"✗ 缓存测试失败：{e}")
        return False
    
    # 测试 3: 测试统计信息
    stats = client.get_stats()
    print(f"✓ 统计信息：{stats}")
    
    return True


def test_memory_service():
    """测试记忆服务"""
    print("\n=== 测试记忆服务 ===")
    
    from services.memory_service import MemoryService, MemoryFragment
    
    # 测试 1: 创建记忆服务
    try:
        memory = MemoryService()
        print("✓ 记忆服务创建成功")
        print(f"  向量检索：{memory.vector_store_enabled}")
        print(f"  最大片段数：{memory.max_fragments_per_user}")
    except Exception as e:
        print(f"✗ 记忆服务创建失败：{e}")
        return False
    
    # 测试 2: 添加记忆片段
    try:
        fragment = memory.add_fragment(
            user_id=1,
            content="学生擅长记叙文写作",
            category='writing_profile',
            interaction_type='guidance',
            metadata={'grade': 8}
        )
        
        if fragment and fragment.id:
            print("✓ 添加记忆片段成功")
            print(f"  ID: {fragment.id[:8]}...")
            print(f"  重要性：{fragment.importance:.2f}")
        else:
            print("✗ 添加记忆片段失败")
            return False
    except Exception as e:
        print(f"✗ 添加记忆片段失败：{e}")
        return False
    
    # 测试 3: 检索记忆
    try:
        fragments = memory.retrieve(
            user_id=1,
            query="写作",
            top_k=5,
            min_importance=0.3
        )
        
        print(f"✓ 检索记忆成功，找到 {len(fragments)} 条")
        for i, f in enumerate(fragments[:3]):
            print(f"  [{i+1}] {f.content[:50]}... (重要性：{f.importance:.2f})")
    except Exception as e:
        print(f"✗ 检索记忆失败：{e}")
        return False
    
    # 测试 4: 聚合摘要
    try:
        summary = memory.aggregate_memories(
            user_id=1,
            time_range_days=30
        )
        
        print("✓ 聚合摘要成功")
        print(f"  总片段数：{summary.get('total_fragments', 0)}")
        print(f"  类别数：{len(summary.get('categories', {}))}")
    except Exception as e:
        print(f"✗ 聚合摘要失败：{e}")
        return False
    
    # 测试 5: 统计信息
    stats = memory.get_stats()
    print(f"✓ 统计信息：{stats}")
    
    return True


def test_ai_service_integration():
    """测试 AI 服务集成"""
    print("\n=== 测试 AI 服务集成 ===")
    
    try:
        from services.ai_service import AIService
        from app import create_app
        
        # 创建 Flask 应用上下文
        app = create_app('testing')
        
        with app.app_context():
            # 创建 AI 服务（带记忆和缓存）
            ai_service = AIService(
                provider='openai',
                api_key='test-key',
                model='gpt-4o',
                enable_memory=True,
                enable_cache=True
            )
            
            print("✓ AI 服务创建成功")
            print(f"  提供商：{ai_service.provider}")
            print(f"  模型：{ai_service.model}")
            print(f"  记忆增强：{ai_service.enable_memory}")
            print(f"  缓存：{ai_service.api_client.cache_enabled}")
            
            # 测试模拟响应
            messages = [{"role": "user", "content": "测试消息"}]
            response = ai_service._mock_response(messages)
            
            if response:
                print("✓ 模拟响应正常")
                print(f"  响应长度：{len(response)}")
            else:
                print("✗ 模拟响应异常")
                return False
            
            return True
        
    except Exception as e:
        print(f"✗ AI 服务集成测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """测试配置"""
    print("\n=== 测试配置 ===")
    
    try:
        from config import Config, DevelopmentConfig
        
        config = DevelopmentConfig()
        
        print("✓ 配置加载成功")
        print(f"  AI 提供商：{config.AI_PROVIDER}")
        print(f"  AI 模型：{config.AI_MODEL}")
        print(f"  记忆增强：{config.AI_ENABLE_MEMORY}")
        print(f"  缓存：{config.AI_ENABLE_CACHE}")
        
        return True
        
    except Exception as e:
        print(f"✗ 配置测试失败：{e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("文芽 - API 和记忆功能测试")
    print("=" * 60)
    
    results = {
        '配置': test_config(),
        'API 客户端': test_api_client(),
        '记忆服务': test_memory_service(),
        'AI 服务集成': test_ai_service_integration()
    }
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("所有测试通过！✓")
    else:
        print(f"部分测试失败 ({sum(results.values())}/{len(results)})")
    print("=" * 60)
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
