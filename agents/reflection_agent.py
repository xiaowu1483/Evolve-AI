# 反思代理，对话后生成摘要并更新 Wiki
# TODO: Implement logic here
# agents/reflection_agent.py

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List  # 确保 Any 已导入
import json

from src.core.wiki_manager import WikiManager
from src.core.security import SecurityManager
from src.utils.logger import get_logger
from src.utils.text_processors import truncate_text

logger = get_logger("ReflectionAgent")



class ReflectionAgent:
    """
    反思代理 (The "Dreamer")
    在会话结束后运行，读取原始日志，提取知识，更新 Wiki
    核心逻辑：对话 -> 摘要 -> 记忆固化
    """
    
    def __init__(self, root_path: str, llm_client: Any, wiki_manager: WikiManager):
        self.root_path = Path(root_path)
        self.llm = llm_client
        self.wiki = wiki_manager
        self.session_id = None
        
    def run(self, session_id: str, log_path: str):
        """
        执行反思流程
        :param session_id: 会话 ID
        :param log_path: 原始日志路径 (runtime/active_session/raw_log.md 或归档路径)
        """
        self.session_id = session_id
        logger.info(f"Starting reflection for session {session_id}")
        
        try:
            # 1. 读取原始对话
            raw_log = self._read_log(log_path)
            if not raw_log:
                logger.warning("Empty log, skipping reflection")
                return
                
            # 2. 读取当前记忆上下文 (避免冲突)
            current_memory = self.wiki.read_file("04_LongTerm_Memory/User_Profile.md")
            
            # 3. 调用 LLM 进行反思分析
            reflection_result = self._analyze_conversation(raw_log, current_memory)
            
            # 4. 生成反思日志 (梦境记录)
            self._save_reflection_log(reflection_result)
            
            # 5. 更新长期记忆 (记忆固化)
            self._update_long_term_memory(reflection_result)
            
            # 6. 更新模块文档 (如果涉及代码变更)
            if reflection_result.get('code_changes'):
                self._update_module_docs(reflection_result)
                
            logger.info(f"Reflection completed for session {session_id}")
            
        except Exception as e:
            logger.error(f"Reflection failed: {e}")
            # 失败不影响主程序，只记录错误
            
    def _read_log(self, log_path: str) -> str:
        """读取日志文件"""
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""
            
    def _analyze_conversation(self, raw_log: str, current_memory: str) -> Dict:
        """
        调用 LLM 分析对话
        :return: 结构化反思结果
        """
        # 截断日志以防 Token 溢出 (只取最近部分进行反思，或分段)
        safe_log = truncate_text(raw_log, max_tokens=8000) 
        
        prompt = f"""
        你是一个记忆管理员。请分析以下对话日志，提取需要固化的知识。
        
        当前用户记忆：
        {current_memory}
        
        本次对话日志：
        {safe_log}
        
        请返回 JSON 格式：
        {{
            "summary": "本次对话的简短摘要 (100 字以内)",
            "new_preferences": ["用户新偏好 1", "用户新偏好 2"],
            "code_changes": ["修改了哪个模块", "修复了什么 bug"],
            "decisions": ["做出的重要决定"],
            "confidence": 0.9 (0-1 之间，表示提取信息的可信度)
        }}
        """
        
        response = self.llm.generate(prompt)
        try:
            # 尝试解析 JSON，处理可能的 Markdown 代码块标记
            clean_response = response.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_response)
        except json.JSONDecodeError:
            logger.error("Failed to parse reflection JSON")
            return {
                "summary": response,
                "new_preferences": [],
                "code_changes": [],
                "decisions": [],
                "confidence": 0.5
            }
            
    def _save_reflection_log(self, result: Dict):
        """
        保存反思摘要到 wiki/05_Reflection_Logs/
        """
        date_folder = datetime.now().strftime("%Y-%m")
        filename = f"{self.session_id}_Summary.md"
        relative_path = f"05_Reflection_Logs/{date_folder}/{filename}"
        
        content = f"""# Session Reflection: {self.session_id}

## 时间
{datetime.now().isoformat()}

## 摘要
{result.get('summary', 'No summary')}

## 提取偏好
{chr(10).join('- ' + p for p in result.get('new_preferences', []))}

## 代码变更
{chr(10).join('- ' + c for c in result.get('code_changes', []))}

## 置信度
{result.get('confidence', 0)}
"""
        self.wiki.write_file(relative_path, content, author="ReflectionAgent")
        
    def _update_long_term_memory(self, result: Dict):
        """
        更新用户画像 (仅当置信度高时)
        """
        if result.get('confidence', 0) < 0.7:
            logger.info("Confidence too low, skipping memory update")
            return
            
        preferences = result.get('new_preferences', [])
        if not preferences:
            return
            
        # 读取现有文件
        current_content = self.wiki.read_file("04_LongTerm_Memory/User_Profile.md")
        
        # 简单追加逻辑 (实际应由 Consolidator 处理冲突，此处为简化演示)
        # 在实际生产中，应调用 Consolidator 来处理这里
        new_section = "\n## 最新更新\n"
        for pref in preferences:
            new_section += f"- {pref} [来源：Session {self.session_id}]\n"
            
        self.wiki.write_file("04_LongTerm_Memory/User_Profile.md", current_content + new_section, author="ReflectionAgent")
        
    def _update_module_docs(self, result: Dict):
        """
        如果对话涉及代码修改，提示更新模块文档
        此处仅记录日志，具体同步由 tools/sync_wiki.py 或 MaintenanceAgent 处理
        """
        logger.info(f"Code changes detected: {result.get('code_changes')}")
        # 可以在 wiki/02_Modules/Module_Registry.md 中标记待更新
