# Prompt Doc

该项目用于管理多版本、多场景、多适用模型的 Prompt 集合。基于Python和Flask框架开发，提供了一组 RESTful API，用于对 Prompt 模板进行创建、检索、更新和删除等操作。

## 技术栈

- Python
- Flask
- MongoDB（使用 MongoEngine 作为 ODM）

## 如何运行

1. 安装Python3和MongoDB

2. 克隆项目代码
    ```bash
   git clone https://github.com/worldwonderer/promptdoc.git
    ```

3. 安装项目依赖
   ```bash
   pip install -r requirements.txt
   ```

4. 配置MONGODB_HOST环境变量
   ```bash
   export MONGODB_HOST=<mongodb://>
   ```

5. 运行Flask应用
   ```bash
   python debug.py
   ```

## 数据模型
- `prompt_id`：Prompt 的唯一标识符，是一个必填字段，并且是唯一的。
- `content`：Prompt 的模板内容，是一个必填字段。
- `variables`：Prompt 中的变量列表，是一个字符串列表。
- `example`：Prompt 的示例，是一个字典字段。
- `version`：Prompt 的版本号，是一个必填字段。
- `applicable_llm`：适用的 LLM（Language Model），是一个必填字段。
- `created_at`：Prompt 的创建时间，默认为当前时间。
- `updated_at`：Prompt 的更新时间，默认为当前时间。
- `tags`：Prompt 的标签列表。

## API接口

### 创建Prompt

- 请求方法：POST
- 请求路径：/prompt
- 请求体：JSON 格式，包含 Prompt 的内容、变量、示例、版本、适用的 LLM 和标签等信息

### 获取Prompt详情

- 请求方法：GET
- 请求路径：/prompt/<prompt_id>

### 更新Prompt

- 请求方法：PUT
- 请求路径：/prompt/<prompt_id>
- 请求体：JSON 格式，包含要更新的 Prompt 字段及其值

### 删除Prompt

- 请求方法：DELETE
- 请求路径：/prompt/<prompt_id>

### 获取Prompt列表

- 请求方法：GET
- 请求路径：/prompts
- 查询参数：
  - applicable_llm：按照适用的 LLM 过滤
  - tag：按照标签过滤
  - keywords：按照关键字在 Prompt 内容中进行模糊搜索
  - offset：分页偏移量，默认为0
  - limit：分页大小，默认为10
  - sort_by：排序字段，默认为按照创建时间倒序排列
