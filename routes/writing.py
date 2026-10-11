"""
文芽 - 写作核心路由
"""
from flask import Blueprint, request, current_app
from flask_login import login_required, current_user
from datetime import datetime

from app import db, limiter
from models.writing import Writing, WritingDraft, WritingScore
from models.ai_memory import AIConversation, AIMemory
from models.compliance import ComplianceLog, AlgorithmLog
from services.ai_service import AIService
from services.content_safe import ContentSafeService
from utils.response import success_response, error_response, paginated_response
from utils.helpers import count_words, get_client_ip
from utils.validators import validate_content_length

writing_bp = Blueprint('writing', __name__)

MAX_DRAFT_VERSIONS = 50


def _check_content_safety(content):
    """统一内容安全检查"""
    safe_service = ContentSafeService()
    result = safe_service.check_content(content)
    if not result['is_safe']:
        return error_response(
            '内容包含不当信息',
            message=result['reason'],
            status_code=403
        )
    return None


@writing_bp.route('', methods=['POST'])
@login_required
def create_writing():
    """创建新作文"""
    data = request.get_json()
    if not data:
        return error_response('Invalid request', status_code=400)

    title = (data.get('title') or '').strip()
    prompt = data.get('prompt') or ''
    content = data.get('content') or ''

    if not title:
        return error_response('标题不能为空', status_code=400)
    if len(title) > 200:
        return error_response('标题不能超过 200 字', status_code=400)

    ok, msg = validate_content_length(content, min_len=1)
    if not ok:
        return error_response(msg, status_code=400)

    # 内容安全检查
    err = _check_content_safety(content)
    if err:
        return err

    word_count = count_words(content)

    writing = Writing(
        user_id=current_user.id,
        title=title,
        prompt=prompt,
        content=content,
        word_count=word_count,
        status='draft'
    )
    db.session.add(writing)
    db.session.flush()

    draft = WritingDraft(
        writing_id=writing.id,
        content=content,
        word_count=word_count,
        version=1
    )
    db.session.add(draft)

    compliance_log = ComplianceLog(
        log_type='user_action',
        user_id=current_user.id,
        related_id=writing.id,
        related_type='writing',
        action='writing_created',
        details={'title': title, 'word_count': word_count},
        ip_address=get_client_ip()
    )
    db.session.add(compliance_log)
    db.session.commit()

    return success_response({'writing': writing.to_dict()}, message='创建成功', status_code=201)


@writing_bp.route('/<int:writing_id>', methods=['GET'])
@login_required
def get_writing(writing_id):
    """获取作文详情"""
    writing = Writing.query.filter_by(id=writing_id, user_id=current_user.id, is_deleted=False).first()
    if not writing:
        return error_response('作文不存在', status_code=404)

    return success_response({
        'writing': writing.to_dict(include_content=True, include_scores=True)
    })


@writing_bp.route('/<int:writing_id>', methods=['PUT'])
@login_required
def update_writing(writing_id):
    """更新作文"""
    writing = Writing.query.filter_by(id=writing_id, user_id=current_user.id, is_deleted=False).first()
    if not writing:
        return error_response('作文不存在', status_code=404)
    if writing.status != 'draft':
        return error_response('已提交的作文不能修改', status_code=400)

    data = request.get_json()
    if not data:
        return error_response('Invalid request', status_code=400)

    if 'title' in data:
        title = data['title'].strip()
        if not title:
            return error_response('标题不能为空', status_code=400)
        writing.title = title

    if 'content' in data:
        content = data['content']
        ok, msg = validate_content_length(content, min_len=1)
        if not ok:
            return error_response(msg, status_code=400)

        err = _check_content_safety(content)
        if err:
            return err

        writing.content = content
        writing.word_count = count_words(content)

        version = WritingDraft.query.filter_by(writing_id=writing.id).count() + 1
        draft = WritingDraft(
            writing_id=writing.id,
            content=content,
            word_count=writing.word_count,
            version=version
        )
        db.session.add(draft)

    writing.updated_at = datetime.utcnow()
    db.session.commit()

    return success_response({'writing': writing.to_dict()}, message='更新成功')


