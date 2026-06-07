---
description: 网文工具箱主入口，自动路由到对应 skill
agent: code
---
网络小说工具箱主入口。根据用户需求自动路由到对应 skill。

触发方式：/story、/网文、「我想写小说」「帮我写书」「写网文」

## 路由表

| 用户意图 | 关键词示例 | 路由到 |
|---|---|---|
| 写长篇 | 开书、写大纲、长篇、连载 | 使用 skill: story-long-write |
| 写短篇 | 短篇、盐言、一万字 | 使用 skill: story-short-write |
| 长篇拆文 | 拆文、分析这本书、黄金三章 | 使用 skill: story-long-analyze |
| 短篇拆文 | 拆短篇、分析这个故事 | 使用 skill: story-short-analyze |
| 长篇扫榜 | 长篇排行、什么火、起点/番茄/晋江 | 使用 skill: story-long-scan |
| 短篇扫榜 | 短篇排行、知乎盐言排行 | 使用 skill: story-short-scan |
| 去 AI 味 | 去 AI 味、太 AI、去味 | 使用 skill: story-deslop |
| 封面 | 封面、封面图 | 使用 skill: story-cover |
| 环境部署 | 准备写书、搭环境、初始化 | 使用 skill: story-setup |
| 导入小说 | 导入、反向解析、导入小说 | 使用 skill: story-import |
| 审查 | 审查、审稿、评分 | 使用 skill: story-review |
| 浏览器操控 | 浏览器、抓取、登录态 | 使用 skill: browser-cdp |

根据用户输入 $ARGUMENTS 分析意图，然后调用对应的 skill。