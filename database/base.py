"""
数据模块基类
定义所有数据模块的统一接口规范
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from .connection import db_connection


class BaseDataModule(ABC):
    """数据模块基类"""
    
    def __init__(self, collection_name: str, db_name: Optional[str] = None):
        """
        初始化数据模块
        
        Args:
            collection_name: 集合名称
            db_name: 数据库名称，默认使用配置中的数据库名
        """
        self.collection_name = collection_name
        self.db_name = db_name
        self._collection = None
    
    @property
    def collection(self):
        """获取集合实例（延迟加载）"""
        if self._collection is None:
            self._collection = db_connection.get_collection(self.collection_name, self.db_name)
        return self._collection
    
    def _get_current_timestamp(self) -> datetime:
        """获取当前时间戳"""
        return datetime.utcnow()
    
    def _ensure_connection(self):
        """确保数据库连接正常"""
        if not db_connection.is_connected():
            db_connection.connect()
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> str:
        """
        创建数据
        
        Args:
            data: 要创建的数据字典
            
        Returns:
            str: 新创建数据的ID
        """
        pass
    
    @abstractmethod
    def read(self, query: Dict[str, Any], projection: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        读取数据
        
        Args:
            query: 查询条件
            projection: 返回字段投影
            
        Returns:
            查询结果数据
        """
        pass
    
    @abstractmethod
    def update(self, query: Dict[str, Any], update_data: Dict[str, Any]) -> bool:
        """
        更新数据
        
        Args:
            query: 查询条件
            update_data: 要更新的数据
            
        Returns:
            bool: 是否更新成功
        """
        pass
    
    @abstractmethod
    def delete(self, query: Dict[str, Any]) -> bool:
        """
        删除数据
        
        Args:
            query: 查询条件
            
        Returns:
            bool: 是否删除成功
        """
        pass
    
    def count(self, query: Dict[str, Any]) -> int:
        """
        统计数据数量
        
        Args:
            query: 查询条件
            
        Returns:
            int: 符合条件的数据数量
        """
        self._ensure_connection()
        return self.collection.count_documents(query)
    
    def exists(self, query: Dict[str, Any]) -> bool:
        """
        检查数据是否存在
        
        Args:
            query: 查询条件
            
        Returns:
            bool: 数据是否存在
        """
        return self.count(query) > 0