# 记忆系统架构说明
# wiki/01_Architecture/Memory_System.md

# 记忆系统设计

## 概述

本系统采用 **LLM Wiki + 反思固化** 模式，而非传统向量数据库。

**核心理念**: 对话是源代码，Wiki 是编译后的可执行文件。

## 记忆层次
┌─────────────────────────────────────────────────────────┐ 
│ 长期记忆 (持久化) │ │ wiki/04_LongTerm_Memory/ │ 
│ 
├── User_Profile.md (用户画像) 
│
│ 
├── Preferences.md (偏好设置) 
│
│ 
└── Decision_Log.md (决策记录) 
│
└─────────────────────────────────────────────────────────┘ 
▲ 
│ 固化 │
 ┌─────────────────────────────────────────────────────────┐
 │ 反思日志 (中间层) │ │ wiki/05_Reflection_Logs/
 │
 │ └── YYYY-MM/Session_ID_Summary.md
 │
 └─────────────────────────────────────────────────────────┘
 ▲ 
│ 提取 │ 
┌─────────────────────────────────────────────────────────┐ 
│ 原始对话 (临时) │ │ runtime/active_session/raw_log.md │
│ → 迁移 → wiki/06_Raw_Archives/YYYY-MM/ │ 
└─────────────────────────────────────────────────────────┘


## 记忆固化流程
会话结束 
│ ▼ReflectionAgent.run() 
│ 
├── 读取 raw_log.md (原始对话) 
├── 读取 User_Profile.md (现有记忆) 
├── 调用 LLM 分析提取 
│ ├── 新偏好 │ 
├── 代码变更 │ 
└── 重要决策 │ 
├── 生成 Reflection_Log (反思日志) 
│ 
└── 更新 User_Profile.md (记忆固化) 
│ ▼ MemoryConsolidator.run_consolidation() 
│ 
└── 合并碎片、解决冲突


## 关键组件

| 组件 | 文件 | 职责 |
|------|------|------|
| `ReflectionAgent` | `agents/reflection_agent.py` | 对话后反思分析 |
| `MemoryConsolidator` | `agents/consolidator.py` | 记忆合并与冲突解决 |
| `WikiManager` | `src/core/wiki_manager.py` | Wiki 读写 API |

## 记忆更新规则

1. **置信度阈值**: 仅当 `confidence > 0.7` 时更新长期记忆
2. **冲突处理**: 新信息覆盖旧信息，保留来源标注
3. **溯源要求**: 每条记忆需标注来源会话 ID

### 示例格式

```markdown
## 用户偏好

- 喜欢深色模式 [来源：Session a1b2c3d4, 2024-05-20]
- 偏好 Python 而非 Java [来源：Session e5f6g7h8, 2024-05-21]
日志保留策略
类型	保留时间	压缩策略
原始对话	90 天	7 天后 gzip 压缩
反思日志	永久	6 个月后可压缩
长期记忆	永久	不压缩
详细配置见 config/retention.yaml。

相关文档
[[Core_Engine]] - 核心引擎会话管理
[[Wiki_Sync_Rule]] - 记忆文档同步规则
[[User_Profile]] - 用户画像模板
最后更新：2024-01-01 维护者：System
