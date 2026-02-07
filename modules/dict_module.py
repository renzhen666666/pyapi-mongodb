"""
字典型数据模块
支持用户扩展信息、配置项等字典结构数据的存储
"""
from typing import Dict, List, Optional, Any
from pymongo import ASCENDING
from bson import ObjectId
from database.base import BaseDataModule


class DictModule(BaseDataModule):
    """字典型数据模块"""
    
    def __init__(self, collection_name: str = 'dict_data', db_name: Optional[str] = None):
        super().__init__(collection_name, db_name)
        self._init_indexes()
    
    def _init_indexes(self):
        """初始化索引"""
        try:
            self.collection.create_index([('dict_key', ASCENDING)], unique=True)
        except Exception as e:
            print(f"索引创建警告: {e}")
    
    def create(self, data: Dict[str, Any]) -> str:
        """
        创建字典数据
        
        Args:
            data: 字典数据，包含dict_key, data等
            
        Returns:
            str: 字典数据ID
        """
        self._ensure_connection()
        
        dict_data = {
            'dict_key': data['dict_key'],
            'data': data.get('data', {}),
            'created_at': self._get_current_timestamp(),
            'updated_at': self._get_current_timestamp()
        }
        
        result = self.collection.insert_one(dict_data)
        return str(result.inserted_id)
    
    def read(self, query: Dict[str, str], projection: Optional[Dict[str, str]] = None) -> Optional[Dict[str, str]]:
        """读取字典数据"""
        self._ensure_connection()
        return self.collection.find_one(query, projection)
    
    def update(self, query: Dict[str, str], update_data: Dict[str, str]) -> bool:
        """更新字典数据"""
        self._ensure_connection()
        update_data['updated_at'] = self._get_current_timestamp()
        result = self.collection.update_one(query, {'$set': update_data})
        return result.modified_count > 0
    
    def delete(self, query: Dict[str, str]) -> bool:
        """删除字典数据"""
        self._ensure_connection()
        result = self.collection.delete_one(query)
        return result.deleted_count > 0
    
    def set_field(self, dict_key: str, field_path: str, value: Any) -> bool:
        """
        设置字典字段值
        
        Args:
            dict_key: 字典标识
            field_path: 字段路径，支持嵌套，如 'user.profile.name'
            value: 要设置的值
            
        Returns:
            bool: 是否设置成功
        """
        self._ensure_connection()
        
        # 构建嵌套更新路径
        update_path = f'data.{field_path}'
        
        result = self.collection.update_one(
            {'dict_key': dict_key},
            {
                '$set': {
                    update_path: value,
                    'updated_at': self._get_current_timestamp()
                }
            },
            upsert=True
        )
        
        return result.modified_count > 0 or result.upserted_id is not None
    
    def get_field(self, dict_key: str, field_path: str) -> Optional[Any]:
        """
        获取字典字段值
        
        Args:
            dict_key: 字典标识
            field_path: 字段路径，支持嵌套，如 'user.profile.name'
            
        Returns:
            字段值，如果不存在返回None
        """
        self._ensure_connection()
        
        # 构建嵌套查询路径
        query_path = f'data.{field_path}'
        
        result = self.collection.find_one(
            {'dict_key': dict_key},
            {query_path: 1, '_id': 0}
        )
        
        if not result:
            return None
        
        # 从嵌套路径中提取值
        keys = field_path.split('.')
        value = result.get('data', {})
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        
        return value
    
    def delete_field(self, dict_key: str, field_path: str) -> bool:
        """
        删除字典字段
        
        Args:
            dict_key: 字典标识
            field_path: 字段路径，支持嵌套，如 'user.profile.name'
            
        Returns:
            bool: 是否删除成功
        """
        self._ensure_connection()
        
        # 构建嵌套删除路径
        update_path = f'data.{field_path}'
        
        result = self.collection.update_one(
            {'dict_key': dict_key},
            {
                '$unset': {update_path: 1},
                '$set': {'updated_at': self._get_current_timestamp()}
            }
        )
        
        return result.modified_count > 0
    
    def set_multiple_fields(self, dict_key: str, fields: Dict[str, Any]) -> bool:
        """
        批量设置字典字段
        
        Args:
            dict_key: 字典标识
            fields: 字段字典，如 {'user.name': 'John', 'user.age': 30}
            
        Returns:
            bool: 是否设置成功
        """
        self._ensure_connection()
        
        update_dict = {'updated_at': self._get_current_timestamp()}
        
        for field_path, value in fields.items():
            update_path = f'data.{field_path}'
            update_dict[update_path] = value
        
        result = self.collection.update_one(
            {'dict_key': dict_key},
            {'$set': update_dict},
            upsert=True
        )
        
        return result.modified_count > 0 or result.upserted_id is not None
    
    def get_all_fields(self, dict_key: str) -> Dict[str, Any]:
        """
        获取字典所有字段
        
        Args:
            dict_key: 字典标识
            
        Returns:
            Dict[str, Any]: 所有字段的字典
        """
        self._ensure_connection()
        
        result = self.collection.find_one(
            {'dict_key': dict_key},
            {'data': 1, '_id': 0}
        )
        
        return result.get('data', {}) if result else {}
    
    def merge_dict(self, dict_key: str, data: Dict[str, Any], overwrite: bool = True) -> bool:
        """
        合并字典数据
        
        Args:
            dict_key: 字典标识
            data: 要合并的数据
            overwrite: 是否覆盖已存在的字段
            
        Returns:
            bool: 是否合并成功
        """
        self._ensure_connection()
        
        if overwrite:
            update_dict = {
                f'data.{k}': v for k, v in data.items()
            }
            update_dict['updated_at'] = self._get_current_timestamp()
            
            result = self.collection.update_one(
                {'dict_key': dict_key},
                {'$set': update_dict},
                upsert=True
            )
        else:
            # 只添加不存在的字段
            update_dict = {
                f'data.{k}': v for k, v in data.items()
            }
            update_dict['updated_at'] = self._get_current_timestamp()
            
            result = self.collection.update_one(
                {'dict_key': dict_key},
                {'$setOnInsert': update_dict},
                upsert=True
            )
        
        return result.modified_count > 0 or result.upserted_id is not None
    
    def clear_dict(self, dict_key: str) -> bool:
        """
        清空字典数据
        
        Args:
            dict_key: 字典标识
            
        Returns:
            bool: 是否清空成功
        """
        return self.update(
            {'dict_key': dict_key},
            {'data': {}}
        )