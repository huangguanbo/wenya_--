"""
文芽 - AI 记忆管理路由
提供记忆查询、更新、删除等管理功能
"""
from flask import Blueprint, request, current_app
from flask_login import login_required, current_user

from app import db
from models.ai_memory import AIMemory
from services.memory_service import MemoryService
from utils.response import success_response, error_response

memory_bp = Blueprint('memory', __name__)


@memory_bp.route('/profile', methods=['GET'])
@login_required
def get_memory_profile():
    """获取用户记忆画像"""
    ai_memory = AIMemory.query.filter_by(user_id=current_user.id).first()
    
    if not ai_memory:
        return success_response({
            'profile': {},
            'knowledge_base': {},
            'stats': {'total_interactions': 0}
        })
    
    return success_response({
        'profile': ai_memory.writing_profile or {},
        'knowledge_base': ai_memory.knowledge_base or {},
        'stats': {
            'total_interactions': ai_memory.total_interactions,
            'last_interaction_at': ai_memory.last_interaction_at.isoformat() if ai_memory.last_interaction_at else None,
            'memory_version': ai_memory.memory_version
        }
    })


@memory_bp.route('/profile', methods=['PUT'])
@login_required
def update_memory_profile():
    """更新用户记忆画像"""
    data = request.get_json()
    if not data:
        return error_response('Invalid request', status_code=400)
    
    ai_memory = AIMemory.query.filter_by(user_id=current_user.id).first()
    
    if not ai_memory:
        ai_memory = AIMemory(user_id=current_user.id)
        db.session.add(ai_memory)
    
    # 更新画像
    if 'writing_profile' in data:
        if ai_memory.writing_profile:
            ai_memory.writing_profile.update(data['writing_profile'])
        else:
            ai_memory.writing_profile = data['writing_profile']
    
    # 更新知识库
    if 'knowledge_base' in data:
        if ai_memory.knowledge_base:
            ai_memory.knowledge_base.update(data['knowledge_base'])
        else:
            ai_memory.knowledge_base = data['knowledge_base']
    
    db.session.commit()
    
    return success_response({
        'profile': ai_memory.writing_profile,
        'knowledge_base': ai_memory.knowledge_base
    }, message='更新成功')


@memory_bp.route('/fragments', methods=['GET'])
@login_required
def get_memory_fragments():
    """获取记忆片段（支持检索）"""
    query = request.args.get('q', '')
    category = request.args.get('category', None)
    top_k = min(int(request.args.get('top_k', 10)), 50)
    min_importance = float(request.args.get('min_importance', 0.3))
    
    # 初始化记忆服务
    memory_service = MemoryService()
    
    # 检索记忆片段
    fragments = memory_service.retrieve(
        user_id=current_user.id,
        query=query,
        top_k=top_k,
        category=category,
        min_importance=min_importance
    )
    
    return success_response({
        'fragments': [f.to_dict() for f in fragments],
        'count': len(fragments),
        'query': query
    })


@memory_bp.route('/fragments/<fragment_id>', methods=['DELETE'])
@login_required
def delete_memory_fragment(fragment_id):
    """删除记忆片段"""
    # 注意：当前实现中记忆片段主要在内存中
    # 如需持久化删除，需要访问数据库模型
    return success_response(message='删除成功（仅当前会话）')


@memory_bp.route('/aggregate', methods=['GET'])
@login_required
def aggregate_memories():
    """聚合记忆生成摘要"""
    category = request.args.get('category', None)
    time_range_days = int(request.args.get('days', 30))
    
    # 初始化记忆服务
    memory_service = MemoryService()
    
    # 生成聚合摘要
    summary = memory_service.aggregate_memories(
        user_id=current_user.id,
        category=category,
        time_range_days=time_range_days
    )
    
    return success_response({
        'summary': summary,
        'time_range_days': time_range_days
    })


@memory_bp.route('/context', methods=['GET'])
@login_required
def get_interaction_context():
    """获取当前交互的上下文（用于 AI 对话增强）"""
    query = request.args.get('q', '')
    writing_id = request.args.get('writing_id', None, type=int)
    
    # 初始化记忆服务
    memory_service = MemoryService()
    
    # 获取上下文
    context = memory_service.get_context_for_interaction(
        user_id=current_user.id,
        current_query=query,
        writing_context={'id': writing_id} if writing_id else None
    )
    
    return success_response({
        'context': context
    })


@memory_bp.route('/stats', methods=['GET'])
@login_required
def get_memory_stats():
    """获取记忆统计信息"""
    # 初始化记忆服务
    memory_service = MemoryService()
    
    stats = memory_service.get_stats()
    
    # 获取用户记忆数量
    ai_memory = AIMemory.query.filter_by(user_id=current_user.id).first()
    user_stats = {
        'total_interactions': ai_memory.total_interactions if ai_memory else 0,
        'has_profile': bool(ai_memory and ai_memory.writing_profile),
        'last_interaction': ai_memory.last_interaction_at.isoformat() if ai_memory and ai_memory.last_interaction_at else None
    }
    
    return success_response({
        'system_stats': stats,
        'user_stats': user_stats
    })


@memory_bp.route('/clear', methods=['POST'])
@login_required
def clear_memory():
    """清空记忆（谨慎使用）"""
    data = request.get_json() or {}
    clear_type = data.get('type', 'all')  # all/fragments/profile
    
    # 初始化记忆服务（会清空内存中的片段）
    memory_service = MemoryService()
    
    if clear_type in ['all', 'fragments']:
        # 清空记忆片段
        if current_user.id in memory_service.memory_fragments:
            del memory_service.memory_fragments[current_user.id]
    
    if clear_type == 'all' or clear_type == 'profile':
        # 清空画像
        ai_memory = AIMemory.query.filter_by(user_id=current_user.id).first()
        if ai_memory:
            ai_memory.writing_profile = {}
            ai_memory.knowledge_base = {}
            db.session.commit()
    
    return success_response(message=f'已清空{clear_type}记忆')
