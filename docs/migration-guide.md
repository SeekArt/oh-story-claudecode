# 多工具迁移指南

本指南帮助你在不同的 AI 编程工具之间迁移使用本 skill 包。

## 支持的工具

| 工具 | 状态 | 配置目录 | Agent 调用 |
|------|------|----------|-----------|
| **Claude Code** | ✅ 完全支持 | `.claude/` | `Agent(subagent_type: "...")` |
| **Kilo** | ✅ 完全支持 | `.kilo/` | Task 工具 / skill 加载 |
| **OpenClaw** | ✅ 兼容 | `.claude/` | `Agent(subagent_type: "...")` |
| **TRAE** | ✅ 兼容 | 项目 skills | skill 系统加载 |

## 快速开始

### Claude Code / OpenClaw

```bash
# 安装 skill
npx skills add worldwonderer/oh-story-claudecode -y -g

# 部署到项目
/story-setup

# 开始使用
/story-long-write
```

### Kilo

```bash
# 克隆或下载项目
git clone https://github.com/worldwonderer/oh-story-claudecode.git

# 在项目中使用
# 1. 确保 kilo.json 包含 skills 配置
# 2. 使用 /story 命令或直接调用 skills

/story
/story-setup
/story-long-write
```

### 其他工具

1. 将 `skills/` 目录复制到你的项目
2. 将 `.kilo/agent/` 下的 agent 定义复制到对应工具的 agent 目录
3. 将 `.kilo/command/` 下的命令定义复制到对应工具的命令目录
4. 参考 `AGENTS.md` 进行配置

## 配置差异对比

### Agent 定义格式

**Claude Code / OpenClaw**（`.claude/agents/*.md`）：
```yaml
---
name: story-architect
description: 故事架构师
tools: [Read, Glob, Grep, Write, Edit]
model: opus
maxTurns: 30
memory: project
---
```

**Kilo**（`.kilo/agent/*.md`）：
```yaml
---
description: 故事架构师
mode: subagent
model: anthropic/claude-opus
steps: 30
hidden: false
color: "#4A9BE8"
permission:
  bash: ask
  edit:
    "**/设定/**": allow
---
```

### Commands 定义

**Claude Code**：无原生 command 系统，使用 skill 触发

**Kilo**（`.kilo/command/*.md`）：
```yaml
---
description: 网文工具箱主入口
agent: code
---
命令内容...
```

### Skills 定义

两种格式相同（`skills/<name>/SKILL.md`）：
```yaml
---
name: story-long-write
description: 长篇网文写作
---
```

## 功能差异

| 功能 | Claude Code | Kilo | 其他工具 |
|------|-------------|------|----------|
| Skills | ✅ | ✅ | ✅ |
| Agents | ✅ | ✅ | ⚠️ 需适配 |
| Commands | ❌ | ✅ | ⚠️ 需适配 |
| Hooks | ✅ | ❌ | ❌ |
| Rules | ✅ | ❌ | ❌ |

### Hooks 替代方案

Kilo 和其他工具不支持 Claude Code 的 hooks 系统。替代方案：

1. **Session start/end**：通过 AGENTS.md 的上下文恢复功能实现
2. **Pre-commit validation**：通过 `/story-review` 命令手动执行
3. **Context management**：通过 story-explorer agent 手动调用

## 迁移步骤

### 从 Claude Code 迁移到 Kilo

1. 保留 `.claude/` 目录（双工具兼容）
2. 添加 `.kilo/` 目录（已包含在本项目中）
3. 确保 `kilo.json` 存在且配置正确
4. 测试 `/story-setup` 命令
5. 正常使用 skills

### 从 Kilo 迁移到 Claude Code

1. 保留 `.kilo/` 目录（双工具兼容）
2. 运行 `/story-setup` 部署 `.claude/` 配置
3. 测试 hooks 和 agents
4. 正常使用 skills

### 迁移到其他工具

1. 复制 `skills/` 目录
2. 参考 `.kilo/agent/` 创建 agent 定义（适配目标工具格式）
3. 参考 `.kilo/command/` 创建命令定义（如支持）
4. 复制 `AGENTS.md` 到项目根
5. 测试基本功能

## 常见问题

### Q: Hooks 功能丢失怎么办？

A: 使用替代方案：
- Session 状态：通过 `.story-deployed` 和 `上下文.md` 管理
- 提交验证：手动运行 `/story-review`
- 上下文管理：调用 story-explorer agent

### Q: Agent 调用失败？

A: 检查：
1. Agent 定义文件是否存在于对应目录
2. Agent frontmatter 格式是否正确
3. 调用语法是否符合当前工具

### Q: Skills 加载失败？

A: 检查：
1. `skills/` 目录是否存在
2. `SKILL.md` 文件是否存在于正确位置
3. 配置文件（kilo.json 或 .claude/settings.local.json）是否正确

## 获取帮助

- **GitHub Issues**: https://github.com/worldwonderer/oh-story-claudecode/issues
- **Telegram**: https://t.me/ohstoryclaudecode
- **文档**: `docs/agent-compatibility.md`
