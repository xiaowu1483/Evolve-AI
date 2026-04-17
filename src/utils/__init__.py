# src/utils/__init__.py

"""
工具函数包初始化
提供通用辅助功能，不包含业务逻辑
"""

from .logger import setup_logger, get_logger
from .file_helpers import safe_read, safe_write, ensure_dir
from .text_processors import truncate_text, extract_markdown_links, parse_index
from .time_utils import get_timestamp, get_folder_name

__all__ = [
    'setup_logger', 'get_logger',
    'safe_read', 'safe_write', 'ensure_dir',
    'truncate_text', 'extract_markdown_links', 'parse_index',
    'get_timestamp', 'get_folder_name'
]
