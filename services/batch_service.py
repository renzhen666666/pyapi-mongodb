"""
批量操作服务模块
提供批量数据导入/删除接口，支持事务控制、失败重试机制
"""
import time
from typing import Dict, List, Optional, Any, Callable
from pymongo import InsertOne, UpdateOne, DeleteOne
from pymongo.errors import BulkWriteError
from database.connection import db_connection
from config import config


class BatchService:
    """批量操作服务类"""
    
    def __init__(self, db_name: Optional[str] = None):
        self.db_name = db_name
        self.batch_size = config.BATCH_SIZE
        self.max_retries = config.BATCH_RETRY_TIMES
        self.retry_delay = config.BATCH_RETRY_DELAY
    
    def batch_insert(self, collection_name: str, 
                     documents: List[Dict[str, Any]],
                     ordered: bool = False) -> Dict[str, Any]:
        """
        批量插入文档
        
        Args:
            collection_name: 集合名称
            documents: 文档列表
            ordered: 是否有序插入（遇到错误停止）
            
        Returns:
            操作结果字典
        """
        return self._execute_with_retry(
            lambda: self._batch_insert_internal(collection_name, documents, ordered)
        )
    
    def _batch_insert_internal(self, collection_name: str, 
                                documents: List[Dict[str, Any]],
                                ordered: bool) -> Dict[str, Any]:
        """内部批量插入实现"""
        collection = db_connection.get_collection(collection_name, self.db_name)
        
        # 分批处理
        results = {
            'inserted_count': 0,
            'failed_count': 0,
            'errors': []
        }
        
        for i in range(0, len(documents), self.batch_size):
            batch = documents[i:i + self.batch_size]
            operations = [InsertOne(doc) for doc in batch]
            
            try:
                result = collection.bulk_write(operations, ordered=ordered)
                results['inserted_count'] += result.inserted_count
            except BulkWriteError as e:
                results['failed_count'] += len(batch) - e.details.get('nInserted', 0)
                results['errors'].append({
                    'batch': i // self.batch_size,
                    'error': str(e)
                })
                if ordered:
                    break
        
        return results
    
    def batch_update(self, collection_name: str,
                     updates: List[Dict[str, Any]],
                     ordered: bool = False) -> Dict[str, Any]:
        """
        批量更新文档
        
        Args:
            collection_name: 集合名称
            updates: 更新操作列表，每个元素包含filter和update
            ordered: 是否有序更新（遇到错误停止）
            
        Returns:
            操作结果字典
        """
        return self._execute_with_retry(
            lambda: self._batch_update_internal(collection_name, updates, ordered)
        )
    
    def _batch_update_internal(self, collection_name: str,
                                updates: List[Dict[str, Any]],
                                ordered: bool) -> Dict[str, Any]:
        """内部批量更新实现"""
        collection = db_connection.get_collection(collection_name, self.db_name)
        
        results = {
            'matched_count': 0,
            'modified_count': 0,
            'failed_count': 0,
            'errors': []
        }
        
        for i in range(0, len(updates), self.batch_size):
            batch = updates[i:i + self.batch_size]
            operations = [
                UpdateOne(
                    update['filter'],
                    update['update'],
                    upsert=update.get('upsert', False)
                )
                for update in batch
            ]
            
            try:
                result = collection.bulk_write(operations, ordered=ordered)
                results['matched_count'] += result.matched_count
                results['modified_count'] += result.modified_count
            except BulkWriteError as e:
                results['failed_count'] += len(batch) - e.details.get('nModified', 0)
                results['errors'].append({
                    'batch': i // self.batch_size,
                    'error': str(e)
                })
                if ordered:
                    break
        
        return results
    
    def batch_delete(self, collection_name: str,
                     filters: List[Dict[str, Any]],
                     ordered: bool = False) -> Dict[str, Any]:
        """
        批量删除文档
        
        Args:
            collection_name: 集合名称
            filters: 删除条件列表
            ordered: 是否有序删除（遇到错误停止）
            
        Returns:
            操作结果字典
        """
        return self._execute_with_retry(
            lambda: self._batch_delete_internal(collection_name, filters, ordered)
        )
    
    def _batch_delete_internal(self, collection_name: str,
                                filters: List[Dict[str, Any]],
                                ordered: bool) -> Dict[str, Any]:
        """内部批量删除实现"""
        collection = db_connection.get_collection(collection_name, self.db_name)
        
        results = {
            'deleted_count': 0,
            'failed_count': 0,
            'errors': []
        }
        
        for i in range(0, len(filters), self.batch_size):
            batch = filters[i:i + self.batch_size]
            operations = [DeleteOne(filter_) for filter_ in batch]
            
            try:
                result = collection.bulk_write(operations, ordered=ordered)
                results['deleted_count'] += result.deleted_count
            except BulkWriteError as e:
                results['failed_count'] += len(batch) - e.details.get('nRemoved', 0)
                results['errors'].append({
                    'batch': i // self.batch_size,
                    'error': str(e)
                })
                if ordered:
                    break
        
        return results
    
    def batch_mixed_operations(self, collection_name: str,
                               operations: List[Dict[str, Any]],
                               ordered: bool = False) -> Dict[str, Any]:
        """
        批量混合操作（插入、更新、删除混合）
        
        Args:
            collection_name: 集合名称
            operations: 操作列表，每个元素包含type和data
            ordered: 是否有序执行（遇到错误停止）
            
        Returns:
            操作结果字典
        """
        return self._execute_with_retry(
            lambda: self._batch_mixed_internal(collection_name, operations, ordered)
        )
    
    def _batch_mixed_internal(self, collection_name: str,
                               operations: List[Dict[str, Any]],
                               ordered: bool) -> Dict[str, Any]:
        """内部批量混合操作实现"""
        collection = db_connection.get_collection(collection_name, self.db_name)
        
        results = {
            'inserted_count': 0,
            'matched_count': 0,
            'modified_count': 0,
            'deleted_count': 0,
            'failed_count': 0,
            'errors': []
        }
        
        for i in range(0, len(operations), self.batch_size):
            batch = operations[i:i + self.batch_size]
            mongo_operations = []
            
            for op in batch:
                op_type = op['type']
                op_data = op['data']
                
                if op_type == 'insert':
                    mongo_operations.append(InsertOne(op_data))
                elif op_type == 'update':
                    mongo_operations.append(
                        UpdateOne(
                            op_data['filter'],
                            op_data['update'],
                            upsert=op_data.get('upsert', False)
                        )
                    )
                elif op_type == 'delete':
                    mongo_operations.append(DeleteOne(op_data))
            
            try:
                result = collection.bulk_write(mongo_operations, ordered=ordered)
                results['inserted_count'] += result.inserted_count
                results['matched_count'] += result.matched_count
                results['modified_count'] += result.modified_count
                results['deleted_count'] += result.deleted_count
            except BulkWriteError as e:
                results['failed_count'] += len(batch) - e.details.get('nInserted', 0)
                results['errors'].append({
                    'batch': i // self.batch_size,
                    'error': str(e)
                })
                if ordered:
                    break
        
        return results
    
    def _execute_with_retry(self, operation: Callable) -> Dict[str, Any]:
        """
        带重试机制的操作执行
        
        Args:
            operation: 要执行的操作函数
            
        Returns:
            操作结果
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return operation()
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay / 1000)
        
        return {
            'success': False,
            'error': str(last_error)
        }
    
    def import_from_json(self, collection_name: str, 
                         json_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        从JSON数据导入
        
        Args:
            collection_name: 集合名称
            json_data: JSON数据列表
            
        Returns:
            操作结果
        """
        return self.batch_insert(collection_name, json_data)
    
    def export_to_json(self, collection_name: str, 
                       query: Optional[Dict[str, Any]] = None,
                       limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        导出为JSON数据
        
        Args:
            collection_name: 集合名称
            query: 查询条件
            limit: 限制返回数量
            
        Returns:
            文档列表
        """
        collection = db_connection.get_collection(collection_name, self.db_name)
        
        cursor = collection.find(query or {})
        if limit:
            cursor = cursor.limit(limit)
        
        return list(cursor)