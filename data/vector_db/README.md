# data/vector_db/README.md

# 向量数据库目录说明

## 用途
存储嵌入向量索引，用于辅助检索。
**注意**: 在本架构中，向量检索仅作为 Wiki 结构化检索的补充，而非核心。

## 支持后端
- ChromaDB (默认)
- FAISS
- SQLite Vector (实验性)

## 初始化
首次运行时，`src/core/engine.py` 会自动初始化向量库。
如需重置索引，删除本目录所有文件后重启系统。

## 同步机制
- 当 `wiki/` 内容变更时，`agents/maintenance_agent` 会触发向量索引更新。
- 确保向量索引与 Wiki 内容一致，避免检索到过期信息。

## 性能
- 预计大小：每 1000 页 Wiki 文档约占用 50MB。
- 如超过 500MB，建议清理旧向量或优化嵌入模型。
