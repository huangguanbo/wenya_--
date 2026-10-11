# 微信小程序 API 适配指南

## 概述

本文档说明如何将现有 Flask 后端 API 适配到微信小程序，包括新增的微信登录端点和修改建议。

## 新增 API 端点

### 1. 微信登录

**端点**: `POST /api/auth/wx-login`

**请求体**:
```json
{
  "code": "微信登录 code"
}
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "token": "jwt_token",
    "user": {
      "id": 1,
      "username": "user123",
      "nickname": "用户昵称",
      "avatar": "头像 URL",
      "phone": "138****1234",
      "grade_name": "初中二年级",
      "level": "写作达人"
    }
  }
}
```

**后端实现示例**:

```python
# routes/auth.py
import requests
from flask import Blueprint, request, jsonify
from models.user import User
from services.auth import generate_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/wx-login', methods=['POST'])
def wx_login():
    """
    微信小程序登录
    1. 使用 code 调用微信 API 获取 openid 和 session_key
    2. 根据 openid 查找或创建用户
    3. 返回 JWT token
    """
    data = request.get_json()
    code = data.get('code')
    
    if not code:
        return jsonify({'error': 'code 必填'}), 400
    
    # 调用微信 API
    appid = current_app.config['WECHAT_APPID']
    secret = current_app.config['WECHAT_SECRET']
    
    wx_url = 'https://api.weixin.qq.com/sns/jscode2session'
    params = {
        'appid': appid,
        'secret': secret,
        'js_code': code,
        'grant_type': 'authorization_code'
    }
    
    response = requests.get(wx_url, params=params)
    wx_data = response.json()
    
    if 'errcode' in wx_data:
        return jsonify({'error': '微信登录失败'}), 400
    
    openid = wx_data['openid']
    session_key = wx_data['session_key']
    
    # 查找或创建用户
    user = User.query.filter_by(wechat_openid=openid).first()
    
    if not user:
        # 创建新用户（需要后续补充信息）
        user = User(
            username=f'wx_{openid[:8]}',
            wechat_openid=openid,
            nickname=wx_data.get('nickname', '微信用户')
        )
        db.session.add(user)
        db.session.commit()
    
    # 生成 token
    token = generate_token(user)
    
    return jsonify({
        'code': 0,
        'data': {
            'token': token,
            'user': user.to_dict()
        }
    })
```

### 2. 发送验证码

**端点**: `POST /api/auth/send-code`

**请求体**:
```json
{
  "phone": "13800138000"
}
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "message": "验证码已发送"
  }
}
```

**后端实现示例**:

```python
@auth_bp.route('/send-code', methods=['POST'])
def send_verification_code():
    """发送验证码（短信或微信模板消息）"""
    data = request.get_json()
    phone = data.get('phone')
    
    if not phone or not re.match(r'^1[3-9]\d{9}$', phone):
        return jsonify({'error': '手机号格式错误'}), 400
    
    # 生成 6 位验证码
    code = ''.join(random.choices('0123456789', k=6))
    
    # 存储验证码到 Redis（5 分钟有效期）
    redis_client.setex(f'verify_code:{phone}', 300, code)
    
    # 发送短信（使用阿里云/腾讯云短信服务）
    # send_sms(phone, code)
    
    # 或发送微信模板消息
    # send_wechat_template(phone, code)
    
    return jsonify({
        'code': 0,
        'data': {'message': '验证码已发送'}
    })
```

### 3. 获取我的排名

**端点**: `GET /api/ranking/my-rank`

**响应**:
```json
{
  "code": 0,
  "data": {
    "rank": 15,
    "score": 87.5,
    "percentile": 92.5,
    "total_users": 500
  }
}
```

### 4. 获取统计数据

**端点**: `GET /api/stats`

**响应**:
```json
{
  "code": 0,
  "data": {
    "total_writings": 25,
    "average_score": 82.5,
    "best_score": 95.0,
    "profile": {
      "consecutive_days": 12,
      "total_words": 15000
    }
  }
}
```

## 修改现有 API

