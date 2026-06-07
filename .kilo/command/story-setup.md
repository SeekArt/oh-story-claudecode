---
description: 网文写作环境部署，部署 hooks/rules/agents/AGENTS.md
agent: code
---
网文写作工具集基础设施部署。将网文写作工具集的全套基础设施部署到用户项目目录。

触发方式：/story-setup、「准备写书」「帮我搭一下环境」「配置写作项目」

执行铁律：不覆盖用户已有配置，合并而非替换。

执行步骤：
1. 检查当前目录是否已部署过（存在 .story-deployed）
2. 检查是否有书名目录（包含 追踪/ 子目录的目录）
3. 部署基础设施文件（agents、rules、instructions）
4. 创建部署标记 .story-deployed

部署文件：
- agents/ 目录：故事架构师、角色设计师、叙事写手、一致性检查器、资料研究员、故事查询器、章节提取器
- AGENTS.md：项目根说明文件
- .story-deployed：部署标记文件

用户输入：$ARGUMENTS（可选的项目路径或配置选项）