# 晨报改造需求

## 1. Mock 数据 URL 替换
当前 morning-brief.py 的 MOCK_DATA 中有大量 fake URL（如 `https://indienova.com/game/dyson-sphere/001`），需要替换为真实的文章链接。

对每个分类，搜索真实存在的网页 URL，更新到 MOCK_DATA 中。

## 2. HTML 页面改造
修改 morning-brief.html，将当前列表布局改为：
- 每篇文章显示：**网页快照缩略图 + 标题 + 摘要**
- 快照缩略图从 `晨报/YYYY-MM-DD/snapshots/` 目录加载
- 点击缩略图或标题在新标签打开原文

## 3. 快照机制
由于直接生成网页截图需要浏览器，可以先做布局改造，URL 替换真实链接后，用户可手动点击打开查看原文。

## 实现顺序
1. 先用 web_search 找真实文章 URL，更新 MOCK_DATA
2. 改造 HTML 布局为缩略图+标题+摘要
3. 代码审查确认无误
