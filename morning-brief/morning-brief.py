#!/usr/bin/env python3
"""
Morning Brief - 游戏行业每日晨报生成器
自动抓取游戏行业资讯，生成结构化的晨报数据（JSON + Markdown）。
纯 Python 标准库实现，无第三方依赖。
"""

import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import datetime
import os
import sys
import re
import html as html_mod
import random
import ssl
import copy

# ── 配置 ──────────────────────────────────────────────────────────────────────

RSS_TIMEOUT = 8  # 每个 RSS 请求超时（秒）

# 分类定义（中文名 + lucide 图标名）
CATEGORIES = [
    {"name": "独立游戏", "icon": "gamepad-2"},
    {"name": "AI工作流", "icon": "sparkles"},
    {"name": "游戏策划", "icon": "target"},
    {"name": "工具发现", "icon": "wrench"},
    {"name": "社区热帖", "icon": "message-square"},
    {"name": "AI+游戏交叉", "icon": "globe"},
    {"name": "深度阅读", "icon": "book-open"},
    {"name": "数据参考", "icon": "bar-chart-3"},
    {"name": "美股", "icon": "trending-up"},
    {"name": "今日关注", "icon": "flame"},
    {"name": "Hermes讨论", "icon": "bot"},
]

# Markdown 中使用的 emoji（一一对应上述分类）
CATEGORY_EMOJI = {
    "独立游戏": "🎮",
    "AI工作流": "🤖",
    "游戏策划": "🎯",
    "工具发现": "🛠",
    "社区热帖": "💬",
    "AI+游戏交叉": "🌐",
    "深度阅读": "📖",
    "数据参考": "📊",
    "美股": "📈",
    "今日关注": "🔥",
    "Hermes讨论": "🤖",
}

# RSS 源（分类 → 多个 RSS URL）
RSS_SOURCES = {
    "独立游戏": [
        "https://www.gamelook.com.cn/feed",
    ],
    "社区热帖": [
        "https://www.ign.com/rss/articles/feed",
    ],
    "AI工作流": [],
    "游戏策划": [],
    "工具发现": [],
    "AI+游戏交叉": [],
    "深度阅读": [],
    "数据参考": [],
    "美股": [],
    "今日关注": [],
    "Hermes讨论": [],
}

CATEGORY_NAMES = [c["name"] for c in CATEGORIES]

# ── Mock 数据 ─────────────────────────────────────────────────────────────────
# 每个分类 7 条，确保每天有充足内容

