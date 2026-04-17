# 指南
# README.md

# PersonalAI - 个人 AI 助手

基于 LLM Wiki 架构的自进化个人 AI 助手系统。

## 核心理念

1. **Wiki 即知识**：结构化 Markdown 文档是唯一事实来源，而非向量数据库
2. **对话即训练**：每次对话结束后自动反思并固化记忆
3. **代码即文档**：代码与 Wiki 文档严格同步，AI 可扩展模块
4. **安全优先**：沙箱执行、权限控制、自动备份

## 目录结构
PersonalAI/ 

├── wiki/ # 核心知识库 (LLM Wiki 模式) 

├── src/ # 源代码 

├── agents/ # 智能代理 (反思、维护、固化) 

├── tools/ # 维护工具 (备份、验证、同步) 

├── runtime/ # 运行时数据 

├── triggers/ # 触发器配置

├── config/ # 系统配置

├── templates/ # 标准模板 

└── data/ # 持久化数据


## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd PersonalAI

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

### 2. bash配置
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填写 LLM API Key
vim .env

### 3.运行
python main.py
核心功能
1. 分层 Wiki 知识库
_Index.md 导航页，支持懒加载，减少 Token 消耗
模块化文档结构，与代码目录一一映射
自动链接验证，防止死链
2. 反思与记忆固化
会话结束后自动触发 ReflectionAgent
生成反思日志 (wiki/05_Reflection_Logs/)
更新长期记忆 (wiki/04_LongTerm_Memory/)
3. 模块扩展系统
复制 templates/module_template/ 创建新模块
自动注册到 Wiki 模块注册表
沙箱测试，安全执行
4. 自动维护
空闲时运行 MaintenanceAgent
日志轮转与压缩 (tools/log_rotator.py)
链接验证与修复 (tools/validate_links.py)
配置说明
文件	用途
config/system.yaml	系统核心配置 (LLM、安全策略)
config/ai_profile.yaml	AI 人设与行为边界
config/retention.yaml	日志保留策略
.env	敏感环境变量 (API Key 等)
安全特性
沙箱执行：AI 生成代码在隔离环境运行
权限控制：只读目录保护 (src/core, config)
自动备份：修改前自动快照 (tools/backup.py)
审计追踪：所有变更可追溯 (data/audit_trail.json)
开发指南
添加新模块
复制 templates/module_template/ 到 src/modules/[模块名]/
修改 main.py 实现业务逻辑
修改 config.yaml 配置元数据
重启系统或触发模块重载
修改 Wiki 规范
遵循 wiki/03_Protocols/Wiki_Sync_Rule.md
创建新文档后更新对应 _Index.md
运行 tools/validate_links.py 检查链接
技术栈
语言: Python 3.11+
LLM: OpenAI / Anthropic / 本地模型
数据库: SQLite + 可选向量库
配置: YAML
日志: Python logging


贡献
欢迎提交 Issue 和 Pull Request。
