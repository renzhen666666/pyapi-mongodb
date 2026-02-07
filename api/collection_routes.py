"""
集合管理API路由
"""
from flask import Blueprint, request, jsonify
from services.collection_service import CollectionService
from middleware.auth_middleware import auth_middleware

collection_bp = Blueprint('collection', __name__, url_prefix='/api/collections')
collection_service = CollectionService()


@collection_bp.route('/', methods=['POST'])
@auth_middleware.require_auth
def create_collection():
    """动态创建集合"""
    try:
        data = request.get_json()
        
        if not data or 'collection_name' not in data:
            return jsonify({
                'success': False,
                'error': 'collection_name不能为空'
            }), 400
        
        success = collection_service.create_collection(
            data['collection_name'],
            data.get('structure'),
            data.get('indexes')
        )
        
        if not success:
            return jsonify({
                'success': False,
                'error': '创建集合失败'
            }), 400
        
        return jsonify({
            'success': True,
            'message': '集合创建成功'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@collection_bp.route('/<collection_name>', methods=['DELETE'])
@auth_middleware.require_auth
def drop_collection(collection_name):
    """删除集合"""
    try:
        success = collection_service.drop_collection(collection_name)
        
        if not success:
            return jsonify({
                'success': False,
                'error': '删除集合失败'
            }), 400
        
        return jsonify({
            'success': True,
            'message': '集合删除成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@collection_bp.route('/', methods=['GET'])
@auth_middleware.require_auth
def list_collections():
    """列出所有集合"""
    try:
        collections = collection_service.list_collections()
        
        return jsonify({
            'success': True,
            'data': collections
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@collection_bp.route('/<collection_name>/info', methods=['GET'])
@auth_middleware.require_auth
def get_collection_info(collection_name):
    """获取集合信息"""
    try:
        info = collection_service.get_collection_info(collection_name)
        
        if not info:
            return jsonify({
                'success': False,
                'error': '集合不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@collection_bp.route('/<collection_name>/index', methods=['POST'])
@auth_middleware.require_auth
def add_index(collection_name):
    """为集合添加索引"""
    try:
        data = request.get_json()
        
        if not data or 'index_def' not in data:
            return jsonify({
                'success': False,
                'error': 'index_def不能为空'
            }), 400
        
        success = collection_service.add_index_to_collection(
            collection_name,
            data['index_def']
        )
        
        if not success:
            return jsonify({
                'success': False,
                'error': '添加索引失败'
            }), 400
        
        return jsonify({
            'success': True,
            'message': '索引添加成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500