# config/__init__.py

"""
配置包初始化
提供统一的配置加载接口
"""

from .config_loader import ConfigLoader

__all__ = ['ConfigLoader']

# 默认配置路径
DEFAULT_CONFIG_DIR = 'config'
