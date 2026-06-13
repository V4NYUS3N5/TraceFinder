"""
报告生成器 - 时间线排序 / 可疑标记 / 统计摘要
"""

# 可疑关键词
_SUS_KEYWORDS = [
    "密码", "账号", "账户", "机密", "保密", "漏洞", "后门",
    "password", "secret", "token", "api_key", "credential",
    "exploit", "payload", "shell", "backdoor", "bypass",
    "pastebin", "anonfile", "file.io", "transfer.sh",
    "hack", "crack", "keygen", "破解", "入侵", "木马",
    "勒索", "ransomware", "暗网", "deepweb", "torrent",
]

_SUS_DOMAINS = ["pastebin.com", "anonfile.com", "file.io", "transfer.sh",
                "mega.nz", "mega.co.nz", "mediafire.com"]


def _mark_suspicious(traces):
    """标记可疑痕迹"""
    for t in traces:
        content = t.get("content", "").lower()
        is_sus = any(kw in content for kw in _SUS_KEYWORDS)
        is_sus |= any(d in content for d in _SUS_DOMAINS)
        t["suspicious"] = is_sus
    return traces


def _build_summary(traces):
    """生成底部统计摘要"""
    total = len(traces)
    types = {}
    sources = {}
    sus_count = 0
    sus_items = []

    for t in traces:
        tp = t.get("type", "其他")
        types[tp] = types.get(tp, 0) + 1
        src = t.get("source", "未知")
        sources[src] = sources.get(src, 0) + 1
        if t.get("suspicious"):
            sus_count += 1
            sus_items.append(f"  [{t['type']}] [{t.get('source', '')}] "
                           f"{t.get('time_str', '')}  {t['content']}")

    lines = []
    lines.append("")
    lines.append("=" * 80)
    lines.append("统计摘要")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"  总痕迹数: {total}")

    lines.append("")
    lines.append("  【按类型统计】")
    for tp, cnt in sorted(types.items(), key=lambda x: -x[1]):
        lines.append(f"    {tp}: {cnt}")

    lines.append("")
    lines.append("  【按来源统计】")
    for src, cnt in sorted(sources.items(), key=lambda x: -x[1]):
        lines.append(f"    {src}: {cnt}")

    lines.append("")
    if sus_count:
        lines.append(f"  【可疑标记: {sus_count} 条】")
        for item in sus_items:
            lines.append(item)
    else:
        lines.append("  【可疑标记: 0】 未发现明显可疑行为")

    lines.append("")
    lines.append("=" * 80)
    return "\n".join(lines)


def generate_report(all_traces):
    """生成完整报告（时间线 + 摘要）"""
    all_traces = _mark_suspicious(all_traces)

    timed = sorted(
        [t for t in all_traces if t.get("time") is not None],
        key=lambda x: x["time"], reverse=True
    )
    untimed = [t for t in all_traces if t.get("time") is None]

    lines = []
    lines.append("=" * 80)
    lines.append("WebTrail 浏览器痕迹取证报告")
    lines.append("=" * 80)
    lines.append("")

    if not all_traces:
        lines.append("未提取到任何痕迹")
        return "\n".join(lines)

    lines.append(f"共 {len(all_traces)} 条痕迹 "
                 f"({len(timed)} 条带时间戳, {len(untimed)} 条统计信息)")
    lines.append("")
    lines.append("-" * 80)

    for t in timed:
        src = f" [{t['source']}]" if t.get('source') else ""
        flag = " !!可疑!!" if t.get("suspicious") else ""
        lines.append(f"{t['time_str']}  {t['type']}{src}  {t['content']}{flag}")

    lines.append("-" * 80)

    if untimed:
        lines.append("")
        lines.append("【统计信息】")
        for t in untimed:
            src = f" [{t['source']}]" if t.get('source') else ""
            lines.append(f"  {t['type']}{src}  {t['content']}")

    # 底部摘要
    lines.append(_build_summary(all_traces))

    return "\n".join(lines)
