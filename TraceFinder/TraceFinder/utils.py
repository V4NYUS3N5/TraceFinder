"""
TraceFinder 公共工具函数
"""
import datetime


def filetime_to_datetime(filetime_bytes):
    """将Windows FILETIME转换为datetime对象"""
    if len(filetime_bytes) < 8:
        return None
    filetime = int.from_bytes(filetime_bytes, byteorder='little')
    if filetime == 0:
        return None
    timestamp = filetime / 10_000_000 - 11644473600
    try:
        return datetime.datetime.fromtimestamp(timestamp)
    except (OSError, ValueError, OverflowError):
        return None
