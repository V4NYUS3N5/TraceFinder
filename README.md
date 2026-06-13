# TraceFinder - 浏览器痕迹取证提取工具

Windows 平台浏览器痕迹一键提取工具，支持 Chrome / Edge / Brave / Opera / 360 / Firefox 六款浏览器，涵盖浏览历史、书签、下载记录、Cookie、登录凭据、会话标签页、扩展插件七大维度，并自动标记可疑行为。

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行提取（控制台输出报告）
python main.py

# 保存报告到文件
python main.py -o report.txt

# 导出JSON数据
python main.py --json data.json

# 静默模式
python main.py --quiet
```

## 支持范围

| 浏览器 | 内核 | 历史 | 书签 | 下载 | Cookie | 登录 | 会话 | 扩展 |
|--------|------|:----:|:----:|:----:|:------:|:----:|:----:|:----:|
| Chrome | Chromium | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Edge | Chromium | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Brave | Chromium | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Opera | Chromium | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 360浏览器 | Chromium | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Firefox | Gecko | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ |

系统级痕迹：UserAssist 启动记录 / DNS 缓存 / Prefetch 预读取文件。


## 项目结构

```
TraceFinder/
├── main.py                     # CLI入口
├── utils.py                    # 时间转换 / SQLite工具
├── system.py                   # 系统级痕迹 (UserAssist/DNS/Prefetch)
├── reporter.py                 # 报告生成 + 可疑标记 + 统计摘要
├── requirements.txt
└── extractors/
    ├── chromium.py             # Chrome/Edge/Brave/Opera/360 提取器
    └── firefox.py              # Firefox 提取器
```

## 技术要求

- Windows 10 / 11
- Python 3.8+
- 标准库依赖（`sqlite3`, `winreg`, `json`, `argparse`），无需第三方包

## 注意事项

- SQLite 数据库采用 "先复制后读取" 策略，避免浏览器锁定冲突
- 登录凭据模块仅统计来源 URL 和数量，**不输出明文密码**
- DNS 缓存需管理员权限运行方可获取完整结果
