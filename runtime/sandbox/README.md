# runtime/sandbox/README.md

# 沙箱安全规范

## 目的
本目录用于隔离执行 AI 生成的代码，防止对主系统造成破坏。

## 权限限制
1. **文件系统**:
   - 允许读写：`runtime/sandbox/workspace/`
   - 禁止访问：`src/`, `wiki/`, `data/`, `config/`
   - 禁止访问：系统根目录 `/`

2. **网络**:
   - 默认禁止外部网络访问。
   - 如需联网，需在 `config.yaml` 中显式授权。

3. **资源**:
   - 最大内存：512MB
   - 最大 CPU 时间：30 秒
   - 禁止 fork 子进程

## 执行流程
1. AI 将代码写入 `workspace/test_script.py`。
2. 系统调用 `src/core/security.py` 进行静态检查。
3. 在隔离环境中运行代码。
4. 结果输出到 `test_results.md`。
5. 执行完毕后清理 `workspace/` 中的临时文件。

## 违规处理
- 检测到违规操作（如尝试读取 `.env`）将立即终止进程。
- 违规记录将写入 `wiki/05_Reflection_Logs/` 供后续分析。
