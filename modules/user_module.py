"""
用户管理模块
提供用户CRUD、认证、会话管理功能
"""
import hashlib
import secrets
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pymongo import ASCENDING
from bson import ObjectId
from database.base import BaseDataModule
from database.connection import db_connection
from config import config


class UserModule(BaseDataModule):
    """用户管理模块"""
    
    def __init__(self, db_name: Optional[str] = None):
        super().__init__('users', db_name)
        self._init_indexes()
    
    def _init_indexes(self):
        """初始化索引"""
        try:
            self.collection.create_index([('username', ASCENDING)], unique=True)
            self.collection.create_index([('phone', ASCENDING)], unique=True, sparse=True)
            self.collection.create_index([('email', ASCENDING)], unique=True, sparse=True)
            self.collection.create_index([('session_id', ASCENDING)], sparse=True)
        except Exception as e:
            print(f"索引创建警告: {e}")
    
    def _hash_password(self, password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        return secrets.token_urlsafe(32)
    
    def create(self, data: Dict[str, str]) -> str:
        """
        创建用户
        
        Args:
            data: 用户数据，包含username, password, phone, email等
            
        Returns:
            str: 用户ID
        """
        self._ensure_connection()
        
        user_data = {
            'username': data['username'],
            'password': self._hash_password(data['password']),
            'phone': data.get('phone'),
            'email': data.get('email'),
            'created_at': self._get_current_timestamp(),
            'updated_at': self._get_current_timestamp(),
            'is_active': True,
            'session_id': None,
            'session_expires': None
        }
        
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)
    
    def read(self, query: Dict[str, str], projection: Optional[Dict[str, str]] = None) -> Optional[Dict[str, str]]:
        """
        读取用户信息
        
        Args:
            query: 查询条件
            projection: 返回字段投影
            
        Returns:
            用户信息字典
        """
        self._ensure_connection()
        
        # 默认不返回密码
        if projection is None:
            projection = {'password': 0}
        elif 'password' not in projection:
            projection['password'] = 0
        
        return self.collection.find_one(query, projection)
    
    def update(self, query: Dict[str, str], update_data: Dict[str, str]) -> bool:
        """
        更新用户信息
        
        Args:
            query: 查询条件
            update_data: 更新数据
            
        Returns:
            bool: 是否更新成功
        """
        self._ensure_connection()
        
        # 如果更新密码，需要哈希
        if 'password' in update_data:
            update_data['password'] = self._hash_password(update_data['password'])
        
        update_data['updated_at'] = self._get_current_timestamp()
        
        result = self.collection.update_one(
            query,
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def delete(self, query: Dict[str, str]) -> bool:
        """
        删除用户（软删除，设置is_active为False）
        
        Args:
            query: 查询条件
            
        Returns:
            bool: 是否删除成功
        """
        return self.update(query, {'is_active': False})
    
    def login_by_password(self, username: str, password: str) -> Optional[Dict[str, str]]:
        """
        账号密码登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            用户信息和会话信息
        """
        user = self.read({'username': username, 'is_active': True})
        if not user:
            return None
        
        if user.get('password') != self._hash_password(password):
            return None
        
        # 创建会话
        session_id = self._generate_session_id()
        session_expires = self._get_current_timestamp() + timedelta(seconds=config.SESSION_MAX_AGE)
        
        self.update(
            {'_id': ObjectId(user['_id'])},
            {'session_id': session_id, 'session_expires': session_expires}
        )
        
        return {
            'user_id': str(user['_id']),
            'username': user['username'],
            'session_id': session_id,
            'expires_at': session_expires.isoformat()
        }
    
    def login_by_code(self, phone: str, code: str, correct_code: str) -> Optional[Dict[str, str]]:
        """
        验证码登录
        
        Args:
            phone: 手机号
            code: 用户输入的验证码
            correct_code: 正确的验证码
            
        Returns:
            用户信息和会话信息
        """
        if code != correct_code:
            return None
        
        user = self.read({'phone': phone, 'is_active': True})
        if not user:
            # 如果用户不存在，自动创建
            user_id = self.create({
                'username': phone,
                'password': secrets.token_urlsafe(16),
                'phone': phone
            })
            user = self.read({'_id': ObjectId(user_id)})
        
        # 创建会话
        session_id = self._generate_session_id()
        session_expires = self._get_current_timestamp() + timedelta(seconds=config.SESSION_MAX_AGE)
        
        self.update(
            {'_id': ObjectId(user['_id'])},
            {'session_id': session_id, 'session_expires': session_expires}
        )
        
        return {
            'user_id': str(user['_id']),
            'username': user['username'],
            'session_id': session_id,
            'expires_at': session_expires.isoformat()
        }
    
    def verify_session(self, session_id: str) -> Optional[Dict[str, str]]:
        """
        验证会话有效性
        
        Args:
            session_id: 会话ID
            
        Returns:
            用户信息
        """
        user = self.read({
            'session_id': session_id,
            'is_active': True
        })
        
        if not user:
            return None
        
        # 检查会话是否过期
        if user.get('session_expires') and user['session_expires'] < self._get_current_timestamp():
            return None
        
        return {
            'user_id': str(user['_id']),
            'username': user['username']
        }
    
    def refresh_session(self, session_id: str) -> bool:
        """
        刷新会话有效期
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 是否刷新成功
        """
        new_expires = self._get_current_timestamp() + timedelta(seconds=config.SESSION_MAX_AGE)
        return self.update(
            {'session_id': session_id, 'is_active': True},
            {'session_expires': new_expires}
        )
    
    def logout(self, session_id: str) -> bool:
        """
        用户登出，销毁会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 是否登出成功
        """
        return self.update(
            {'session_id': session_id},
            {'session_id': None, 'session_expires': None}
        )
    
    def get_users_list(self, skip: int = 0, limit: int = 20) -> List[Dict[str, str]]:
        """
        获取用户列表（分页）
        
        Args:
            skip: 跳过数量
            limit: 返回数量限制
            
        Returns:
            用户列表
        """
        self._ensure_connection()
        users = self.collection.find(
            {'is_active': True},
            {'password': 0}
        ).skip(skip).limit(limit)
        
        return [
            {**user, '_id': str(user['_id'])}
            for user in users
        ]