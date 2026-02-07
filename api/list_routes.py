"""
列表面数据API路由
"""
from flask import Blueprint, request, jsonify
from modules.list_module import ListModule
from middleware.auth_middleware import auth_middleware

list_bp = Blueprint('list', __name__, url_prefix='/api/lists')
list_module = ListModule()


@list_bp.route('/item', methods=['POST'])
@auth_middleware.require_auth
def add_item():
    """添加列表元素"""
    try:
        data = request.get_json()
        
        if not data or 'list_key' not in data or 'item_key' not in data:
            return jsonify({
                'success': False,
                'error': 'list_key和item_key不能为空'
            }), 400
        
        item_id = list_module.add_item(
            data['list_key'],
            data['item_key'],
            data.get('value'),
            data.get('order', 0)
        )
        
        return jsonify({
            'success': True,
            'data': {'item_id': item_id}
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@list_bp.route('/item', methods=['DELETE'])
@auth_middleware.require_auth
def remove_item():
    """删除列表元素"""
    try:
        list_key = request.args.get('list_key')
        item_key = request.args.get('item_key')
        
        if not list_key or not item_key:
            return jsonify({
                'success': False,
                'error': 'list_key和item_key不能为空'
            }), 400
        
        success = list_module.remove_item(list_key, item_key)
        
        if not success:
            return jsonify({
                'success': False,
                'error': '删除失败'
            }), 400
        
        return jsonify({
            'success': True,
            'message': '删除成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@list_bp.route('/<list_key>', methods=['GET'])
@auth_middleware.require_auth
def get_list(list_key):
    """获取列表（分页、排序）"""
    try:
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 20))
        sort_by = request.args.get('sort_by', 'order')
        sort_order = int(request.args.get('sort_order', 1))
        
        items = list_module.get_list(list_key, skip, limit, sort_by, sort_order)
        
        return jsonify({
            'success': True,
            'data': items
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@list_bp.route('/<list_key>/count', methods=['GET'])
@auth_middleware.require_auth
def get_list_count(list_key):
    """获取列表元素总数"""
    try:
        count = list_module.get_list_count(list_key)
        
        return jsonify({
            'success': True,
            'data': {'count': count}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@list_bp.route('/<list_key>/deduplicate', methods=['POST'])
@auth_middleware.require_auth
def deduplicate_list(list_key):
    """去重操作"""
    try:
        field = request.args.get('field', 'item_key')
        deleted_count = list_module.deduplicate(list_key, field)
        
        return jsonify({
            'success': True,
            'data': {'deleted_count': deleted_count}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@list_bp.route('/batch', methods=['POST'])
@auth_middleware.require_auth
def batch_add():
    """批量添加列表元素"""
    try:
        data = request.get_json()
        
        if not data or 'list_key' not in data or 'items' not in data:
            return jsonify({
                'success': False,
                'error': 'list_key和items不能为空'
            }), 400
        
        item_ids = list_module.batch_add(data['list_key'], data['items'])
        
        return jsonify({
            'success': True,
            'data': {'item_ids': item_ids}
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@list_bp.route('/batch', methods=['DELETE'])
@auth_middleware.require_auth
def batch_remove():
    """批量删除列表元素"""
    try:
        data = request.get_json()
        
        if not data or 'list_key' not in data or 'item_keys' not in data:
            return jsonify({
                'success': False,
                'error': 'list_key和item_keys不能为空'
            }), 400
        
        deleted_count = list_module.batch_remove(data['list_key'], data['item_keys'])
        
        return jsonify({
            'success': True,
            'data': {'deleted_count': deleted_count}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@list_bp.route('/<list_key>/clear', methods=['DELETE'])
@auth_middleware.require_auth
def clear_list(list_key):
    """清空列表"""
    try:
        deleted_count = list_module.clear_list(list_key)
        
        return jsonify({
            'success': True,
            'data': {'deleted_count': deleted_count}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500