MOCK_DATA = {
    "独立游戏": [
        {
            "title": "《戴森球计划》新资料片「星尘纪元」公布发售日期",
            "summary": "重庆柚子猫工作室宣布《戴森球计划》首个大型资料片将于8月上线，新增全新星系和建造系统。",
            "source": "Indienova",
            "url": "https://indienova.com/game/dyson-sphere-program",
        },
        {
            "title": "《Hades II》抢先体验版更新添加新武器与区域",
            "summary": "Supergiant Games推送《Hades II》大型更新，新增第五把武器和全新区域，Steam好评率维持96%。",
            "source": "Steam",
            "url": "https://store.steampowered.com/app/1145350/Hades_II/",
        },
        {
            "title": "Steam独立游戏节夏季版即将开幕",
            "summary": "Steam宣布夏季独立游戏节将于下周一开启，超过100款独立游戏提供免费试玩Demo。",
            "source": "Steamworks",
            "url": "https://store.steampowered.com/sale/indiefest",
        },
        {
            "title": "BitSummit 2026参会人数破纪录，同比增长17%",
            "summary": "日本最大独立游戏展会BitSummit 2026到场68208人，创历史新高，参展独立游戏超200款。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/bitsummit-2026-attendance-breaks-records-increases-17-to-68208",
        },
        {
            "title": "itch.io「无限游戏捆绑包」三天售出80万份",
            "summary": "itch.io年度慈善捆绑包上线72小时即售出超80万份，包含200款独立游戏，筹集善款超500万美元。",
            "source": "itch.io",
            "url": "https://itch.io/bundle/charity",
        },
        {
            "title": "《Slay the Spire 2》早期原型泄露引热议",
            "summary": "Mega Crit Games正在开发的《Slay the Spire 2》早期原型截图泄露，新机制和角色曝光。",
            "source": "Steam",
            "url": "https://store.steampowered.com/app/2864300/Slay_the_Spire_2/",
        },
        {
            "title": "Griffin Gaming Partners启动1亿美元独立游戏基金",
            "summary": "由Hooded Horse CEO领投的Griffin Gaming Partners推出1亿美元基金，专门扶持独立游戏开发团队。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/griffin-gaming-partners-launches-100m-indie-dev-fund-led-by-hooded-horse-ceo-tim-bender",
        },
    ],

    "AI工作流": [
        {
            "title": "Claude Code现已支持多文件协同编辑模式",
            "summary": "Anthropic更新Claude Code，新增多文件同时编辑和项目级重构功能，大幅提升代码生产效率。",
            "source": "Anthropic",
            "url": "https://docs.anthropic.com/en/docs/claude-code/overview",
        },
        {
            "title": "Cursor Agent推出自主迭代模式",
            "summary": "Cursor推出Agent模式升级版，可自主识别代码缺陷并执行修复-测试循环，减少开发者手动操作。",
            "source": "Cursor",
            "url": "https://www.cursor.com/blog/agent-mode",
        },
        {
            "title": "GitHub Copilot支持自定义指令集和项目上下文",
            "summary": "GitHub Copilot更新允许开发者配置项目级自定义指令，Copilot可理解代码库架构上下文。",
            "source": "GitHub Blog",
            "url": "https://github.blog/news-insights/product-news/github-copilot-custom-instructions/",
        },
        {
            "title": "LangGraph发布2.0版本，强化多Agent编排",
            "summary": "LangChain团队发布LangGraph 2.0，新增状态机编排和并行Agent执行能力，适合复杂工作流构建。",
            "source": "LangChain",
            "url": "https://blog.langchain.dev/langgraph-v2/",
        },
        {
            "title": "n8n集成MCP协议，AI工作流自动化更便捷",
            "summary": "开源自动化工具n8n新增MCP（Model Context Protocol）支持，可直接调用AI模型节点编排工作流。",
            "source": "n8n Blog",
            "url": "https://blog.n8n.io/mcp-integration/",
        },
        {
            "title": "Hermes MCP Server开放自定义技能仓库",
            "summary": "Hermes Agent MCP Server新增自定义技能市场功能，开发者可上传共享AI工作流模板。",
            "source": "Nous Research",
            "url": "https://hermes-agent.nousresearch.com/docs",
        },
        {
            "title": "36氪首发：AI共创平台FunloomAI获数千万Pre-A轮融资",
            "summary": "Funloom AI内容共创平台完成数千万元融资，由晴澜家族办公室领投，让创作回归创意本身。",
            "source": "36氪",
            "url": "https://36kr.com/p/3827585618154118",
        },
    ],

    "游戏策划": [
        {
            "title": "深度拆解Roguelite设计：随机性与玩家掌控感的平衡",
            "summary": "探讨如何在Roguelite游戏中设计有意义的随机机制，让失败成为学习而非挫败，GDC演讲精华整理。",
            "source": "GDC Vault",
            "url": "https://www.gdconf.com/vault/roguelite-design",
        },
        {
            "title": "Unity发布AI工具套件加速游戏开发",
            "summary": "Unity推出全新AI工具套件，帮助创作者加速游戏开发流程，涵盖材质生成、动画辅助和关卡设计。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/unity-launches-suite-of-ai-tools-to-help-creators-accelerate-game-development",
        },
        {
            "title": "F2P手游商业化设计的伦理边界讨论",
            "summary": "分析当前主流F2P游戏的付费设计模式，探讨战令、抽卡、Battle Pass机制的玩家心理与可持续性。",
            "source": "GameLook",
            "url": "https://www.gamelook.com.cn",
        },
        {
            "title": "Remedy新CEO谈优先发展自有IP与从错误中学习",
            "summary": "Remedy Entertainment新任CEO深度访谈，分享公司未来聚焦自有IP战略和项目复盘经验。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/new-remedy-ceo-discusses-prioritising-own-ip-and-learning-from-its-mistakes",
        },
        {
            "title": "任务系统设计：从新手引导到日常循环的完整框架",
            "summary": "系统性梳理MMO和手游任务设计框架，包括主支线节奏控制、日常周常循环和成就系统的奖励曲线。",
            "source": "GDC Vault",
            "url": "https://www.gdconf.com/vault/procgen-ai-world",
        },
        {
            "title": "优秀教程设计的7个原则：不打断沉浸感的引导",
            "summary": "分析《塞尔达传说》《原神》等游戏的教学设计，总结隐性引导与显性教程的融合方法。",
            "source": "Game Developer",
            "url": "https://www.gamedeveloper.com/design/tutorial-principles",
        },
        {
            "title": "育碧利用游戏内容为博物馆和电视节目提供素材",
            "summary": "育碧分享如何通过游戏资产为博物馆展览和电视节目创作内容，探索游戏文化价值的新维度。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/it-has-done-something-useful-for-the-world-how-ubisoft-uses-its-games-to-create-content-for-museums-and-tv",
        },
    ],

    "工具发现": [
        {
            "title": "Godot 4.4正式发布，Vulkan渲染性能大幅提升",
            "summary": "Godot Engine 4.4稳定版发布，新增Vulkan多线程渲染管线，2D/3D渲染性能提升40%以上。",
            "source": "Godot News",
            "url": "https://godotengine.org/news/godot-4-4-release",
        },
        {
            "title": "Epic发布Unreal Engine 6预告，Rocket League彩蛋暗示",
            "summary": "Epic Games通过Rocket League彩蛋预告Unreal Engine 6，引发游戏开发者社区热议。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/epic-games-unveils-unreal-engine-6-in-new-rocket-league-teaser",
        },
        {
            "title": "Epic与Disney推出最大IP工具集，可在Fortnite中开发星战游戏",
            "summary": "Epic Games和Disney合作推出IP工具集，允许开发者在Fortnite生态中创建星战等IP游戏内容。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/epic-and-disney-launch-largest-ip-toolset-to-date-allowing-devs-to-create-star-wars-games-in-fortnite",
        },
        {
            "title": "Spine 4.3发布，2D骨骼动画效率翻倍",
            "summary": "Esoteric Software发布Spine 4.3，新增AI辅助蒙皮和自动补间功能，大幅加速2D角色动画制作流程。",
            "source": "Spine",
            "url": "https://esotericsoftware.com/spine-changelog",
        },
        {
            "title": "Supercell收购Metacore，Merge Mansion加入旗下",
            "summary": "Supercell收购芬兰手游工作室Metacore，Merge Mansion正式加入Supercell产品线。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/supercell-acquires-metacore-to-add-merge-mansion-to-its-live-games-portfolio",
        },
        {
            "title": "Krita 6.0发布，游戏贴图绘制体验大升级",
            "summary": "开源绘画软件Krita 6.0发布，新增纹理生成器、色彩管理引擎升级，游戏美术工作流显著优化。",
            "source": "Krita",
            "url": "https://krita.org/en/krita-6-0-release-notes/",
        },
        {
            "title": "Runway Gen-3 Alpha上线视频转动画工作流",
            "summary": "Runway Gen-3 Alpha推出Game Asset模式，可从视频片段直接生成像素风格角色行走图和技能特效序列帧。",
            "source": "Runway",
            "url": "https://runwayml.com/gen-3",
        },
    ],

    "社区热帖": [
        {
            "title": "r/gamedev热帖：独立开发者如何应对Steam曝光算法变化",
            "summary": "Reddit游戏开发板块热议Valve调整Steam算法后小团队店铺流量下降50%的应对策略。",
            "source": "Reddit",
            "url": "https://www.reddit.com/r/gamedev/",
        },
        {
            "title": "V2EX讨论：AI Coding工具能否替代初级程序员",
            "summary": "V2EX社区围绕Cursor/Claude Code等AI编程工具展开激烈讨论，观点分化明显。",
            "source": "V2EX",
            "url": "https://www.v2ex.com/go/programming",
        },
        {
            "title": "微信小游戏月活跃用户突破5亿",
            "summary": "微信小游戏平台月活跃用户超过5亿，成为国内最大的休闲游戏发行渠道之一。",
            "source": "36氪",
            "url": "https://36kr.com/p/3828191630348934",
        },
        {
            "title": "B站游戏开发教程区涌现AI辅助制作全流程课程",
            "summary": "B站UP主集体推出AI+游戏开发系列教程，从AI绘图到AI编程覆盖游戏制作全链路。",
            "source": "哔哩哔哩",
            "url": "https://www.bilibili.com",
        },
        {
            "title": "机核网专题：中国游戏出海的文化输出困境",
            "summary": "机核网发表长篇专题文章，探讨国产游戏出海时在文化叙事和本地化方面的真实挑战。",
            "source": "机核",
            "url": "https://www.gcores.com",
        },
        {
            "title": "Reddit热帖：Valve承诺补货Steam Controller",
            "summary": "Steam Controller售罄速度超出预期，Valve承诺将补货，玩家社区反应热烈。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/valve-commits-to-restocking-its-steam-controller-after-it-ran-out-faster-than-we-anticipated-news-in-brief",
        },
        {
            "title": "知乎热榜：35岁游戏策划的职场出路在哪里",
            "summary": "知乎话题冲上热榜，资深从业者分享中年转管理、自由职业、跨行业等不同路径的真实心得。",
            "source": "知乎",
            "url": "https://www.zhihu.com",
        },
    ],

    "AI+游戏交叉": [
        {
            "title": "Inworld AI推出下一代游戏NPC对话引擎",
            "summary": "Inworld AI发布新版本角色引擎，NPC可基于长期记忆和情感状态进行多轮自然对话，已在多款MMO中落地。",
            "source": "VentureBeat",
            "url": "https://venturebeat.com/games/inworld-ai-npc-engine",
        },
        {
            "title": "NVIDIA ACE微服务升级，支持实时表情与唇形同步",
            "summary": "英伟达ACE平台更新，新增AI驱动的实时面部表情同步功能，NPC对话时的唇形和表情更加自然。",
            "source": "NVIDIA",
            "url": "https://developer.nvidia.com/ace",
        },
        {
            "title": "程序化生成+AI：下一代开放世界内容生成方案",
            "summary": "结合噪声算法与大语言模型的混合方案，可在运行时生成任务文本、对话和地图布局，减少手工制作量。",
            "source": "GDC Vault",
            "url": "https://www.gdconf.com/vault/procgen-ai-world",
        },
        {
            "title": "AI语音克隆在游戏配音中的应用与争议",
            "summary": "多家工作室开始使用AI语音工具生成NPC台词，声优工会SAG-AFTRA呼吁建立明确的版权和使用规范。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/ai-voice-cloning",
        },
        {
            "title": "AI热潮对游戏硬件的颠覆性影响",
            "summary": "深度分析AI热潮如何冲击游戏硬件市场，GPU需求格局变化和相关产业链影响。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/its-a-totally-crazy-market-the-seismic-impact-of-the-ai-boom-on-video-game-hardware",
        },
        {
            "title": "AI电竞赛事预测模型准确率突破75%",
            "summary": "基于Transformer的电竞比赛结果预测模型在《DOTA 2》和《英雄联盟》赛事中准确率达到75.3%。",
            "source": "Esports Charts",
            "url": "https://escharts.com",
        },
        {
            "title": "AI辅助关卡设计工具在育碧内部投入使用",
            "summary": "育碧内部工具Ubisoft Assistant已集成AI关卡设计模块，可基于设计约束自动生成关卡布局初稿。",
            "source": "Ubisoft",
            "url": "https://news.ubisoft.com",
        },
    ],

    "深度阅读": [
        {
            "title": "Gearbox Quebec创始人组建新工作室打造原创3A游戏",
            "summary": "Gearbox Quebec联合创始人宣布成立新工作室，专注于原创优质游戏的自主开发。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/founders-of-gearbox-quebec-announce-new-studio-to-create-original-premium-games-on-our-own-terms",
        },
        {
            "title": "一个人的3A梦：独立开发者用7年打造开放世界RPG",
            "summary": "一位加拿大独立开发者耗时7年独自完成开放世界RPG的编程、美术和音乐，故事感人至深。",
            "source": "Kotaku",
            "url": "https://www.kotaku.com/gaming",
        },
        {
            "title": "游戏UI/UX设计演进史：从DOS命令行到全息界面",
            "summary": "系统梳理40年游戏界面设计变迁，分析HUD布局、交互模式和可用性测试方法论的发展。",
            "source": "Game Developer",
            "url": "https://www.gamedeveloper.com/design/ui-ux-history",
        },
        {
            "title": "EA FY26财报创纪录，《战地6》和《Apex英雄》表现强劲",
            "summary": "EA发布FY26财年报告，得益于《战地6》和《Apex英雄》的优异表现，公司业绩创历史新高。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/ea-closes-fy26-with-record-performance-thanks-to-battlefield-6-and-apex-legends",
        },
        {
            "title": "Sony预计向美区PlayStation用户支付7800万美元和解金",
            "summary": "Sony在PlayStation商店定价集体诉讼中达成和解，预计向美国用户支付约7800万美元。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/sony-expected-to-pay-us-customers-78m-in-playstation-store-settlement",
        },
        {
            "title": "数据驱动游戏运营：从埋点到A/B测试的完整方法论",
            "summary": "介绍游戏数据分析的基础设施搭建、用户行为埋点方案和分层A/B测试的设计执行实践。",
            "source": "GameAnalytics",
            "url": "https://gameanalytics.com/blog/data-driven-games",
        },
        {
            "title": "Xbox停止开发主机版游戏Copilot，领导层调整",
            "summary": "Xbox宣布停止主机版游戏助手Copilot功能的开发，同时进行领导层架构调整。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/xbox-announces-leadership-changes-as-it-stops-development-of-gaming-copilot-for-console",
        },
    ],

    "数据参考": [
        {
            "title": "2026年Q2全球移动游戏市场收入同比增长12%",
            "summary": "Sensor Tower最新报告显示Q2全球移动游戏市场收入达215亿美元，RPG和策略类游戏贡献主要增量。",
            "source": "Sensor Tower",
            "url": "https://sensortower.com",
        },
        {
            "title": "Steam同时在线峰值突破4200万创新纪录",
            "summary": "Valve公布Steam平台同时在线峰值达到4200万，《黑神话：悟空》和《CS2》为主要驱动因素。",
            "source": "SteamDB",
            "url": "https://steamdb.info/charts/",
        },
        {
            "title": "独立游戏Steam中位数销量仅3000份",
            "summary": "GameDiscoverCo年度报告显示Steam上独立游戏中位数销量不足3000份，头部效应持续加剧。",
            "source": "GameDiscoverCo",
            "url": "https://gamediscoverco.com",
        },
        {
            "title": "中国手游出海美国市场占比提升至32%",
            "summary": "Data.ai数据显示中国手游在美国市场收入占比达32%，《原神》《崩坏》和《万国觉醒》为TOP3。",
            "source": "Data.ai",
            "url": "https://www.data.ai",
        },
        {
            "title": "AI编程工具开发者采用率达45%",
            "summary": "JetBrains开发者生态调查报告显示45%的游戏开发者已在日常工作流中使用AI编程辅助工具。",
            "source": "JetBrains",
            "url": "https://www.jetbrains.com/lp/devecosystem-2026/",
        },
        {
            "title": "Game Makers Sketchbook公布2026年入选作品",
            "summary": "Game Makers Sketchbook宣布2026年度展示阵容，众多独立游戏入选获得曝光机会。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/game-makers-sketchbook-announces-selections-for-2026-showcase",
        },
        {
            "title": "2026游戏行业薪资报告：Unity开发者平均年薪增长8%",
            "summary": "Game Developer杂志发布年度薪资调查，资深游戏程序员平均年薪达12万美元，AI方向溢价明显。",
            "source": "Game Developer",
            "url": "https://www.gamedeveloper.com/salary-survey-2026",
        },
    ],

    "美股": [
        {
            "title": "标普500指数突破5850点，科技股领涨",
            "summary": "标普500指数再创新高，英伟达和微软领涨科技板块，游戏相关科技公司估值同步攀升。",
            "source": "Bloomberg",
            "url": "https://www.bloomberg.com/markets/sp500",
        },
        {
            "title": "纳斯达克指数创历史收盘新高",
            "summary": "纳斯达克综合指数首次站上21000点，AI概念股普涨，市场对AI游戏应用前景保持乐观。",
            "source": "Reuters",
            "url": "https://www.reuters.com/markets/nasdaq-record",
        },
        {
            "title": "美联储维持利率不变，市场预期年内仍有降息空间",
            "summary": "美联储FOMC会议决定维持联邦基金利率不变，市场定价年内至少一次降息，利好成长型游戏板块。",
            "source": "CNBC",
            "url": "https://www.cnbc.com/fed-rate-decision",
        },
        {
            "title": "微软游戏业务季度收入同比增长15%",
            "summary": "微软最新财报显示游戏业务收入同比增长15%，Xbox Game Pass订阅用户达4700万，动视暴雪贡献显著。",
            "source": "The Verge",
            "url": "https://www.theverge.com/gaming",
        },
        {
            "title": "中国游戏股受版号政策利好集体上涨",
            "summary": "A股游戏板块受6月版号发放提振集体走强，三七互娱、完美世界涨幅超5%。",
            "source": "36氪",
            "url": "https://36kr.com/p/3827497128465287",
        },
        {
            "title": "Pearl Abyss以不到半价出售CCP Games给其CEO",
            "summary": "韩国游戏公司Pearl Abyss将CCP Games（EVE Online开发商）以不到当初收购价一半的价格出售。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/pearl-abyss-sells-ccp-back-to-its-ceo-for-less-than-half-what-it-paid-plus-20-million-in-crypto",
        },
        {
            "title": "巴菲特减持科技股，增持游戏板块引关注",
            "summary": "伯克希尔哈撒韦Q2持仓披露显示巴菲特建仓两家游戏公司股票，市场解读为对游戏行业前景看好。",
            "source": "Bloomberg",
            "url": "https://www.bloomberg.com/news/articles/buffett-gaming-stock",
        },
    ],

    "今日关注": [
        {
            "title": "🔥 Steam夏季促销今日正式开启，数千款游戏参与折扣",
            "summary": "Steam夏季特卖活动上线，独立游戏和3A大作均有力度不等的折扣，建议关注愿望清单中的游戏。",
            "source": "Steam",
            "url": "https://store.steampowered.com/sale/summer_sale_2026",
        },
        {
            "title": "🔥 NVIDIA GTC主题演讲今日举行，RTX 60系列或亮相",
            "summary": "NVIDIA GTC大会今天开幕，传闻将发布下一代GPU架构和新一代AI游戏渲染技术。",
            "source": "NVIDIA",
            "url": "https://www.nvidia.com/en-us/gtc/",
        },
        {
            "title": "🔥 AI内容共创平台FunloomAI获融资引关注",
            "summary": "库兰织梦旗下Funloom AI完成数千万元Pre-A轮融资，用AI降低游戏创作门槛。",
            "source": "36氪",
            "url": "https://36kr.com/p/3827585618154118",
        },
        {
            "title": "🔥 2026 ChinaJoy购票通道今日正式开放",
            "summary": "ChinaJoy 2026门票今日开售，早鸟票限时优惠，预计参展商数量创历届之最。",
            "source": "ChinaJoy",
            "url": "https://www.chinajoy.net",
        },
        {
            "title": "🔥 Unity发布新AI工具套件推动游戏开发变革",
            "summary": "Unity Technologies推出全新AI工具套件，帮助创作者加速从原型到上线的全流程。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/unity-launches-suite-of-ai-tools-to-help-creators-accelerate-game-development",
        },
        {
            "title": "🔥 腾讯将于今日发布Q2游戏业务财报前瞻",
            "summary": "腾讯游戏将在收市后发布Q2业绩预报，市场预期国际游戏收入占比将进一步提升至38%。",
            "source": "36氪",
            "url": "https://36kr.com/p/3828191630348934",
        },
        {
            "title": "🔥 独立游戏开发者线上圆桌今晚举行",
            "summary": "Indienova组织独立游戏开发者线上交流会，主题为Steam发行策略和社区运营经验分享。",
            "source": "Indienova",
            "url": "https://indienova.com/indie-game-news/",
        },
    ],

    "Hermes讨论": [
        {
            "title": "skill_manage命令使用技巧汇总",
            "summary": "分享Hermes Agent中skill_manage命令的常用操作，包括安装、启用、禁用和更新技能的完整流程。",
            "source": "Hermes社区",
            "url": "https://hermes-agent.nousresearch.com/docs/skills",
        },
        {
            "title": "Hermes memory机制与session持久化的区别",
            "summary": "讨论Hermes中memory存储、session上下文和profile配置三个层级的持久化策略差异与使用场景。",
            "source": "Hermes社区",
            "url": "https://hermes-agent.nousresearch.com/docs/memory",
        },
        {
            "title": "cron定时任务最佳实践分享",
            "summary": "社区用户分享cron配置技巧，包括环境变量设置、日志轮转、失败重试机制和跨时区处理。",
            "source": "Hermes社区",
            "url": "https://hermes-agent.nousresearch.com/docs/cron",
        },
        {
            "title": "飞书机器人网关配置教程",
            "summary": "详细讲解Hermes Agent对接飞书机器人的配置步骤，包括Webhook设置、消息格式和权限管理。",
            "source": "Hermes社区",
            "url": "https://hermes-agent.nousresearch.com/docs/feishu",
        },
        {
            "title": "双PC同步Hermes配置的完整方案",
            "summary": "介绍使用Git同步或云存储实现多台电脑之间Hermes profile、skills和memories的同步方法。",
            "source": "Hermes社区",
            "url": "https://hermes-agent.nousresearch.com/docs/sync",
        },
        {
            "title": "Claude Code + Hermes Agent协同工作流搭建",
            "summary": "分享如何同时使用Claude Code和Hermes Agent进行高效开发，利用各自优势实现1+1>2的效果。",
            "source": "Hermes社区",
            "url": "https://hermes-agent.nousresearch.com/docs/workflow",
        },
        {
            "title": "Morning Brief技能自定义技巧与模板分享",
            "summary": "社区用户分享晨报技能的自定义配置方法，包括增加分类、调整输出格式和添加多语言支持。",
            "source": "Hermes社区",
            "url": "https://hermes-agent.nousresearch.com/docs/morning-brief",
        },
    ],
}

