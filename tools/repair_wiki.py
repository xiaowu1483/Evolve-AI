# 修复工具，自动修正 Markdown 格式
# tools/repair_wiki.py

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

class WikiRepairer:
    """
    Wiki 修复器
    自动修复常见的 Markdown 格式错误
    确保 AI 生成的文档格式正确
    """
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.wiki_path = self.root_path / 'wiki'
        
    def scan_for_issues(self) -> List[Dict]:
        """
        扫描 Wiki 中的格式问题
        :return: 问题列表
        """
        issues = []
        
        if not self.wiki_path.exists():
            return issues
            
        for md_file in self.wiki_path.rglob("*.md"):
            file_issues = self._check_file(md_file)
            for issue in file_issues:
                issue['file'] = str(md_file.relative_to(self.wiki_path))
            issues.extend(file_issues)
            
        return issues
        
    def _check_file(self, file_path: Path) -> List[Dict]:
        """
        检查单个文件的格式问题
        :param file_path: Markdown 文件路径
        :return: 问题列表
        """
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception:
            return issues
            
        # 检查 1: 未闭合的代码块
        code_block_count = content.count('```')
        if code_block_count % 2 != 0:
            issues.append({
                'type': 'unclosed_code_block',
                'description': '未闭合的代码块 (```数量为奇数)',
                'line': 0
            })
            
        # 检查 2: 标题层级跳跃 (如# 直接到###)
        prev_level = 0
        for i, line in enumerate(lines):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                if prev_level > 0 and level > prev_level + 1:
                    issues.append({
                        'type': 'heading_skip',
                        'description': f'标题层级跳跃 (从{prev_level}级到{level}级)',
                        'line': i + 1
                    })
                prev_level = level
                
        # 检查 3: 空文件
        if len(content.strip()) == 0:
            issues.append({
                'type': 'empty_file',
                'description': '文件为空',
                'line': 0
            })
            
        return issues
        
    def auto_repair(self, issues: List[Dict]) -> int:
        """
        自动修复可修复的问题
        :param issues: 问题列表
        :return: 修复数量
        """
        repaired = 0
        
        for issue in issues:
            if issue['type'] == 'unclosed_code_block':
                if self._fix_unclosed_code_block(issue['file']):
                    repaired += 1
            elif issue['type'] == 'empty_file':
                if self._fix_empty_file(issue['file']):
                    repaired += 1
                    
        return repaired
        
    def _fix_unclosed_code_block(self, relative_path: str) -> bool:
        """
        修复未闭合的代码块
        :param relative_path: 相对于 wiki 目录的路径
        :return: 是否成功
        """
        file_path = self.wiki_path / relative_path
        if not file_path.exists():
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 如果 ``` 数量为奇数，在末尾添加 ```
            if content.count('```') % 2 != 0:
                content += '\n```\n'
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
        except Exception:
            pass
            
        return False
        
    def _fix_empty_file(self, relative_path: str) -> bool:
        """
        修复空文件 (添加占位内容)
        :param relative_path: 相对于 wiki 目录的路径
        :return: 是否成功
        """
        file_path = self.wiki_path / relative_path
        if not file_path.exists():
            return False
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {file_path.stem}\n\n> 此文件由系统自动创建，请补充内容。\n")
            return True
        except Exception:
            pass
            
        return False
        
    def run_full_repair(self) -> Dict:
        """
        执行完整修复流程
        :return: 修复报告
        """
        issues = self.scan_for_issues()
        repaired = self.auto_repair(issues)
        
        return {
            'total_issues': len(issues),
            'repaired': repaired,
            'remaining': len(issues) - repaired,
            'issues': issues
        }
