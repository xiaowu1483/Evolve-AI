# templates/module_template/README.md

# 模块开发指南

## 用途
本目录包含创建新功能模块的标准模板。

## 使用步骤
1. 在 `src/modules/` 下创建新目录，命名格式为 `小写字母_下划线` (如 `weather_skill`)。
2. 复制 `templates/module_template/main.py` 到新目录。
3. 复制 `templates/module_template/config.yaml` 到新目录。
4. 修改 `main.py` 中的 `ModuleImpl` 类，实现具体逻辑。
5. 修改 `config.yaml` 中的元数据。
6. 重启系统或触发模块重载。

## 规范
- **必须** 继承 `BaseModule`。
- **必须** 实现 `initialize` 和 `execute` 方法。
- **必须** 确保 `config.yaml` 中的 `name` 与目录名一致。
- **建议** 实现 `get_wiki_doc` 以便自动更新文档。

## 测试
- 在 `runtime/sandbox/workspace/` 中编写测试脚本。
- 确保不违反 `config/ai_profile.yaml` 中的安全限制。
