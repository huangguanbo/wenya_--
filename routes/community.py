"""
文芽 - 社区路由
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from app import db
from models.community import CommunityWork, WorkLike, WorkComment
from models.writing import Writing
from models.compliance import ComplianceLog
from utils.response import success_response, error_response, paginated_response
from services.content_safe import content_safety_check

community_bp = Blueprint('community', __name__)


@community_bp.route('/works', methods=['GET'])
def list_works():
    """
    获取社区作品列表
    支持按体裁/年级/维度多维筛选
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    grade = request.args.get('grade', type=int)
    school_stage = request.args.get('school_stage')
    genre = request.args.get('genre')
    tag = request.args.get('tag')

    query = CommunityWork.query.filter(
        CommunityWork.is_deleted == False,
        CommunityWork.review_status == 'approved'
    )

    if grade:
        query = query.filter(CommunityWork.author_grade == grade)
    elif school_stage:
        if school_stage == 'elementary':
            query = query.filter(CommunityWork.author_grade.between(1, 6))
        elif school_stage == 'middle':
            query = query.filter(CommunityWork.author_grade.between(7, 9))
        elif school_stage == 'high':
            query = query.filter(CommunityWork.author_grade.between(10, 12))

    if genre:
        query = query.filter(CommunityWork.genre == genre)

    if tag:
        query = query.filter(CommunityWork.tags.contains([tag]))

    query = query.order_by(
        (CommunityWork.like_count + CommunityWork.comment_count * 2).desc(),
        CommunityWork.published_at.desc()
    )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    works = [w.to_dict(include_content=False) for w in pagination.items]

    return paginated_response(works, pagination)


@community_bp.route('/works/<int:work_id>', methods=['GET'])
def get_work(work_id):
    """获取作品详情"""
    work = CommunityWork.query.filter_by(id=work_id, is_deleted=False).first_or_404()

    work.view_count += 1

    is_liked = False
    if current_user.is_authenticated:
        is_liked = WorkLike.query.filter_by(
            work_id=work_id,
            user_id=current_user.id
        ).first() is not None

    db.session.commit()

    return success_response({
        'work': work.to_dict(include_content=True),
        'is_liked': is_liked
    })


@community_bp.route('/works/<int:work_id>/like', methods=['POST'])
@login_required
def like_work(work_id):
    """点赞作品"""
    work = CommunityWork.query.filter_by(id=work_id, is_deleted=False).first_or_404()

    existing_like = WorkLike.query.filter_by(
        work_id=work_id,
        user_id=current_user.id
    ).first()

    if existing_like:
        db.session.delete(existing_like)
        work.like_count = max(0, work.like_count - 1)
        is_liked = False
    else:
        like = WorkLike(work_id=work_id, user_id=current_user.id)
        db.session.add(like)
        work.like_count += 1
        is_liked = True

    db.session.commit()

    return success_response({
        'like_count': work.like_count,
        'is_liked': is_liked
    }, message=f'已{"点赞" if is_liked else "取消点赞"}')


@community_bp.route('/works/<int:work_id>/comment', methods=['POST'])
@login_required
def comment_work(work_id):
    """评论作品"""
    work = CommunityWork.query.filter_by(id=work_id, is_deleted=False).first_or_404()

    data = request.get_json() or {}
    content = (data.get('content') or '').strip()
    parent_id = data.get('parent_id', type=int)

    if not content:
        return error_response('评论内容不能为空', status_code=400)

    if len(content) > 500:
        return error_response('评论内容不能超过 500 字', status_code=400)

    safety = content_safety_check(content)
    if not safety['is_safe']:
        return error_response('评论包含不当内容，请修改后重试', status_code=400)

    comment = WorkComment(
        work_id=work_id,
        user_id=current_user.id,
        content=content,
        parent_id=parent_id,
        is_approved=True
    )
    db.session.add(comment)

    work.comment_count += 1

    compliance_log = ComplianceLog(
        log_type='user_action',
        user_id=current_user.id,
        related_id=work_id,
        related_type='community_work',
        action='comment_created',
        ip_address=request.remote_addr
    )
    db.session.add(compliance_log)

    db.session.commit()

    return success_response({'comment': comment.to_dict()}, message='评论成功', status_code=201)


@community_bp.route('/works/<int:work_id>/comments', methods=['GET'])
def get_comments(work_id):
    """获取作品评论列表"""
    comments = WorkComment.query.filter_by(
        work_id=work_id,
        is_approved=True,
        is_deleted=False
    ).order_by(WorkComment.created_at.asc()).all()

    return success_response({'comments': [c.to_dict() for c in comments]})


@community_bp.route('/works/<int:work_id>/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(work_id, comment_id):
    """删除自己的评论"""
    comment = WorkComment.query.filter_by(
        id=comment_id,
        work_id=work_id,
        is_deleted=False
    ).first_or_404()

    if comment.user_id != current_user.id:
        return error_response('无权删除该评论', status_code=403)

    comment.is_deleted = True
    comment.deleted_at = datetime.utcnow()

    work = CommunityWork.query.filter_by(id=work_id).first()
    if work:
        work.comment_count = max(0, work.comment_count - 1)

    db.session.commit()

    return success_response(message='评论已删除')


@community_bp.route('/publish/<int:writing_id>', methods=['POST'])
@login_required
def publish_work(writing_id):
    """
    将作文发布到社区
    需要审核通过后才公开
    """
    writing = Writing.query.filter_by(
        id=writing_id,
        user_id=current_user.id,
        is_deleted=False
    ).first_or_404()

    if not writing.is_scored:
        return error_response('作文需先完成评分才能发布', status_code=400)

    existing_work = CommunityWork.query.filter_by(writing_id=writing_id).first()
    if existing_work:
        return error_response('该作文已发布过', status_code=409)

    data = request.get_json() or {}
    tags = data.get('tags', [])
    if not isinstance(tags, list):
        tags = []
    tags = [str(t).strip() for t in tags if str(t).strip()][:5]

    work = CommunityWork(
        writing_id=writing_id,
        user_id=current_user.id,
        title=writing.title,
        content=writing.content,
        word_count=writing.word_count,
        author_grade=current_user.grade,
        author_school_stage=current_user.get_school_stage(),
        overall_score=writing.overall_score,
        dimension_scores=writing.scores.to_dict() if writing.scores else None,
        tags=tags,
        review_status='pending'
    )
    db.session.add(work)

    writing.is_public = True
    writing.published_at = datetime.utcnow()

    compliance_log = ComplianceLog(
        log_type='content_review',
        user_id=current_user.id,
        related_id=writing_id,
        related_type='writing',
        action='work_submitted_for_review',
        ip_address=request.remote_addr
    )
    db.session.add(compliance_log)

    db.session.commit()

    return success_response(
        {'work': work.to_dict(include_content=False)},
        message='作品已提交审核，审核通过后将公开',
        status_code=201
    )


@community_bp.route('/featured', methods=['GET'])
def get_featured_works():
    """获取精选作品"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 6, type=int)

    pagination = CommunityWork.query.filter(
        CommunityWork.is_featured == True,
        CommunityWork.is_deleted == False,
        CommunityWork.review_status == 'approved'
    ).order_by(CommunityWork.published_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    works = [w.to_dict(include_content=False) for w in pagination.items]

    return paginated_response(works, pagination)
