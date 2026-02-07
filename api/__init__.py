"""
API路由模块
"""
from .user_routes import user_bp
from .list_routes import list_bp
from .counter_routes import counter_bp
from .dict_routes import dict_bp
from .collection_routes import collection_bp
from .batch_routes import batch_bp

__all__ = ['user_bp', 'list_bp', 'counter_bp', 'dict_bp', 'collection_bp', 'batch_bp']