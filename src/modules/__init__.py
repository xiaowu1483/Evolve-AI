# src/modules/__init__.py

"""
模块系统初始化
负责动态加载所有子模块并注册到系统
"""

from .base_module import BaseModule
from .loader import ModuleLoader

__all__ = ['BaseModule', 'ModuleLoader']

# 自动加载所有模块
loader = ModuleLoader()
loaded_modules = loader.load_all()
