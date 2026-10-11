"""
文芽 - 排行榜路由
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta

from app import db
from models.ranking import RankingRecord, RankingHistory
from models.user import User, UserProfile
from models.writing import Writing
from utils.response import success_response, error_response

ranking_bp = Blueprint('ranking', __name__)


@ranking_bp.route('/overall', methods=['GET'])
@login_required
def get_overall_ranking():
    """获取同年级综合排行榜（主榜）"""
    grade = request.args.get('grade', current_user.grade, type=int)

    if not grade:
        return error_response('请先设置年级', status_code=400)

    users = User.query.filter(
        User.grade == grade,
        User.is_active == True,
        User.show_in_ranking == True,
        User.is_deleted == False
    ).all()

    if not users:
        return success_response({
            'rankings': [],
            'user_rank': None,
            'total_participants': 0,
            'grade': grade,
            'rank_type': 'overall'
        })

    rankings = []
    for user in users:
        avg_score = db.session.query(func.avg(Writing.overall_score)).filter(
            Writing.user_id == user.id,
            Writing.is_scored == True,
            Writing.is_deleted == False
        ).scalar() or 0

        if avg_score > 0:
            writing_count = Writing.query.filter_by(
                user_id=user.id,
                is_scored=True,
                is_deleted=False
            ).count()
            rankings.append({
                'user_id': user.id,
                'nickname': user.nickname or user.username,
                'avatar_url': user.avatar_url,
                'average_score': round(avg_score, 1),
                'writing_count': writing_count
            })

    rankings.sort(key=lambda x: x['average_score'], reverse=True)

    total = len(rankings)
    for i, rank in enumerate(rankings):
        rank['rank_position'] = i + 1
        rank['percentile'] = round(((total - i) / total) * 100, 1) if total > 0 else 0

    cutoff_index = int(total * 0.5)
    visible_rankings = rankings[:cutoff_index] if cutoff_index > 0 else rankings[:10]

    user_rank = None
    user_ranking = next((r for r in rankings if r['user_id'] == current_user.id), None)
    if user_ranking:
        user_rank = {
            'rank_position': user_ranking['rank_position'],
            'percentile': user_ranking['percentile'],
            'average_score': user_ranking['average_score']
        }

    return success_response({
        'rankings': visible_rankings,
        'user_rank': user_rank,
        'total_participants': total,
        'grade': grade,
        'rank_type': 'overall'
    })


@ranking_bp.route('/progress', methods=['GET'])
@login_required
def get_progress_ranking():
    """获取进步排行榜（核心榜）"""
    grade = request.args.get('grade', current_user.grade, type=int)
    days = request.args.get('days', 30, type=int)

    if not grade:
        return error_response('请先设置年级', status_code=400)

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    users = User.query.filter(
        User.grade == grade,
        User.is_active == True,
        User.show_in_ranking == True
    ).all()

    rankings = []
    for user in users:
        recent_writings = Writing.query.filter(
            Writing.user_id == user.id,
            Writing.is_scored == True,
            Writing.submitted_at >= start_date,
            Writing.is_deleted == False
        ).order_by(Writing.submitted_at.desc()).limit(5).all()

        if len(recent_writings) < 2:
            continue

        recent_scores = [w.overall_score for w in recent_writings]
        if len(recent_scores) >= 5:
            progress = sum(recent_scores[:3]) / 3 - sum(recent_scores[3:]) / 2
        else:
            progress = recent_scores[0] - recent_scores[-1]

        profile = UserProfile.query.filter_by(user_id=user.id).first()
        consecutive_days = profile.consecutive_days if profile else 0

        rankings.append({
            'user_id': user.id,
            'nickname': user.nickname or user.username,
            'avatar_url': user.avatar_url,
            'progress_score': round(progress, 2),
            'consecutive_days': consecutive_days,
            'recent_writings': len(recent_writings)
        })

    rankings.sort(key=lambda x: (x['progress_score'], x['consecutive_days']), reverse=True)

    for i, rank in enumerate(rankings):
        rank['rank_position'] = i + 1

    cutoff_index = max(int(len(rankings) * 0.2), 10)
    visible_rankings = rankings[:cutoff_index]

    user_rank = next((r for r in rankings if r['user_id'] == current_user.id), None)

    return success_response({
        'rankings': visible_rankings,
        'user_rank': user_rank,
        'period_days': days,
        'rank_type': 'progress'
    })


@ranking_bp.route('/dimension/<dimension>', methods=['GET'])
@login_required
def get_dimension_ranking(dimension):
    """获取维度排行榜（专项榜）"""
    valid_dimensions = ['theme', 'content', 'structure', 'language', 'creativity']

    if dimension not in valid_dimensions:
        return error_response(f'无效维度，须为 {valid_dimensions} 之一', status_code=400)

    grade = request.args.get('grade', current_user.grade, type=int)

    if not grade:
        return error_response('请先设置年级', status_code=400)

    dimension_map = {
        'theme': 'theme_score',
        'content': 'content_score',
        'structure': 'structure_score',
        'language': 'language_score',
        'creativity': 'thinking_score'
    }

    score_field = dimension_map[dimension]

    users = User.query.filter(
        User.grade == grade,
        User.is_active == True,
        User.show_in_ranking == True
    ).all()

    from models.writing import WritingScore

    rankings = []
    for user in users:
        best_score = db.session.query(func.max(getattr(WritingScore, score_field))).join(
            Writing, Writing.id == WritingScore.writing_id
        ).filter(
            Writing.user_id == user.id,
            Writing.is_scored == True,
            Writing.is_deleted == False
        ).scalar()

        if best_score:
            rankings.append({
                'user_id': user.id,
                'nickname': user.nickname or user.username,
                'avatar_url': user.avatar_url,
                'dimension_score': best_score,
                'dimension': dimension
            })

    rankings.sort(key=lambda x: x['dimension_score'], reverse=True)

    for i, rank in enumerate(rankings):
        rank['rank_position'] = i + 1

    cutoff_index = max(int(len(rankings) * 0.2), 5)
    visible_rankings = rankings[:cutoff_index]

    user_rank = next((r for r in rankings if r['user_id'] == current_user.id), None)

    return success_response({
        'rankings': visible_rankings,
        'user_rank': user_rank,
        'dimension': dimension,
        'rank_type': 'dimension'
    })


@ranking_bp.route('/my-growth-curve', methods=['GET'])
@login_required
def get_growth_curve():
    """获取个人成长曲线（私密）"""
    days = request.args.get('days', 90, type=int)

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)

    histories = RankingHistory.query.filter(
        RankingHistory.user_id == current_user.id,
        RankingHistory.recorded_date >= start_date
    ).order_by(RankingHistory.recorded_date).all()

    growth_data = {
        'average_score': [],
        'percentile': [],
        'writing_count': []
    }

    for history in histories:
        data_point = {
            'date': history.recorded_date.isoformat(),
            'value': round(history.value, 2)
        }

        if history.data_type in growth_data:
            growth_data[history.data_type].append(data_point)

    if not growth_data['average_score']:
        writings = Writing.query.filter(
            Writing.user_id == current_user.id,
            Writing.is_scored == True,
            Writing.submitted_at >= datetime.combine(start_date, datetime.min.time()),
            Writing.is_deleted == False
        ).order_by(Writing.submitted_at).all()

        daily_scores = {}
        for writing in writings:
            date_str = writing.submitted_at.date().isoformat()
            if date_str not in daily_scores:
                daily_scores[date_str] = []
            daily_scores[date_str].append(writing.overall_score)

        for date_str, scores in daily_scores.items():
            growth_data['average_score'].append({
                'date': date_str,
                'value': round(sum(scores) / len(scores), 2)
            })

    return success_response({
        'growth_data': growth_data,
        'period_days': days,
        'is_private': True
    })


@ranking_bp.route('/toggle-visibility', methods=['POST'])
@login_required
def toggle_ranking_visibility():
    """用户自主退出/加入排行榜"""
    data = request.get_json() or {}
    show = data.get('show', True)

    current_user.show_in_ranking = show
    db.session.commit()

    return success_response({
        'show_in_ranking': show
    }, message=f'排行榜展示已{"开启" if show else "关闭"}')
