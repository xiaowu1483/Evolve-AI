# 模块基类，定义标准接口
# TODO: Implement logic here
# src/modules/base_module.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseModule(ABC):
    """
    所有功能模块的基类
    强制要求每个模块提供元数据、执行逻辑和 Wiki 文档生成能力
    确保 AI 扩展模块时遵循统一标准
    """
    
    def __init__(self):
        self.name = "UnnamedModule"
        self.version = "1.0.0"
        self.description = "No description provided"
        self.triggers = [] # 触发关键词列表
        
    @abstractmethod
    def initialize(self, context: Dict[str, Any]):
        """
        模块初始化
        :param context: 包含 wiki_manager, security_manager 等安全工具上下文
        """
        pass
        
    @abstractmethod
    def execute(self, query: str, context: Dict[str, Any]) -> str:
        """
        执行模块逻辑
        :param query: 用户指令或参数
        :param context: 运行时上下文
        :return: 执行结果字符串
        """
        pass
        
    def get_manifest(self) -> Dict[str, Any]:
        """
        获取模块清单 (用于注册到 Wiki)
        :return: 包含名称、描述、触发词的字典
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "triggers": self.triggers,
            "class_name": self.__class__.__name__
        }
        
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
自动加载，无需手动调用。

## 维护
此文档由模块自动生成。
"""