### 1. 社区作品列表

**原端点**: `GET /api/community/works`

**新增参数**:
- `grade`: 年级筛选（elementary/middle/high）
- `sort`: 排序方式（latest/likes/score）

**响应调整**: 增加 `is_liked` 字段

```python
@community_bp.route('/works', methods=['GET'])
def get_community_works():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    grade = request.args.get('grade')  # 新增
    sort = request.args.get('sort', 'latest')  # 新增
    
    query = CommunityWork.query
    
    # 年级筛选
    if grade:
        query = query.join(User).filter(User.grade_level == grade)
    
    # 排序
    if sort == 'likes':
        query = query.order_by(CommunityWork.like_count.desc())
    elif sort == 'score':
        query = query.order_by(CommunityWork.overall_score.desc())
    else:
        query = query.order_by(CommunityWork.created_at.desc())
    
    works = query.paginate(page=page, per_page=per_page)
    
    # 检查当前用户是否点赞
    current_user_id = get_current_user_id()
    liked_work_ids = set()
    if current_user_id:
        likes = WorkLike.query.filter_by(user_id=current_user_id).all()
        liked_work_ids = {like.work_id for like in likes}
    
    return jsonify({
        'code': 0,
        'data': [{
            **work.to_dict(),
            'is_liked': work.id in liked_work_ids  # 新增字段
        } for work in works.items]
    })
```

### 2. 点赞/取消点赞

**新增端点**: 
- `POST /api/community/works/<id>/like`
- `POST /api/community/works/<id>/unlike`

**后端实现**:

```python
@community_bp.route('/works/<int:id>/like', methods=['POST'])
@login_required
def like_work(id):
    work = CommunityWork.query.get_or_404(id)
    
    # 检查是否已点赞
    existing = WorkLike.query.filter_by(
        user_id=current_user.id,
        work_id=id
    ).first()
    
    if existing:
        return jsonify({'error': '已点赞'}), 400
    
    like = WorkLike(user_id=current_user.id, work_id=id)
    db.session.add(like)
    
    # 增加点赞数
    work.like_count += 1
    db.session.commit()
    
    return jsonify({'code': 0})

@community_bp.route('/works/<int:id>/unlike', methods=['POST'])
@login_required
def unlike_work(id):
    work = CommunityWork.query.get_or_404(id)
    
    like = WorkLike.query.filter_by(
        user_id=current_user.id,
        work_id=id
    ).first()
    
    if not like:
        return jsonify({'error': '未点赞'}), 400
    
    db.session.delete(like)
    
    # 减少点赞数
    work.like_count -= 1
    db.session.commit()
    
    return jsonify({'code': 0})
```

## 环境变量配置

在 `.env` 中添加微信小程序相关配置：

```bash
# 微信小程序配置
WECHAT_APPID=wx1234567890abcdef
WECHAT_SECRET=your-wechat-secret-key

# 短信服务配置（阿里云）
ALIYUN_SMS_ACCESS_KEY=your-access-key
ALIYUN_SMS_ACCESS_SECRET=your-access-secret
ALIYUN_SMS_SIGN_NAME=文芽平台
ALIYUN_SMS_TEMPLATE_CODE=SMS_123456789

# 或腾讯云短信
TENCENT_SMS_SECRET_ID=your-secret-id
TENCENT_SMS_SECRET_KEY=your-secret-key
TENCENT_SMS_APP_ID=1400000000
TENCENT_SMS_TEMPLATE_ID=123456
```

## 数据库变更

### 用户表新增字段

```python
# models/user.py
class User(db.Model, UserMixin):
    # ... 现有字段 ...
    
    # 新增微信相关字段
    wechat_openid = db.Column(db.String(64), unique=True, index=True)
    wechat_unionid = db.Column(db.String(64), unique=True)
    avatar = db.Column(db.String(512))
    gender = db.Column(db.Integer, default=0)  # 0:未知 1:男 2:女
    
    # 新增年级字段
    grade_level = db.Column(db.String(20))  # elementary/middle/high
    grade_name = db.Column(db.String(50))  # 小学一年级/初中二年级等
```

