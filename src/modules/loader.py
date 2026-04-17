# src/modules/loader.py

import os
import importlib.util
import yaml
from pathlib import Path
from typing import List, Dict
from .base_module import BaseModule

class ModuleLoader:
    """
    模块加载器
    扫描 modules 目录，动态导入子类，验证配置
    """
    
    def __init__(self):
        self.root_path = Path(__file__).parent
        self.modules: List[BaseModule] = []
        
    def load_all(self) -> List[BaseModule]:
        """
        加载所有子目录中的模块
        :return: 已初始化的模块列表
        """
        # 跳过目录列表
        skip_dirs = ['__pycache__', 'example_skill', 'module_template', '[module_name]']
        
        for item in self.root_path.iterdir():
            if item.is_dir() and not item.name.startswith('_') and item.name not in skip_dirs:
                try:
                    module = self.load_module(item)
                    if module:
                        self.modules.append(module)
                except Exception as e:
                    print(f"Failed to load module {item.name}: {e}")
                    
        return self.modules
        
    def load_module(self, module_path: Path) -> BaseModule:
        """
        加载单个模块
        :param module_path: 模块目录路径
        :return: BaseModule 实例
        """
        # 1. 验证 config.yaml 存在
        config_file = module_path / 'config.yaml'
        if not config_file.exists():
            raise FileNotFoundError(f"config.yaml missing in {module_path}")
            
        # 2. 读取配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # 3. 动态导入 main.py
        spec = importlib.util.spec_from_file_location(
            f"modules.{module_path.name}", 
            module_path / 'main.py'
        )
        if spec and spec.loader:
            module_impl = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module_impl)
            
            # 4. 实例化类 (假设类名为 ModuleImpl)
            if hasattr(module_impl, 'ModuleImpl'):
                instance = module_impl.ModuleImpl()
                # 注入配置信息
                instance.name = config.get('name', module_path.name)
                instance.description = config.get('description', '')
                instance.triggers = config.get('triggers', [])
                instance.version = config.get('version', '1.0.0')
                return instance
            else:
                raise ImportError(f"ModuleImpl class not found in {module_path}/main.py")
        else:
            raise ImportError(f"Cannot load spec for {module_path}")
            
    def get_registry_data(self) -> List[Dict]:
        """
        获取所有模块的注册数据 (用于更新 Wiki 索引)
        :return: 列表形式的模块清单
        """
        return [m.get_manifest() for m in self.modules]
