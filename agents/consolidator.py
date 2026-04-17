# 记忆固化器，合并碎片记忆解决冲突
# TODO: Implement logic here
# agents/consolidator.py

import os
from pathlib import Path
from typing import List, Dict, Any  # 修复：添加 Any 导入
from datetime import datetime

from src.core.wiki_manager import WikiManager
from src.utils.logger import get_logger
from src.utils.text_processors import extract_markdown_links

logger = get_logger("MemoryConsolidator")

class MemoryConsolidator:
    """
    记忆固化器
    定期扫描反思日志，合并碎片化记忆，解决冲突
    防止 User_Profile.md 无限膨胀或出现矛盾
    """
    
    def __init__(self, root_path: str, llm_client: Any, wiki_manager: WikiManager):
        self.root_path = Path(root_path)
        self.llm = llm_client
        self.wiki = wiki_manager
        
    def run_consolidation(self):
        """
        执行记忆固化流程
        """
        logger.info("Starting memory consolidation...")
        
        try:
            # 1. 获取所有反思日志
            reflection_logs = self._scan_reflection_logs()
            
            # 2. 获取当前用户画像
            current_profile = self.wiki.read_file("04_LongTerm_Memory/User_Profile.md")
            
            # 3. 调用 LLM 合并记忆
            new_profile = self._merge_memories(reflection_logs, current_profile)
            
            # 4. 写入更新后的画像
            if new_profile != current_profile:
                self.wiki.write_file("04_LongTerm_Memory/User_Profile.md", new_profile, author="Consolidator")
                logger.info("Memory consolidated successfully")
            else:
                logger.info("No memory changes needed")
                
        except Exception as e:
            logger.error(f"Consolidation failed: {e}")
            
    def _scan_reflection_logs(self) -> List[str]:
        """
        扫描最近的反思日志 (例如最近 10 篇)
        :return: 日志内容列表
        """
        logs_path = self.root_path / 'wiki' / '05_Reflection_Logs'
        recent_logs = []
        
        if not logs_path.exists():
            return recent_logs
            
        # 简单扫描所有子目录下的 md 文件
        # 实际应按时间排序取最近 N 个
        count = 0
        for month_folder in logs_path.iterdir():
            if month_folder.is_dir():
                for log_file in month_folder.glob("*.md"):
                    with open(log_file, 'r', encoding='utf-8') as f:
                        recent_logs.append(f.read())
                    count += 1
                    if count >= 10: # 只处理最近 10 篇
                        break
            if count >= 10:
                break
                
        return recent_logs
        
    def _merge_memories(self, logs: List[str], current_profile: str) -> str:
        """
        调用 LLM 合并记忆
        :param logs: 反思日志列表
        :param current_profile: 当前画像
        :return: 新画像内容
        """
        logs_content = "\n---\n".join(logs)
        
        prompt = f"""
        你是记忆管理员。请整合以下反思日志到用户画像中。
        规则：
        1. 如果有冲突 (如喜欢红色 vs 喜欢蓝色)，以最新的为准。
        2. 移除重复信息。
        3. 保持格式简洁。
        
        当前画像：
        {current_profile}
        
        新反思日志：
        {logs_content}
        
        请输出完整的更新后的 User_Profile.md 内容。
        """
        
        response = self.llm.generate(prompt)
        return response.strip()
        
    def resolve_conflicts(self, conflict_list: List[Dict]):
        """
        手动解决特定冲突 (可选功能)
        :param conflict_list: 冲突项列表
        """
        # 预留接口，可用于人工介入或更复杂的逻辑
        pass
