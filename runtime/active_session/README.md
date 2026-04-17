# runtime/active_session/README.md

# 活动会话规范

## 写入规则
1. **raw_log.md**:
   - 格式：Markdown
   - 每次交互追加内容，格式如下：
     ```markdown
     ### User
     [用户输入内容]

     ### AI
     [AI 响应内容]
     ```
   - 禁止修改历史记录，只能追加。

2. **context.json**:
   - 格式：JSON
   - 每次交互后更新 `last_activity` 字段。
   - 如果识别到用户意图变更，更新 `user_intent`。

## 生命周期
- **创建**: 由 `src/core/engine.py` 的 `start_session()` 创建。
- **活跃**: 用户交互期间保持锁定。
- **结束**: 用户断开连接或超时 30 分钟后，触发 `end_session()`。
- **迁移**: 结束后由 `tools/migrate_session.py` 移动到归档目录。

## 注意事项
- 本目录文件不包含敏感信息（敏感信息应存储在 `.env`）。
- 如果文件损坏，系统会自动重建并记录错误日志。
