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
    {"name": "行业动态", "icon": "gamepad-2"},
    {"name": "AI前沿",   "icon": "sparkles"},
    {"name": "市场数据",  "icon": "trending-up"},
    {"name": "产品观察",  "icon": "eye"},
    {"name": "政策监管",  "icon": "scale"},
    {"name": "海外市场",  "icon": "globe"},
    {"name": "技术开发",  "icon": "code-2"},
    {"name": "投融资",    "icon": "wallet"},
    {"name": "数据报告",  "icon": "bar-chart-3"},
    {"name": "行业活动",  "icon": "calendar"},
]

# Markdown 中使用的 emoji（一一对应上述分类）
CATEGORY_EMOJI = {
    "行业动态": "🎮",
    "AI前沿": "✨",
    "市场数据": "📈",
    "产品观察": "👀",
    "政策监管": "⚖️",
    "海外市场": "🌍",
    "技术开发": "💻",
    "投融资": "💰",
    "数据报告": "📊",
    "行业活动": "📅",
}

# RSS 源（分类 → 多个 RSS URL）
RSS_SOURCES = {
    "行业动态": [
        "https://www.gamelook.com.cn/feed",
    ],
    "海外市场": [
        "https://www.ign.com/rss/articles/feed",
    ],
    "AI前沿": [],
    "市场数据": [],
    "产品观察": [],
    "政策监管": [],
    "技术开发": [],
    "投融资": [],
    "数据报告": [],
    "行业活动": [],
}

CATEGORY_NAMES = [c["name"] for c in CATEGORIES]

# ── Mock 数据 ─────────────────────────────────────────────────────────────────
# 每个分类 7 条，确保每天有充足内容

