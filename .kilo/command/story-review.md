---
description: 多视角对抗式审查，4 Agent 多视角审稿 + 番茄/起点/知乎评分标准
agent: code
---
多视角对抗式审查工具。使用多个 Agent 从不同视角审稿，并提供平台评分标准。

触发方式：/story-review、「审查」「审稿」「评分」

审查模式：
- full：4 Agent 并行审查
- lean：2 Agent 精简审查
- solo：单 Agent 快速审查

审查维度：
1. 情节逻辑
2. 角色塑造
3. 文风节奏
4. 一致性检查

评分标准：
- 番茄小说标准
- 起点中文网 standard
- 知乎盐言标准

用户输入：$ARGUMENTS（正文文件路径、审查模式、目标平台）
