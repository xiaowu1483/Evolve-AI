# 日志轮转工具，压缩或删除旧日志
# TODO: Implement logic here
# tools/log_rotator.py

import os
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
import yaml

class LogRotator:
    """
    日志轮转器
    根据 retention.yaml 配置自动压缩或删除旧日志
    防止日志占用过多空间
    """
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.config_path = self.root_path / 'config' / 'retention.yaml'
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """
        加载保留策略配置
        :return: 配置字典
        """
        default_config = {
            'retention_policy': {
                'raw_archives': {
                    'keep_days': 30,
                    'compress_after_days': 7,
                    'delete_after_days': 90
                },
                'reflection_logs': {
                    'keep_forever': True,
                    'compress_after_months': 6
                },
                'safety_check': {
                    'require_summary': True,
                    'backup_before_delete': True
                }
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception:
                pass
                
        return default_config
        
    def rotate_raw_archives(self) -> Dict:
        """
        轮转原始归档日志
        :return: 操作报告
        """
        policy = self.config['retention_policy']['raw_archives']
        archives_path = self.root_path / 'wiki' / '06_Raw_Archives'
        
        report = {
            'compressed': 0,
            'deleted': 0,
            'skipped': 0
        }
        
        if not archives_path.exists():
            return report
            
        cutoff_compress = datetime.now() - timedelta(days=policy['compress_after_days'])
        cutoff_delete = datetime.now() - timedelta(days=policy['delete_after_days'])
        
        for month_folder in archives_path.iterdir():
            if month_folder.is_dir():
                for log_file in month_folder.glob("*"):
                    if log_file.is_file():
                        file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                        
                        # 删除检查
                        if file_mtime < cutoff_delete:
                            if self._safe_delete(log_file):
                                report['deleted'] += 1
                            else:
                                report['skipped'] += 1
                        # 压缩检查
                        elif file_mtime < cutoff_compress and not log_file.name.endswith('.gz'):
                            if self._compress_file(log_file):
                                report['compressed'] += 1
                                
        return report
        
    def rotate_reflection_logs(self) -> Dict:
        """
        轮转反思日志
        :return: 操作报告
        """
        policy = self.config['retention_policy']['reflection_logs']
        logs_path = self.root_path / 'wiki' / '05_Reflection_Logs'
        
        report = {
            'compressed': 0,
            'deleted': 0
        }
        
        if not logs_path.exists() or policy.get('keep_forever', True):
            return report
            
        # 反思日志通常只压缩不删除
        cutoff_compress = datetime.now() - timedelta(days=policy['compress_after_months'] * 30)
        
        for month_folder in logs_path.iterdir():
            if month_folder.is_dir():
                for log_file in month_folder.glob("*.md"):
                    if log_file.stat().st_mtime < cutoff_compress and not log_file.name.endswith('.gz'):
                        if self._compress_file(log_file):
                            report['compressed'] += 1
                            
        return report
        
    def _compress_file(self, file_path: Path) -> bool:
        """
        压缩文件为 gzip
        :param file_path: 原文件路径
        :return: 是否成功
        """
        try:
            gz_path = file_path.with_suffix(file_path.suffix + '.gz')
            with open(file_path, 'rb') as f_in:
                with gzip.open(gz_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            file_path.unlink() # 删除原文件
            return True
        except Exception as e:
            print(f"Compression failed for {file_path}: {e}")
            return False
            
    def _safe_delete(self, file_path: Path) -> bool:
        """
        安全删除文件 (检查是否有对应反思摘要)
        :param file_path: 待删除文件
        :return: 是否成功删除
        """
        safety = self.config['retention_policy']['safety_check']
        
        # 检查是否需要反思摘要
        if safety.get('require_summary', True):
            session_id = file_path.stem.split('_')[0]
            reflection_path = self.root_path / 'wiki' / '05_Reflection_Logs'
            # 简单检查：是否存在包含 session_id 的反思文件
            has_summary = any(session_id in f.name for f in reflection_path.rglob("*.md"))
            if not has_summary:
                print(f"Skip delete (no summary): {file_path}")
                return False
                
        # 删除前备份
        if safety.get('backup_before_delete', True):
            from .backup import BackupManager
            backup_mgr = BackupManager(str(self.root_path))
            backup_mgr.create_backup(str(file_path.relative_to(self.root_path)), reason="before_delete")
            
        try:
            file_path.unlink()
            return True
        except Exception as e:
            print(f"Delete failed for {file_path}: {e}")
            return False
            
    def run_full_rotation(self) -> Dict:
        """
        执行完整日志轮转
        :return: 综合报告
        """
        raw_report = self.rotate_raw_archives()
        reflection_report = self.rotate_reflection_logs()
        
        return {
            'raw_archives': raw_report,
            'reflection_logs': reflection_report,
            'total_compressed': raw_report['compressed'] + reflection_report['compressed'],
            'total_deleted': raw_report['deleted'] + reflection_report['deleted']
        }
