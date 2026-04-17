# src/utils/time_utils.py

from datetime import datetime

def get_timestamp(format="%Y-%m-%d_%H-%M-%S"):
    """
    获取当前时间戳字符串
    :param format: 时间格式
    :return: 字符串
    """
    return datetime.now().strftime(format)
    
def get_folder_name():
    """
    获取用于归档文件夹的名称 (YYYY-MM)
    用于 wiki/06_Raw_Archives 和 wiki/05_Reflection_Logs
    :return: 字符串
    """
    return datetime.now().strftime("%Y-%m")
    
def get_session_id_prefix():
    """
    获取会话 ID 前缀 (YYYYMMDD)
    :return: 字符串
    """
    return datetime.now().strftime("%Y%m%d")
    
def parse_date_from_folder(folder_name):
    """
    从文件夹名称解析日期
    :param folder_name: YYYY-MM 格式
    :return: datetime 对象
    """
    try:
        return datetime.strptime(folder_name, "%Y-%m")
    except ValueError:
        return datetime.now()
