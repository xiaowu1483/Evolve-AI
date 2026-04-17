# 归档工具，移动原始日志
# tools/migrate_session.py

import os
import gzip
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

class SessionMigrator:
    """
    会话迁移器
    将 runtime/active_session 中的原始日志移动到 wiki/06_Raw_Archives
    支持按月份归档和压缩
    """
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.active_session_path = self.root_path / 'runtime' / 'active_session'
        self.archives_path = self.root_path / 'wiki' / '06_Raw_Archives'
        
    def migrate_session(self, session_id: str) -> Optional[str]:
        """
        迁移单个会话日志到归档
        :param session_id: 会话 ID
        :return: 归档路径，失败返回 None
        """
        source = self.active_session_path / 'raw_log.md'
        if not source.exists():
            return None
            
        # 目标路径：wiki/06_Raw_Archives/YYYY-MM/session_id_raw.md
        date_folder = datetime.now().strftime("%Y-%m")
        dest_folder = self.archives_path / date_folder
        dest_folder.mkdir(parents=True, exist_ok=True)
        
        dest = dest_folder / f"{session_id}_raw.md"
        
        try:
            shutil.copy2(source, dest)
            # 可选：清空原文件而不是删除，保持文件存在
            with open(source, 'w', encoding='utf-8') as f:
                f.write(f"# Session {session_id}\nMigrated to: {dest}\n")
            return str(dest)
        except Exception as e:
            print(f"Migration failed: {e}")
            return None
            
    def migrate_all_pending(self) -> int:
        """
        迁移所有待迁移的会话
        :return: 迁移数量
        """
        # 检查是否有未迁移的会话 (通过 context.json 判断)
        context_file = self.active_session_path / 'context.json'
        if not context_file.exists():
            return 0
            
        # 读取会话 ID
        try:
            with open(context_file, 'r', encoding='utf-8') as f:
                context = json.load(f)
            session_id = context.get('session_id')
            if session_id:
                self.migrate_session(session_id)
                return 1
        except Exception:
            pass
            
        return 0
        
    def compress_old_archives(self, older_than_days: int = 7) -> int:
        """
        压缩旧归档文件 (gzip)
        :param older_than_days: 多少天前的文件压缩
        :return: 压缩数量
        """
        compressed = 0
        cutoff = datetime.now().timestamp() - (older_than_days * 24 * 60 * 60)
        
        if not self.archives_path.exists():
            return 0
            
        for month_folder in self.archives_path.iterdir():
            if month_folder.is_dir():
                for log_file in month_folder.glob("*.md"):
                    if log_file.stat().st_mtime < cutoff and not log_file.name.endswith('.gz'):
                        try:
                            # 读取原内容
                            with open(log_file, 'rb') as f_in:
                                content = f_in.read()
                            # 写入 gzip
                            gz_path = log_file.with_suffix('.md.gz')
                            with gzip.open(gz_path, 'wb') as f_out:
                                f_out.write(content)
                            # 删除原文件
                            log_file.unlink()
                            compressed += 1
                        except Exception as e:
                            print(f"Compression failed for {log_file}: {e}")
                            
        return compressed
        
    def get_archive_stats(self) -> Dict:
        """
        获取归档统计信息
        :return: 统计字典
        """
        stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'by_month': {}
        }
        
        if not self.archives_path.exists():
            return stats
            
        for month_folder in self.archives_path.iterdir():
            if month_folder.is_dir():
                month_name = month_folder.name
                month_files = list(month_folder.glob("*"))
                month_size = sum(f.stat().st_size for f in month_files if f.is_file())
                
                stats['total_files'] += len(month_files)
                stats['total_size_mb'] += month_size / (1024 * 1024)
                stats['by_month'][month_name] = {
                    'files': len(month_files),
                    'size_mb': month_size / (1024 * 1024)
                }
                
        return stats
