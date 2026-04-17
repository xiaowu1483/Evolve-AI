# triggers/README.md

# 触发器配置说明

## 用途
本目录存储事件驱动的配置文件的，用于定义系统在特定条件下自动执行哪些代理（Agents）或工具（Tools）。
**AI 扩展指南**：当添加新功能需要自动运行时，可在此创建新的触发器配置文件。

## 工作原理
1. 系统启动时加载本目录所有 `.yaml` 文件。
2. 监控特定事件（如会话结束、系统空闲、错误发生）。
3. 匹配配置中的条件，执行指定的 `agent` 或 `tool`。

## 配置文件结构
每个 YAML 文件需遵循 `trigger_schema.json` 定义的格式。

### 核心字段
- `trigger_name`: 唯一标识符
- `event`: 触发事件类型 (session_end, idle, error, startup)
- `enabled`: 是否启用
- `conditions`: 触发条件 (如空闲时长)
- `actions`: 执行动作列表 (调用哪个 Agent 或 Tool)
- `priority`: 优先级 (高优先级先执行)

## 示例
见 `on_session_end.yaml` 和 `on_idle.yaml`。

## 注意事项
- 修改配置后无需重启，系统会热加载（取决于 `src/core` 实现）。
- 确保 `actions` 中引用的 agent 类在 `agents/` 目录中存在。
- 敏感操作（如删除文件）需设置 `require_confirmation: true`。
