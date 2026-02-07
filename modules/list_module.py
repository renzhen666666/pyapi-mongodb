"""
列表面数据模块
支持粉丝列表、点赞记录等有序/无序列表类数据的存储
"""
from typing import Dict, List, Optional, Any
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId
from database.base import BaseDataModule


class ListModule(BaseDataModule):
    """列表面数据模块"""
    
    def __init__(self, collection_name: str = 'list_data', db_name: Optional[str] = None):
        super().__init__(collection_name, db_name)
        self._init_indexes()
    
    def _init_indexes(self):
        """初始化索引"""
        try:
            self.collection.create_index([('list_key', ASCENDING), ('item_key', ASCENDING)], unique=True)
            self.collection.create_index([('list_key', ASCENDING), ('order', ASCENDING)])
            self.collection.create_index([('list_key', ASCENDING), ('created_at', DESCENDING)])
        except Exception as e:
            print(f"索引创建警告: {e}")
    
    def create(self, data: Dict[str, Any]) -> str:
        """
        创建新列表项
        
        Args:
            data: 列表项数据，包含list_key, item_key, value等
            
        Returns:
            str: 列表项ID
        """
        self._ensure_connection()
        
        list_data = {
            'list_key': data['list_key'],
            'item_key': data.get('item_key'),
            'value': data.get('value'),
            'order': data.get('order', 0),
            'created_at': self._get_current_timestamp(),
            'updated_at': self._get_current_timestamp()
        }
        
        result = self.collection.insert_one(list_data)
        return str(result.inserted_id)
    
    def read(self, query: Dict[str, Any], projection: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """读取单个列表项"""
        self._ensure_connection()
        return self.collection.find_one(query, projection)
    
    def update(self, query: Dict[str, Any], update_data: Dict[str, Any]) -> bool:
        """更新列表项"""
        self._ensure_connection()
        update_data['updated_at'] = self._get_current_timestamp()
        result = self.collection.update_one(query, {'$set': update_data})
        return result.modified_count > 0
    
    def delete(self, query: Dict[str, Any]) -> bool:
        """删除列表项"""
        self._ensure_connection()
        result = self.collection.delete_one(query)
        return result.deleted_count > 0
    
    def add_item(self, list_key: str, item_key: str, value: Any = None, order: int = 0) -> str:
        """
        添加列表元素
        
        Args:
            list_key: 列表标识
            item_key: 元素唯一标识
            value: 元素值
            order: 排序值
            
        Returns:
            str: 元素ID
        """
        return self.create({
            'list_key': list_key,
            'item_key': item_key,
            'value': value,
            'order': order
        })
    
    def remove_item(self, list_key: str, item_key: str) -> bool:
        """
        删除列表元素
        
        Args:
            list_key: 列表标识
            item_key: 元素唯一标识
            
        Returns:
            bool: 是否删除成功
        """
        return self.delete({
            'list_key': list_key,
            'item_key': item_key
        })
    
    def get_list(self, list_key: str, skip: int = 0, limit: int = 20, 
                 sort_by: str = 'order', sort_order: int = 1) -> List[Dict[str, Any]]:
        """
        获取列表（分页、排序）
        
        Args:
            list_key: 列表标识
            skip: 跳过数量
            limit: 返回数量限制
            sort_by: 排序字段
            sort_order: 排序方向(1升序, -1降序)
            
        Returns:
            列表元素数组
        """
        self._ensure_connection()
        items = self.collection.find(
            {'list_key': list_key}
        ).sort(sort_by, sort_order).skip(skip).limit(limit)
        
        return [
            {**item, '_id': str(item['_id'])}
            for item in items
        ]
    
    def get_list_count(self, list_key: str) -> int:
        """
        获取列表元素总数
        
        Args:
            list_key: 列表标识
            
        Returns:
            int: 元素总数
        """
        return self.count({'list_key': list_key})
    
    def deduplicate(self, list_key: str, field: str = 'item_key') -> int:
        """
        去重操作
        
        Args:
            list_key: 列表标识
            field: 去重字段
            
        Returns:
            int: 删除的重复项数量
        """
        self._ensure_connection()
        
        # 查找所有重复项
        pipeline = [
            {'$match': {'list_key': list_key}},
            {'$group': {'_id': f'${field}', 'ids': {'$push': '$_id'}, 'count': {'$sum': 1}}},
            {'$match': {'count': {'$gt': 1}}}
        ]
        
        duplicates = list(self.collection.aggregate(pipeline))
        deleted_count = 0
        
        for dup in duplicates:
            # 保留第一个，删除其余的
            ids_to_delete = dup['ids'][1:]
            result = self.collection.delete_many({'_id': {'$in': ids_to_delete}})
            deleted_count += result.deleted_count
        
        return deleted_count
    
    def batch_add(self, list_key: str, items: List[Dict[str, Any]]) -> List[str]:
        """
        批量添加列表元素
        
        Args:
            list_key: 列表标识
            items: 元素列表，每个元素包含item_key, value, order等
            
        Returns:
            List[str]: 新增元素的ID列表
        """
        self._ensure_connection()
        
        documents = []
        for item in items:
            documents.append({
                'list_key': list_key,
                'item_key': item.get('item_key'),
                'value': item.get('value'),
                'order': item.get('order', 0),
                'created_at': self._get_current_timestamp(),
                'updated_at': self._get_current_timestamp()
            })
        
        result = self.collection.insert_many(documents)
        return [str(id_) for id_ in result.inserted_ids]
    
    def batch_remove(self, list_key: str, item_keys: List[str]) -> int:
        """
        批量删除列表元素
        
        Args:
            list_key: 列表标识
            item_keys: 元素标识列表
            
        Returns:
            int: 删除的数量
        """
        self._ensure_connection()
        result = self.collection.delete_many({
            'list_key': list_key,
            'item_key': {'$in': item_keys}
        })
        return result.deleted_count
    
    def clear_list(self, list_key: str) -> int:
        """
        清空列表
        
        Args:
            list_key: 列表标识
            
        Returns:
            int: 删除的数量
        """
        self._ensure_connection()
        result = self.collection.delete_many({'list_key': list_key})
        return result.deleted_count