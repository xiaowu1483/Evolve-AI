# templates/skill_template/skill.py

# 轻量级技能模板
# 适用于不需要完整模块结构的简单功能
# 通常用于快速原型或单一功能脚本

from typing import Dict, Any

class Skill:
    """
    轻量级技能基类
    不同于 Module，Skill 不需要注册到模块加载器，可直接被调用
    """
    
    def __init__(self):
        self.name = "UnnamedSkill"
        self.description = "No description"
        
    def run(self, args: Dict[str, Any]) -> Any:
        """
        执行技能
        :param args: 参数字典
        :return: 执行结果
        """
        # 示例逻辑
        return {"status": "success", "data": None}
        
    def get_help(self) -> str:
        """
        获取帮助信息
        :return: 帮助文本
        """
        return f"Usage: {self.name} [args]"

# 示例实现
class ExampleSkill(Skill):
    def __init__(self):
        super().__init__()
        self.name = "ExampleSkill"
        self.description = "An example skill for testing"
        
    def run(self, args: Dict[str, Any]) -> Any:
        text = args.get('text', '')
        return {"status": "success", "data": text.upper()}
