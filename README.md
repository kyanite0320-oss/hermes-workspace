# 🦊 Hermes Workspace

两电脑 Hermes 工作区，路径自适应（`%~dp0` + `wslpath`）。

## 电脑信息

|          | 电脑 A                 | 电脑 B                 |
|----------|------------------------|------------------------|
| 用户名   | Administrator          | loofnn                 |
| 盘符     | F:                     | C:                     |
| WSL 路径 | /mnt/f/AI/hermes       | /mnt/c/AI/hermes       |
| 桌面路径 | D:\360MoveData\Users\Administrator\Desktop | C:\Users\loofnn\Desktop |
| Claude Code | ✅ 已装 v2.1.128    | ✅ 已装                |

## 灵魂同步

- 灵魂仓库：`git@github.com:kyanite0320-oss/hermes-data.git`
- PC A 每天 0:00 WSL cron → soul-sync.sh → 推送到 GitHub
- PC B Windows 登录 → soul-pull.bat → 拉取并还原到 ~/.hermes/

## 工作区同步

- 工作区仓库：`git@github.com:kyanite0320-oss/hermes-workspace.git`
- 两边登录都有计划任务 `HermesWorkspacePull` 自动 git pull
- 所有 bat 脚本路径自适应，C 盘 F 盘通用

## 已注册的 Windows 登录计划任务

| 任务名 | 动作 |
|--------|------|
| HermesMorningBrief | 生成晨报 + 启动 HTTP 服务器 |
| HermesWorkspacePull | git pull 工作区 |
| HermesSoulPull | 拉取灵魂数据（仅 PC B） |

## 第二台电脑（PC B - loofnn）配置流程

当用户在另一台电脑上找我时，按以下步骤执行：

### 1. 克隆工作区
```bash
mkdir -p /mnt/c/AI/hermes
cd /mnt/c/AI/hermes
git clone git@github.com:kyanite0320-oss/hermes-workspace.git .
```

### 2. 运行配置脚本
```bash
cmd.exe /c C:\AI\hermes\other-pc-setup.bat
```
脚本会自动：
- 注册 3 个计划任务（晨报、工作区同步、灵魂拉取）
- 创建桌面快捷方式

### 3. 灵魂数据仓库
如果 soul-pull.bat 需要灵魂数据仓库：
```bash
cd ~ && git clone git@github.com:kyanite0320-oss/hermes-data.git
```

### 4. 验证
用 Chrome 打开 `http://localhost:8000/morning-brief/morning-brief.html` 确认晨报正常渲染。

## 日常维护

- 所有新项目文件放到工作区根目录下
- 提交后自动同步，无需手动操作
- 路径用 `wslpath` + `%~dp0` 动态获取，不硬编码
- 用户偏好：编程任务用 Claude Code `-p` 模式，先 plan 再执行
