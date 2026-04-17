# 核心引擎设计说明
# wiki/01_Architecture/Core_Engine.md

# 核心引擎设计

## 概述

`CoreEngine` 是系统的主控组件，负责会话管理、上下文加载和 LLM 调用。

**文件位置**: `src/core/engine.py`

## 核心职责

1. **会话生命周期管理**
   - `start_session()`: 创建新会话，生成 `session_id`
   - `process_input()`: 处理用户输入，调用 LLM
   - `end_session()`: 结束会话，触发反思代理

2. **上下文加载**
   - 仅加载 `wiki/_Index.md` 和关键协议
   - 避免一次性加载全部 Wiki，节省 Token

3. **日志记录**
   - 所有对话写入 `runtime/active_session/raw_log.md`
   - 会话结束后迁移到 `wiki/06_Raw_Archives/`

## 类结构

```python
class CoreEngine:
    def __init__(self, root_path, llm_client)
    def start_session(self) -> str
    def load_context(self) -> str
    def process_input(self, user_input) -> str
    def end_session(self)
    def _log_message(self, role, content)
    def _get_recent_log(self) -> str
依赖组件
组件		用途	文件
WikiManager	Wiki 读写	src/core/wiki_manager.py
SecurityManager	权限校验	src/core/security.py
LLM Client	推理调用	外部注入
上下文加载策略
load_context()
├── 读取 wiki/_Index.md (根导航)
├── 读取 wiki/04_LongTerm_Memory/_Index.md (记忆索引)
├── 读取 wiki/03_Protocols/Wiki_Sync_Rule.md (核心协议)
└── 读取 runtime/active_session/raw_log.md (最近 50 行)
设计理由: 分层加载避免 Token 溢出，AI 可按需深入读取子文档。

修改规范
禁止直接修改: 核心引擎应由人类开发者维护
如需扩展: 创建新模块到 src/modules/
文档同步: 修改后更新本文档和 01_Architecture/_Index.md
相关文档
[[Memory_System]] - 记忆系统详细设计
[[Security_Policy]] - 安全访问控制
[[Wiki_Sync_Rule]] - 文档同步规则
---
> 最后更新：2024-01-01
> 维护者：System


