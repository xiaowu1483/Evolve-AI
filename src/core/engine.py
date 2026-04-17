# 推理引擎封装
# src/core/engine.py

import os
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Any

from .wiki_manager import WikiManager
from .security import SecurityManager

class CoreEngine:
    """
    核心推理引擎
    负责会话生命周期管理，调用 WikiManager，触发 Agents
    """
    
    def __init__(self, root_path: str, llm_client: Any):
        self.root_path = Path(root_path)
        self.llm = llm_client
        self.security = SecurityManager(root_path)
        self.wiki = WikiManager(root_path, self.security)
        self.session_id = None
        self.session_log_path = None
        
    def start_session(self):
        """
        启动新会话
        """
        self.session_id = str(uuid.uuid4())[:8]
        session_dir = self.root_path / 'runtime' / 'active_session'
        session_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_log_path = session_dir / 'raw_log.md'
        with open(self.session_log_path, 'w', encoding='utf-8') as f:
            f.write(f"# Session {self.session_id}\nStarted: {datetime.now().isoformat()}\n\n")
            
        return self.session_id
        
    def load_context_this_issue_is_too_slow(self):
        """
        加载上下文 (基于 Hierarchical Wiki)
        只读取 _Index.md 和关键记忆，避免 Token 溢出
        """
        context = []
        
        root_index = self.wiki.read_file("_Index.md")
        context.append(f"## Wiki Index\n{root_index}")
        
        memory_index = self.wiki.read_index("04_LongTerm_Memory")
        context.append(f"## Memory Index\n{memory_index}")
        
        protocols = self.wiki.read_file("03_Protocols/Wiki_Sync_Rule.md")
        context.append(f"## Protocols\n{protocols}")
        
        return "\n".join(context)

    def load_context(self):
        """
        加载上下文 (优化版)
        只读取必要的索引，避免 Token 过多
        """
        context = []
    
        # 1. 只读取根索引的前 20 行 (足够导航)
        root_index = self.wiki.read_file("_Index.md")
        root_index_short = "\n".join(root_index.split("\n")[:20])
        context.append(f"## Wiki Index\n{root_index_short}")
        
        # 2. 只读取用户画像 (不读取整个记忆目录)
        user_profile = self.wiki.read_file("04_LongTerm_Memory/User_Profile.md")
        if user_profile:
            context.append(f"## User Profile\n{user_profile[:500]}")  # 限制 500 字符
        
        # 3. 只读取核心协议 (不读取全部)
        protocols = self.wiki.read_file("03_Protocols/Wiki_Sync_Rule.md")
        if protocols:
            context.append(f"## Protocols\n{protocols[:500]}")  # 限制 500 字符
        
        return "\n".join(context)
    
        
    def process_input_this_issue_is_too_slow(self, user_input: str) -> str:
        """
        处理用户输入
        :param user_input: 用户文本
        :return: AI 响应
        """
        self._log_message("User", user_input)
        
        context = self.load_context()
        prompt = f"{context}\n\nCurrent Session Log:\n{self._get_recent_log()}\n\nUser: {user_input}"
        
        response = self.llm.generate(prompt)
        
        self._log_message("AI", response)
        
        return response

    def process_input(self, user_input: str) -> str:
        """
        处理用户输入 (优化版)
        """
        self._log_message("User", user_input)
        
        context = self.load_context()
        
        # 只加载最近 15 行对话，而不是 50 行
        recent_log = self._get_recent_log(limit=15)
        
        # 精简 Prompt
        prompt = f"""{context}
    
        ## 当前对话
        {recent_log}
    
        用户：{user_input}
    
        请简洁回答，遵循 Wiki 中的协议。"""
        
        response = self.llm.generate(prompt)
        
        self._log_message("AI", response)
        
        return response

        
    def end_session(self):
        """
        结束会话，触发反思机制
        """
        if not self.session_log_path:
            return
            
        archive_dir = self.root_path / 'wiki' / '06_Raw_Archives' / datetime.now().strftime("%Y-%m")
        archive_dir.mkdir(parents=True, exist_ok=True)
        dest = archive_dir / f"{self.session_id}_raw.md"
        if self.session_log_path.exists():
            os.rename(self.session_log_path, dest)
            
        print(f"Session {self.session_id} ended. Triggering reflection...")
        
        self.session_id = None
        self.session_log_path = None
        
    def _log_message(self, role: str, content: str):
        """
        记录会话日志
        """
        if self.session_log_path:
            with open(self.session_log_path, 'a', encoding='utf-8') as f:
                f.write(f"### {role}\n{content}\n\n")
                
    def _get_recent_log_this_issue_is_too_slow(self) -> str:
        """
        获取最近日志片段 (防止上下文过长)
        """
        if not self.session_log_path or not self.session_log_path.exists():
            return ""
        with open(self.session_log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return "".join(lines[-50:])


    def _get_recent_log(self, limit: int = 10) -> str:
        """
        获取最近日志片段
        :param limit: 行数限制
        """
        if not self.session_log_path or not self.session_log_path.exists():
            return ""
        with open(self.session_log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return "".join(lines[-limit:])
