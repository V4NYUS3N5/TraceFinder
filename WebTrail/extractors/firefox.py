"""
Firefox 浏览器提取器
"""
import os
import json
import datetime

try:
    from TraceFinder.utils import firefox_time_to_dt, read_sqlite_copy
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from TraceFinder.utils import firefox_time_to_dt, read_sqlite_copy


PROFILES_DIR = os.path.expanduser("~/AppData/Roaming/Mozilla/Firefox/Profiles")


# ---- 浏览历史 ----
def _history(profile_name, places_db):
    results = []
    conn, tmp = read_sqlite_copy(places_db)
    if not conn:
        return results
    try:
        for url, title, last_visit, visit_count in conn.execute(
            "SELECT url, title, last_visit_date, visit_count FROM moz_places "
            "WHERE last_visit_date > 0 ORDER BY last_visit_date DESC LIMIT 200"
        ):
            dt = firefox_time_to_dt(last_visit)
            results.append({
                "type": "浏览历史",
                "source": f"Firefox [{profile_name}]",
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
def _bookmarks(profile_name, places_db):
    results = []
    conn, tmp = read_sqlite_copy(places_db)
    if not conn:
        return results
    try:
        for title, url, date_added in conn.execute(
            "SELECT b.title, p.url, b.dateAdded "
            "FROM moz_bookmarks b JOIN moz_places p ON b.fk = p.id "
            "WHERE b.type = 1 AND b.title IS NOT NULL "
            "ORDER BY b.dateAdded DESC LIMIT 100"
        ):
            dt = firefox_time_to_dt(date_added)
            results.append({
                "type": "书签",
                "source": f"Firefox [{profile_name}]",
                "time": dt,
                "time_str": dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "",
                "content": (title or url)[:80]
            })
    except Exception:
        pass
    finally:
        conn.close()
        try: os.remove(tmp)
        except OSError: pass
    return results


# ---- 下载记录 ----
def _downloads(profile_name, places_db):
    results = []
    conn, tmp = read_sqlite_copy(places_db)
    if not conn:
        return results
    try:
        for source_url, date_added in conn.execute(
            "SELECT p.url, a.dateAdded "
            "FROM moz_annos a JOIN moz_places p ON a.place_id = p.id "
            "WHERE a.anno_attribute_id = ("
            "  SELECT id FROM moz_anno_attributes WHERE name='downloads/destinationFileURI'"
            ") ORDER BY a.dateAdded DESC LIMIT 50"
        ):
            dt = firefox_time_to_dt(date_added)
            results.append({
                "type": "下载",
                "source": f"Firefox [{profile_name}]",
                "time": dt,
                "time_str": dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "",
                "content": source_url[:80]
            })
    except Exception:
        pass
    finally:
        conn.close()
        try: os.remove(tmp)
        except OSError: pass
    return results


# ---- Cookie ----
def _cookies(profile_name, cookies_db):
    results = []
    conn, tmp = read_sqlite_copy(cookies_db)
    if not conn:
        return results
    try:
        for host, cnt in conn.execute(
            "SELECT host, COUNT(*) FROM moz_cookies GROUP BY host ORDER BY 2 DESC LIMIT 50"
        ):
            results.append({
                "type": "Cookie",
                "source": f"Firefox [{profile_name}]",
                "time": None,
                "time_str": "",
                "content": f"{host} ({cnt}条)"
            })
    except Exception:
        pass
    finally:
        conn.close()
        try: os.remove(tmp)
        except OSError: pass
    return results


# ---- 登录凭据 ----
def _logins(profile_name, logins_json):
    results = []
    try:
        with open(logins_json, 'r', encoding='utf-8') as f:
            logins = json.load(f).get('logins', [])
        counts = {}
        for l in logins:
            h = l.get('hostname', '')
            counts[h] = counts.get(h, 0) + 1
        for host, cnt in sorted(counts.items(), key=lambda x: -x[1])[:30]:
            results.append({
                "type": "登录凭据",
                "source": f"Firefox [{profile_name}]",
                "time": None,
                "time_str": "",
                "content": f"{host} ({cnt}条)"
            })
    except Exception:
        pass
    return results


# ---- 扩展 ----
def _extensions(profile_name, ext_json):
    results = []
    try:
        with open(ext_json, 'r', encoding='utf-8') as f:
            addons = json.load(f).get('addons', [])
        for a in addons[:30]:
            if a.get('active'):
                name = a.get('defaultLocale', {}).get('name', a.get('id', ''))
                results.append({
                    "type": "扩展",
                    "source": f"Firefox [{profile_name}]",
                    "time": None,
                    "time_str": "",
                    "content": name
                })
    except Exception:
        pass
    return results


# ---- 统一提取入口 ----
def extract_all():
    results = []
    if not os.path.exists(PROFILES_DIR):
        return results

    for profile_name in os.listdir(PROFILES_DIR):
        profile_path = os.path.join(PROFILES_DIR, profile_name)
        if not os.path.isdir(profile_path):
            continue

        places_db = os.path.join(profile_path, "places.sqlite")
        if os.path.exists(places_db):
            results.extend(_history(profile_name, places_db))
            results.extend(_bookmarks(profile_name, places_db))
            results.extend(_downloads(profile_name, places_db))

        cookies_db = os.path.join(profile_path, "cookies.sqlite")
        if os.path.exists(cookies_db):
            results.extend(_cookies(profile_name, cookies_db))

        logins_json = os.path.join(profile_path, "logins.json")
        if os.path.exists(logins_json):
            results.extend(_logins(profile_name, logins_json))

        ext_json = os.path.join(profile_path, "extensions.json")
        if os.path.exists(ext_json):
            results.extend(_extensions(profile_name, ext_json))

    return results
