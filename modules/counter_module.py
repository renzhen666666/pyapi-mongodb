"""
数值型数据模块
针对点赞数、关注数、浏览量等int类型数据，封装原子性增减接口
"""
from typing import Dict, Optional
from pymongo import ASCENDING
from bson import ObjectId
from database.base import BaseDataModule


class CounterModule(BaseDataModule):
    """数值型数据模块"""
    
    def __init__(self, collection_name: str = 'counters', db_name: Optional[str] = None):
        super().__init__(collection_name, db_name)
        self._init_indexes()
    
    def _init_indexes(self):
        """初始化索引"""
        try:
            self.collection.create_index([('counter_key', ASCENDING)], unique=True)
        except Exception as e:
            print(f"索引创建警告: {e}")
    
    def create(self, data: Dict[str, int]) -> str:
        """
        创建计数器
        
        Args:
            data: 计数器数据，包含counter_key, value等
            
        Returns:
            str: 计数器ID
        """
        self._ensure_connection()
        
        counter_data = {
            'counter_key': data['counter_key'],
            'value': data.get('value', 0),
            'created_at': self._get_current_timestamp(),
            'updated_at': self._get_current_timestamp()
        }
        
        result = self.collection.insert_one(counter_data)
        return str(result.inserted_id)
    
    def read(self, query: Dict[str, str], projection: Optional[Dict[str, str]] = None) -> Optional[Dict[str, str]]:
        """读取计数器"""
        self._ensure_connection()
        return self.collection.find_one(query, projection)
    
    def update(self, query: Dict[str, str], update_data: Dict[str, str]) -> bool:
        """更新计数器"""
        self._ensure_connection()
        update_data['updated_at'] = self._get_current_timestamp()
        result = self.collection.update_one(query, {'$set': update_data})
        return result.modified_count > 0
    
    def delete(self, query: Dict[str, str]) -> bool:
        """删除计数器"""
        self._ensure_connection()
        result = self.collection.delete_one(query)
        return result.deleted_count > 0
    
    def increment(self, counter_key: str, delta: int = 1) -> int:
        """
        原子性增加计数器值
        
        Args:
            counter_key: 计数器标识
            delta: 增加的值，默认为1
            
        Returns:
            int: 增加后的值
        """
        self._ensure_connection()
        
        result = self.collection.find_one_and_update(
            {'counter_key': counter_key},
            {
                '$inc': {'value': delta},
                '$set': {'updated_at': self._get_current_timestamp()}
            },
            return_document=True
        )
        
        if result:
            return result['value']
        
        # 如果计数器不存在，创建新的
        self.create({'counter_key': counter_key, 'value': delta})
        return delta
    
    def decrement(self, counter_key: str, delta: int = 1, min_value: int = 0) -> int:
        """
        原子性减少计数器值
        
        Args:
            counter_key: 计数器标识
            delta: 减少的值，默认为1
            min_value: 最小值，默认为0
            
        Returns:
            int: 减少后的值
        """
        self._ensure_connection()
        
        # 先获取当前值
        current = self.read({'counter_key': counter_key})
        if current is None:
            # 如果计数器不存在，创建新的（值为0）
            self.create({'counter_key': counter_key, 'value': 0})
            return 0
        
        new_value = max(current['value'] - delta, min_value)
        
        result = self.collection.find_one_and_update(
            {'counter_key': counter_key},
            {
                '$set': {
                    'value': new_value,
                    'updated_at': self._get_current_timestamp()
                }
            },
            return_document=True
        )
        
        return result['value'] if result else 0
    
    def get_value(self, counter_key: str) -> int:
        """
        获取计数器当前值
        
        Args:
            counter_key: 计数器标识
            
        Returns:
            int: 当前值
        """
        counter = self.read({'counter_key': counter_key})
        return counter['value'] if counter else 0
    
    def set_value(self, counter_key: str, value: int) -> int:
        """
        设置计数器值
        
        Args:
            counter_key: 计数器标识
            value: 要设置的值
            
        Returns:
            int: 设置后的值
        """
        self._ensure_connection()
        
        result = self.collection.find_one_and_update(
            {'counter_key': counter_key},
            {
                '$set': {
                    'value': value,
                    'updated_at': self._get_current_timestamp()
                }
            },
            upsert=True,
            return_document=True
        )
        
        return result['value']
    
    def reset(self, counter_key: str) -> int:
        """
        重置计数器为0
        
        Args:
            counter_key: 计数器标识
            
        Returns:
            int: 重置后的值(0)
        """
        return self.set_value(counter_key, 0)
    
    def batch_increment(self, counters: Dict[str, int]) -> Dict[str, int]:
        """
        批量增加多个计数器
        
        Args:
            counters: 计数器字典 {counter_key: delta}
            
        Returns:
            Dict[str, int]: 更新后的值字典
        """
        results = {}
        for counter_key, delta in counters.items():
            results[counter_key] = self.increment(counter_key, delta)
        return results
    
    def batch_get_values(self, counter_keys: list) -> Dict[str, int]:
        """
        批量获取多个计数器的值
        
        Args:
            counter_keys: 计数器标识列表
            
        Returns:
            Dict[str, int]: 计数器值字典
        """
        self._ensure_connection()
        
        counters = self.collection.find({
            'counter_key': {'$in': counter_keys}
        })
        
        return {
            counter['counter_key']: counter['value']
            for counter in counters
        }