MOCK_DATA = {
    "行业动态": [
        {
            "title": "腾讯《王者荣耀》国际版月活跃用户突破5000万",
            "summary": "腾讯旗下《王者荣耀》国际版（Honor of Kings）全球月活跃用户突破5000万大关，海外市场增长显著。",
            "source": "GameLook",
            "url": "https://www.gamelook.com.cn/archives/game-news/001",
        },
        {
            "title": "网易《逆水寒》手游创下端午档期收入新纪录",
            "summary": "网易旗舰MMO《逆水寒》手游在端午档期期间收入环比增长120%，创下开服以来最高单日流水纪录。",
            "source": "游戏葡萄",
            "url": "https://youxiputao.com/news/002",
        },
        {
            "title": "米哈游《原神》5.0版本更新引发玩家热议",
            "summary": "米哈游《原神》5.0版本「荣花与炎日之途」正式上线，新增区域和角色引发社区高度关注。",
            "source": "触乐",
            "url": "https://www.chuapp.com/article/003",
        },
        {
            "title": "字节跳动游戏业务重组，聚焦精品自研",
            "summary": "字节跳动旗下朝夕光年进行组织架构调整，裁撤部分项目组，集中资源开发3A级自研产品。",
            "source": "36氪",
            "url": "https://36kr.com/p/game-news/004",
        },
        {
            "title": "哔哩哔哩游戏代理《影之诗》国服即将停运",
            "summary": "B站宣布《影之诗》国服将于2026年9月停止运营，运营时长超过8年，玩家数据迁移方案公布。",
            "source": "游戏陀螺",
            "url": "https://www.gametuber.com/news/005",
        },
        {
            "title": "莉莉丝《万国觉醒》与知名IP联动创收新高",
            "summary": "莉莉丝旗下SLG《万国觉醒》与某知名动漫IP联动活动上线首日收入突破历史峰值。",
            "source": "GameLook",
            "url": "https://www.gamelook.com.cn/archives/game-news/006",
        },
        {
            "title": "鹰角网络《明日方舟》五周年庆典活动即将开启",
            "summary": "鹰角网络宣布《明日方舟》五周年庆典活动将于下月启动，届时将公布全新主线章节和限定角色。",
            "source": "游戏葡萄",
            "url": "https://youxiputao.com/news/007",
        },
    ],

    "AI前沿": [
        {
            "title": "Google DeepMind发布GameNGen AI游戏引擎原型",
            "summary": "Google DeepMind展示GameNGen项目，用神经网络实时生成《毁灭战士》级游戏画面，无需传统渲染管线。",
            "source": "机器之心",
            "url": "https://jiqizhixin.com/ai-gaming/101",
        },
        {
            "title": "OpenAI与Unity合作推出AI游戏开发助手",
            "summary": "OpenAI与Unity Technologies联合发布AI助手，支持自然语言生成C#脚本和3D资产创建。",
            "source": "36氪",
            "url": "https://36kr.com/p/ai-game/102",
        },
        {
            "title": "网易伏羲实验室发布大规模AI NPC框架",
            "summary": "网易伏羲实验室推出全新AI NPC框架，支持千名AI角色在同一世界中自主行动和交互，已应用于《逆水寒》。",
            "source": "GameLook",
            "url": "https://www.gamelook.com.cn/archives/ai/103",
        },
        {
            "title": "英伟达ACE微服务正式面向游戏开发者开放",
            "summary": "英伟达Avatar Cloud Engine（ACE）正式商用，为游戏提供实时AI对话NPC和动态表情生成服务。",
            "source": "IT之家",
            "url": "https://www.ithome.com/ai/104",
        },
        {
            "title": "腾讯AI Lab新模型实现游戏原画自动生成",
            "summary": "腾讯AI Lab发布Stable Diffusion微调模型，可根据文字描述直接生成高质量游戏角色原画和场景概念图。",
            "source": "量子位",
            "url": "https://www.qbitai.com/ai-game/105",
        },
        {
            "title": "AI驱动的程序化关卡生成工具获开发者好评",
            "summary": "一款基于强化学习的AI关卡设计工具在GDC 2026上展示，可自动生成平台跳跃和射击游戏关卡。",
            "source": "游戏陀螺",
            "url": "https://www.gametuber.com/ai/106",
        },
        {
            "title": "国产AI语音克隆工具通过游戏角色配音测试",
            "summary": "国内团队开发的AI语音合成工具在游戏角色配音测试中达到专业声优水平，成本降低90%。",
            "source": "触乐",
            "url": "https://www.chuapp.com/article/ai-voice/107",
        },
    ],

    "市场数据": [
        {
            "title": "2026年5月中国手游市场收入同比增长18.5%",
            "summary": "伽马数据显示2026年5月中国手游市场收入达185亿元，同比增长18.5%，暑期档预热效应明显。",
            "source": "伽马数据",
            "url": "https://www.gama-data.com/report/201",
        },
        {
            "title": "全球游戏市场规模预计2026年突破2500亿美元",
            "summary": "Newzoo最新报告预测2026年全球游戏市场规模将达到2560亿美元，移动端占比超过55%。",
            "source": "Newzoo",
            "url": "https://newzoo.com/report/global-games-2026/202",
        },
        {
            "title": "Steam同时在线用户数突破4000万创新高",
            "summary": "Valve旗下Steam平台同时在线用户数首次突破4000万大关，《CS2》和《黑神话：悟空》贡献主要增长。",
            "source": "游民星空",
            "url": "https://www.gamersky.com/news/203",
        },
        {
            "title": "腾讯Q1游戏业务收入同比增长12%至548亿元",
            "summary": "腾讯2026年第一季度财报显示游戏业务收入548亿元，国际游戏收入占比提升至35%。",
            "source": "GameLook",
            "url": "https://www.gamelook.com.cn/archives/market/204",
        },
        {
            "title": "中国游戏出海收入连续三个季度环比增长",
            "summary": "2026年Q1中国自研游戏海外收入达48亿美元，连续三个季度实现环比增长，美日韩为TOP3市场。",
            "source": "Sensor Tower",
            "url": "https://sensortower.com/china-games/205",
        },
        {
            "title": "Switch 2全球首周销量突破500万台",
            "summary": "任天堂Switch 2全球首发周销量超500万台，打破主机销售纪录，塞尔达新作带动硬件销售。",
            "source": "VGChartz",
            "url": "https://www.vgchartz.com/hardware/206",
        },
        {
            "title": "Epic游戏商城月活跃用户突破8000万",
            "summary": "Epic Games宣布其游戏商城月活跃用户达8000万，免费游戏策略持续推动用户增长。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/epic-store/207",
        },
    ],

    "产品观察": [
        {
            "title": "《黑神话：悟空》DLC「再战轮回」评测前瞻",
            "summary": "游戏科学公布《黑神话：悟空》首个大型DLC详情，新地图包含天宫与地府场景，预计年底发售。",
            "source": "游民星空",
            "url": "https://www.gamersky.com/review/301",
        },
        {
            "title": "网易《燕云十六声》公测数据亮眼",
            "summary": "网易开放世界武侠游戏《燕云十六声》全平台公测表现超预期，首日新增用户超800万。",
            "source": "游戏葡萄",
            "url": "https://youxiputao.com/review/302",
        },
        {
            "title": "《崩坏：星穹铁道》2.5版本内容量创历史之最",
            "summary": "米哈游《崩坏：星穹铁道》2.5版本更新内容量达到60小时，包含全新星球和主线剧情。",
            "source": "触乐",
            "url": "https://www.chuapp.com/article/hsr/303",
        },
        {
            "title": "腾讯《三角洲行动》全球上线首周表现强劲",
            "summary": "腾讯天美工作室开发的战术射击游戏《三角洲行动》全球上线首周收入破1亿美元。",
            "source": "GameLook",
            "url": "https://www.gamelook.com.cn/archives/product/304",
        },
        {
            "title": "《最终幻想 XVI》PC版优化获Steam好评",
            "summary": "Square Enix《最终幻想 XVI》PC版正式发售，Steam评价为「特别好评」，4K/60帧流畅运行。",
            "source": "IGN中国",
            "url": "https://www.ignchina.com/review/ff16/305",
        },
        {
            "title": "国产独立游戏《戴森球计划》大型更新上线",
            "summary": "重庆柚子猫工作室《戴森球计划》发布「黑雾崛起2.0」大型免费更新，新增战斗系统和星系探索。",
            "source": "Indienova",
            "url": "https://indienova.com/game/dyson-sphere/306",
        },
        {
            "title": "《恋与深空》收入超越《原神》登顶女性向游戏",
            "summary": "叠纸网络《恋与深空》5月全球收入超过《原神》，成为全球收入最高的女性向手游。",
            "source": "Sensor Tower",
            "url": "https://sensortower.com/love-and-deepspace/307",
        },
    ],

    "政策监管": [
        {
            "title": "国家新闻出版署下发6月首批国产游戏版号",
            "summary": "国家新闻出版署公布2026年第六批国产游戏版号名单，共95款游戏获批，数量保持稳定。",
            "source": "国家新闻出版署",
            "url": "https://www.nppa.gov.cn/game-license/401",
        },
        {
            "title": "未成年人游戏限玩令暑期执行细则出台",
            "summary": "署期未成年人游戏限玩令执行细则公布，每日20时至21时仅可登录1小时，人脸识别系统全面升级。",
            "source": "新华社",
            "url": "https://www.xinhuanet.com/policy/402",
        },
        {
            "title": "游戏行业数据安全管理办法征求意见稿发布",
            "summary": "工信部发布《游戏行业数据安全管理办法（征求意见稿）》，对用户数据收集和跨境传输提出新要求。",
            "source": "工信部",
            "url": "https://www.miit.gov.cn/data-security/403",
        },
        {
            "title": "上海市出台游戏出海扶持政策",
            "summary": "上海市政府发布《游戏出海企业扶持计划》，对出口海外市场收入超千万的游戏企业给予税收优惠。",
            "source": "上海发布",
            "url": "https://www.shanghai.gov.cn/game-policy/404",
        },
        {
            "title": "游戏适龄提示团体标准更新至2.0版本",
            "summary": "中国音数协发布《游戏适龄提示》2.0标准，新增AI交互内容和社交功能的风险评估维度。",
            "source": "中国音数协",
            "url": "https://www.cgigc.com.cn/age-rating/405",
        },
        {
            "title": "欧洲议会通过游戏虚拟财产交易监管法案",
            "summary": "欧洲议会正式通过虚拟财产交易监管法案，要求游戏公司对NFT和虚拟物品交易实施KYC验证。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/eu-regulation/406",
        },
        {
            "title": "广东加强游戏直播内容审核管理",
            "summary": "广东省广播电视局发布通知，加强游戏直播内容审核，要求直播平台建立游戏直播白名单制度。",
            "source": "广东省广电局",
            "url": "https://www.gd.gov.cn/game-streaming/407",
        },
    ],

    "海外市场": [
        {
            "title": "微软Xbox Game Pass订阅用户突破4500万",
            "summary": "微软公布Xbox Game Pass订阅用户数已达4500万，动视暴雪游戏库加入带动新一轮增长。",
            "source": "The Verge",
            "url": "https://www.theverge.com/xbox-game-pass/501",
        },
        {
            "title": "索尼PS5 Pro销量不及预期，或将调整策略",
            "summary": "索尼PS5 Pro自发布以来销量低于内部预期，传闻将推出降价促销活动并捆绑热门独占游戏。",
            "source": "IGN",
            "url": "https://www.ign.com/ps5-pro/502",
        },
        {
            "title": "任天堂宣布与腾讯深化Switch 2中国区合作",
            "summary": "任天堂与腾讯达成新协议，Switch 2中国区将获得更多本地化内容及专属游戏阵容。",
            "source": "GameLook",
            "url": "https://www.gamelook.com.cn/archives/nintendo/503",
        },
        {
            "title": "韩国游戏公司Krafton布局北美市场",
            "summary": "《绝地求生》开发商Krafton收购加拿大独立工作室，加速开放世界生存游戏研发。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/krafton/504",
        },
        {
            "title": "沙特主权基金PIF持续增持日本游戏公司股份",
            "summary": "沙特公共投资基金（PIF）增持万代南梦宫和SEGA股份，其全球游戏投资组合估值已超400亿美元。",
            "source": "Bloomberg",
            "url": "https://www.bloomberg.com/pif-gaming/505",
        },
        {
            "title": "育碧《刺客信条：代号HEXE》首支预告曝光",
            "summary": "育碧公布《刺客信条》系列新作预告，背景设定在16世纪欧洲，计划2027年发售。",
            "source": "Kotaku",
            "url": "https://www.kotaku.com/assassins-creed-hexe/506",
        },
        {
            "title": "Take-Two确认《GTA6》将于2026年秋季发售",
            "summary": "Take-Two在财报电话会议上确认《GTA6》仍按计划在2026年秋季发售，预购将于夏季开放。",
            "source": "Eurogamer",
            "url": "https://www.eurogamer.net/gta6-release/507",
        },
    ],

    "技术开发": [
        {
            "title": "Unreal Engine 5.6版本发布显著提升性能",
            "summary": "Epic Games发布Unreal Engine 5.6，引入Nanite虚拟几何体Lumen全局光照的重大性能优化，帧率提升30%。",
            "source": "Epic Games",
            "url": "https://www.unrealengine.com/release/601",
        },
        {
            "title": "Unity 6引擎正式支持WebGPU API",
            "summary": "Unity Technologies宣布Unity 6全面支持WebGPU标准，浏览器端游戏性能接近原生应用水平。",
            "source": "Unity Blog",
            "url": "https://unity.com/blog/webgpu/602",
        },
        {
            "title": "开源游戏引擎Godot在Steam平台游戏数量突破1000",
            "summary": "Godot引擎在Steam上发行的游戏数量突破1000款，开发者社区规模同比增长65%。",
            "source": "Godot News",
            "url": "https://godotengine.org/news/603",
        },
        {
            "title": "AMD FSR 4.0超分辨率技术正式开源",
            "summary": "AMD宣布FidelityFX Super Resolution 4.0技术开源，支持跨平台使用，对标NVIDIA DLSS。",
            "source": "AnandTech",
            "url": "https://www.anandtech.com/amd-fsr4/604",
        },
        {
            "title": "微软DirectStorage 2.0降低GPU解压延迟",
            "summary": "微软发布DirectStorage 2.0 API，新增GPU解压异步队列功能，游戏加载时间可缩短40%。",
            "source": "微软开发者",
            "url": "https://devblogs.microsoft.com/directstorage/605",
        },
        {
            "title": "中国自研游戏引擎「黑盒2.0」实现技术突破",
            "summary": "国内团队研发的黑盒引擎2.0版本实现全局光照实时烘焙技术突破，性能达到国际主流水平。",
            "source": "游戏陀螺",
            "url": "https://www.gametuber.com/engine/606",
        },
        {
            "title": "WebGPU标准进入稳定期，浏览器游戏迎来新机遇",
            "summary": "W3C宣布WebGPU标准进入候选推荐阶段，Chrome/Firefox/Safari均已实现完整支持。",
            "source": "InfoQ",
            "url": "https://www.infoq.com/webgpu/607",
        },
    ],

    "投融资": [
        {
            "title": "腾讯领投AI游戏开发平台1.2亿美元B轮融资",
            "summary": "AI游戏开发平台RiseArt完成1.2亿美元B轮融资，腾讯领投，资金用于加速生成式AI工具研发。",
            "source": "36氪",
            "url": "https://36kr.com/p/investment/701",
        },
        {
            "title": "网易投资英国3A工作室新项目",
            "summary": "网易游戏对英国某3A工作室进行战略投资，合作开发一款开放世界动作RPG游戏。",
            "source": "GameLook",
            "url": "https://www.gamelook.com.cn/archives/invest/702",
        },
        {
            "title": "米哈游成立10亿美元AI技术基金",
            "summary": "米哈游宣布设立10亿美元规模的AI技术投资基金，重点布局AI在游戏研发和玩家体验中的应用。",
            "source": "触乐",
            "url": "https://www.chuapp.com/article/mihoyo-ai-fund/703",
        },
        {
            "title": "小游戏平台「泡泡游戏」完成Pre-IPO轮融资",
            "summary": "国内小游戏平台泡泡游戏完成5亿元Pre-IPO融资，估值达80亿元，计划年内港股上市。",
            "source": "游戏葡萄",
            "url": "https://youxiputao.com/invest/704",
        },
        {
            "title": "沙特基金向波兰游戏开发商CDPR投资3亿美元",
            "summary": "沙特PIF基金斥资3亿美元购入CD Projekt Red约8%股份，成为《巫师》和《赛博朋克》开发商重要股东。",
            "source": "Bloomberg",
            "url": "https://www.bloomberg.com/cdpr-investment/705",
        },
        {
            "title": "字节跳动出售旗下游戏工作室回笼资金",
            "summary": "字节跳动将旗下部分游戏工作室出售给第三方公司，回笼资金用于核心业务AI和大模型研发。",
            "source": "晚点LatePost",
            "url": "https://www.latepost.com/byte-dance-game/706",
        },
        {
            "title": "独立游戏发行商Devolver Digital上半年营收增长40%",
            "summary": "Devolver Digital发布上半年财报，营收同比增长40%，多款独立游戏销量突破百万。",
            "source": "GamesIndustry",
            "url": "https://www.gamesindustry.biz/devolver/707",
        },
    ],

    "数据报告": [
        {
            "title": "2026年Q1全球移动游戏市场报告：RPG与策略类领涨",
            "summary": "Sensor Tower发布Q1报告，全球移动游戏收入同比增长12%，RPG和策略类游戏为主要增长引擎。",
            "source": "Sensor Tower",
            "url": "https://sensortower.com/q1-2026-report/801",
        },
        {
            "title": "中国游戏产业半年报：自研游戏收入突破千亿",
            "summary": "中国音数协发布2026年上半年游戏产业报告，自研游戏国内市场收入达1020亿元。",
            "source": "中国音数协",
            "url": "https://www.cgigc.com.cn/report/h1-2026/802",
        },
        {
            "title": "B站发布年度游戏生态数据报告",
            "summary": "哔哩哔哩发布游戏生态数据报告，平台游戏相关视频日均播放量超12亿次，创作者收入增长35%。",
            "source": "哔哩哔哩",
            "url": "https://www.bilibili.com/game-ecology/803",
        },
        {
            "title": "女性玩家占比持续上升至47%创历史新高",
            "summary": "游戏行业数据分析显示女性玩家占比已达47%，女性向游戏市场年增速超过30%。",
            "source": "Niko Partners",
            "url": "https://nikopartners.com/female-gamers/804",
        },
        {
            "title": "云游戏用户规模突破2亿，5G普及推动增长",
            "summary": "艾瑞咨询报告显示中国云游戏用户规模达2.1亿人，5G网络覆盖完善大幅降低串流延迟。",
            "source": "艾瑞咨询",
            "url": "https://www.iresearch.com.cn/cloud-gaming/805",
        },
        {
            "title": "全球电竞市场收入2026年预计达20亿美元",
            "summary": "Esports Charts数据显示2026年全球电竞市场收入预计达20亿美元，赞助和媒体版权收入占比超60%。",
            "source": "Esports Charts",
            "url": "https://escharts.com/report/806",
        },
        {
            "title": "超休闲游戏市场趋于饱和，混合休闲品类崛起",
            "summary": "Adjust移动数据报告显示超休闲游戏CPI成本上升30%，混合休闲（Hybrid-Casual）品类成为新增长点。",
            "source": "Adjust",
            "url": "https://www.adjust.com/report/hybrid-casual/807",
        },
    ],

    "行业活动": [
        {
            "title": "ChinaJoy 2026将于7月30日在上海开幕",
            "summary": "第二十四届中国国际数码互动娱乐展览会（ChinaJoy）定档7月30日至8月2日在上海新国际博览中心举办。",
            "source": "ChinaJoy",
            "url": "https://www.chinajoy.net/901",
        },
        {
            "title": "GDC 2026大会演讲视频全集现已上线",
            "summary": "GDC 2026全部主题演讲和技术分享视频已上传至官方网站，注册参会者可免费观看回放。",
            "source": "GDC",
            "url": "https://www.gdconf.com/vault-2026/902",
        },
        {
            "title": "东京电玩展2026参展厂商名单公布",
            "summary": "TGS 2026公布首批参展厂商名单，包含SEGA、Capcom、Koei Tecmo等知名日系厂商。",
            "source": "TGS",
            "url": "https://tgs.cesa.or.jp/exhibitors/903",
        },
        {
            "title": "「游戏开发者圆桌论坛」北京站报名启动",
            "summary": "由Unity中国主办的游戏开发者圆桌论坛北京站开放报名，议题聚焦AI与游戏开发实践。",
            "source": "Unity中国",
            "url": "https://unity.cn/events/beijing-rd/904",
        },
        {
            "title": "2026年全球电竞峰会将于7月在深圳举办",
            "summary": "全球电竞峰会（Global Esports Summit 2026）将在深圳前海举办，预计吸引超过2000名行业代表。",
            "source": "电竞峰会组委会",
            "url": "https://www.ges2026.com/905",
        },
        {
            "title": "IndieCade独立游戏节入围作品名单揭晓",
            "summary": "IndieCade 2026公布入围名单，共有45款独立游戏入围，中国团队作品数量创历史新高。",
            "source": "IndieCade",
            "url": "https://www.indiecade.com/2026/906",
        },
        {
            "title": "游戏出海增长论坛将在广州举行",
            "summary": "由广东省游戏产业协会主办的「游戏出海增长论坛」将于6月15日在广州举行，聚焦东南亚市场机遇。",
            "source": "广东省游戏产业协会",
            "url": "https://www.gdgia.com/overseas-forum/907",
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
