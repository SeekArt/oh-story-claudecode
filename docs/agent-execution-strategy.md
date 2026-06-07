# Agent 执行策略

本文档说明项目中所有 skill 的 agent 调用执行策略。

## 统一执行策略

所有 skill 在调用 agent 时，都遵循以下优先级：

### 优先级 1：项目部署的 Agent

**检测条件**：
- `.kilo/agent/{agent-name}.md` 存在
- 或 `.claude/agents/{agent-name}.md` 存在

**执行方式**：
- 使用 Agent 工具调用：`Agent(subagent_type: "{agent-name}", prompt: "...")`
- 模型配置使用 agent 定义的 `model` 字段
- 并行任务按 skill 定义的批量策略执行

**适用场景**：
- 已运行 `/story-setup` 部署的项目
- 用户自定义 agent 的项目

### 优先级 2：环境子代理能力

**检测条件**：
- 项目 agents 不可用
- 当前环境支持子代理调用（如 Task 工具、subagent 能力）

**执行方式**：
- 使用环境子代理工具（如 Task）
- 将 agent 能力描述直接写在 prompt 中
- 根据环境能力选择并行或串行执行

**适用场景**：
- 未运行 story-setup 的项目
- TRAE、Cursor 等非 Claude Code 环境
- 支持 Task 工具的环境

### 优先级 3：降级处理

**检测条件**：
- 既无项目 agents，也无环境子代理能力
- 或当前已在子代理上下文中（递归保护）

**执行方式**：
- 由当前会话直接执行任务
- 按 agent 能力清单在主会话中完成
- 结果格式与 agent 输出完全相同

**适用场景**：
- 简单环境
- 单会话工具
- 递归保护场景

## 各 Skill 的执行策略

### story-review（多视角审查）

**并行 agents**：
- story-architect（结构审查）
- character-designer（角色审查）
- narrative-writer（文字审查）
- consistency-checker（一致性检查）

**执行模式**：
- full：并行执行 4 个 agents
- lean：并行执行 2 个 agents（story-architect + consistency-checker）
- solo：单会话执行

**报告元数据**：
```
Requested Mode: full | lean | solo
Effective Mode: full | lean | solo
Execution: project-agents | environment-subagents | solo
Agent Source: .kilo/agent | .claude/agents | environment | none
Fallback: none | no project agents -> environment | no subagent capability -> solo
```

### story-long-analyze（长篇拆文）

**并行 agents**：
- chapter-extractor（每章一个，5-8 个并行）

**批量策略**：
- 每次 5-8 个并行任务
- 等待当前批次完成后再启动下一批
- 失败重试：同级别重试 → 升级重试

**自动降级**：
- agents 未部署 → 环境子代理 → 串行处理

### story-import（导入小说）

**并行 agents**：
- chapter-extractor（长篇阶段 2）

**执行策略**：
- 同 story-long-analyze

### story-long-write / story-short-write

**可选 agents**：
- story-architect（架构设计）
- character-designer（角色设定）
- narrative-writer（正文写作）
- consistency-checker（一致性检查）
- story-explorer（上下文加载）
- story-researcher（资料研究）

**执行策略**：
- 检查 agent 可用性，不可用时主会话直接执行
- 已支持多工具兼容（见各 SKILL.md）

## 环境适配建议

### Claude Code / OpenClaw

推荐运行 `/story-setup` 部署 agents，获得最佳性能。

### Kilo

agents 已在 `.kilo/agent/` 中定义，无需额外部署。

### TRAE / 其他工具

两种方式：
1. 运行 `/story-setup` 部署到对应目录
2. 使用环境子代理能力（自动检测）

### 单会话工具

自动降级为 solo/串行模式，功能完整但速度较慢。

## 故障处理

### Agent 调用失败

1. 记录失败原因
2. 同级别重试 1 次
3. 重试失败 → 升级到高级别模型重试 1 次
4. 仍失败 → 标记跳过，继续其他任务

### 质量检查失败

1. 执行自检清单
2. 不达标 → 升级模型重试
3. 仍不达标 → 标记警告，记录原因

### 递归保护

当前已在子代理上下文中时：
- 不再递归调用子代理
- 自动降级为主会话执行
- 报告中标注 `Fallback: recursion guard -> solo`

---

更新时间：2026-06-07
版本：v1.2.0
