"""
Flask应用主入口
"""
from flask import Flask, jsonify
from database.connection import db_connection
from config import config
from api import user_bp, list_bp, counter_bp, dict_bp, collection_bp, batch_bp


def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = config.SESSION_SECRET_KEY
    app.config['JSON_AS_ASCII'] = False
    
    # 注册蓝图
    app.register_blueprint(user_bp)
    app.register_blueprint(list_bp)
    app.register_blueprint(counter_bp)
    app.register_blueprint(dict_bp)
    app.register_blueprint(collection_bp)
    app.register_blueprint(batch_bp)
    
    # 健康检查端点
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查"""
        db_status = db_connection.is_connected()
        
        return jsonify({
            'status': 'healthy' if db_status else 'unhealthy',
            'database': 'connected' if db_status else 'disconnected'
        })
    
    # 根路径
    @app.route('/', methods=['GET'])
    def index():
        """根路径"""
        return jsonify({
            'name': 'pymongoddb API',
            'version': '1.0.0',
            'description': 'MongoDB后端API服务'
        })
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': '接口不存在'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': '服务器内部错误'
        }), 500
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': '请求方法不允许'
        }), 405
    
    # 启动前初始化数据库连接
    @app.before_request
    def before_request():
        """请求前处理"""
        if not db_connection.is_connected():
            db_connection.connect()
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # 初始化数据库连接
    db_connection.connect()
    
    # 启动应用
    app.run(
        host=config.API_HOST,
        port=config.API_PORT,
        debug=config.API_DEBUG
    )