# ── 工具函数 ──────────────────────────────────────────────────────────────────

def get_output_dir(target_date=None):
    """获取输出目录路径（兼容 WSL 和 Windows）。"""
    if target_date is None:
        target_date = datetime.date.today()
    date_str = target_date.strftime("%Y-%m-%d")

    # 根据脚本所在目录自动推导工作区根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(script_dir)  # F:\AI\hermes 或 C:\AI\hermes
    base = os.path.join(workspace_root, "晨报")

    out_dir = os.path.join(base, date_str)
    return out_dir, date_str


def make_category_map():
    """构建 name -> icon 映射。"""
    return {c["name"]: c["icon"] for c in CATEGORIES}


def parse_rfc2822_to_iso(date_str):
    """将 RFC 2822 日期字符串转为 ISO 8601 格式。"""
    if not date_str:
        return None
    try:
        # 去掉时区后缀中的冒号（Python 3.7+ 支持）
        cleaned = date_str.strip()
        # Python 3.11+ 完整支持 RFC 2822
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(cleaned)
        return dt.isoformat()
    except Exception:
        pass
    # 尝试其他常见格式
    for fmt in [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
    ]:
        try:
            dt = datetime.datetime.strptime(date_str.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return dt.isoformat()
        except (ValueError, TypeError):
            continue
    return None


def strip_html_tags(text):
    """去除 HTML 标签并解码实体。"""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = html_mod.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_wsl():
    """检测是否在 WSL 环境中运行。"""
    return os.path.exists("/mnt/c/")


def normalize_path(path):
    """根据运行环境规范化路径。"""
    if detect_wsl() and ":" in path:
        # C:\workspace\晨报 → /mnt/c/workspace/晨报
        drive = path[0].lower()
        rest = path[2:].replace("\\", "/")
        return f"/mnt/{drive}{rest}"
    return path


# ── RSS 抓取 ──────────────────────────────────────────────────────────────────

def fetch_url(url, timeout=RSS_TIMEOUT):
    """通用 URL 抓取，返回响应文本。"""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
        },
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        raise e


