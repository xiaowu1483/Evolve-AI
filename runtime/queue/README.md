# runtime/queue/README.md

# 任务队列说明

## 用途
存储待处理的异步任务，主要用于解耦主对话流程和后台维护任务。

## 任务类型
1. **reflection**: 会话结束后的反思任务。
   - 优先级：高
   - 处理者：`agents/reflection_agent`
2. **maintenance**: 系统维护任务（链接检查、日志清理）。
   - 优先级：低
   - 处理者：`agents/maintenance_agent`
3. **consolidation**: 记忆固化任务。
   - 优先级：中
   - 处理者：`agents/consolidator`

## 文件格式
- 扩展名：`.jsonl` (JSON Lines)
- 示例：
  ```json
  {"task_id": "t1", "type": "reflection", "payload": {"session_id": "abc"}, "created_at": "2024-05-20T10:00:00"}
