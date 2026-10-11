"""
文芽 - 通用 API 路由
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func

from app import db
from models.user import UserProfile
from models.writing import Writing, WritingScore
from models.ranking import RankingRecord
from utils.response import success_response

api_bp = Blueprint('api', __name__)


WRITING_CHALLENGES = [
    {
        'id': 'describe_person',
        'title': '人物速写挑战',
        'description': '用 200 字描写一位给你留下深刻印象的人，突出其一个鲜明特点。',
        'genre': '记叙文',
        'min_words': 200,
        'max_words': 500,
        'difficulty': 'easy'
    },
    {
        'id': 'five_senses',
        'title': '五感描写挑战',
        'description': '运用视觉、听觉、嗅觉、味觉、触觉描写一个场景，让读者身临其境。',
        'genre': '散文',
        'min_words': 300,
        'max_words': 800,
        'difficulty': 'medium'
    },
    {
        'id': 'argument_essay',
        'title': '观点论证挑战',
        'description': '针对"电子产品是否有利于学习"提出你的观点，并用至少两个论据支撑。',
        'genre': '议论文',
        'min_words': 400,
        'max_words': 1000,
        'difficulty': 'hard'
    },
    {
        'id': 'story_continuation',
        'title': '故事续写挑战',
        'description': '以"那天，我打开了那扇尘封已久的门……"为开头，续写一个完整故事。',
        'genre': '想象文',
        'min_words': 400,
        'max_words': 1000,
        'difficulty': 'medium'
    }
]

MATERIAL_LIBRARY = {
    'quote': [
        '学而不思则罔，思而不学则殆。——孔子',
        '读书破万卷，下笔如有神。——杜甫',
        '生活不是缺少美，而是缺少发现美的眼睛。——罗丹',
        '时间就像海绵里的水，只要愿挤，总还是有的。——鲁迅'
    ],
    'idiom': [
        {'word': '画龙点睛', 'meaning': '比喻在关键处用精辟语句点明要旨，使内容更加生动有力。'},
        {'word': '胸有成竹', 'meaning': '比喻做事之前已有通盘考虑。'},
        {'word': '妙笔生花', 'meaning': '形容文笔好，善于写作。'},
        {'word': '文思泉涌', 'meaning': '形容行文思路像泉水奔涌那样迅速、丰富。'}
    ],
    'example': [
        {'title': '春天的校园', 'genre': '写景', 'snippet': '清晨的阳光透过梧桐叶的缝隙，洒在校园的小路上，像撒了一地碎金。'},
        {'title': '我的妈妈', 'genre': '写人', 'snippet': '妈妈的手很粗糙，却总能把我的衣服洗得干干净净，把饭菜做得香甜可口。'}
    ]
}


@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return success_response({'status': 'ok', 'service': 'wenya'})


@api_bp.route('/stats', methods=['GET'])
@login_required
def get_user_stats():
    """获取用户统计数据"""
    total_writings = Writing.query.filter_by(
        user_id=current_user.id,
        is_deleted=False
    ).count()

    scored_writings = Writing.query.filter_by(
        user_id=current_user.id,
        is_scored=True,
        is_deleted=False
    ).count()

    avg_score = db.session.query(func.avg(Writing.overall_score)).filter(
        Writing.user_id == current_user.id,
        Writing.is_scored == True,
        Writing.is_deleted == False
    ).scalar() or 0

    best_score = db.session.query(func.max(Writing.overall_score)).filter(
        Writing.user_id == current_user.id,
        Writing.is_scored == True,
        Writing.is_deleted == False
    ).scalar() or 0

    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    if profile:
        profile.total_writings = total_writings
        profile.average_score = avg_score
        profile.best_score = best_score
        db.session.commit()

    return success_response({
        'total_writings': total_writings,
        'scored_writings': scored_writings,
        'average_score': round(avg_score, 1),
        'best_score': round(best_score, 1),
        'profile': profile.to_dict() if profile else None
    })


@api_bp.route('/compliance/info', methods=['GET'])
def get_compliance_info():
    """获取合规信息"""
    from flask import current_app

    return success_response({
        'icp_number': current_app.config.get('ICP_NUMBER', ''),
        'algorithm_number': current_app.config.get('ALGORITHM_NUMBER', ''),
        'privacy_policy_url': '/privacy-policy',
        'terms_of_service_url': '/terms-of-service'
    })


@api_bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """获取用户通知列表"""
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()

    notifications = []

    if profile:
        if profile.consecutive_days and profile.consecutive_days > 0:
            notifications.append({
                'id': 'streak',
                'type': 'achievement',
                'title': f'连续写作 {profile.consecutive_days} 天',
                'content': '坚持就是胜利，继续保持！',
                'created_at': None,
                'is_read': False
            })

        if profile.average_score and profile.average_score >= 85:
            notifications.append({
                'id': 'high_score',
                'type': 'achievement',
                'title': '写作小达人',
                'content': f'你的平均得分达到 {round(profile.average_score, 1)} 分，太棒了！',
                'created_at': None,
                'is_read': False
            })

    notifications.append({
        'id': 'challenge',
        'type': 'challenge',
        'title': '本周写作挑战',
        'content': f'本周共有 {len(WRITING_CHALLENGES)} 个写作挑战等你完成',
        'created_at': None,
        'is_read': False
    })

    return success_response({'notifications': notifications, 'unread_count': len(notifications)})


@api_bp.route('/challenges', methods=['GET'])
@login_required
def get_challenges():
    """获取写作挑战列表"""
    return success_response({'challenges': WRITING_CHALLENGES})


@api_bp.route('/challenges/<challenge_id>', methods=['GET'])
@login_required
def get_challenge(challenge_id):
    """获取单个写作挑战详情"""
    challenge = next((c for c in WRITING_CHALLENGES if c['id'] == challenge_id), None)
    if not challenge:
        from utils.response import error_response
        return error_response('挑战不存在', status_code=404)
    return success_response({'challenge': challenge})


@api_bp.route('/materials', methods=['GET'])
@login_required
def get_materials():
    """获取素材库"""
    category = request.args.get('category')
    if category and category in MATERIAL_LIBRARY:
        return success_response({'category': category, 'items': MATERIAL_LIBRARY[category]})
    return success_response({'categories': list(MATERIAL_LIBRARY.keys()), 'materials': MATERIAL_LIBRARY})
