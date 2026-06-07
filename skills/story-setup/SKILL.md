---
name: story-setup
version: 1.2.0
description: |
  网文写作工具集基础设施部署。将 agents/AGENTS.md 等基础设施部署到用户项目目录。
  触发方式：/story-setup、「准备写书」「帮我搭一下环境」「配置写作项目」
  支持：Claude Code、Kilo、OpenClaw、TRAE 等多种 AI 编程工具
metadata:
  openclaw:
    source: https://github.com/worldwonderer/oh-story-claudecode
  kilo:
    commands: .kilo/command/
    agents: .kilo/agent/
---

# story-setup：网文写作工具集基础设施部署

你是写作基础设施部署器。将网文写作工具集的全套基础设施（agents、AGENTS.md）部署到用户项目目录。

**执行铁律：不覆盖用户已有配置，合并而非替换。**

**多工具兼容**：支持 Claude Code、Kilo、OpenClaw、TRAE 等多种 AI 编程工具。

---

## Phase 1：检测项目状态与工具类型

1. 检查当前目录是否已部署过（存在 `.story-deployed`）
   - 如果已存在 → 使用 AskUserQuestion 确认是否重新部署
2. 检查是否有书名目录（包含 `追踪/` 子目录的目录，或用户自定义结构）
   - 有 → 识别为长篇项目，显示当前项目信息
   - 无 → 识别为新项目或短篇项目
3. **检测工具类型**：
   - 检查 `.kilo/` 目录 → Kilo 工具
   - 检查 `.claude/` 目录 → Claude Code/OpenClaw
   - 两者都有 → 双工具兼容模式
   - 都没有 → 询问用户使用哪种工具
4. 检查配置文件是否存在：
   - Kilo: `kilo.json`
   - Claude Code: `.claude/settings.local.json`
   - 存在 → 读取现有配置，后续合并
   - 不存在 → 后续创建新文件
5. 检查 `.active-book` 文件是否存在
   - 存在 → 显示当前活跃书目
   - 不存在 → 跳过

## Phase 2：部署基础设施

使用 AskUserQuestion 确认部署位置后，依次执行。

### 2.0 部署清单（多工具兼容）

**通用部署**（所有工具都需要）：

| Source path | Target path | Owner class | Merge mode | Validation check |
|-------------|-------------|-------------|------------|------------------|
| `skills/story-setup/references/templates/AGENTS.md.tmpl` | `AGENTS.md` | user+managed | marker/section merge | contains story skill routing sections |
| `skills/story-setup/references/templates/上下文.md.tmpl` | `{书名}/追踪/上下文.md` | user state | create only if absent | never overwrite existing writing context |
| generated sentinel | `.story-deployed` | story-setup managed | replace | contains `agents_version`, `setup_skill_version`, `target_tool`, `resolver_strategy` |

**Claude Code/OpenClaw 专用**：

| Source path | Target path | Owner class | Merge mode | Validation check |
|-------------|-------------|-------------|------------|------------------|
| `skills/story-setup/references/templates/hooks/` | `.claude/hooks/` | story-setup managed | recursive replace | hooks exist and executable |
| `skills/story-setup/references/templates/rules/*.md` | `.claude/rules/*.md` | story-setup managed | replace | every rule contains `paths` frontmatter |
| `skills/story-setup/references/templates/agents/*.md` | `.claude/agents/*.md` | story-setup managed | replace | 7 agent files exist |
| `skills/story-setup/references/agent-references/*.md` | `.claude/skills/story-setup/references/agent-references/*.md` | story-setup managed | replace | all reference files exist |
| `skills/story-setup/references/templates/settings-hooks.json` | `.claude/settings.local.json` | user+managed | merge by hook command | hook JSON valid |

**Kilo 专用**：

| Source path | Target path | Owner class | Merge mode | Validation check |
|-------------|-------------|-------------|------------|------------------|
| `.kilo/agent/*.md` | 已在源码中 | story-setup managed | N/A | agent files exist in .kilo/agent/ |
| `.kilo/command/*.md` | 已在源码中 | story-setup managed | N/A | command files exist in .kilo/command/ |
| `kilo.json` | `kilo.json` | user+managed | merge | valid JSON config |

### 2.1 部署 AGENTS.md

- 读取 `skills/story-setup/references/templates/AGENTS.md.tmpl`（优先）或 `CLAUDE.md.tmpl`
- 替换占位符（见下方「模板占位符」段）
- 写入项目根目录 `AGENTS.md`（如已存在，按「AGENTS.md 合并策略」处理）
- 同时兼容写入 `CLAUDE.md`（Claude Code 兼容）

### 2.2 部署 Agents（工具特定）

**Claude Code/OpenClaw**：
- 读取 `skills/story-setup/references/templates/agents/` 下所有 `.md` 文件
- 复制到用户项目的 `.claude/agents/` 目录
- Agent 文件属于 story-setup 管理文件，可安全覆盖

**Kilo**：
- Agent 定义已在 `.kilo/agent/` 目录中
- 无需额外部署，直接使用
- 用户可在项目中添加自定义 agent

**通用说明**：
- Agent 兼容性处理：保留 `name`、`description`、核心字段，删除不支持的字段
- 参考资料路径：优先用项目内 `.kilo/skills/` 或 `skills/` 作为规范路径前缀

### 2.3 部署工具特定配置

**Claude Code/OpenClaw 专用**：
- **Hooks**：递归复制 `templates/hooks/` 到 `.claude/hooks/`
- **Rules**：复制 `templates/rules/*.md` 到 `.claude/rules/`
- **Settings**：合并 `settings-hooks.json` 到 `.claude/settings.local.json`

