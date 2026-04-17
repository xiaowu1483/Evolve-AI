# 审计工具，确保删除前有摘要
# TODO: Implement logic here
# tools/audit_trail.py

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class AuditTrailer:
    """
    审计追踪器
    记录所有 Wiki 和代码的变更历史，确保可追溯
    用于验证 AI 操作的合规性
    """
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.audit_path = self.root_path / 'data' / 'audit_trail.json'
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        self.trail = self._load_trail()
        
    def _load_trail(self) -> List[Dict]:
        """
        加载审计日志
        :return: 审计记录列表
        """
        if self.audit_path.exists():
            try:
                with open(self.audit_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []
        
    def _save_trail(self):
        """保存审计日志"""
        try:
            with open(self.audit_path, 'w', encoding='utf-8') as f:
                json.dump(self.trail, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save audit trail: {e}")
            
    def record_change(self, action: str, path: str, details: Dict = None):
        """
        记录变更
        :param action: 操作类型 (create, update, delete)
        :param path: 变更文件路径
        :param details: 详细信息
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'path': path,
            'details': details or {},
            'agent': details.get('agent', 'unknown') if details else 'unknown'
        }
        self.trail.append(record)
        self._save_trail()
        
    def record_reflection(self, session_id: str, summary: str, changes: List[str]):
        """
        记录反思操作
        :param session_id: 会话 ID
        :param summary: 反思摘要
        :param changes: 变更列表
        """
        self.record_change(
            action='reflection',
            path=f'wiki/05_Reflection_Logs/{session_id}',
            details={
                'session_id': session_id,
                'summary': summary[:200], # 截断避免过大
                'changes': changes,
                'agent': 'ReflectionAgent'
            }
        )
        
    def record_memory_update(self, memory_type: str, content_hash: str, changes: List[str]):
        """
        记录记忆更新
        :param memory_type: 记忆类型 (User_Profile, Preferences 等)
        :param content_hash: 内容哈希 (用于验证)
        :param changes: 变更描述
        """
        self.record_change(
            action='memory_update',
            path=f'wiki/04_LongTerm_Memory/{memory_type}',
            details={
                'memory_type': memory_type,
                'content_hash': content_hash,
                'changes': changes,
                'agent': 'MemoryConsolidator'
            }
        )
        
    def get_recent_changes(self, limit: int = 50) -> List[Dict]:
        """
        获取最近的变更记录
        :param limit: 返回数量限制
        :return: 变更记录列表
        """
        return self.trail[-limit:]
        
    def search_changes(self, keyword: str) -> List[Dict]:
        """
        搜索变更记录
        :param keyword: 搜索关键词
        :return: 匹配的记录
        """
        matches = []
        for record in self.trail:
            if keyword.lower() in record['path'].lower():
                matches.append(record)
            elif keyword.lower() in str(record.get('details', {})).lower():
                matches.append(record)
        return matches
        
    def generate_report(self, days: int = 7) -> str:
        """
        生成审计报告
        :param days: 最近多少天
        :return: 报告内容 (Markdown)
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent = [r for r in self.trail if datetime.fromisoformat(r['timestamp']) > cutoff]
        
        report = f"# 审计报告 (最近{days}天)\n\n"
        report += f"总操作数：{len(recent)}\n\n"
        
        # 按操作类型统计
        by_action = {}
        for r in recent:
            action = r['action']
            by_action[action] = by_action.get(action, 0) + 1
            
        report += "## 操作统计\n\n"
        for action, count in by_action.items():
            report += f"- {action}: {count}\n"
            
        report += "\n## 最近操作\n\n"
        for r in recent[-20:]: # 显示最近 20 条
            report += f"- [{r['timestamp']}] {r['action']}: `{r['path']}`\n"
            
        return report
        
    def verify_integrity(self) -> Dict:
        """
        验证审计日志完整性
        :return: 验证结果
        """
        # 简单验证：检查是否有连续记录
        issues = []
        
        if len(self.trail) == 0:
            issues.append("审计日志为空")
            
        # 检查时间戳是否连续 (无未来时间)
        now = datetime.now()
        for r in self.trail:
            try:
                ts = datetime.fromisoformat(r['timestamp'])
                if ts > now:
                    issues.append(f"未来时间戳：{r['timestamp']}")
            except Exception:
                issues.append(f"无效时间戳：{r['timestamp']}")
                
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'total_records': len(self.trail)
        }