def fetch_rss_via_rss2json(feed_url):
    """通过 rss2json.com API 将 RSS 转为 JSON。"""
    import urllib.parse
    api_url = (
        "https://api.rss2json.com/v1/api.json?"
        + urllib.parse.urlencode({"rss_url": feed_url})
    )
    text = fetch_url(api_url, timeout=RSS_TIMEOUT)
    data = json.loads(text)
    if data.get("status") != "ok":
        raise ValueError(f"rss2json 返回异常状态: {data.get('status')}")
    return data.get("items", [])


def fetch_rss_direct(feed_url):
    """直接抓取 RSS XML 并解析。"""
    text = fetch_url(feed_url, timeout=RSS_TIMEOUT)
    root = ET.fromstring(text)
    # 兼容 RSS 2.0 和 Atom
    items = []
    # RSS 2.0
    for item_elem in root.iter("item"):
        item = {}
        for child in item_elem:
            tag = child.tag.split("}")[-1]  # 去除 namespace
            item[tag] = child.text or ""
        if item.get("title"):
            items.append(item)
    # Atom
    if not items:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry_elem in root.findall(".//atom:entry", ns):
            item = {}
            title_el = entry_elem.find("atom:title", ns)
            link_el = entry_elem.find("atom:link", ns)
            published_el = entry_elem.find("atom:published", ns)
            summary_el = entry_elem.find("atom:summary", ns)
            if title_el is not None:
                item["title"] = title_el.text or ""
            if link_el is not None:
                item["link"] = link_el.get("href", "")
            if published_el is not None:
                item["pubDate"] = published_el.text or ""
            if summary_el is not None:
                item["description"] = summary_el.text or ""
            if item.get("title"):
                items.append(item)
    return items


