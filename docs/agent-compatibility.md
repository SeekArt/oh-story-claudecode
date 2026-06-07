# Agent 调用兼容性指南

本项目支持多种 AI 编程工具，不同工具的 agent 调用方式略有不同。

## 支持的工具

| 工具 | Agent 调用方式 | 配置目录 |
|------|----------------|----------|
| **Claude Code** | `Agent(subagent_type: "agent-name")` | `.claude/agents/` |
| **Kilo** | 通过 Task 工具或 skill 加载 | `.kilo/agent/` |
| **OpenClaw** | `Agent(subagent_type: "agent-name")` | `.claude/agents/` |
| **TRAE** | 通过 skill 系统加载 | 项目 skills 目录 |

## Agent 定义位置

项目同时提供两种配置目录：

### Claude Code / OpenClaw 格式
- 目录：`.claude/agents/`
- 文件：`*.md` 带 YAML frontmatter
- 字段：`name`, `description`, `tools`, `model`, `maxTurns`, `memory`

### Kilo 通用格式
- 目录：`.kilo/agent/`
- 文件：`*.md` 带 YAML frontmatter
- 字段：`description`, `mode`, `model`, `steps`, `hidden`, `color`, `permission`

## 在 SKILL.md 中调用 Agent

推荐使用**条件调用**语法，兼容所有工具：

```markdown
**Agent 可用时**：如果已部署对应 agent（检查 agent 定义文件是否存在），
可调用该 agent 辅助任务。如 agent 不可用，由主线程直接执行。

**Claude Code/OpenClaw**：
```
Agent(subagent_type: "agent-name", prompt: "任务描述...")
```

**Kilo**：
```
使用 skill 加载或通过 Task 工具调用 agent
```

**通用**：
```
直接在主会话中执行相关任务，或按 agent 定义中的能力清单执行
```
```

## Agent 清单

| Agent | 职责 | 模型建议 |
|-------|------|----------|
| story-architect | 故事架构、世界观、大纲设计 | Opus (高质量创作) |
| character-designer | 角色设定、语言风格 | Sonnet |
| narrative-writer | 正文写作、去AI味 | Sonnet |
| consistency-checker | 一致性检查 | Haiku (快速检查) |
| story-researcher | 资料研究 | Sonnet |
| story-explorer | 故事查询、上下文加载 | Haiku |
| chapter-extractor | 章节提取 | Haiku |

## 部署方式

### Claude Code / OpenClaw
运行 `/story-setup` 部署到 `.claude/` 目录

### Kilo
agent 定义已在 `.kilo/agent/` 目录，无需额外部署

### 其他工具
将 `.kilo/agent/` 下的 agent 定义复制到对应工具的配置目录
