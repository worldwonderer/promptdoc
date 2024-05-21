# Prompt Doc

该项目用于管理多版本、多场景、多适用模型的 Prompt 模板集合。基于 Python 和 Flask 框架开发，提供了一组 RESTful API 和管理后台，用于对 Prompt 模板进行创建、检索、更新和删除等操作。

## 技术栈

- Python
- Flask
- MongoDB（使用 MongoEngine 作为 ODM）

## 如何运行

1. 安装 Python3 和 MongoDB

2. 克隆项目代码
    ```bash
   git clone https://github.com/worldwonderer/promptdoc.git
    ```

3. 安装项目依赖
   ```bash
   pip install -r requirements.txt
   ```

4. 配置环境变量
    ```bash
    export MONGODB_HOST=<mongodb://>
    export SECRET_KEY=<flask secret>
    ```
    为管理后台生成 Google Authenticator App 二维码和密钥
    ```bash
    python tool.py
    export ADMIN_SECRET=<admin secret>
    export AUTH_SECRET=<api secret>
    ```

5. 运行 Flask 应用
   ```bash
   python debug.py
   ```

## 开始使用

### Admin UI

**Login Page**: http://127.0.0.1:5000/admin/login

默认开启动态验证码鉴权，需打开 Google Authenticator App 扫描 `admin_auth.png` 中的二维码，随后输入动态密码登录

**List Page**: http://127.0.0.1:5000/admin/prompts

![](./images/admin_ui.png)

### API 示例

```bash
curl --location 'http://127.0.0.1:5000/api/prompts' \
--header 'Authorization: Bearer {AUTH_SECRET}'
```

完整接口示例可参考`.\tests\test_api.py`

## 贡献

欢迎对 Prompt Doc 项目做出贡献！如果你发现了任何问题或有改进建议，请在 GitHub 上提交 Issue 或 Pull Request。

## 许可证

Prompt Doc 项目采用 MIT 许可证，详情请参阅 [LICENSE](LICENSE) 文件。

## 联系方式
如果你有任何问题或建议，欢迎通过以下方式联系我：

邮箱: xtchen.pitt@gmail.com
