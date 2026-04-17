# config/config_loader.py

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from src.utils.logger import get_logger

logger = get_logger("ConfigLoader")

class ConfigLoader:
    """
    配置加载器
    负责加载、验证和合并配置文件
    支持环境变量覆盖配置值
    """
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.config_dir = self.root_path / 'config'
        self.cache = {}
        
    def load_yaml(self, filename: str, required: bool = True) -> Dict:
        """
        加载 YAML 配置文件
        :param filename: 文件名 (如 'system.yaml')
        :param required: 是否必须存在
        :return: 配置字典
        """
        file_path = self.config_dir / filename
        
        if not file_path.exists():
            if required:
                logger.warning(f"Config file {filename} not found, using defaults")
                return {}
            else:
                return {}
                
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            logger.info(f"Loaded config: {filename}")
            return config
        except Exception as e:
            logger.error(f"Failed to load {filename}: {e}")
            return {}
            
    def load_all(self) -> Dict[str, Dict]:
        """
        加载所有配置文件
        :return: 包含所有配置的字典
        """
        configs = {
            'system': self.load_yaml('system.yaml'),
            'ai_profile': self.load_yaml('ai_profile.yaml'),
            'retention': self.load_yaml('retention.yaml')
        }
        return configs
        
    def get_system_config(self) -> Dict:
        """获取系统配置"""
        if 'system' not in self.cache:
            self.cache['system'] = self.load_yaml('system.yaml')
        return self.cache['system']
        
    def get_ai_profile(self) -> Dict:
        """获取 AI 人设配置"""
        if 'ai_profile' not in self.cache:
            self.cache['ai_profile'] = self.load_yaml('ai_profile.yaml')
        return self.cache['ai_profile']
        
    def get_retention_policy(self) -> Dict:
        """获取日志保留策略"""
        if 'retention' not in self.cache:
            self.cache['retention'] = self.load_yaml('retention.yaml')
        return self.cache['retention']
        
    def validate_config(self, config_type: str, config_data: Dict) -> bool:
        """
        简单验证配置合法性
        :param config_type: 配置类型
        :param config_data: 配置数据
        :return: 是否合法
        """
        # 此处可扩展加载 JSON Schema 进行严格验证
        if config_type == 'system':
            required_keys = ['llm', 'security_level']
            for key in required_keys:
                if key not in config_data:
                    logger.warning(f"Missing key {key} in system config")
        return True
        
    def save_config(self, filename: str, config_data: Dict) -> bool:
        """
        保存配置 (需谨慎使用，防止 AI 误改)
        :param filename: 文件名
        :param config_data: 配置数据
        :return: 是否成功
        """
        # 安全检查：禁止修改某些关键配置
        if filename == 'system.yaml' and 'security_level' in config_data:
            logger.error("Attempt to modify security_level blocked")
            return False
            
        file_path = self.config_dir / filename
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)
            logger.info(f"Config saved: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save {filename}: {e}")
            return False
