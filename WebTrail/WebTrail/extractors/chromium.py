"""
Chromium 内核浏览器提取器 (Chrome / Edge / Brave / Opera / 360)
"""
import os
import json
import datetime

try:
    from WebTrail.utils import chrome_time_to_dt, read_sqlite_copy
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from WebTrail.utils import chrome_time_to_dt, read_sqlite_copy


BROWSERS = [
    ("Chrome",    "~/AppData/Local/Google/Chrome/User Data"),
    ("Edge",      "~/AppData/Local/Microsoft/Edge/User Data"),
    ("Brave",     "~/AppData/Local/BraveSoftware/Brave-Browser/User Data"),
    ("Opera",     "~/AppData/Roaming/Opera Software/Opera Stable"),
    ("360浏览器", "~/AppData/Local/360Chrome/Chrome/User Data"),
]


def _list_profiles(data_path):
    """读取 Local State 获取 profile 列表"""
    profiles = ["Default"]
    local_state = os.path.join(data_path, "Local State")
    if os.path.exists(local_state):
        try:
            with open(local_state, 'r', encoding='utf-8') as f:
                ls = json.load(f)
            keys = ls.get("profile", {}).get("profiles_order", [])
            if keys:
                profiles = keys
        except Exception:
            pass
    return profiles


# ---- 浏览历史 ----
def _history(browser_name, profile_path):
    results = []
    conn, tmp = read_sqlite_copy(os.path.join(profile_path, "History"))
    if not conn:
        return results
    try:
        for url, title, last_visit, visit_count in conn.execute(
            "SELECT url, title, last_visit_time, visit_count FROM urls "
            "ORDER BY last_visit_time DESC LIMIT 200"
        ):
            dt = chrome_time_to_dt(last_visit)
            results.append({
                "type": "浏览历史",
                "source": browser_name,
                "time": dt,
                "time_str": dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "",
                "content": (title or url)[:120]
            })
    except Exception:
        pass
    finally:
        conn.close()
        try: os.remove(tmp)
        except OSError: pass
    return results


