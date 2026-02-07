"""
用户管理API路由
"""
from flask import Blueprint, request, jsonify, make_response
from modules.user_module import UserModule
from middleware.auth_middleware import auth_middleware

user_bp = Blueprint('user', __name__, url_prefix='/api/users')
user_module = UserModule()


@user_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': '用户名和密码不能为空'
            }), 400
        
        # 检查用户名是否已存在
        if user_module.exists({'username': data['username']}):
            return jsonify({
                'success': False,
                'error': '用户名已存在'
            }), 400
        
        # 检查手机号是否已存在
        if 'phone' in data and user_module.exists({'phone': data['phone']}):
            return jsonify({
                'success': False,
                'error': '手机号已被注册'
            }), 400
        
        # 检查邮箱是否已存在
        if 'email' in data and user_module.exists({'email': data['email']}):
            return jsonify({
                'success': False,
                'error': '邮箱已被注册'
            }), 400
        
        # 创建用户
        user_id = user_module.create(data)
        
        return jsonify({
            'success': True,
            'data': {'user_id': user_id}
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@user_bp.route('/login/password', methods=['POST'])
def login_by_password():
    """账号密码登录"""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': '用户名和密码不能为空'
            }), 400
        
        result = user_module.login_by_password(data['username'], data['password'])
        
        if not result:
            return jsonify({
                'success': False,
                'error': '用户名或密码错误'
            }), 401
        
        # 创建响应并设置Cookie
        response = make_response(jsonify({
            'success': True,
            'data': result
        }))
        
        response.set_cookie(
            'session_id',
            result['session_id'],
            max_age=86400,  # 24小时
            httponly=True,
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@user_bp.route('/login/code', methods=['POST'])
def login_by_code():
    """验证码登录"""
    try:
        data = request.get_json()
        
        if not data or 'phone' not in data or 'code' not in data:
            return jsonify({
                'success': False,
                'error': '手机号和验证码不能为空'
            }), 400
        
        # 这里需要实际的验证码校验逻辑
        # 暂时使用示例代码
        correct_code = '123456'  # 实际应从缓存或数据库获取
        
        result = user_module.login_by_code(data['phone'], data['code'], correct_code)
        
        if not result:
            return jsonify({
                'success': False,
                'error': '验证码错误'
            }), 401
        
        # 创建响应并设置Cookie
        response = make_response(jsonify({
            'success': True,
            'data': result
        }))
        
        response.set_cookie(
            'session_id',
            result['session_id'],
            max_age=86400,
            httponly=True,
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@user_bp.route('/logout', methods=['POST'])
@auth_middleware.require_auth
def logout():
    """用户登出"""
    try:
        session_id = request.cookies.get('session_id')
        user_module.logout(session_id)
        
        response = make_response(jsonify({
            'success': True,
            'message': '登出成功'
        }))
        
        response.delete_cookie('session_id')
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@user_bp.route('/profile', methods=['GET'])
@auth_middleware.require_auth
def get_profile():
    """获取当前用户信息"""
    try:
        user_id = request.user['user_id']
        
        from bson import ObjectId
        user = user_module.read({'_id': ObjectId(user_id)})
        
        if not user:
            return jsonify({
                'success': False,
                'error': '用户不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@user_bp.route('/<user_id>', methods=['GET'])
@auth_middleware.require_auth
def get_user(user_id):
    """获取指定用户信息"""
    try:
        from bson import ObjectId
        user = user_module.read({'_id': ObjectId(user_id)})
        
        if not user:
            return jsonify({
                'success': False,
                'error': '用户不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@user_bp.route('/<user_id>', methods=['PUT'])
@auth_middleware.require_auth
def update_user(user_id):
    """更新用户信息"""
    try:
        data = request.get_json()
        
        # 只允许更新自己的信息
        if request.user['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': '无权修改其他用户信息'
            }), 403
        
        from bson import ObjectId
        success = user_module.update({'_id': ObjectId(user_id)}, data)
        
        if not success:
            return jsonify({
                'success': False,
                'error': '更新失败'
            }), 400
        
        return jsonify({
            'success': True,
            'message': '更新成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@user_bp.route('/list', methods=['GET'])
@auth_middleware.require_auth
def get_users_list():
    """获取用户列表（分页）"""
    try:
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 20))
        
        users = user_module.get_users_list(skip, limit)
        
        return jsonify({
            'success': True,
            'data': users
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500