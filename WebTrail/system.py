"""
系统级浏览器痕迹提取 (UserAssist 注册表 / DNS 缓存 / Prefetch)
"""
import winreg
import subprocess
import datetime
import os

try:
    from TraceFinder.utils import filetime_to_datetime
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from TraceFinder.utils import filetime_to_datetime


_BROWSER_EXES = ["chrome.exe", "msedge.exe", "firefox.exe",
                 "brave.exe", "opera.exe", "360chrome.exe"]
_BROWSER_PF = ["CHROME", "MSEDGE", "FIREFOX", "BRAVE", "OPERA", "360CHROME"]


def _rot13(s):
    return s.translate(str.maketrans(
        "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"))


# ---- UserAssist 注册表 (浏览器启动记录) ----
def get_userassist():
    results = []
    ua = r"Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist\{CEBFF5CD-ACE2-4F4F-9178-9926F41749EA}\Count"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, ua)
        for i in range(winreg.QueryInfoKey(key)[1]):
            try:
                name, value, _ = winreg.EnumValue(key, i)
                decoded = _rot13(name)
                if any(b in decoded.lower() for b in _BROWSER_EXES) and len(value) >= 72:
                    dt = filetime_to_datetime(value[64:72])
                    if dt:
                        results.append({
                            "type": "启动记录",
                            "source": "UserAssist",
                            "time": dt,
                            "time_str": dt.strftime("%Y-%m-%d %H:%M:%S"),
                            "content": decoded
                        })
            except (OSError, ValueError):
                continue
        winreg.CloseKey(key)
    except (OSError, FileNotFoundError):
        pass
    return results


# ---- DNS 缓存 ----
def get_dns():
    results = []
    seen = set()
    skip = ['queniuck', 'bytedns', 'bytedance', 'zijieapi',
            'nic.', 'akadns', 'cloudfront', 'azure', '.internal', '.corp', '.intranet']
    try:
        out = subprocess.check_output(
            "ipconfig /displaydns", shell=True, stderr=subprocess.STDOUT
        ).decode('gbk', errors='ignore')
        rec = {}
        for line in out.split('\n'):
            line = line.strip()
            if line.startswith("\u8bb0\u5f55\u540d\u79f0"):
                rec['name'] = line.split(":", 1)[1].strip()
            elif line.startswith("\u8bb0\u5f55\u7c7b\u578b"):
                rec['type'] = line.split(":", 1)[1].strip()
            elif line.startswith("\u751f\u5b58\u65f6\u95f4"):
                domain = rec.get('name', '')
                if ('.' in domain and
                    not domain.endswith(('.lan', '.local', '.')) and
                    domain not in seen and
                    not any(k in domain.lower() for k in skip)):
                    seen.add(domain)
                    results.append({
                        "type": "DNS",
                        "source": "DNS缓存",
                        "time": None,
                        "time_str": "",
                        "content": domain
                    })
                rec = {}
    except subprocess.CalledProcessError:
        pass
    return results


# ---- Prefetch ----
def get_prefetch():
    results = []
    pf_dir = r"C:\Windows\Prefetch"
    if not os.path.exists(pf_dir):
        return results
    try:
        for f in os.listdir(pf_dir):
            if f.endswith('.pf'):
                if any(b in f.upper() for b in _BROWSER_PF):
                    mtime = datetime.datetime.fromtimestamp(
                        os.path.getmtime(os.path.join(pf_dir, f)))
                    results.append({
                        "type": "Prefetch",
                        "source": "Prefetch",
                        "time": mtime,
                        "time_str": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                        "content": f[:-3]
                    })
    except OSError:
        pass
    return results


# ---- 统一入口 ----
def extract_all():
    return get_userassist() + get_dns() + get_prefetch()
