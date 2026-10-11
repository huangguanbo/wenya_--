"""
文芽 - 数据库迁移脚本
创建所有表
"""
from app import create_app, db
from models.user import User, Guardian, UserProfile
from models.writing import Writing, WritingDraft, WritingScore
from models.ai_memory import AIMemory, AIConversation
from models.ranking import RankingRecord, RankingHistory
from models.community import CommunityWork, WorkLike, WorkComment
from models.compliance import ComplianceLog, AlgorithmLog


def init_db():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✅ 数据库表创建成功")


def drop_db():
    """删除所有表（危险操作！）"""
    app = create_app()
    
    with app.app_context():
        db.drop_all()
        print("⚠️ 所有数据库表已删除")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'drop':
        confirm = input("确定要删除所有数据库表吗？此操作不可恢复！(yes/no): ")
        if confirm == 'yes':
            drop_db()
        else:
            print("已取消操作")
    else:
        init_db()
