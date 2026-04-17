# triggers/__init__.py

"""
触发器配置包初始化
提供配置加载和验证功能
"""

import os
import yaml
import json
from pathlib import Path
from typing import List, Dict

class TriggerLoader:
    """
    触发器配置加载器
    读取 triggers/ 目录下的 YAML 文件并验证
    """
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.triggers_dir = self.root_path / 'triggers'
        self.schema_path = self.triggers_dir / 'trigger_schema.json'
        self.schema = self._load_schema()
        
    def _load_schema(self) -> Dict:
        """加载验证 Schema"""
        if self.schema_path.exists():
            try:
                with open(self.schema_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
        
    def load_all(self) -> List[Dict]:
        """
        加载所有启用的触发器配置
        :return: 配置列表
        """
        triggers = []
        
        if not self.triggers_dir.exists():
            return triggers
            
        for yaml_file in self.triggers_dir.glob("*.yaml"):
            if yaml_file.name in ['README.md', 'trigger_schema.json']:
                continue
                
            try:
                config = self._load_single(yaml_file)
                if config and config.get('enabled', True):
                    triggers.append(config)
            except Exception as e:
                print(f"Failed to load trigger {yaml_file.name}: {e}")
                
        # 按优先级排序
        triggers.sort(key=lambda x: x.get('priority', 0), reverse=True)
        return triggers
        
    def _load_single(self, file_path: Path) -> Dict:
        """加载单个配置文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # 简单验证必填字段
        if not config.get('trigger_name') or not config.get('event'):
            raise ValueError(f"Invalid config in {file_path}")
            
        config['_source_file'] = str(file_path)
        return config
        
    def get_triggers_by_event(self, event_type: str) -> List[Dict]:
        """
        根据事件类型获取触发器
        :param event_type: 事件类型 (如 'session_end')
        :return: 匹配的配置列表
        """
        all_triggers = self.load_all()
        return [t for t in all_triggers if t.get('event') == event_type]

__all__ = ['TriggerLoader']