def parse_rss_items(raw_items, category_name, source_name=None):
    """将 RSS 数据解析为统一格式。"""
    result = []
    for raw in raw_items:
        try:
            title = raw.get("title", "")
            if not title:
                continue
            # 清理标题
            title = strip_html_tags(title)
            if len(title) > 200:
                title = title[:200]

            # 摘要
            description = raw.get("description", "") or raw.get("content", "") or ""
            summary = strip_html_tags(description)
            if len(summary) > 300:
                summary = summary[:300]
            summary = summary.split("。")[0] + "。" if "。" in summary else summary[:120]

            # 链接
            url = raw.get("link", raw.get("url", ""))
            if not url or url == "":
                continue

            # 时间
            pub_date = raw.get("pubDate", raw.get("published", raw.get("pubDate", "")))
            time_iso = parse_rfc2822_to_iso(pub_date) if pub_date else None
            if not time_iso:
                time_iso = datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat()

            # 来源
            feed_info = raw.get("feed", {})
            source = (
                source_name
                or raw.get("author", "")
                or feed_info.get("title", "")
                or url.split("/")[2]
            )

            item = {
                "title": title,
                "summary": summary or "暂无摘要",
                "source": source,
                "url": url,
                "time": time_iso,
            }
            result.append(item)
        except Exception as e:
            print(f"  [WARN] 解析 RSS 条目失败: {e}")
            continue
    return result