**Kilo 专用**：
- **Commands**：`.kilo/command/` 目录已存在，无需部署
- **Config**：确保 `kilo.json` 包含 skills 配置

### 2.4 部署 Session State 模板

- 读取 `skills/story-setup/references/templates/上下文.md.tmpl`
- 仅当已识别为长篇书目且 `{书名}/追踪/` 已存在时，创建缺失的 `{书名}/追踪/上下文.md`
- 如果目标文件已存在，不覆盖；短篇项目不得因此创建 `追踪/` 目录

### 2.5 创建部署标记

- 创建 `.story-deployed` 文件（sentinel file）
- 写入以下字段（YAML `key: value` 格式）：
  ```
  deployed_at: <date -u +"%Y-%m-%dT%H:%M:%SZ">
  agents_version: 11
  setup_skill_version: 1.2.0
  target_tool: <claude-code|kilo|both>
  resolver_strategy: project-local-skill-reference
  ```
- 此文件供 skill 检测部署状态，避免重复提示

## Phase 3：验证安装

根据部署的工具类型验证：

**通用验证**：
1. 验证 AGENTS.md 存在且包含 skill 路由表
2. 验证 `.story-deployed` 存在且包含正确字段

**Claude Code/OpenClaw 验证**：
1. 验证 hooks 注册：`.claude/settings.local.json`
2. 验证 hooks 脚本：`.claude/hooks/` 可执行
3. 验证 rules：`.claude/rules/` 包含 `paths` frontmatter
4. 验证 agents：`.claude/agents/` 7个文件存在
5. 验证 references：`.claude/skills/story-setup/references/agent-references/`

**Kilo 验证**：
1. 验证 kilo.json 包含 skills 配置
2. 验证 agent 定义：`.kilo/agent/` 文件存在
3. 验证 commands：`.kilo/command/` 文件存在

**输出安装报告**：
- 列出已部署的文件
- 列出需要注意的事项
- 提示用户可使用的命令（根据工具类型）

---

## 模板占位符

| 占位符 | 替换规则 | 示例 |
|--------|----------|------|
| `{项目名}` | 用户项目名称或目录名 | 《剑来》、《暗卫》 |
| `{书名}` | 书名目录名（与目录一致） | 与 `{项目名}` 相同，或用户自定义 |
| `{目标平台}` | 目标发布平台 | 起点、番茄、晋江、知乎盐言 |
| `{作者名}` | 用户笔名或昵称 | 未指定时用「作者」 |

替换时去掉花括号。如果用户未指定项目名，用当前目录名。未指定的占位符保留原样不替换。

## CLAUDE.md 合并策略

用户已有 CLAUDE.md 时，按 marker/section 合并：
1. 优先识别 story-setup 管理块标记（如果旧项目已有标记，只替换标记内内容）
2. 无标记时，读取用户现有 CLAUDE.md，按 `##` 标题切分为 section map
3. 读取模板 CLAUDE.md.tmpl，同样切分
4. 模板中的标准 section（Skill 路由表、文件结构、协作规则、Context Recovery、语言）**覆盖**用户同名 section
5. 用户独有的 section（自定义内容）**保留**不动
6. 未知冲突用 AskUserQuestion 让用户选择保留哪个版本

## settings-hooks.json 合并算法

hooks 注册合并按 command 字段去重：
1. 读取用户现有 `.claude/settings.local.json`（如存在），提取 hooks 部分
2. 读取 `settings-hooks.json` 模板，提取要注册的 hooks
3. 对每个 hook event（SessionStart、PreToolUse 等）：
   - 用户已有的 hook command → 保留，不重复添加
   - 模板中的新 hook command → append 到对应 event 的 hooks 数组
   - 用户独有的其他配置（permissions、env 等）→ 完整保留
4. 写入合并后的完整 settings.local.json

## 重新部署

- `.story-deployed` 不存在 → 全新安装，Phase 2 全部执行
- `.story-deployed` 存在且 `agents_version: 10` → 提示已部署，AskUserQuestion 确认是否重新部署
- `.story-deployed` 存在但 `agents_version` < 10 → 提示需要更新，重新执行 Phase 2 覆盖 agents/hooks/rules/reference bundle，CLAUDE.md 和 settings.local.json 走合并策略

---

## 参考资料

| 文件 | 用途 |
|------|------|
| references/templates/CLAUDE.md.tmpl | 项目根 CLAUDE.md 模板 |
| references/templates/hooks/ | 6 个 hook 脚本模板 + `lib/common.sh`/`lib/sentinel.sh` |
| references/templates/rules/ | 4 条 path-scoped 规则模板 |
| references/templates/agents/ | 7 个 agent 定义模板（story-architect, character-designer, narrative-writer, consistency-checker, story-researcher, story-explorer, chapter-extractor） |
| references/agent-references/ | Agent 模板自带的参考资料副本；部署到 `.claude/skills/story-setup/references/agent-references/`，避免跨 skill references |
| references/templates/settings-hooks.json | hooks 注册 JSON 片段 |
| references/templates/上下文.md.tmpl | 写作上下文模板 |

---

## 流程衔接

**流水线：** 部署
**位置：** 初始化（最前置）

| 时机 | 跳转到 | 命令 |
|---|---|---|
| 部署完成，开始写作 | story-long-write / story-short-write | `/story-long-write` 或 `/story-short-write` |
| 导入已有小说做拆解 | story-import | `/story-import` |
| 需要浏览器登录态（扫榜/拆文取原文） | browser-cdp | `/browser-cdp` |
