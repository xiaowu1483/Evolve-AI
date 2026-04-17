# Wiki 读写 API（供 agents 调用）
# TODO: Implement logic here
# src/core/wiki_manager.py

import os
import json
from pathlib import Path
from datetime import datetime
from .security import SecurityManager
from typing import List, Dict, Any, Optional

class WikiManager:
    """
    Wiki 知识库管理器
    负责 hierarchical wiki 结构的读写，支持懒加载索引
    """
    
    def __init__(self, root_path, security_manager: SecurityManager):
        self.root_path = Path(root_path)
        self.wiki_path = self.root_path / 'wiki'
        self.security = security_manager
        self.index_cache = {} # 缓存索引结构，减少 IO
        
    def get_index_path(self, sub_dir):
        """
        获取子目录的索引文件路径
        :param sub_dir: 子目录名，如 '01_Architecture'
        :return: Path to _Index.md
        """
        return self.wiki_path / sub_dir / '_Index.md'
        
    def read_index(self, sub_dir):
        """
        读取子目录索引 (懒加载核心)
        AI 只读取 _Index.md 而不是整个目录，节省 Token
        :param sub_dir: 子目录名
        :return: str 索引内容
        """
        index_path = self.get_index_path(sub_dir)
        if not index_path.exists():
            return f"# Index for {sub_dir}\nNo index found."
            
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    def read_file(self, relative_path):
        """
        读取 Wiki 文件
        :param relative_path: 相对于 wiki 目录的路径
        :return: str 文件内容
        """
        allowed, msg = self.security.validate_path(f"wiki/{relative_path}", 'read')
        if not allowed:
            raise PermissionError(msg)
            
        full_path = self.wiki_path / relative_path
        if not full_path.exists():
            return ""
            
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    def write_file(self, relative_path, content, author="AI"):
        """
        写入 Wiki 文件 (带安全校验和备份)
        :param relative_path: 相对于 wiki 目录的路径
        :param content: 文件内容
        :param author: 修改者标识
        """
        # 1. 安全校验
        allowed, msg = self.security.validate_path(f"wiki/{relative_path}", 'write')
        if not allowed:
            raise PermissionError(msg)
            
        content_allowed, msg = self.security.check_content(content)
        if not content_allowed:
            raise PermissionError(msg)
            
        # 2. 备份旧文件 (如果存在)
        full_path = self.wiki_path / relative_path
        if full_path.exists():
            backup_path = self.root_path / 'data' / 'backups' / f"{relative_path.replace('/', '_')}.{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'r', encoding='utf-8') as f:
                old_content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(old_content)
                
        # 3. 写入新内容
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            # 自动添加元数据头
            meta = f"---\nlast_modified: {datetime.now().isoformat()}\nauthor: {author}\n---\n"
            f.write(meta + content)
            
    def update_index(self, sub_dir, entry_name, file_path):
        """
        更新子目录索引 (维护 hierarchical 结构)
        :param sub_dir: 子目录名
        :param entry_name: 显示名称
        :param file_path: 实际文件路径
        """
        index_path = self.get_index_path(sub_dir)
        current_index = ""
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                current_index = f.read()
                
        # 简单追加逻辑，实际项目中应解析 Markdown 列表后插入
        new_line = f"- [{entry_name}]({file_path})\n"
        if new_line not in current_index:
            self.write_file(f"{sub_dir}/_Index.md", current_index + new_line, author="System")
            
    def get_reflection_path(self, session_id):
        """
        获取反思日志存储路径
        :param session_id: 会话 ID
        :return: Path
        """
        date_str = datetime.now().strftime("%Y-%m")
        return self.wiki_path / '05_Reflection_Logs' / date_str / f"{session_id}_Summary.md"
