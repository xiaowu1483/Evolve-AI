# config/README.md

# 配置目录说明

## 用途
本目录存储系统的所有配置文件，控制 AI 的行为、安全策略和数据保留规则。

## 文件说明

### 1. system.yaml
- **用途**: 核心系统设置 (LLM 模型、安全级别、路径)。
- **AI 操作规范**: 
  - 禁止修改 `security.level` 和 `security.read_only_dirs`。
  - 修改 `llm.model` 需确保新模型可用。
  - 修改后需重启系统生效。

### 2. ai_profile.yaml
- **用途**: 定义 AI 人设、目标和禁止事项。
- **AI 操作规范**:
  - 可根据用户反馈优化 `instructions`。
  - 禁止移除 `restrictions` 中的安全限制。
  - 这是 AI 的"宪法"，修改需慎重。

### 3. retention.yaml
- **用途**: 控制日志和备份的保留策略。
- **AI 操作规范**:
  - 可根据磁盘空间调整 `keep_days`。
  - 建议保持 `reflection_logs.keep_forever: true` 以保护知识。

### 4. config_loader.py
- **用途**: Python 配置加载工具。
- **注意**: 代码文件，通常只读。

## 修改流程
1. 备份原文件 (`tools/backup.py`)。
2. 修改 YAML 内容。
3. 运行 `config_loader.py` 验证格式。
4. 重启系统或触发热加载。

## 环境变量
敏感信息 (如 API Key) 不应存入本目录，请使用 `.env` 文件。
本目录配置可引用环境变量，格式：`${ENV_VAR_NAME}`。
