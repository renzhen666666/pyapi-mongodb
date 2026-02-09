"""
批量操作API路由
"""
from flask import Blueprint, request, jsonify 
from services.batch_service import BatchService
from middleware.auth_middleware import auth_middleware

batch_bp = Blueprint('batch', __name__, url_prefix='/api/batch')
batch_service = BatchService()


@batch_bp.route('/insert', methods=['POST'])
@auth_middleware.require_auth
def batch_insert():
    """批量插入文档"""
    try:
        data = request.get_json()
        
        if not data or 'collection_name' not in data or 'documents' not in data:
            return jsonify({
                'success': False,
                'error': 'collection_name和documents不能为空'
            }), 400
        
        ordered = data.get('ordered', False)
        result = batch_service.batch_insert(data['collection_name'], data['documents'], ordered)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@batch_bp.route('/update', methods=['POST'])
@auth_middleware.require_auth
def batch_update():
    """批量更新文档"""
    try:
        data = request.get_json()
        
        if not data or 'collection_name' not in data or 'updates' not in data:
            return jsonify({
                'success': False,
                'error': 'collection_name和updates不能为空'
            }), 400
        
        ordered = data.get('ordered', False)
        result = batch_service.batch_update(data['collection_name'], data['updates'], ordered)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@batch_bp.route('/delete', methods=['POST'])
@auth_middleware.require_auth
def batch_delete():
    """批量删除文档"""
    try:
        data = request.get_json()
        
        if not data or 'collection_name' not in data or 'filters' not in data:
            return jsonify({
                'success': False,
                'error': 'collection_name和filters不能为空'
            }), 400
        
        ordered = data.get('ordered', False)
        result = batch_service.batch_delete(data['collection_name'], data['filters'], ordered)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@batch_bp.route('/mixed', methods=['POST'])
@auth_middleware.require_auth
def batch_mixed():
    """批量混合操作"""
    try:
        data = request.get_json()
        
        if not data or 'collection_name' not in data or 'operations' not in data:
            return jsonify({
                'success': False,
                'error': 'collection_name和operations不能为空'
            }), 400
        
        ordered = data.get('ordered', False)
        result = batch_service.batch_mixed_operations(data['collection_name'], data['operations'], ordered)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@batch_bp.route('/import', methods=['POST'])
@auth_middleware.require_auth
def import_json():
    """从JSON数据导入"""
    try:
        data = request.get_json()
        
        if not data or 'collection_name' not in data or 'json_data' not in data:
            return jsonify({
                'success': False,
                'error': 'collection_name和json_data不能为空'
            }), 400
        
        result = batch_service.import_from_json(data['collection_name'], data['json_data'])
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@batch_bp.route('/export', methods=['POST'])
@auth_middleware.require_auth
def export_json():
    """导出为JSON数据"""
    try:
        data = request.get_json()
        
        if not data or 'collection_name' not in data:
            return jsonify({
                'success': False,
                'error': 'collection_name不能为空'
            }), 400
        
        result = batch_service.export_to_json(
            data['collection_name'],
            data.get('query'),
            data.get('limit')
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500