# pymongoddb

基于 Flask 和 MongoDB 的后端 API 服务。

## 功能特性

- 用户管理 (user_routes)
- 列表数据管理 (list_routes)
- 计数器管理 (counter_routes)
- 字典数据管理 (dict_routes)
- 集合操作 (collection_routes)
- 批量操作 (batch_routes)
- MongoDB 连接池管理
- 请求重试机制
- 健康检查端点

## 技术栈

- Python 3.11+
- Flask 3.0.0
- PyMongo 4.6.1
- Pydantic 2.5.3
- python-dotenv 1.0.0

## 安装

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 配置

复制 `.env.example` 为 `.env` 并配置相应参数：

```bash
cp .env.example .env
```

主要配置项：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| MONGODB_URI | MongoDB 连接地址 | mongodb://localhost:27017/ |
| MONGODB_DATABASE | 数据库名称 | longgaowall_db |
| API_HOST | API 监听地址 | 0.0.0.0 |
| API_PORT | API 监听端口 | 5000 |
| API_DEBUG | 调试模式 | True |
| SESSION_SECRET_KEY | 会话密钥 | default-secret-key |
| BATCH_SIZE | 批量操作大小 | 1000 |

## 运行

```bash
python run.py
```

或：

```bash
python app.py
```

服务启动后访问：

- API 根路径: http://localhost:5000/
- 健康检查: http://localhost:5000/health

## API 端点

### 基础端点

- `GET /` - API 信息
- `GET /health` - 健康检查

### 用户模块

见 `api/user_routes.py`

### 列表模块

见 `api/list_routes.py`

### 计数器模块

见 `api/counter_routes.py`

### 字典模块

见 `api/dict_routes.py`

### 集合模块

见 `api/collection_routes.py`

### 批量操作模块

批量操作模块提供了高效的 MongoDB 批量数据操作接口。

#### 批量插入文档
```
POST /api/batch/insert
```

**功能：** 向指定集合批量插入多个文档

**请求参数（JSON Body）：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| collection_name | string | 是 | 目标集合名称 |
| documents | array | 是 | 要插入的文档数组 |
| ordered | boolean | 否 | 是否有序执行，默认 false（失败不影响其他） |

**请求示例：**
```json
{
  "collection_name": "users",
  "documents": [
    {"name": "张三", "age": 25},
    {"name": "李四", "age": 30}
  ],
  "ordered": false
}
```

**返回内容：**
```json
{
  "success": true,
  "data": {
    "inserted_count": 2,
    "inserted_ids": ["id1", "id2"]
  }
}
```

---

#### 批量更新文档
```
POST /api/batch/update
```

**功能：** 批量更新符合条件的文档

**请求参数（JSON Body）：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| collection_name | string | 是 | 目标集合名称 |
| updates | array | 是 | 更新操作数组，每项包含 filter 和 update |
| ordered | boolean | 否 | 是否有序执行，默认 false |

**请求示例：**
```json
{
  "collection_name": "users",
  "updates": [
    {"filter": {"name": "张三"}, "update": {"$set": {"age": 26}}},
    {"filter": {"name": "李四"}, "update": {"$set": {"age": 31}}}
  ],
  "ordered": false
}
```

**返回内容：**
```json
{
  "success": true,
  "data": {
    "matched_count": 2,
    "modified_count": 2
  }
}
```

---

#### 批量删除文档
```
POST /api/batch/delete
```

**功能：** 批量删除符合条件的文档

**请求参数（JSON Body）：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| collection_name | string | 是 | 目标集合名称 |
| filters | array | 是 | 删除条件数组 |
| ordered | boolean | 否 | 是否有序执行，默认 false |

**请求示例：**
```json
{
  "collection_name": "users",
  "filters": [
    {"name": "张三"},
    {"age": {"$lt": 20}}
  ],
  "ordered": false
}
```

**返回内容：**
```json
{
  "success": true,
  "data": {
    "deleted_count": 2
  }
}
```

---

#### 批量混合操作
```
POST /api/batch/mixed
```

**功能：** 在单次事务中执行多种操作（插入、更新、删除）

**请求参数（JSON Body）：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| collection_name | string | 是 | 目标集合名称 |
| operations | array | 是 | 操作数组，支持 insert/update/delete |
| ordered | boolean | 否 | 是否有序执行，默认 false |

**请求示例：**
```json
{
  "collection_name": "users",
  "operations": [
    {"operation": "insert", "document": {"name": "王五", "age": 28}},
    {"operation": "update", "filter": {"name": "张三"}, "update": {"$set": {"age": 27}}},
    {"operation": "delete", "filter": {"name": "赵六"}}
  ],
  "ordered": false
}
```

**返回内容：**
```json
{
  "success": true,
  "data": {
    "inserted_count": 1,
    "matched_count": 1,
    "modified_count": 1,
    "deleted_count": 1
  }
}
```

---

#### JSON 数据导入
```
POST /api/batch/import
```

**功能：** 从 JSON 数据导入到指定集合

**请求参数（JSON Body）：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| collection_name | string | 是 | 目标集合名称 |
| json_data | array | 是 | JSON 格式的文档数组 |

**请求示例：**
```json
{
  "collection_name": "users",
  "json_data": [
    {"name": "张三", "age": 25},
    {"name": "李四", "age": 30}
  ]
}
```

**返回内容：**
```json
{
  "success": true,
  "data": {
    "inserted_count": 2,
    "inserted_ids": ["id1", "id2"]
  }
}
```

---

#### JSON 数据导出
```
POST /api/batch/export
```

**功能：** 从指定集合导出数据为 JSON 格式

**请求参数（JSON Body）：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| collection_name | string | 是 | 源集合名称 |
| query | object | 否 | 查询条件，默认为 {} |
| limit | number | 否 | 导出数量限制，默认无限制 |

**请求示例：**
```json
{
  "collection_name": "users",
  "query": {"age": {"$gte": 25}},
  "limit": 100
}
```

**返回内容：**
```json
{
  "success": true,
  "data": {
    "documents": [
      {"_id": "id1", "name": "张三", "age": 25},
      {"_id": "id2", "name": "李四", "age": 30}
    ],
    "count": 2
  }
}
```

**注意：** 以上所有批量操作接口均需要认证（`@auth_middleware.require_auth`）

## 项目结构

```
pymongoddb/
├── api/                    # API 路由
│   ├── batch_routes.py
│   ├── collection_routes.py
│   ├── counter_routes.py
│   ├── dict_routes.py
│   ├── list_routes.py
│   └── user_routes.py
├── database/               # 数据库连接
│   ├── base.py
│   └── connection.py
├── middleware/             # 中间件
│   └── auth_middleware.py
├── modules/                # 业务模块
│   ├── counter_module.py
│   ├── dict_module.py
│   ├── list_module.py
│   └── user_module.py
├── services/               # 服务层
│   ├── batch_service.py
│   └── collection_service.py
├── app.py                  # Flask 应用
├── config.py               # 配置管理
├── run.py                  # 启动脚本
├── requirements.txt        # 依赖列表
└── .env.example            # 环境变量示例
```

## 数据库连接

项目使用单例模式的 MongoDB 连接管理，支持连接池和自动重试：

```python
from database.connection import db_connection

# 获取集合
collection = db_connection.get_collection('collection_name')

# 检查连接状态
if db_connection.is_connected():
    # 执行操作
    pass
```