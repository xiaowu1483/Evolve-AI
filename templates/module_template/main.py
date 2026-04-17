# templates/module_template/main.py

# 新模块实现模板
# 复制此文件到 src/modules/[模块名]/main.py
# 必须继承 BaseModule 并实现所有抽象方法

from src.modules.base_module import BaseModule
from typing import Dict, Any, List

class ModuleImpl(BaseModule):
    """
    [Module_Name] 模块实现
    请在此处填写模块的具体功能描述
    """
    
    def __init__(self):
        super().__init__()
        # 以下属性通常由 loader.py 从 config.yaml 注入，但可在此设置默认值
        self.name = "[Module_Name]"
        self.version = "1.0.0"
        self.description = "请在此处填写模块描述"
        self.triggers = ["[trigger_word]"]
        
    def initialize(self, context: Dict[str, Any]):
        """
        模块初始化
        :param context: 包含 wiki_manager, security_manager 等安全工具上下文
        """
        # 在此处建立数据库连接、加载缓存或初始化资源
        # 示例：
        # self.db = context.get('database')
        # self.wiki = context.get('wiki_manager')
        self.context = context
        print(f"[{self.name}] Initialized successfully")
        
    def execute(self, query: str, context: Dict[str, Any]) -> str:
        """
        执行模块逻辑
        :param query: 用户指令或参数
        :param context: 运行时上下文
        :return: 执行结果字符串
        """
        # 在此处编写核心业务逻辑
        # 示例：
        # result = self.process_data(query)
        # return f"处理结果：{result}"
        
        # 安全提示：如需写入文件，请使用 context['wiki_manager'].write_file()
        # 禁止直接使用 open() 写入受保护目录
        
        return f"[Module_Name] 收到指令：{query} (此为模板返回，请实现具体逻辑)"
        
    def get_wiki_doc(self) -> str:
        """
        生成模块的 Wiki 文档内容
        用于自动同步到 wiki/02_Modules/ 目录
        :return: Markdown 格式的文档内容
        """
        return f"""# {self.name}

## 描述
{self.description}

## 版本
{self.version}

## 触发词
{', '.join(self.triggers)}

## 使用方法
自动加载，通过触发词或 API 调用。

## 配置
见 `config.yaml`。

## 维护
此文档由模块自动生成，修改代码后请更新此方法。
"""