@writing_bp.route('/<int:writing_id>', methods=['DELETE'])
@login_required
def delete_writing(writing_id):
    """删除作文（软删除）"""
    writing = Writing.query.filter_by(id=writing_id, user_id=current_user.id, is_deleted=False).first()
    if not writing:
        return error_response('作文不存在', status_code=404)

    writing.is_deleted = True
    writing.deleted_at = datetime.utcnow()
    db.session.commit()

    compliance_log = ComplianceLog(
        log_type='user_action',
        user_id=current_user.id,
        related_id=writing.id,
        related_type='writing',
        action='writing_deleted',
        ip_address=get_client_ip()
    )
    db.session.add(compliance_log)
    db.session.commit()

    return success_response(message='删除成功')


@writing_bp.route('/<int:writing_id>/submit', methods=['POST'])
@login_required
@limiter.limit("3 per minute")
def submit_writing(writing_id):
    """提交作文进行 AI 评分"""
    writing = Writing.query.filter_by(id=writing_id, user_id=current_user.id, is_deleted=False).first()
    if not writing:
        return error_response('作文不存在', status_code=404)
    if writing.status != 'draft':
        return error_response('作文已提交，不能重复评分', status_code=400)

    ai_service = AIService()
    try:
        scoring_result = ai_service.score_writing(writing)
    except Exception as e:
        current_app.logger.error(f'AI 评分失败 writing_id={writing_id}: {e}')
        db.session.rollback()
        return error_response('AI 评分服务暂时不可用，请稍后重试', status_code=503)

    score = WritingScore(
        writing_id=writing.id,
        task_score=scoring_result['task_score'],
        theme_score=scoring_result['theme_score'],
        content_score=scoring_result['content_score'],
        structure_score=scoring_result['structure_score'],
        language_score=scoring_result['language_score'],
        genre_score=scoring_result['genre_score'],
        thinking_score=scoring_result['thinking_score'],
        weights=scoring_result['weights'],
        ai_comment=scoring_result['ai_comment'],
        ai_suggestions=scoring_result['ai_suggestions'],
        confidence=scoring_result['confidence'],
        needs_human_review=scoring_result['needs_human_review']
    )
    db.session.add(score)

    writing.status = 'submitted'
    writing.is_scored = True
    writing.overall_score = score.calculate_overall()
    writing.submitted_at = datetime.utcnow()

    algorithm_log = AlgorithmLog(
        algorithm_type='writing_score',
        input_summary={'writing_id': writing.id, 'word_count': writing.word_count, 'grade': current_user.grade},
        output_summary={'overall_score': writing.overall_score, 'confidence': scoring_result['confidence']},
        confidence_score=scoring_result['confidence'],
        algorithm_version='v1.0',
        decision_factors=scoring_result.get('decision_factors', [])
    )
    db.session.add(algorithm_log)

    compliance_log = ComplianceLog(
        log_type='content_review',
        user_id=current_user.id,
        related_id=writing.id,
        related_type='writing',
        action='writing_submitted_for_scoring',
        ip_address=get_client_ip()
    )
    db.session.add(compliance_log)
    db.session.commit()

    return success_response(
        {'writing': writing.to_dict(include_scores=True)},
        message='评分完成'
    )


@writing_bp.route('/<int:writing_id>/draft', methods=['POST'])
@login_required
@limiter.limit("30 per minute")
def save_draft(writing_id):
    """保存草稿（自动保存）"""
    writing = Writing.query.filter_by(id=writing_id, user_id=current_user.id, is_deleted=False).first()
    if not writing:
        return error_response('作文不存在', status_code=404)

    data = request.get_json()
    content = (data.get('content') or '') if data else ''

    if not content:
        return error_response('内容不能为空', status_code=400)

    word_count = count_words(content)
    version = WritingDraft.query.filter_by(writing_id=writing.id).count() + 1

    draft = WritingDraft(
        writing_id=writing.id,
        content=content,
        word_count=word_count,
        version=version
    )
    db.session.add(draft)

    writing.content = content
    writing.word_count = word_count
    writing.updated_at = datetime.utcnow()
    db.session.commit()

    return success_response({'version': draft.version}, message='已保存')


