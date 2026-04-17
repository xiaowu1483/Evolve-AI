# 备份工具，修改前自动快照
# TODO: Implement logic here
# tools/backup.py

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional

class BackupManager:
    """
    备份管理器
    在 AI 修改关键文件前自动创建快照，支持回滚
    """
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.backup_dir = self.root_path / 'data' / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def create_backup(self, file_path: str, reason: str = "manual") -> Optional[str]:
        """
        创建单个文件备份
        :param file_path: 相对于根目录的文件路径
        :param reason: 备份原因
        :return: 备份文件路径，失败返回 None
        """
        source = self.root_path / file_path
        if not source.exists():
            return None
            
        # 生成备份文件名：原文件名.时间戳.原因.bak
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = file_path.replace('/', '_').replace('\\', '_')
        backup_name = f"{safe_name}.{timestamp}.{reason}.bak"
        backup_path = self.backup_dir / backup_name
        
        try:
            # 确保备份目录存在
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            # 复制文件
            shutil.copy2(source, backup_path)
            return str(backup_path)
        except Exception as e:
            print(f"Backup failed for {file_path}: {e}")
            return None
            
    def create_directory_backup(self, dir_path: str, reason: str = "manual") -> Optional[str]:
        """
        创建整个目录的备份
        :param dir_path: 相对于根目录的目录路径
        :param reason: 备份原因
        :return: 备份目录路径
        """
        source = self.root_path / dir_path
        if not source.exists() or not source.is_dir():
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = dir_path.replace('/', '_').replace('\\', '_')
        backup_name = f"{safe_name}.{timestamp}.{reason}"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copytree(source, backup_path)
            return str(backup_path)
        except Exception as e:
            print(f"Directory backup failed for {dir_path}: {e}")
            return None
            
    def list_backups(self, file_pattern: str = "*") -> List[str]:
        """
        列出备份文件
        :param file_pattern: 文件名匹配模式
        :return: 备份文件路径列表
        """
        backups = []
        for backup in self.backup_dir.glob(file_pattern):
            backups.append(str(backup))
        return sorted(backups, reverse=True) # 最新的在前
        
    def restore_backup(self, backup_path: str, target_path: str = None) -> bool:
        """
        从备份恢复文件
        :param backup_path: 备份文件路径
        :param target_path: 恢复目标路径 (默认恢复原位置)
        :return: 是否成功
        """
        backup = Path(backup_path)
        if not backup.exists():
            return False
            
        # 解析原路径 (从备份文件名推断)
        if target_path is None:
            # 备份名格式：path_to_file.timestamp.reason.bak
            parts = backup.stem.split('.')
            if len(parts) >= 3:
                original_name = '.'.join(parts[:-2]) # 去掉时间戳和原因
                target_path = original_name.replace('_', '/')
            else:
                return False
                
        target = self.root_path / target_path
        
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup, target)
            return True
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
            
    def cleanup_old_backups(self, keep_days: int = 30) -> int:
        """
        清理旧备份
        :param keep_days: 保留天数
        :return: 删除的文件数量
        """
        deleted = 0
        cutoff = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        
        for backup in self.backup_dir.glob("*.bak"):
            if backup.stat().st_mtime < cutoff:
                try:
                    backup.unlink()
                    deleted += 1
                except Exception:
                    pass
                    
        return deleted
