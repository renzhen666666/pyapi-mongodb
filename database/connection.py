"""
MongoDB连接管理模块
提供连接池管理和异常处理
"""
import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError
from config import config

logger = logging.getLogger(__name__)


class MongoDBConnection:
    """MongoDB连接管理类"""
    
    _instance: Optional['MongoDBConnection'] = None
    _client: Optional[MongoClient] = None
    
    def __new__(cls):
        """单例模式确保全局只有一个连接实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self) -> bool:
        """
        建立MongoDB连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            if self._client is None:
                self._client = MongoClient(
                    config.MONGODB_URI,
                    maxPoolSize=config.MONGODB_MAX_POOL_SIZE,
                    minPoolSize=config.MONGODB_MIN_POOL_SIZE,
                    connectTimeoutMS=config.MONGODB_CONNECT_TIMEOUT,
                    serverSelectionTimeoutMS=config.MONGODB_SERVER_SELECTION_TIMEOUT,
                    retryWrites=True,
                    w='majority'
                )
            
            # 测试连接
            self._client.admin.command('ping')
            logger.info(f"成功连接到MongoDB: {config.MONGODB_URI}")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"MongoDB连接失败: {e}")
            return False
        except ServerSelectionTimeoutError as e:
            logger.error(f"MongoDB服务器选择超时: {e}")
            return False
        except Exception as e:
            logger.error(f"MongoDB连接异常: {e}")
            return False
    
    def disconnect(self):
        """关闭MongoDB连接"""
        if self._client:
            self._client.close()
            self._client = None
            logger.info("MongoDB连接已关闭")
    
    def get_client(self) -> Optional[MongoClient]:
        """
        获取MongoDB客户端实例
        
        Returns:
            MongoClient: MongoDB客户端实例
        """
        if self._client is None:
            self.connect()
        return self._client
    
    def get_database(self, db_name: Optional[str] = None):
        """
        获取数据库实例
        
        Args:
            db_name: 数据库名称，默认使用配置中的数据库名
            
        Returns:
            Database: MongoDB数据库实例
        """
        client = self.get_client()
        if client is None:
            raise ConnectionError("无法获取MongoDB客户端连接")
        
        database_name = db_name or config.MONGODB_DATABASE
        return client[database_name]
    
    def get_collection(self, collection_name: str, db_name: Optional[str] = None):
        """
        获取集合实例
        
        Args:
            collection_name: 集合名称
            db_name: 数据库名称，默认使用配置中的数据库名
            
        Returns:
            Collection: MongoDB集合实例
        """
        database = self.get_database(db_name)
        return database[collection_name]
    
    def is_connected(self) -> bool:
        """
        检查连接状态
        
        Returns:
            bool: 是否已连接
        """
        if self._client is None:
            return False
        
        try:
            self._client.admin.command('ping')
            return True
        except Exception:
            return False
    
    def execute_with_retry(self, operation, max_retries: int = 3, retry_delay: int = 1000):
        """
        带重试机制的操作执行
        
        Args:
            operation: 要执行的操作函数
            max_retries: 最大重试次数
            retry_delay: 重试延迟(毫秒)
            
        Returns:
            操作执行结果
            
        Raises:
            Exception: 重试次数用尽后仍失败
        """
        import time
        
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return operation()
            except (ConnectionFailure, OperationFailure, ServerSelectionTimeoutError) as e:
                last_exception = e
                logger.warning(f"操作失败，第{attempt + 1}次重试: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay / 1000)
            except Exception as e:
                logger.error(f"操作执行异常(非网络错误): {e}")
                raise
        
        raise last_exception if last_exception else Exception("操作执行失败")


# 全局连接实例
db_connection = MongoDBConnection()