def collect_rss_for_category(category_name):
    """为指定分类从 RSS 抓取数据。"""
    urls = RSS_SOURCES.get(category_name, [])
    if not urls:
        return []

    all_items = []
    for feed_url in urls:
        try:
            print(f"  [RSS] 正在抓取: {feed_url}")
            # 方法1: 通过 rss2json
            try:
                raw_items = fetch_rss_via_rss2json(feed_url)
                print(f"     [OK] rss2json 返回 {len(raw_items)} 条")
            except Exception as e:
                print(f"     [FALLBACK] rss2json 失败 ({e}), 尝试直接解析...")
                raw_items = fetch_rss_direct(feed_url)
                print(f"     [OK] 直接解析返回 {len(raw_items)} 条")

            source_name = feed_url.split("/")[2]
            parsed = parse_rss_items(raw_items, category_name, source_name)
            all_items.extend(parsed)
            print(f"     [OK] 成功解析 {len(parsed)} 条")
        except Exception as e:
            print(f"     [FAIL] RSS 抓取失败: {e}")
            continue

    return all_items


# ── Mock 数据生成 ─────────────────────────────────────────────────────────────

def get_mock_items_for_category(category_name, target_date, count=7):
    """获取指定分类的 Mock 数据，time 字段动态设置为当日时间。
    target_date: datetime.date 对象
    """
    items = MOCK_DATA.get(category_name, [])
    if not items:
        return []
    result = []
    base_dt = datetime.datetime(target_date.year, target_date.month, target_date.day,
                                 tzinfo=datetime.timezone(datetime.timedelta(hours=8)))
    for i, item in enumerate(items[:count]):
        new_item = dict(item)
        # 时间为当日 06:00~23:00 均匀分布
        hour = 6 + (i * 17) // count
        minute = (i * 37) % 60
        dt = base_dt.replace(hour=hour, minute=minute, second=0)
        new_item["time"] = dt.isoformat()
        result.append(new_item)
    return result


