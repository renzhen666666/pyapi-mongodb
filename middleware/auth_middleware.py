"""
权限校验中间件
提供接口访问权限拦截功能
"""
from functools import wraps
from flask import request, jsonify
from typing import Callable, Optional
from modules.user_module import UserModule


class AuthMiddleware:
    """权限校验中间件类"""
    
    def __init__(self):
        self.user_module = UserModule()
    
    def require_auth(self, f: Callable) -> Callable:
        """
        需要认证的装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 从Cookie中获取session_id
            session_id = request.cookies.get('session_id')
            
            if not session_id:
                return jsonify({
                    'success': False,
                    'error': '未登录，请先登录'
                }), 401
            
            # 验证会话
            user_info = self.user_module.verify_session(session_id)
            
            if not user_info:
                return jsonify({
                    'success': False,
                    'error': '会话已过期，请重新登录'
                }), 401
            
            # 将用户信息添加到请求上下文
            request.user = user_info
            request.session_id = session_id
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def require_role(self, roles: list) -> Callable:
        """
        需要特定角色的装饰器
        
        Args:
            roles: 允许的角色列表
            
        Returns:
            装饰器函数
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # 先检查认证
                session_id = request.cookies.get('session_id')
                
                if not session_id:
                    return jsonify({
                        'success': False,
                        'error': '未登录，请先登录'
                    }), 401
                
                user_info = self.user_module.verify_session(session_id)
                
                if not user_info:
                    return jsonify({
                        'success': False,
                        'error': '会话已过期，请重新登录'
                    }), 401
                
                # 检查角色（这里需要根据实际业务扩展）
                # 假设用户信息中有role字段
                user_role = user_info.get('role', 'user')
                
                if user_role not in roles:
                    return jsonify({
                        'success': False,
                        'error': '权限不足'
                    }), 403
                
                request.user = user_info
                request.session_id = session_id
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def optional_auth(self, f: Callable) -> Callable:
        """
        可选认证的装饰器（如果已登录则获取用户信息，否则继续执行）
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            session_id = request.cookies.get('session_id')
            
            if session_id:
                user_info = self.user_module.verify_session(session_id)
                if user_info:
                    request.user = user_info
                    request.session_id = session_id
                else:
                    request.user = None
                    request.session_id = None
            else:
                request.user = None
                request.session_id = None
            
            return f(*args, **kwargs)
        
        return decorated_function


# 全局中间件实例
auth_middleware = AuthMiddleware()