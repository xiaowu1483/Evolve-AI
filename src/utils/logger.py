# src/utils/logger.py

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

# 全局日志缓存
_loggers = {}

def setup_logger(name, log_path, level=logging.INFO):
    """
    配置旋转文件日志处理器
    :param name: 日志名称
    :param log_path: 日志文件路径
    :param level: 日志级别
    :return: Logger 实例
    """
    if name in _loggers:
        return _loggers[name]
        
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 防止重复添加 handler
    if logger.handlers:
        return logger
        
    # 确保目录存在
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    
    # 文件处理器 (旋转日志，最大 10MB，保留 5 个备份)
    file_handler = RotatingFileHandler(log_path, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    _loggers[name] = logger
    return logger
    
def get_logger(name):
    """
    获取已配置的日志实例
    :param name: 日志名称
    :return: Logger 实例
    """
    return _loggers.get(name, logging.getLogger(name))
