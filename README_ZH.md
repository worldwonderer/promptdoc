中文 | [English](README.md)

<div align="center">

# PromptDoc

**Prompt 版本管理与分享平台**

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-orange.svg)](https://flask.palletsprojects.com)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB-47A248.svg)](https://www.mongodb.com)

Prompt 散落在聊天记录、文档和代码注释里，版本模糊不清，改动无从追溯，分享只能截图复制。

**PromptDoc 补上了 Prompt 工程缺失的基础设施** — 带逐行 diff 的版本历史、一键分享链接、变量预览和完整的 REST API。把 Prompt 当作一等公民来管理。

</div>

## 界面预览

| 登录 | 列表 |
|:---:|:---:|
| ![](./images/login.png) | ![](./images/prompts.png) |

| 详情 · 版本历史 · 分享 |
|:---:|
| ![](./images/detail.png) |

## 功能特性

- **版本历史与 Diff 对比** — 每次编辑或删除前自动保存快照。浏览历史记录，查看字段级变更和逐行内容差异，红绿高亮一目了然。
- **公开分享链接** — 一键生成分享链接，接收方无需登录即可查看 Prompt 内容、适用模型和标签。随时可撤销。
- **变量预览** — 在 Prompt 中使用 `{{变量名}}` 占位符，填入示例值即可即时预览渲染结果，告别手动替换。
- **中英双语界面** — 一键切换界面语言，选择通过 cookie 持久化。
- **REST API** — 完整的 CRUD 操作，Bearer Token 认证，直接对接现有工作流。
- **TOTP 双因素认证** — 管理后台使用 Google Authenticator 二次验证，告别弱密码。

## 快速开始

**1. 安装依赖**

```bash
git clone https://github.com/worldwonderer/promptdoc.git
cd promptdoc
pip install -r requirements.txt
```

**2. 配置环境变量**

```bash
export MONGODB_HOST="mongodb://localhost:27017/prompt"
export SECRET_KEY="任意随机字符串"
```

**3. 生成 TOTP 密钥**

```bash
python tool.py
```

用 Google Authenticator 扫描输出的二维码，然后：

```bash
export ADMIN_SECRET="tool.py 输出的密钥"
export AUTH_TOKEN="你自定义的 API Token"
```

**4. 启动服务**

```bash
python debug.py
```

打开 `http://127.0.0.1:5000`，使用 Google Authenticator 验证码登录。

## API 参考

除分享接口外，所有接口均需 `Authorization: Bearer YOUR_TOKEN` 认证。

```bash
# 列表（分页、搜索、标签筛选）
curl "http://127.0.0.1:5000/api/prompts?page=1&per_page=10&search=关键词" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 创建 Prompt
curl -X POST "http://127.0.0.1:5000/api/prompt" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"You are a {{role}}.","variables":["role"],"version":"1","applicable_llm":"GPT-4","tags":["test"]}'

# 查看版本历史
curl "http://127.0.0.1:5000/api/prompt/PROMPT_ID/versions" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 版本 Diff 对比
curl "http://127.0.0.1:5000/api/prompt/PROMPT_ID/versions/VERSION_ID/diff" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 访问分享的 Prompt（无需认证）
curl "http://127.0.0.1:5000/api/share/SHARE_TOKEN"
```

## 环境变量配置

| 变量 | 必填 | 说明 |
|------|:----:|------|
| `MONGODB_HOST` | 是 | MongoDB 连接地址 |
| `SECRET_KEY` | 是 | Flask session 密钥 |
| `ADMIN_SECRET` | 是 | TOTP 密钥（由 `tool.py` 生成） |
| `AUTH_TOKEN` | 是 | API Bearer Token |

## 许可证

[MIT](LICENSE)
