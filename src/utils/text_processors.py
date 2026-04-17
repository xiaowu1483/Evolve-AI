# src/utils/text_processors.py

import re
from typing import List, Dict

def truncate_text(text, max_tokens=2000, truncation_marker="\n...[truncated]...\n"):
    """
    简单文本截断 (基于字符数近似 token)
    用于防止上下文溢出，保留头部和尾部
    :param text: 原始文本
    :param max_tokens: 最大字符数限制
    :param truncation_marker: 截断标记
    :return: 截断后的文本
    """
    if len(text) <= max_tokens:
        return text
        
    head_len = int(max_tokens * 0.7)
    tail_len = max_tokens - head_len - len(truncation_marker)
    
    return text[:head_len] + truncation_marker + text[-tail_len:]
    
def extract_markdown_links(content):
    """
    提取 Markdown 中的链接 [text](path)
    用于解析 _Index.md 中的导航结构
    :param content: Markdown 内容
    :return: List[Dict] {'text': str, 'path': str}
    """
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, content)
    return [{'text': m[0], 'path': m[1]} for m in matches]
    
def parse_index(content):
    """
    解析 Wiki 索引文件结构
    识别 #-标题 和 - 列表
    :param content: 索引文件内容
    :return: Dict 结构化数据
    """
    structure = {
        'headers': [],
        'links': []
    }
    
    lines = content.split('\n')
    for line in lines:
        if line.startswith('#'):
            structure['headers'].append(line.strip())
        elif line.strip().startswith('- ['):
            links = extract_markdown_links(line)
            structure['links'].extend(links)
            
    return structure
    
def clean_markdown_formatting(text):
    """
    清理 Markdown 格式，用于纯文本日志或摘要
    :param text: Markdown 文本
    :return: 纯文本
    """
    # 移除代码块
    text = re.sub(r'```[\s\S]*?```', '', text)
    # 移除链接标记
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # 移除粗体/斜体
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    return text
