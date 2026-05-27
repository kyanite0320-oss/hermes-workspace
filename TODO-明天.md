# 明天在另一台电脑的操作计划

## 目标
把 Hermes 工作区 + 灵魂同步从电脑 A 同步到这台电脑（loofnn，C 盘）

## 操作步骤

### 1. 获取仓库
```bash
mkdir -p /mnt/c/AI/hermes
cd /mnt/c/AI/hermes
git clone git@github.com:kyanite0320-oss/hermes-workspace.git .
```

### 2. 运行配置脚本
```bash
cd /mnt/c/AI/hermes
cmd.exe /c other-pc-setup.bat
```

### 3. 拉取灵魂数据
灵魂仓库（如果还没有）：
```bash
cd ~
git clone git@github.com:kyanite0320-oss/hermes-data.git
```

### 4. 验证
- 重启 Windows 或手动运行计划任务
- 或直接打开晨报：`http://localhost:8000/morning-brief/morning-brief.html`
  （如果 HTTP 没启动，先双击 open-morning-brief.bat）

## 有问题找我
直接在飞书 @Hermes 问我
