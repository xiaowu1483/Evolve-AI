# 维护代理，定期扫描 Wiki 一致性
# TODO: Implement logic here
# agents/maintenance_agent.py

import os
from pathlib import Path
from datetime import datetime
from typing import List, Any  # 确保 Any 已导入

from src.core.wiki_manager import WikiManager
from src.utils.logger import get_logger
from src.utils.file_helpers import safe_read

logger = get_logger("MaintenanceAgent")

class MaintenanceAgent:
    """
    维护代理
    定期扫描系统健康状态，检查链接、同步代码与文档、清理日志
    通常在系统空闲时运行
    """
    
    def __init__(self, root_path: str, wiki_manager: WikiManager):
        self.root_path = Path(root_path)
        self.wiki = wiki_manager
        self.report_path = self.root_path / 'runtime' / 'maintenance_report.md'
        
    def run_full_check(self):
        """
        执行完整维护检查
        """
        logger.info("Starting maintenance check...")
        report = []
        
        # 1. 检查 Wiki 链接有效性
        link_issues = self._check_wiki_links()
        if link_issues:
            report.append("## 链接问题\n" + "\n".join(link_issues))
            
        # 2. 检查代码与文档同步
        sync_issues = self._check_code_doc_sync()
        if sync_issues:
            report.append("## 同步问题\n" + "\n".join(sync_issues))
            
        # 3. 检查日志保留策略 (调用 tools 逻辑的简化版)
        log_issues = self._check_log_retention()
        if log_issues:
            report.append("## 日志清理\n" + "\n".join(log_issues))
            
        # 4. 生成报告
        if not report:
            report.append("## 状态\n系统健康，无问题。")
            
        final_report = f"# 维护报告\n时间：{datetime.now().isoformat()}\n\n" + "\n".join(report)
        
        # 保存报告
        try:
            self.report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.report_path, 'w', encoding='utf-8') as f:
                f.write(final_report)
            logger.info("Maintenance check completed")
        except Exception as e:
            logger.error(f"Failed to write report: {e}")
            
    def _check_wiki_links(self) -> List[str]:
        """
        扫描 Wiki 中的死链
        :return: 问题列表
        """
        issues = []
        wiki_path = self.root_path / 'wiki'
        # 简单实现：遍历所有 md 文件，检查 []() 链接是否存在
        # 实际应使用 tools/validate_links.py 的逻辑
        # 此处仅做示意
        issues.append("- 链接检查需调用 tools/validate_links.py (此处为占位)")
        return issues
        
    def _check_code_doc_sync(self) -> List[str]:
        """
        检查 src/modules 是否有新模块但 Wiki 未更新
        :return: 问题列表
        """
        issues = []
        modules_path = self.root_path / 'src' / 'modules'
        wiki_modules_path = self.root_path / 'wiki' / '02_Modules'
        
        if not modules_path.exists():
            return issues
            
        # 扫描模块目录
        for item in modules_path.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                # 检查 Wiki 中是否有对应文档
                doc_name = f"{item.name}.md" # 假设命名规范
                # 注意：实际应读取 Module_Registry.md 或 _Index.md
                # 此处简化逻辑
                pass
                
        issues.append("- 代码文档同步需读取 Module_Registry.md 比对 (此处为占位)")
        return issues
        
    def _check_log_retention(self) -> List[str]:
        """
        检查日志是否超出保留策略
        :return: 问题列表
        """
        issues = []
        # 实际应调用 tools/log_rotator.py
        issues.append("- 日志轮转需调用 tools/log_rotator.py (此处为占位)")
        return issues
        
    def auto_fix(self, issue_type: str):
        """
        尝试自动修复特定问题
        :param issue_type: 问题类型
        """
        logger.info(f"Attempting auto fix for {issue_type}")
        # 预留接口，可调用 tools 中的修复脚本
