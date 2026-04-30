中文 | [English](README.md)

# Prompt Doc

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org) [![Flask](https://img.shields.io/badge/Flask-3.0-orange.svg)](https://flask.palletsprojects.com) [![MongoDB](https://img.shields.io/badge/Database-MongoDB-47A248.svg)](https://www.mongodb.com)

轻量级 Prompt 模板管理平台，支持多版本、多场景的 Prompt 模板创建、管理与分发，提供 RESTful API 和可视化管理后台。

## 功能特性

- **多版本 Prompt 管理** — 按版本、场景和目标 LLM 模型组织 Prompt 模板
- **RESTful API** — 完整的 CRUD 操作，支持 Bearer Token 认证
- **管理后台** — 基于 Web 的可视化管理界面，支持 TOTP（Google Authenticator）双因素认证
- **变量预览** — 使用示例值替换 `{{变量}}` 并实时预览渲染效果
- **搜索与过滤** — 支持分页浏览、全文搜索和标签筛选

## 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| Web 框架 | [Flask](https://flask.palletsprojects.com) | 3.0.3 |
| ODM | [MongoEngine](http://mongoengine.org) | 0.28.2 |
| Flask-MongoEngine | [flask-mongoengine-3](https://pypi.org/project/flask-mongoengine-3/) | 1.0.9 |
| 序列化 | [marshmallow](https://marshmallow.readthedocs.io) + marshmallow-mongoengine | 3.21.2 / 0.31.2 |
| 双因素认证 | [pyotp](https://pypi.org/project/pyotp/) | 2.9.0 |
| 数据库 | [MongoDB](https://www.mongodb.com) | 4.0+ |
| 测试 | [pytest](https://pytest.org) | 8.2.0 |

## 快速开始

### 环境要求

- Python 3.8+
- MongoDB 4.0+（本地或远程运行）

### 安装步骤

1. **克隆仓库**

   ```bash
   git clone https://github.com/worldwonderer/promptdoc.git
   cd promptdoc
   ```

2. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**

   ```bash
   export MONGODB_HOST="mongodb://localhost:27017/prompt"
   export SECRET_KEY="your-flask-secret-key"
   ```

4. **配置管理后台认证**

   生成 TOTP 密钥和 Google Authenticator 二维码：

   ```bash
   python tool.py
   ```

   执行后会生成 `admin_auth.png` 二维码图片。使用 Google Authenticator App 扫描该二维码，然后导出生成的密钥：

   ```bash
   export ADMIN_SECRET="tool-输出的密钥"
   export AUTH_TOKEN="你的-API-认证令牌"
   ```

5. **启动开发服务器**

   ```bash
   python debug.py
   ```

   服务启动后访问 `http://127.0.0.1:5000`。注意：`debug.py` 仅用于本地开发环境。

## API 文档

所有 API 端点均需在请求头中通过 `Authorization` 字段提供 Bearer Token 认证。

### 获取 Prompt 列表

```
GET /api/prompts
```

**查询参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `page` | integer | 1 | 页码（≥ 1） |
| `per_page` | integer | 10 | 每页条数（1–100） |
| `tag` | string | — | 按标签筛选 |
| `search` | string | — | 在 Prompt 内容中全文搜索 |

**示例：**

```bash
curl -s "http://127.0.0.1:5000/api/prompts?page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

**响应：**

```json
{
  "data": [
    {
      "prompt_id": "uuid-string",
      "content": "You are a {{role}}...",
      "variables": ["role"],
      "example": {"role": "helpful assistant"},
      "version": "1",
      "applicable_llm": "GPT-4",
      "tags": ["general", "chat"],
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "pagination": {
    "total_count": 1,
    "page": 1,
    "per_page": 10,
    "total_pages": 1
  }
}
```

### 创建 Prompt

```
POST /api/prompt
```

**请求体：**

```json
{
  "content": "You are a {{role}} expert in {{domain}}.",
  "variables": ["role", "domain"],
  "example": {"role": "senior", "domain": "machine learning"},
  "version": "1",
  "applicable_llm": "GPT-4",
  "tags": ["expert", "domain"]
}
```

**响应：** `201 Created`

```json
{
  "message": "Prompt created successfully",
  "prompt_id": "generated-uuid"
}
```

### 获取 Prompt 详情

```
GET /api/prompt/<prompt_id>
```

**响应：** `200 OK` — 返回 Prompt 对象。

### 更新 Prompt

```
PUT /api/prompt/<prompt_id>
```

**请求体：** 仅包含需要更新的字段，所有字段均为可选。

**响应：** `200 OK`

```json
{
  "message": "Prompt updated successfully"
}
```

### 删除 Prompt

```
DELETE /api/prompt/<prompt_id>
```

**响应：** `200 OK`

```json
{
  "message": "Prompt deleted successfully"
}
```

## 管理后台

管理后台提供了可视化的 Prompt 管理界面。

### 访问方式

1. 访问 **登录页面**：`http://127.0.0.1:5000/admin/login`
2. 打开 Google Authenticator，输入通过 `tool.py` 生成的二维码所对应的动态验证码
3. 登录后进入 **Prompt 列表**：`http://127.0.0.1:5000/admin/prompts`

### 功能

- **浏览与搜索** — 分页列表，支持标签筛选和内容搜索
- **创建与编辑** — 表单化编辑，自带字段校验
- **变量预览** — 使用示例值替换 `{{变量}}`，实时预览渲染效果
- **删除** — 一键删除 Prompt

![](./images/admin_ui.png)

## 项目结构

```
promptdoc/
├── api/
│   ├── __init__.py         # 包初始化
│   ├── config.py           # 应用配置与环境变量
│   ├── models.py           # MongoDB 文档模型（Prompt、PromptSchema）
│   ├── index.py            # Flask 应用工厂与蓝图注册
│   ├── api_routes.py       # RESTful API 端点 (/api/*)
│   ├── admin_routes.py     # 管理后台路由 (/admin/*)
│   └── templates/          # Jinja2 HTML 模板
├── tests/
│   └── test_api.py         # API 测试套件（pytest）
├── tool.py                 # TOTP 密钥与二维码生成工具
├── debug.py                # 开发服务器入口
├── requirements.txt        # Python 依赖
├── vercel.json             # Vercel 部署配置
├── README.md               # 英文文档
└── README_ZH.md            # 中文文档
```

## 配置说明

| 环境变量 | 必填 | 说明 |
|----------|------|------|
| `MONGODB_HOST` | 是 | MongoDB 连接 URI（如 `mongodb://localhost:27017/prompt`） |
| `SECRET_KEY` | 是 | Flask 会话密钥 |
| `ADMIN_SECRET` | 是 | 管理后台 TOTP 密钥（由 `tool.py` 生成） |
| `AUTH_TOKEN` | 是 | API Bearer Token 认证令牌 |

## 贡献指南

欢迎贡献！参与步骤：

1. Fork 本仓库
2. 创建功能分支（`git checkout -b feature/my-feature`）
3. 提交更改（`git commit -m 'Add my feature'`）
4. 推送分支（`git push origin feature/my-feature`）
5. 提交 Pull Request

提交前请确保测试通过：

```bash
pytest tests/
```

## 许可证

本项目基于 MIT 许可证开源，详见 [LICENSE](LICENSE) 文件。
