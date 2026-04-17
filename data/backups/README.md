# data/backups/README.md

# 备份目录说明

## 用途
存储由 `tools/backup.py` 自动生成的文件快照。

## 命名规范
格式：`{原路径}_{时间戳}_{原因}.bak`
示例：`wiki_04_LongTerm_Memory_User_Profile_md.20240520_100000.before_edit.bak`

## 保留策略
- **默认保留**: 30 天
- **最大版本数**: 每个文件保留最近 10 个版本
- **清理工具**: `tools/backup.py cleanup_old_backups()`

## 恢复方法
1. 找到需要的 `.bak` 文件。
2. 运行 `tools/backup.py restore_backup --path <backup_path>`。
3. 或手动复制回原位置。

## 安全
- 本目录包含历史代码和配置，可能包含敏感信息。
- 禁止将本目录内容上传到公共仓库。
