"""
字典型数据API路由
"""
from flask import Blueprint, request, jsonify
from modules.dict_module import DictModule
from middleware.auth_middleware import auth_middleware

dict_bp = Blueprint('dict', __name__, url_prefix='/api/dicts')
dict_module = DictModule()


@dict_bp.route('/field', methods=['PUT'])
@auth_middleware.require_auth
def set_field():
    """设置字典字段值"""
    try:
        data = request.get_json()
        
        if not data or 'dict_key' not in data or 'field_path' not in data:
            return jsonify({
                'success': False,
                'error': 'dict_key和field_path不能为空'
            }), 400
        
        success = dict_module.set_field(
            data['dict_key'],
            data['field_path'],
            data.get('value')
        )
        
        if not success:
            return jsonify({
                'success': False,
                'error': '设置失败'
            }), 400
        
        return jsonify({
            'success': True,
            'message': '设置成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dict_bp.route('/field', methods=['GET'])
@auth_middleware.require_auth
def get_field():
    """获取字典字段值"""
    try:
        dict_key = request.args.get('dict_key')
        field_path = request.args.get('field_path')
        
        if not dict_key or not field_path:
            return jsonify({
                'success': False,
                'error': 'dict_key和field_path不能为空'
            }), 400
        
        value = dict_module.get_field(dict_key, field_path)
        
        return jsonify({
            'success': True,
            'data': {'value': value}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dict_bp.route('/field', methods=['DELETE'])
@auth_middleware.require_auth
def delete_field():
    """删除字典字段"""
    try:
        dict_key = request.args.get('dict_key')
        field_path = request.args.get('field_path')
        
        if not dict_key or not field_path:
            return jsonify({
                'success': False,
                'error': 'dict_key和field_path不能为空'
            }), 400
        
        success = dict_module.delete_field(dict_key, field_path)
        
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


@dict_bp.route('/fields', methods=['PUT'])
@auth_middleware.require_auth
def set_multiple_fields():
    """批量设置字典字段"""
    try:
        data = request.get_json()
        
        if not data or 'dict_key' not in data or 'fields' not in data:
            return jsonify({
                'success': False,
                'error': 'dict_key和fields不能为空'
            }), 400
        
        success = dict_module.set_multiple_fields(data['dict_key'], data['fields'])
        
        if not success:
            return jsonify({
                'success': False,
                'error': '设置失败'
            }), 400
        
        return jsonify({
            'success': True,
            'message': '设置成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dict_bp.route('/<dict_key>', methods=['GET'])
@auth_middleware.require_auth
def get_all_fields(dict_key):
    """获取字典所有字段"""
    try:
        fields = dict_module.get_all_fields(dict_key)
        
        return jsonify({
            'success': True,
            'data': fields
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dict_bp.route('/merge', methods=['POST'])
@auth_middleware.require_auth
def merge_dict():
    """合并字典数据"""
    try:
        data = request.get_json()
        
        if not data or 'dict_key' not in data or 'data' not in data:
            return jsonify({
                'success': False,
                'error': 'dict_key和data不能为空'
            }), 400
        
        overwrite = data.get('overwrite', True)
        success = dict_module.merge_dict(data['dict_key'], data['data'], overwrite)
        
        if not success:
            return jsonify({
                'success': False,
                'error': '合并失败'
            }), 400
        
        return jsonify({
            'success': True,
            'message': '合并成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dict_bp.route('/<dict_key>/clear', methods=['DELETE'])
@auth_middleware.require_auth
def clear_dict(dict_key):
    """清空字典数据"""
    try:
        success = dict_module.clear_dict(dict_key)
        
        if not success:
            return jsonify({
                'success': False,
                'error': '清空失败'
            }), 400
        
        return jsonify({
            'success': True,
            'message': '清空成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500