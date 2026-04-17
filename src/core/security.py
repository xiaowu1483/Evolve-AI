# 权限校验模块
# TODO: Implement logic here
# src/core/security.py

import os
import re
from pathlib import Path

class SecurityManager:
    """
    安全校验模块
    负责验证 AI 对文件系统的访问权限，防止越权操作
    """
    
    # 定义只读目录，AI 不可修改
    READ_ONLY_DIRS = ['src/core', 'tools', 'agents', '.git', 'config']
    
    # 定义敏感文件模式
    SENSITIVE_PATTERNS = [r'\.env', r'\.git.*', r'system\.yaml']
    
    def __init__(self, root_path):
        self.root_path = Path(root_path).resolve()
        
    def validate_path(self, relative_path, mode='read'):
        """
        验证路径是否允许访问
        :param relative_path: 相对于根目录的路径
        :param mode: 'read' 或 'write'
        :return: (bool, str) 是否允许，错误信息
        """
        full_path = (self.root_path / relative_path).resolve()
        
        # 防止路径遍历攻击 (../../)
        try:
            full_path.relative_to(self.root_path)
        except ValueError:
            return False, "Access denied: Path traversal detected"
            
        # 检查敏感文件
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, str(relative_path)):
                return False, f"Access denied: Sensitive file matched {pattern}"
                
        # 检查只读目录 (仅针对写操作)
        if mode == 'write':
            rel_parts = Path(relative_path).parts
            for read_only in self.READ_ONLY_DIRS:
                if rel_parts[0] == read_only:
                    return False, f"Access denied: {read_only} is read-only"
                    
        return True, "OK"
        
    def check_content(self, content):
        """
        检查写入内容是否包含危险代码
        :param content: 待写入的字符串内容
        :return: (bool, str)
        """
        # 简单检查：防止删除整个系统的关键命令
        dangerous_cmds = ['rm -rf /', 'sudo', 'chmod 777']
        for cmd in dangerous_cmds:
            if cmd in content:
                return False, f"Security alert: Dangerous command '{cmd}' detected"
        return True, "OK"
