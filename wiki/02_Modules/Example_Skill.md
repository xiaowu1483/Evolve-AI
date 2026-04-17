# wiki/02_Modules/Example_Skill.md

# Example_Skill 模块文档

> 示例模块文档，对应 `src/modules/example_skill/`。
> 用于演示模块文档的标准结构和内容。

## 概述

- **模块名称**: Example_Skill
- **文件位置**: `src/modules/example_skill/`
- **版本**: 1.0.0
- **作者**: System
- **创建时间**: 2024-01-01

## 功能描述

这是一个示例技能模块，用于演示模块系统的结构。
主要功能是将输入文本反转返回，无实际业务用途。

## 配置项

| 配置键 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `enabled` | bool | `true` | 是否启用模块 |
| `timeout` | int | `30` | 执行超时时间 |

## 触发词

- `example`
- `test`
- `demo`

## 使用方法

### 1. 自然语言调用
用户说："example hello world"
AI 响应："Example Skill received: hello world. Reverse: dlrow olleh"

### 2. 代码调用
```python
from src.modules.loader import ModuleLoader
loader = ModuleLoader()
modules = loader.load_all()
example = [m for m in modules if m.name == 'Example_Skill'][0]
result = example.execute("hello")
依赖项
Python 包：无
系统工具：无
外部 API：无
权限需求
 读取 Wiki
 写入 Wiki
 执行代码
 网络访问
代码结构
src/modules/example_skill/
├── __init__.py
├── main.py          # 核心逻辑
├── config.yaml      # 元数据配置
└── README.md        # 开发说明
已知问题
无
更新日志
2024-01-01: 初始创建
2024-01-02: 更新文档结构
维护提示：此为示例文档，实际模块请参考此结构编写。 对应代码：src/modules/example_skill/main.py