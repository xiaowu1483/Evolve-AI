# src/modules/example_skill/main.py

from src.modules.base_module import BaseModule
from typing import Dict, Any

class ModuleImpl(BaseModule):
    """
    示例模块实现
    继承 BaseModule 并实现抽象方法
    """
    
    def initialize(self, context: Dict[str, Any]):
        """
        初始化模块
        :param context: 包含 wiki_manager 等工具
        """
        # 可以在这里建立数据库连接或加载缓存
        self.context = context
        print(f"[{self.name}] Initialized")
        
    def execute(self, query: str, context: Dict[str, Any]) -> str:
        """
        执行具体逻辑
        :param query: 用户输入
        :param context: 运行时上下文
        :return: 结果
        """
        # 示例逻辑：返回输入的反转
        # 实际模块应调用 context 中的工具 (如 wiki_manager)
        return f"Example Skill received: {query}. Reverse: {query[::-1]}"
        
    def get_wiki_doc(self) -> str:
        """
        生成专属 Wiki 文档
        """
        base_doc = super().get_wiki_doc()
        return base_doc + "\n## 示例说明\n这是一个模板模块，请复制此结构创建新功能。"
