"""
配置管理模块
"""
import os
from dotenv import load_dotenv

import uuid

load_dotenv()


class Config:
    """应用配置类"""
    
    # MongoDB配置
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'longgaowall_db')
    
    # 连接池配置
    MONGODB_MAX_POOL_SIZE = int(os.getenv('MONGODB_MAX_POOL_SIZE', 100))
    MONGODB_MIN_POOL_SIZE = int(os.getenv('MONGODB_MIN_POOL_SIZE', 5))
    MONGODB_CONNECT_TIMEOUT = int(os.getenv('MONGODB_CONNECT_TIMEOUT', 10000))
    MONGODB_SERVER_SELECTION_TIMEOUT = int(os.getenv('MONGODB_SERVER_SELECTION_TIMEOUT', 30000))
    
    # API配置
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    API_DEBUG = os.getenv('API_DEBUG', 'True').lower() == 'true'
    
    # 会话配置
    SESSION_SECRET_KEY = os.getenv('SESSION_SECRET_KEY', 'default-secret-key-change-in-production')
    SESSION_MAX_AGE = int(os.getenv('SESSION_MAX_AGE', 86400))  # 24小时
    
    # 密码配置
    ACCESS_PASSWORD = os.getenv('ACCESS_PASSWORD', uuid.uuid4().hex)
    
    # 批量操作配置
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 1000))
    BATCH_RETRY_TIMES = int(os.getenv('BATCH_RETRY_TIMES', 3))
    BATCH_RETRY_DELAY = int(os.getenv('BATCH_RETRY_DELAY', 1000))


config = Config()