# ---- 书签 ----
def _bookmarks(browser_name, profile_path):
    def _walk(nodes):
        out = []
        if not isinstance(nodes, list):
            return out
        for n in nodes:
            if n.get('type') == 'url':
                out.append((n.get('name', ''), chrome_time_to_dt(n.get('date_added', 0))))
            if 'children' in n:
                out.extend(_walk(n['children']))
        return out

    results = []
    bm_file = os.path.join(profile_path, "Bookmarks")
    if not os.path.exists(bm_file):
        return results
    try:
        with open(bm_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for root in data.get('roots', {}).values():
            if isinstance(root, dict) and 'children' in root:
                for name, dt in _walk(root['children']):
                    results.append({
                        "type": "书签",
                        "source": browser_name,
                        "time": dt,
                        "time_str": dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "",
                        "content": name[:80]
                    })
    except Exception:
        pass
    return results


# ---- 下载记录 ----
def _downloads(browser_name, profile_path):
    results = []
    conn, tmp = read_sqlite_copy(os.path.join(profile_path, "History"))
    if not conn:
        return results
    try:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='downloads'")
        if cur.fetchone():
            for target_path, start_time, total_bytes, state in conn.execute(
                "SELECT target_path, start_time, total_bytes, state FROM downloads "
                "ORDER BY start_time DESC LIMIT 100"
            ):
                dt = chrome_time_to_dt(start_time)
                filename = os.path.basename(target_path or "")
                state_map = {1: "已完成", 2: "已取消", 3: "中断", 4: "中断"}
                size_mb = f"{total_bytes/1024/1024:.1f}MB" if total_bytes else ""
                results.append({
                    "type": "下载",
                    "source": browser_name,
                    "time": dt,
                    "time_str": dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "",
                    "content": f"{filename[:60]} {size_mb} {state_map.get(state, '')}"
                })
    except Exception:
        pass
    finally:
        conn.close()
        try: os.remove(tmp)
        except OSError: pass
    return results


# ---- Cookie 域名统计 ----
def _cookies(browser_name, profile_path):
    results = []
    db = os.path.join(profile_path, "Network", "Cookies")
    if not os.path.exists(db):
        db = os.path.join(profile_path, "Cookies")
    conn, tmp = read_sqlite_copy(db)
    if not conn:
        return results
    try:
        for host_key, cnt, last_ts in conn.execute(
            "SELECT host_key, COUNT(*), MAX(last_access_utc) FROM cookies "
            "GROUP BY host_key ORDER BY 2 DESC LIMIT 50"
        ):
            results.append({
                "type": "Cookie",
                "source": browser_name,
                "time": chrome_time_to_dt(last_ts),
                "time_str": (chrome_time_to_dt(last_ts) or datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                "content": f"{host_key} ({cnt}条)"
            })
    except Exception:
        pass
    finally:
        conn.close()
        try: os.remove(tmp)
        except OSError: pass
    return results


# ---- 登录凭据统计 ----
def _logins(browser_name, profile_path):
    results = []
    conn, tmp = read_sqlite_copy(os.path.join(profile_path, "Login Data"))
    if not conn:
        return results
    try:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='logins'")
        if cur.fetchone():
            for origin_url, cnt in conn.execute(
                "SELECT origin_url, COUNT(*) FROM logins GROUP BY origin_url "
                "ORDER BY COUNT(*) DESC LIMIT 30"
            ):
                results.append({
                    "type": "登录凭据",
                    "source": browser_name,
                    "time": None,
                    "time_str": "",
                    "content": f"{origin_url[:100]} ({cnt}条)"
                })
    except Exception:
        pass
    finally:
        conn.close()
        try: os.remove(tmp)
        except OSError: pass
    return results


# ---- 最近会话 ----
def _sessions(browser_name, profile_path):
    results = []
    sessions_dir = os.path.join(profile_path, "Sessions")
    if not os.path.exists(sessions_dir):
        return results
    try:
        for fname in os.listdir(sessions_dir):
            if fname.startswith("Session_") or fname.startswith("Tabs_"):
                fpath = os.path.join(sessions_dir, fname)
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(fpath))
                results.append({
                    "type": "会话",
                    "source": browser_name,
                    "time": mtime,
                    "time_str": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                    "content": f"{fname} ({os.path.getsize(fpath)/1024:.1f}KB)"
                })
    except OSError:
        pass
    return results


# ---- 扩展插件 ----
def _extensions(browser_name, profile_path):
    results = []
    ext_dir = os.path.join(profile_path, "Extensions")
    if not os.path.exists(ext_dir):
        return results
    try:
        for ext_id in os.listdir(ext_dir)[:30]:
            ext_path = os.path.join(ext_dir, ext_id)
            if not os.path.isdir(ext_path):
                continue
            name = ext_id[:16]
            for ver in os.listdir(ext_path):
                mf = os.path.join(ext_path, ver, "manifest.json")
                if os.path.exists(mf):
                    try:
                        with open(mf, 'r', encoding='utf-8') as f:
                            name = json.load(f).get('name', name)
                        break
                    except Exception:
                        pass
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(ext_path))
            results.append({
                "type": "扩展",
                "source": browser_name,
                "time": mtime,
                "time_str": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                "content": name
            })
    except OSError:
        pass
    return results


# ---- 统一提取入口 ----
_EXTRACTORS = [_history, _bookmarks, _downloads, _cookies, _logins, _sessions, _extensions]


def extract_all():
    """提取所有 Chromium 浏览器的全部痕迹"""
    results = []
    for name, path in BROWSERS:
        data_path = os.path.expanduser(path)
        if not os.path.exists(data_path):
            continue
        for profile in _list_profiles(data_path):
            profile_path = os.path.join(data_path, profile)
            if not os.path.isdir(profile_path):
                continue
            src = f"{name}" + (f" [{profile}]" if profile != "Default" else "")
            for fn in _EXTRACTORS:
                try:
                    results.extend(fn(src, profile_path))
                except Exception:
                    pass
    return results
