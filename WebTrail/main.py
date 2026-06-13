#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TraceFinder - 浏览器痕迹取证提取工具
支持 Chrome / Edge / Brave / Opera / 360 / Firefox
"""
import argparse
import sys
import json
import os

try:
    from TraceFinder.extractors.chromium import extract_all as extract_chromium
    from TraceFinder.extractors.firefox import extract_all as extract_firefox
    from TraceFinder.system import extract_all as extract_system
    from TraceFinder.reporter import generate_report
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from extractors.chromium import extract_all as extract_chromium
    from extractors.firefox import extract_all as extract_firefox
    from system import extract_all as extract_system
    from reporter import generate_report


BANNER = """
╔══════════════════════════════════════════════════════════╗
║           TraceFinder 浏览器痕迹取证提取工具             ║
║           v1.0  |  Windows 10/11                         ║
╚══════════════════════════════════════════════════════════╝
"""


def main():
    p = argparse.ArgumentParser(description="TraceFinder - 浏览器痕迹取证提取工具")
    p.add_argument("--output", "-o", help="保存报告到指定文件")
    p.add_argument("--json", help="导出JSON到指定文件")
    p.add_argument("--quiet", "-q", action="store_true", help="静默模式")
    args = p.parse_args()

    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    if not args.quiet:
        print(BANNER)

    # 提取
    traces = extract_chromium() + extract_firefox() + extract_system()

    if not traces:
        print("\n[!] 未提取到浏览器痕迹")
        return

    report = generate_report(traces)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"[+] 报告已保存: {args.output}")
    else:
        try:
            print(report)
        except UnicodeEncodeError:
            print(report.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))

    # 控制台简要统计
    sus = sum(1 for t in traces if t.get("suspicious"))
    print(f"\n[+] 总计 {len(traces)} 条痕迹, 其中可疑 {sus} 条")

    if args.json:
        data = [{"type": t["type"], "source": t.get("source", ""),
                 "time": t["time_str"], "content": t["content"]} for t in traces]
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[+] JSON已保存: {args.json}")


if __name__ == "__main__":
    main()