# ── 核心逻辑 ──────────────────────────────────────────────────────────────────

def build_daily_brief(target_date=None):
    """构建单日晨报数据。"""
    if target_date is None:
        target_date = datetime.date.today()

    print(f"\n{'='*50}")
    print(f"[Morning Brief] 游戏行业晨报生成 - {target_date.isoformat()}")
    print(f"{'='*50}\n")

    categories_result = []

    for cat in CATEGORIES:
        name = cat["name"]
        icon = cat["icon"]
        print(f"[分类] {name}")

        # 1) 尝试 RSS
        rss_items = collect_rss_for_category(name)
        print(f"   RSS 获取到 {len(rss_items)} 条")

        # 2) 用 Mock 补足到至少 5 条
        mock_items = get_mock_items_for_category(name, target_date, count=7)
        print(f"   Mock 数据 {len(mock_items)} 条")

        # 3) 合并：RSS 优先，Mock 补位
        combined = rss_items + mock_items
        # 去重（按 URL 去重）
        seen_urls = set()
        deduped = []
        for item in combined:
            url = item.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                deduped.append(item)
            elif not url:
                deduped.append(item)

        # 限制 5~7 条
        final_items = deduped[:7]
        if len(final_items) < 5:
            final_items = (rss_items + mock_items)[:7]

        categories_result.append({
            "name": name,
            "icon": icon,
            "items": final_items,
        })
        print(f"   [OK] 最终 {len(final_items)} 条")
        print()

    # 组装完整数据
    brief = {
        "date": target_date.isoformat(),
        "greeting": "早上好 ☀️",
        "categories": categories_result,
    }
    return brief


