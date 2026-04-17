# 同步工具，确保代码与文档一致
# TODO: Implement logic here
# tools/sync_wiki.py

import os
import yaml
from pathlib import Path
from typing import List, Dict
from datetime import datetime

class WikiSynchronizer:
    """
    Wiki 同步器
    确保 src/modules 中的代码与 wiki/02_Modules 中的文档保持一致
    强制落实"代码即文档"原则
    """
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.src_modules_path = self.root_path / 'src' / 'modules'
        self.wiki_modules_path = self.root_path / 'wiki' / '02_Modules'
        self.registry_path = self.wiki_modules_path / 'Module_Registry.md'
        
    def scan_code_modules(self) -> List[Dict]:
        """
        扫描代码中的模块
        :return: 模块信息列表
        """
        modules = []
        
        if not self.src_modules_path.exists():
            return modules
            
        for item in self.src_modules_path.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                config_file = item / 'config.yaml'
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = yaml.safe_load(f)
                        modules.append({
                            'name': item.name,
                            'config': config,
                            'path': str(item.relative_to(self.root_path))
                        })
                    except Exception:
                        pass
                        
        return modules
        
    def scan_wiki_modules(self) -> List[str]:
        """
        扫描 Wiki 中的模块文档
        :return: 文档名称列表
        """
        docs = []
        
        if not self.wiki_modules_path.exists():
            return docs
            
        for md_file in self.wiki_modules_path.glob("*.md"):
            if md_file.name not in ['_Index.md', 'Template.md', 'Module_Registry.md']:
                docs.append(md_file.stem) # 去掉.md 后缀
                
        return docs
        
    def find_discrepancies(self) -> Dict:
        """
        查找代码与文档的不一致
        :return: 差异报告
        """
        code_modules = [m['name'] for m in self.scan_code_modules()]
        wiki_docs = self.scan_wiki_modules()
        
        # 代码有但 Wiki 没有
        missing_docs = [m for m in code_modules if m not in wiki_docs]
        
        # Wiki 有但代码没有 (可能是旧文档)
        orphan_docs = [d for d in wiki_docs if d not in code_modules]
        
        return {
            'code_modules': code_modules,
            'wiki_docs': wiki_docs,
            'missing_docs': missing_docs,
            'orphan_docs': orphan_docs,
            'synced': len(code_modules) - len(missing_docs)
        }
        
    def generate_registry(self) -> str:
        """
        生成模块注册表 (Module_Registry.md)
        :return: 注册表内容
        """
        modules = self.scan_code_modules()
        
        content = "# 模块注册表\n\n"
        content += f"最后更新：{datetime.now().isoformat()}\n\n"
        content += "## 已注册模块\n\n"
        content += "| 模块名 | 版本 | 描述 | 触发词 |\n"
        content += "|--------|------|------|--------|\n"
        
        for mod in modules:
            config = mod.get('config', {})
            name = config.get('name', mod['name'])
            version = config.get('version', '1.0.0')
            desc = config.get('description', '无描述')
            triggers = ', '.join(config.get('triggers', []))
            content += f"| {name} | {version} | {desc} | {triggers} |\n"
            
        return content
        
    def run_sync(self, auto_fix: bool = False) -> Dict:
        """
        执行同步检查
        :param auto_fix: 是否自动创建缺失文档
        :return: 同步结果
        """
        discrepancies = self.find_discrepancies()
        
        # 更新注册表
        registry_content = self.generate_registry()
        self.wiki_modules_path.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            f.write(registry_content)
            
        # 可选：自动创建缺失文档
        created_docs = []
        if auto_fix:
            template_path = self.wiki_modules_path / 'Template.md'
            template_content = ""
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                    
            for mod_name in discrepancies['missing_docs']:
                doc_path = self.wiki_modules_path / f"{mod_name}.md"
                if not doc_path.exists():
                    with open(doc_path, 'w', encoding='utf-8') as f:
                        f.write(template_content.replace('[Module_Name]', mod_name))
                    created_docs.append(mod_name)
                    
        return {
            'discrepancies': discrepancies,
            'auto_created': created_docs,
            'registry_updated': True
        }
