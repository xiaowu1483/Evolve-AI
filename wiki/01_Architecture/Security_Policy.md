# 安全策略与权限说明
# wiki/01_Architecture/Security_Policy.md

# 安全策略说明

## 概述

本系统采用多层安全机制，防止 AI 越权操作和代码注入。

**核心原则**: 最小权限 + 沙箱隔离 + 自动备份

## 权限层级
┌─────────────────────────────────────────────────────────┐ 
│ 只读区域 (AI 禁止修改) 
│ 
│ 
├── src/core/ (核心引擎) 
│ 
│ 
├── config/ (系统配置) 
│ 
│ 
├── .env (环境变量) 
│ 
│ 
└── .git/ (版本控制) 
│ 
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐ 
│ 受限写入区域 (AI 可修改，需备份) 
│ 
│ 
├── src/modules/ (功能模块) 
│ 
│ 
├── wiki/02_Modules/ (模块文档) 
│ 
│ 
└── wiki/04_LongTerm_Memory/ (长期记忆) 
│ 
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐ 
│ 自由写入区域 (AI 完全控制) │ 
│ 
├── runtime/ (运行时数据) 
│ 
│ 
├── wiki/05_Reflection_Logs/ (反思日志) 
│ 
│ 
└── wiki/06_Raw_Archives/ (原始归档) 
│ 
└─────────────────────────────────────────────────────────┘


## 安全组件

### 1. SecurityManager

**文件**: `src/core/security.py`

**职责**:
- 路径遍历攻击防护 (`../../`)
- 敏感文件模式匹配 (`.env`, `.git`)
- 危险命令检测 (`rm -rf`, `sudo`)

**示例**:
```python
security.validate_path("wiki/04_LongTerm_Memory/User_Profile.md", "write")
# 返回：(True, "OK")

security.validate_path("src/core/engine.py", "write")
# 返回：(False, "Access denied: src/core is read-only")
2. 沙箱执行
目录: runtime/sandbox/

限制:

文件系统：仅可读写 workspace/
网络：默认禁止
资源：最大 512MB 内存，30 秒超时
进程：禁止 fork 子进程
3. 自动备份
工具: tools/backup.py

触发时机:

任何 Wiki 文件修改前
任何代码文件修改前
错误恢复前
备份位置: data/backups/

审计追踪
所有变更记录到 data/audit_trail.json，包含：

时间戳
操作类型 (create/update/delete)
文件路径
执行代理
变更摘要
违规处理
违规类型	处理方式
路径遍历	立即拒绝，记录日志
敏感文件访问	立即拒绝，通知用户
危险命令	立即拒绝，触发审计
沙箱逃逸尝试	终止进程，隔离会话
相关文档
[[Core_Engine]] - 引擎安全调用
[[Wiki_Sync_Rule]] - 安全同步规则
[[Coding_Standards]] - 安全编码规范
最后更新：2024-01-01 维护者：System

警告: 修改安全策略需人类确认，AI 禁止自行更改。
