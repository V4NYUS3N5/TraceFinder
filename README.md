# WebTrail - 浏览器痕迹取证提取工具

Windows 平台数字取证工具，支持从 Chromium 内核浏览器（Chrome / Edge / Brave / Opera / 360）和 Firefox 中提取浏览痕迹，并生成时间线报告。

## 支持的浏览器

| 浏览器 | 内核 |
|--------|------|
| Google Chrome | Chromium |
| Microsoft Edge | Chromium |
| Brave | Chromium |
| Opera | Chromium |
| 360安全浏览器 | Chromium |
| Mozilla Firefox | Gecko |

## 提取维度

### 浏览器级
- 浏览历史（最近200条）
- 书签
- 下载记录
- Cookie 域名统计（Top50）
- 登录凭据统计（不提取明文）
- 会话标签页（Chromium）
- 已安装扩展插件

### 系统级
- 浏览器启动记录（UserAssist 注册表）
- DNS 缓存记录
- Prefetch 预读取文件

### 报告功能
- 按时间线倒序排列
- 基于关键词和可疑域名自动标记可疑痕迹
- 统计摘要（按类型、来源分布）

## 环境要求

- Windows 10 / 11
- Python 3.8+
- 标准库（无需额外安装依赖）

## 使用方法

```bash
# 直接在控制台输出报告
python -m WebTrail.main

# 保存报告到文件
python -m WebTrail.main -o report.txt

# 静默模式 + 导出 JSON
python -m WebTrail.main -q --json traces.json

# 同时输出报告和 JSON
python -m WebTrail.main -o report.txt --json traces.json
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `-o`, `--output` | 保存文本报告到指定文件 |
| `--json` | 导出 JSON 格式数据到指定文件 |
| `-q`, `--quiet` | 静默模式，不打印 Banner |

## 项目结构

```
WebTrail/
├── main.py                  # CLI 入口，协调各模块
├── extractors/
│   ├── chromium.py          # Chromium 内核浏览器提取
│   └── firefox.py           # Firefox 浏览器提取
├── system.py                # 系统级痕迹提取
├── reporter.py              # 报告生成 & 可疑标记
└── utils.py                 # 公共工具函数
```

## 示例输出

```
╔══════════════════════════════════════════════════════════╗
║           WebTrail 浏览器痕迹取证提取工具               ║
║           v1.0  |  Windows 10/11                         ║
╚══════════════════════════════════════════════════════════╝

[1] 浏览历史 | Chrome
    2024-06-12 15:30:00  https://www.example.com  - 示例网站

[2] 下载记录 | Edge
    2024-06-12 14:20:00  setup.exe  45.3 MB  已完成

...

================================================================================
统计摘要
总计: 156 条痕迹
  - 浏览历史: 89
  - 书签: 32
  - 下载记录: 12
  ...
可疑痕迹: 3 条
  [浏览历史] [Chrome] ...pastebin.com/...
```

## 注意事项

- 仅适用于 Windows 系统
- 部分浏览器数据可能被锁定，工具通过复制数据库副本读取以避免冲突
- 出于隐私保护，登录凭据仅统计数量，不输出明文密码
- 运行需要读取注册表和系统命令（`ipconfig /displaydns`），建议以管理员权限运行以获取完整数据
