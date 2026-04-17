```sql
# data/schema.sql

-- PersonalAI 数据库架构定义
-- 用于初始化 data/sqlite.db
-- 由 src/core/engine.py 或初始化脚本调用

-- 用户配置表
CREATE TABLE IF NOT EXISTS user_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 会话元数据表 (用于快速检索历史会话)
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status TEXT DEFAULT 'active', -- active, archived, error
    summary TEXT, -- 会话摘要
    log_path TEXT -- 指向 wiki/06_Raw_Archives 的路径
);

-- 模块注册表 (缓存 src/modules 的状态)
CREATE TABLE IF NOT EXISTS module_registry (
    module_name TEXT PRIMARY KEY,
    version TEXT,
    status TEXT DEFAULT 'active', -- active, disabled, error
    last_loaded TIMESTAMP,
    config_hash TEXT -- 用于检测 config.yaml 变更
);

-- 审计日志索引 (详细日志在 data/audit_trail.json)
CREATE TABLE IF NOT EXISTS audit_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL,
    action TEXT NOT NULL, -- create, update, delete, reflection
    path TEXT,
    agent TEXT,
    summary TEXT
);

-- 创建索引以加速查询
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_index(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_index(action);

-- 插入默认配置
INSERT OR IGNORE INTO user_config (key, value) VALUES ('version', '1.0.0');
INSERT OR IGNORE INTO user_config (key, value) VALUES ('created_at', datetime('now'));