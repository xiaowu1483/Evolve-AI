# 链接检查，扫描 Wiki 死链
# TODO: Implement logic here
# tools/validate_links.py

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

class LinkValidator:
    """
    链接验证器
    扫描 Wiki 中的 Markdown 链接，检查是否指向存在的文件
    防止 AI 生成死链
    """
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.wiki_path = self.root_path / 'wiki'
        self.markdown_link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        
    def scan_all_links(self) -> List[Dict]:
        """
        扫描所有 Wiki 文件中的链接
        :return: 链接信息列表
        """
        all_links = []
        
        if not self.wiki_path.exists():
            return all_links
            
        for md_file in self.wiki_path.rglob("*.md"):
            links = self._extract_links_from_file(md_file)
            for link in links:
                link['source_file'] = str(md_file.relative_to(self.wiki_path))
            all_links.extend(links)
            
        return all_links
        
    def _extract_links_from_file(self, file_path: Path) -> List[Dict]:
        """
        从单个文件提取链接
        :param file_path: Markdown 文件路径
        :return: 链接列表
        """
        links = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return links
            
        matches = self.markdown_link_pattern.findall(content)
        for text, path in matches:
            # 跳过外部链接
            if path.startswith('http://') or path.startswith('https://'):
                continue
            links.append({
                'text': text,
                'path': path,
                'line': content[:content.find(f'[{text}]({path})')].count('\n') + 1
            })
            
        return links
        
    def validate_links(self, links: List[Dict]) -> List[Dict]:
        """
        验证链接是否有效
        :param links: 链接列表
        :return: 无效链接列表
        """
        invalid_links = []
        
        for link in links:
            target_path = self._resolve_link_path(link['path'], link.get('source_file', ''))
            if not self._check_path_exists(target_path):
                invalid_links.append(link)
                
        return invalid_links
        
    def _resolve_link_path(self, link_path: str, source_file: str) -> Path:
        """
        解析链接的绝对路径
        :param link_path: 链接中的路径
        :param source_file: 源文件路径 (用于相对路径解析)
        :return: 绝对路径
        """
        if link_path.startswith('/'):
            # 绝对路径 (相对于 wiki 根目录)
            return self.wiki_path / link_path.lstrip('/')
        else:
            # 相对路径 (相对于源文件所在目录)
            if source_file:
                source_dir = (self.wiki_path / source_file).parent
                return (source_dir / link_path).resolve()
            else:
                return self.wiki_path / link_path
                
    def _check_path_exists(self, path: Path) -> bool:
        """
        检查路径是否存在 (文件或目录)
        :param path: 待检查路径
        :return: 是否存在
        """
        # 处理带锚点的链接 (如 file.md#section)
        clean_path = str(path).split('#')[0]
        return Path(clean_path).exists()
        
    def run_validation(self) -> Dict:
        """
        执行完整验证流程
        :return: 验证报告
        """
        all_links = self.scan_all_links()
        invalid_links = self.validate_links(all_links)
        
        return {
            'total_links': len(all_links),
            'valid_links': len(all_links) - len(invalid_links),
            'invalid_links': invalid_links,
            'health_rate': (len(all_links) - len(invalid_links)) / max(len(all_links), 1)
        }
        
    def generate_report(self) -> str:
        """
        生成验证报告 (Markdown 格式)
        :return: 报告内容
        """
        result = self.run_validation()
        
        report = f"# Wiki 链接验证报告\n\n"
        report += f"- 总链接数：{result['total_links']}\n"
        report += f"- 有效链接：{result['valid_links']}\n"
        report += f"- 无效链接：{len(result['invalid_links'])}\n"
        report += f"- 健康度：{result['health_rate']:.2%}\n\n"
        
        if result['invalid_links']:
            report += "## 无效链接列表\n\n"
            for link in result['invalid_links'][:20]: # 最多显示 20 个
                report += f"- `{link['path']}` in `{link['source_file']}` (第{link['line']}行)\n"
                
        return report