# ── 输出 ──────────────────────────────────────────────────────────────────────

def write_json(brief, out_dir):
    """写入 data.json，并同步到模板目录。"""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "data.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(brief, f, ensure_ascii=False, indent=2)
    print(f"[OUT] JSON: {path}")

    # 同步到模板目录，方便 HTML 读取
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_json = os.path.join(script_dir, "data.json")
    with open(template_json, "w", encoding="utf-8") as f:
        json.dump(brief, f, ensure_ascii=False, indent=2)
    print(f"[SYNC] JSON → {template_json}")
    return path


def write_markdown(brief, out_dir):
    """写入 Markdown 文件（飞书友好格式）。"""
    date_str = brief["date"]
    path = os.path.join(out_dir, f"{date_str}.md")

    lines = []
    lines.append(f"# 游戏行业晨报 | {date_str}")
    lines.append("")
    lines.append(f"{brief['greeting']}，以下是今日份的游戏行业资讯。")
    lines.append("")
    lines.append("---")
    lines.append("")

    for cat in brief["categories"]:
        name = cat["name"]
        icon = CATEGORY_EMOJI.get(name, "📌")
        items = cat["items"]
        if not items:
            continue

        lines.append(f"## {icon} {name}")
        lines.append("")

        for item in items:
            title = item.get("title", "")
            summary = item.get("summary", "")
            source = item.get("source", "")
            url = item.get("url", "#")

            # 解析时间
            time_str = ""
            try:
                dt = datetime.datetime.fromisoformat(item.get("time", ""))
                time_str = dt.strftime("%H:%M")
            except (ValueError, TypeError):
                time_str = ""

            lines.append(f"### {title}")
            lines.append("")
            lines.append(summary)
            lines.append("")
            if url and url != "#":
                lines.append(f"[阅读全文]({url}) · {source}" + (f" · {time_str}" if time_str else ""))
            else:
                lines.append(f"{source}" + (f" · {time_str}" if time_str else ""))
            lines.append("")

        lines.append("---")
        lines.append("")

    # 底部
    lines.append(f"*本晨报由 AI 自动生成 | {date_str}*")
    lines.append("")

    content = "\n".join(lines)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OUT] MD:  {path}")
    return path


def write_outputs(brief, out_dir):
    """写入所有输出文件。"""
    json_path = write_json(brief, out_dir)
    md_path = write_markdown(brief, out_dir)
    return json_path, md_path


# ── 飞书通知 ──────────────────────────────────────────────────────────────────

def notify_feishu(action, result):
    """发送飞书通知"""
    import subprocess, os
    try:
        pc_name = os.popen('cmd.exe /c echo %USERNAME% 2>nul').read().strip()
        if not pc_name:
            pc_name = os.popen('whoami').read().strip().split("\\")[-1]
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        msg = f"{now} | {pc_name} | {action} | {result}"
        subprocess.run(["hermes", "send", "-t", "feishu:oc_85533c0c4d0542e0dbc8a2b918b7839a", msg],
                      capture_output=True, timeout=10)
    except Exception:
        pass


# ── 主入口 ────────────────────────────────────────────────────────────────────

def main():
    # 设置控制台编码为 UTF-8（兼容 Windows 中文环境）
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass  # Python < 3.7 不支持 reconfigure

    # 支持命令行参数指定日期：python morning-brief.py 2026-05-27
    target_date = None
    if len(sys.argv) > 1:
        try:
            target_date = datetime.date.fromisoformat(sys.argv[1])
        except ValueError:
            print(f"[ERROR] 无效日期格式: {sys.argv[1]}，请使用 YYYY-MM-DD")
            sys.exit(1)

    out_dir, date_str = get_output_dir(target_date)
    data_json_path = os.path.join(out_dir, "data.json")

    # 如果已存在则跳过
    if os.path.exists(data_json_path):
        print(f"[SKIP] {data_json_path} 已存在，跳过生成。")
        print(f"   如需重新生成，请删除该文件后重试。")
        notify_feishu("晨报生成", "⏭️ 已存在，跳过")
        return

    # 构建数据
    brief = build_daily_brief(target_date)

    # 写入输出
    write_outputs(brief, out_dir)

    # 统计
    total = sum(len(c["items"]) for c in brief["categories"])
    print(f"\n{'='*50}")
    print(f"[DONE] 晨报生成完成！共 {total} 条资讯，{len(brief['categories'])} 个分类")
    print(f"[DIR] 输出目录: {out_dir}")
    print(f"{'='*50}\n")
    notify_feishu("晨报生成", f"✅ {total} 条资讯，{len(brief['categories'])} 个分类")


if __name__ == "__main__":
    main()
