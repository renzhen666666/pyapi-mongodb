"""
应用启动脚本
"""
import sys
import logging
from app import create_app
from database.connection import db_connection
from config import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    logger.info("正在启动pymongoddb API服务...")
    
    # 创建应用
    app = create_app()
    
    # 初始化数据库连接
    logger.info("正在连接MongoDB数据库...")
    if not db_connection.connect():
        logger.error("MongoDB连接失败，请检查配置")
        sys.exit(1)
    
    logger.info("MongoDB连接成功")
    
    # 启动应用
    logger.info(f"API服务启动中，监听 {config.API_HOST}:{config.API_PORT}")
    try:
        app.run(
            host=config.API_HOST,
            port=config.API_PORT,
            debug=config.API_DEBUG
        )
    except KeyboardInterrupt:
        logger.info("正在关闭服务...")
        db_connection.disconnect()
        logger.info("服务已关闭")
        sys.exit(0)
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        db_connection.disconnect()
        sys.exit(1)


if __name__ == '__main__':
    main()