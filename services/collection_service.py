"""
集合服务模块
提供动态添加MongoDB集合、索引创建等高级功能
"""
from typing import Dict, List, Optional, Any
from pymongo import ASCENDING, DESCENDING
from database.connection import db_connection


class CollectionService:
    """集合服务类"""
    
    def __init__(self, db_name: Optional[str] = None):
        self.db_name = db_name
    
    def create_collection(self, collection_name: str, 
                         structure: Optional[Dict[str, Any]] = None,
                         indexes: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        动态创建集合
        
        Args:
            collection_name: 集合名称
            structure: 集合结构定义（用于文档验证）
            indexes: 索引定义列表
            
        Returns:
            bool: 是否创建成功
        """
        try:
            database = db_connection.get_database(self.db_name)
            
            # 创建集合
            collection = database.create_collection(collection_name)
            
            # 如果有结构定义，创建验证规则
            if structure:
                self._create_validation_rule(database, collection_name, structure)
            
            # 如果有索引定义，创建索引
            if indexes:
                for index_def in indexes:
                    self._create_index(collection, index_def)
            
            return True
            
        except Exception as e:
            print(f"创建集合失败: {e}")
            return False
    
    def _create_validation_rule(self, database, collection_name: str, structure: Dict[str, Any]):
        """
        创建文档验证规则
        
        Args:
            database: 数据库实例
            collection_name: 集合名称
            structure: 结构定义
        """
        # 构建验证规则
        validator = {}
        properties = {}
        required = []
        
        for field_name, field_config in structure.items():
            field_type = field_config.get('type', 'string')
            is_required = field_config.get('required', False)
            
            # 根据类型添加验证规则
            if field_type == 'string':
                properties[field_name] = {'bsonType': 'string'}
            elif field_type == 'int':
                properties[field_name] = {'bsonType': 'int'}
            elif field_type == 'float':
                properties[field_name] = {'bsonType': 'double'}
            elif field_type == 'bool':
                properties[field_name] = {'bsonType': 'bool'}
            elif field_type == 'array':
                properties[field_name] = {'bsonType': 'array'}
            elif field_type == 'object':
                properties[field_name] = {'bsonType': 'object'}
            
            if is_required:
                required.append(field_name)
        
        if properties:
            validator = {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'properties': properties
                }
            }
            if required:
                validator['$jsonSchema']['required'] = required
            
            # 应用验证规则
            database.command({
                'collMod': collection_name,
                'validator': validator
            })
    
    def _create_index(self, collection, index_def: Dict[str, Any]):
        """
        创建索引
        
        Args:
            collection: 集合实例
            index_def: 索引定义
        """
        index_keys = index_def.get('keys', {})
        index_options = index_def.get('options', {})
        
        # 转换键方向
        keys = []
        for key, direction in index_keys.items():
            if direction == 'asc':
                keys.append((key, ASCENDING))
            elif direction == 'desc':
                keys.append((key, DESCENDING))
            else:
                keys.append((key, direction))
        
        collection.create_index(keys, **index_options)
    
    def drop_collection(self, collection_name: str) -> bool:
        """
        删除集合
        
        Args:
            collection_name: 集合名称
            
        Returns:
            bool: 是否删除成功
        """
        try:
            database = db_connection.get_database(self.db_name)
            database.drop_collection(collection_name)
            return True
        except Exception as e:
            print(f"删除集合失败: {e}")
            return False
    
    def list_collections(self) -> List[str]:
        """
        列出所有集合
        
        Returns:
            集合名称列表
        """
        try:
            database = db_connection.get_database(self.db_name)
            return database.list_collection_names()
        except Exception as e:
            print(f"获取集合列表失败: {e}")
            return []
    
    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """
        获取集合信息
        
        Args:
            collection_name: 集合名称
            
        Returns:
            集合信息字典
        """
        try:
            database = db_connection.get_database(self.db_name)
            collection = database[collection_name]
            
            # 获取集合统计信息
            stats = database.command('collstats', collection_name)
            
            # 获取索引信息
            indexes = list(collection.list_indexes())
            
            return {
                'name': collection_name,
                'document_count': stats.get('count', 0),
                'size_bytes': stats.get('size', 0),
                'avg_obj_size': stats.get('avgObjSize', 0),
                'indexes': [idx['name'] for idx in indexes]
            }
        except Exception as e:
            print(f"获取集合信息失败: {e}")
            return None
    
    def add_index_to_collection(self, collection_name: str, 
                                index_def: Dict[str, Any]) -> bool:
        """
        为现有集合添加索引
        
        Args:
            collection_name: 集合名称
            index_def: 索引定义
            
        Returns:
            bool: 是否添加成功
        """
        try:
            collection = db_connection.get_collection(collection_name, self.db_name)
            self._create_index(collection, index_def)
            return True
        except Exception as e:
            print(f"添加索引失败: {e}")
            return False