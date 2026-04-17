# src/utils/file_helpers.py

import os
from pathlib import Path
from typing import Optional

def ensure_dir(path):
    """
    确保目录存在，不存在则创建
    :param path: 目录路径
    """
    Path(path).mkdir(parents=True, exist_ok=True)
    
def safe_read(file_path, default=""):
    """
    安全读取文件，处理编码和不存在的情况
    :param file_path: 文件路径
    :param default: 文件不存在时的默认返回值
    :return: 文件内容字符串
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return default
    except UnicodeDecodeError:
        # 尝试 fallback 编码
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
        except:
            return default
    except Exception:
        return default
        
def safe_write(file_path, content):
    """
    安全写入文件，确保目录存在
    :param file_path: 文件路径
    :param content: 写入内容
    :return: bool 是否成功
    """
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False
        
def get_relative_path(full_path, base_path):
    """
    获取相对路径，安全处理跨平台问题
    :param full_path: 完整路径
    :param base_path: 基准路径
    :return: 相对路径字符串
    """
    try:
        return Path(full_path).relative_to(Path(base_path)).as_posix()
    except ValueError:
        return str(full_path)