@writing_bp.route('/<int:writing_id>/drafts', methods=['GET'])
@login_required
def list_drafts(writing_id):
    """获取草稿历史版本"""
    writing = Writing.query.filter_by(id=writing_id, user_id=current_user.id, is_deleted=False).first()
    if not writing:
        return error_response('作文不存在', status_code=404)

    drafts = WritingDraft.query.filter_by(writing_id=writing_id)\
        .order_by(WritingDraft.version.desc())\
        .limit(MAX_DRAFT_VERSIONS).all()

    return success_response({
        'drafts': [{'version': d.version, 'word_count': d.word_count, 'created_at': d.created_at.isoformat()} for d in drafts]
    })


@writing_bp.route('/<int:writing_id>/ai-chat', methods=['POST'])
@login_required
@limiter.limit("20 per minute")
def ai_chat(writing_id):
    """与 AI 写作教练对话"""
    writing = Writing.query.filter_by(id=writing_id, user_id=current_user.id, is_deleted=False).first()
    if not writing:
        return error_response('作文不存在', status_code=404)

    data = request.get_json()
    if not data:
        return error_response('Invalid request', status_code=400)

    message = (data.get('message') or '').strip()
    session_type = data.get('session_type', 'writing_guidance')

    if not message:
        return error_response('消息不能为空', status_code=400)

    err = _check_content_safety(message)
    if err:
        return err

    ai_memory = AIMemory.query.filter_by(user_id=current_user.id).first()
    if not ai_memory:
        ai_memory = AIMemory(user_id=current_user.id)
        db.session.add(ai_memory)
        db.session.flush()

    recent = AIConversation.query.filter_by(memory_id=ai_memory.id, writing_id=writing_id)\
        .order_by(AIConversation.created_at.desc()).limit(10).all()

    messages_history = []
    for conv in recent:
        messages_history.extend(conv.messages[-2:])

    ai_service = AIService()
    try:
        ai_response = ai_service.chat(
            message=message,
            writing_context=writing,
            user_profile=current_user.profile,
            memory=ai_memory,
            history=messages_history,
            session_type=session_type
        )
    except Exception as e:
        current_app.logger.error(f'AI 对话失败 writing_id={writing_id}: {e}')
        return error_response('AI 服务暂时不可用', status_code=503)

    # AI 响应安全检查
    safe_service = ContentSafeService()
    ai_safety = safe_service.check_content(ai_response['content'])
    if not ai_safety['is_safe']:
        ai_response['content'] = '抱歉，我需要专注于写作指导。让我们继续讨论你的作文吧。'
        ai_response['is_filtered'] = True

    conversation = AIConversation(
        memory_id=ai_memory.id,
        user_id=current_user.id,
        writing_id=writing_id,
        session_type=session_type,
        messages=[
            {'role': 'user', 'content': message, 'timestamp': datetime.utcnow().isoformat()},
            {'role': 'assistant', 'content': ai_response['content'], 'timestamp': datetime.utcnow().isoformat()}
        ],
        summary=ai_response.get('summary', ''),
        key_points=ai_response.get('key_points', [])
    )
    db.session.add(conversation)

    ai_memory.last_interaction_at = datetime.utcnow()
    ai_memory.total_interactions += 1

    compliance_log = ComplianceLog(
        log_type='ai_interaction',
        user_id=current_user.id,
        related_id=conversation.id,
        related_type='ai_conversation',
        action='ai_chat',
        details={'session_type': session_type, 'is_filtered': ai_response.get('is_filtered', False)},
        ip_address=get_client_ip()
    )
    db.session.add(compliance_log)

    algorithm_log = AlgorithmLog(
        algorithm_type='ai_response',
        input_summary={'message_length': len(message)},
        output_summary={'response_length': len(ai_response['content'])},
        algorithm_version='v1.0',
        model_version=current_app.config.get('AI_MODEL', 'unknown')
    )
    db.session.add(algorithm_log)

    db.session.commit()

    return success_response({
        'response': ai_response['content'],
        'conversation_id': conversation.id
    })


@writing_bp.route('', methods=['GET'])
@login_required
def list_writings():
    """获取用户作文列表"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    status = request.args.get('status', 'all')

    query = Writing.query.filter_by(user_id=current_user.id, is_deleted=False)
    if status != 'all':
        query = query.filter_by(status=status)

    pagination = query.order_by(Writing.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    writings = [w.to_dict(include_content=False, include_scores=True) for w in pagination.items]
    return paginated_response(writings, pagination)
