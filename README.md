# 🦊 Hermes Workspace

Hermes Agent 工作区 — 晨报系统 + 新闻页 + 双电脑同步方案。

## 📁 目录结构

```
F:\AI\hermes\          （电脑 A） /  C:\AI\hermes\        （电脑 B）
├── morning-brief\
│   ├── morning-brief.py              ← 每日晨报生成脚本
│   ├── morning-brief.html            ← 晨报展示页面（暗色/浅色/折叠/打印）
│   ├── morning-brief-startup.bat     ← 登录时自动运行
│   └── open-morning-brief.bat        ← 手动打开晨报
├── news-app\
│   ├── index.html / style.css / app.js  ← 实时新闻页面
├── 晨报\YYYY-MM-DD\                  ← 每日生成的晨报数据
├── hermes-workspace-pull.bat         ← 登录时自动 git pull
├── soul-pull.bat                     ← 灵魂同步拉取
├── other-pc-setup.bat                ← 另一台电脑一键配置
└── .gitignore
```

## 🚀 电脑 A（当前，Administrator，F: 盘）

### 已配置
- ✅ Windows 登录计划任务 `HermesMorningBrief` → 自动生成晨报 + 启动 HTTP
- ✅ Windows 登录计划任务 `HermesWorkspacePull` → 自动 git pull
- ✅ 每天 0:00 WSL cron → 灵魂同步推送到 GitHub
- ✅ HTTP 服务器 `localhost:8000` 自动启动
- ✅ Chrome CDP 远程调试端口 9222

### 打开晨报
```bash
# 方式一：桌面双击 open-morning-brief.bat
# 方式二：浏览器打开
http://localhost:8000/morning-brief/morning-brief.html
```

### 手动生成晨报
```bash
cd F:\AI\hermes\morning-brief
python morning-brief.py
```

---

## 💻 电脑 B（loofnn，仅 C 盘）— 配置指南

### 前置条件
- [ ] Windows 用户名为 `loofnn`
- [ ] WSL（Ubuntu）已安装
- [ ] GitHub SSH 密钥已配置并添加到 GitHub
- [ ] Python 3 已安装（`python3 --version`）

### 一键配置

在 WSL 中执行：

```bash
# 1. 克隆工作区
mkdir -p /mnt/c/AI/hermes
cd /mnt/c/AI/hermes
git clone git@github.com:kyanite0320-oss/hermes-workspace.git .

# 2. 运行配置脚本
cd /mnt/c/AI/hermes
./other-pc-setup.bat
```

或在 Windows 中直接双击 `C:\AI\hermes\other-pc-setup.bat` 即可。

### 配置脚本会自动
1. ✅ 克隆/拉取工作区
2. ✅ 注册 `HermesMorningBrief` 计划任务（登录自动生成晨报）
3. ✅ 注册 `HermesWorkspacePull` 计划任务（登录自动拉取更新）
4. ✅ 注册 `HermesSoulPull` 计划任务（登录自动拉取灵魂数据）
5. ✅ 桌面创建快捷方式

### 灵魂同步
灵魂数据仓库：`git@github.com:kyanite0320-oss/hermes-data.git`

电脑 A 每天 0:00 自动推送 → 电脑 B 登录时自动拉取。

如需手动拉取灵魂：
```bash
cd ~/hermes-data && git pull
cp MEMORY.md ~/.hermes/memories/
cp USER.md ~/.hermes/memories/
rsync -a --delete skills/ ~/.hermes/skills/
```

---

## 🔧 日常使用

### 晨报
每天早上 Windows 登录后，双击桌面的 `🌅 晨报` 快捷方式。

### 更新工作区
代码提交后，另一台电脑登录时自动拉取。如需手动：
```bash
cd F:\AI\hermes  （或 C:\AI\hermes）
git pull
```

### 添加新项目
所有新文件统一放 `F:\AI\hermes\`（另一台 `C:\AI\hermes\`），提交即同步。

---

## 📝 注意事项

- 所有 `.bat` 脚本已做路径自适应（`%~dp0` + `wslpath`），C 盘 / F 盘通用
- `morning-brief.py` 根据脚本位置自动推导晨报输出目录
- 飞书网关在 tmux 中后台运行
- HTTP 服务器根目录为工作区根目录
