"""
数值型数据API路由
"""
from flask import Blueprint, request, jsonify
from modules.counter_module import CounterModule
from middleware.auth_middleware import auth_middleware

counter_bp = Blueprint('counter', __name__, url_prefix='/api/counters')
counter_module = CounterModule()


@counter_bp.route('/', methods=['POST'])
@auth_middleware.require_auth
def create_counter():
    """创建计数器"""
    try:
        data = request.get_json()
        
        if not data or 'counter_key' not in data:
            return jsonify({
                'success': False,
                'error': 'counter_key不能为空'
            }), 400
        
        counter_id = counter_module.create(data)
        
        return jsonify({
            'success': True,
            'data': {'counter_id': counter_id}
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@counter_bp.route('/<counter_key>/increment', methods=['POST'])
@auth_middleware.require_auth
def increment_counter(counter_key):
    """增加计数器值"""
    try:
        delta = int(request.args.get('delta', 1))
        value = counter_module.increment(counter_key, delta)
        
        return jsonify({
            'success': True,
            'data': {'value': value}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@counter_bp.route('/<counter_key>/decrement', methods=['POST'])
@auth_middleware.require_auth
def decrement_counter(counter_key):
    """减少计数器值"""
    try:
        delta = int(request.args.get('delta', 1))
        min_value = int(request.args.get('min_value', 0))
        value = counter_module.decrement(counter_key, delta, min_value)
        
        return jsonify({
            'success': True,
            'data': {'value': value}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@counter_bp.route('/<counter_key>', methods=['GET'])
@auth_middleware.require_auth
def get_counter_value(counter_key):
    """获取计数器当前值"""
    try:
        value = counter_module.get_value(counter_key)
        
        return jsonify({
            'success': True,
            'data': {'value': value}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@counter_bp.route('/<counter_key>', methods=['PUT'])
@auth_middleware.require_auth
def set_counter_value(counter_key):
    """设置计数器值"""
    try:
        data = request.get_json()
        
        if not data or 'value' not in data:
            return jsonify({
                'success': False,
                'error': 'value不能为空'
            }), 400
        
        value = counter_module.set_value(counter_key, data['value'])
        
        return jsonify({
            'success': True,
            'data': {'value': value}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@counter_bp.route('/<counter_key>/reset', methods=['POST'])
@auth_middleware.require_auth
def reset_counter(counter_key):
    """重置计数器为0"""
    try:
        value = counter_module.reset(counter_key)
        
        return jsonify({
            'success': True,
            'data': {'value': value}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@counter_bp.route('/batch/increment', methods=['POST'])
@auth_middleware.require_auth
def batch_increment():
    """批量增加多个计数器"""
    try:
        data = request.get_json()
        
        if not data or 'counters' not in data:
            return jsonify({
                'success': False,
                'error': 'counters不能为空'
            }), 400
        
        results = counter_module.batch_increment(data['counters'])
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@counter_bp.route('/batch/get', methods=['POST'])
@auth_middleware.require_auth
def batch_get_values():
    """批量获取多个计数器的值"""
    try:
        data = request.get_json()
        
        if not data or 'counter_keys' not in data:
            return jsonify({
                'success': False,
                'error': 'counter_keys不能为空'
            }), 400
        
        results = counter_module.batch_get_values(data['counter_keys'])
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500