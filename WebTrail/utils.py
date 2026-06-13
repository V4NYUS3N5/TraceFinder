"""
公共工具函数 - 时间转换 & SQLite 安全读取
"""
import datetime
import os
import sqlite3


def filetime_to_datetime(filetime_bytes):
    """Windows FILETIME (8字节小端) -> datetime"""
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


def chrome_time_to_dt(usec_val):
    """Chromium 时间戳 (1601年起微秒数) -> datetime"""
    if not usec_val or usec_val == 0:
        return None
    try:
        return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=usec_val)
    except (OSError, OverflowError):
        return None


def firefox_time_to_dt(usec_val):
    """Firefox PRTime (1970年起微秒数) -> datetime"""
    if not usec_val or usec_val == 0:
        return None
    try:
        return datetime.datetime(1970, 1, 1) + datetime.timedelta(microseconds=usec_val)
    except (OSError, OverflowError):
        return None


def read_sqlite_copy(db_path):
    """复制 SQLite DB 到临时文件并返回连接，用完需自行关闭并删除"""
    if not os.path.exists(db_path):
        return None, None
    tmp = db_path + ".tf_tmp"
    try:
        with open(db_path, 'rb') as src:
            with open(tmp, 'wb') as dst:
                dst.write(src.read())
        return sqlite3.connect(tmp), tmp
    except Exception:
        return None, None