### 新增点赞表

```python
# models/community.py
class WorkLike(db.Model):
    __tablename__ = 'work_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    work_id = db.Column(db.Integer, db.ForeignKey('community_works.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'work_id', name='uix_user_work')
    )
    
    user = db.relationship('User', backref='likes')
    work = db.relationship('CommunityWork', backref='likes')
```

## 内容安全适配

小程序对用户生成内容有严格审核要求，建议添加：

### 1. 微信内容安全 API 集成

```python
# services/content_safe.py
import requests

class WechatContentSafe:
    """微信内容安全服务"""
    
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = 'https://api.weixin.qq.com/wxa'
    
    def check_text(self, content):
        """文本内容安全检测"""
        url = f'{self.base_url}/msg_sec_check?access_token={self.access_token}'
        
        data = {
            'content': content,
            'version': 2,
            'scene': 1  # 1:评论 2:资料 3:评论 4:昵称 5:签名
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get('errcode') == 0:
            return {
                'valid': result['result']['valid'] == 1,
                'label': result['result']['label']  # 违规类型
            }
        
        return {'valid': True}  # 默认通过
    
    def check_image(self, media_url):
        """图片内容安全检测"""
        # 实现类似逻辑
        pass
```

### 2. 使用位置

```python
# routes/community.py
@community_bp.route('/works', methods=['POST'])
@login_required
def create_work():
    data = request.get_json()
    title = data.get('title', '')
    content = data.get('content', '')
    
    # 内容安全检查
    safe_service = WechatContentSafe(get_wechat_access_token())
    
    title_result = safe_service.check_text(title)
    if not title_result['valid']:
        return jsonify({'error': '标题包含不当内容'}), 400
    
    content_result = safe_service.check_text(content)
    if not content_result['valid']:
        return jsonify({'error': '内容包含不当内容'}), 400
    
    # 继续创建作品...
```

## 测试建议

### 1. 单元测试

```python
# tests/test_wechat_auth.py
def test_wx_login():
    """测试微信登录"""
    response = client.post('/api/auth/wx-login', json={
        'code': 'test_code'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 0
    assert 'token' in data['data']
    assert 'user' in data['data']

def test_send_code():
    """测试发送验证码"""
    response = client.post('/api/auth/send-code', json={
        'phone': '13800138000'
    })
    assert response.status_code == 200
```

### 2. 小程序真机测试

1. 在微信开发者工具中配置后端地址
2. 使用真机调试模式
3. 测试登录、注册、写作、评分等核心流程
4. 检查网络请求和错误处理

## 上线前检查清单

- [ ] 配置微信小程序 AppID 和 Secret
- [ ] 配置短信服务
- [ ] 配置服务器域名（微信公众平台）
- [ ] 测试微信登录流程
- [ ] 测试手机号验证登录
- [ ] 测试内容安全检测
- [ ] 添加日志监控
- [ ] 准备隐私政策和用户协议
- [ ] 准备 ICP 备案和算法备案信息
- [ ] 选择正确的服务类目（教育 - 在线教育）

## 常见问题

### Q: 微信登录失败，提示 invalid code？
A: code 只能使用一次，5 分钟后过期。确保每次登录都调用 wx.login() 获取新 code。

### Q: 小程序请求后端被拒绝？
A: 检查微信公众平台是否配置了正确的服务器域名。

### Q: 如何获取微信 access_token？
A: 使用 AppID 和 Secret 调用 `https://api.weixin.qq.com/cgi-bin/token` 接口。

### Q: 短信服务用什么提供商？
A: 推荐使用阿里云或腾讯云短信服务，价格和稳定性都不错。

## 参考资料

- [微信小程序登录文档](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/login.html)
- [微信内容安全接口](https://developers.weixin.qq.com/miniprogram/dev/api/open-api/security/)
- [微信小程序云开发](https://developers.weixin.qq.com/miniprogram/dev/wxcloud/basis/getting-started.html)
