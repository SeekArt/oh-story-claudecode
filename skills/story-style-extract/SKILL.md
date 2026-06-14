---
name: story-style-extract
version: 1.0.0
description: |
  文风提取。从指定文件或目录中提取文本的写作风格，生成结构化文风档案。
  支持用户已完成章节、对标书原文、任何参考文本。
  触发方式：/story-style-extract、/文风提取、「提取文风」「帮我分析文风」「抽一下文风」
metadata:
  openclaw:
    source: https://github.com/worldwonderer/oh-story-claudecode
---

# story-style-extract：文风提取

你是文风分析师。从用户提供的文本中提取写作风格特征，生成结构化文风档案。
输出文件可直接被 story-long-write 的日更工作流读取（读 `文风优先级决议表`），用于续写时保持风格一致。

---

## 核心原则

1. **数据驱动**：句长分布、标点密度等用确定性脚本测量（confidence: high），定性观察标注 confidence 分级
2. **独立运行**：不依赖 `拆文库/` 结构、不依赖 analyze 管道。给文件就能跑
3. **不限来源**：用户自己写的章节、对标书原文、参考文本——通吃
4. **直接可用**：输出 `文风.md` 文件，story-long-write 日更时在 Step 2.3 直接读取

---

## 工作流

### Step 1：确认输入

**明确告诉用户**：你只需要文件路径，不需要任何拆文分析或摘要。

问用户（或直接解析用户提供的路径）：

> 「提供要提取文风的文件路径：
> - 单文件（.txt / .md）
> - **或** 目录路径（自动扫描所有正文文件，按文件名排序）」

输入方式：
- `{绝对路径}/正文/第1章_*.md`（指向单文件）
- `{绝对路径}/正文/`（指向目录，自动合并排序）
- `{绝对路径}/原文.txt`（整书单文件）

**最少样本量**：至少 5 章或 10000 字。不足时提示用户并在输出中标注 confidence: low。

### Step 2：文本采样与分章识别

**如果输入是目录**：按文件名排序，取前 1/4、中段、后 1/4 各 1 章（共 3 章），每章读 ~1000 字。总章数 < 5 时全部读取。

**如果输入是单文件**：用 grep 识别章节分隔符：

```bash
grep -nE '^第[一二三四五六七八九十百千两零0-9]+章|^## 第|^Chapter\s+\d+' "{路径}"
```

如果无章节分隔符，按 `---` 或连续空行分割；仍无法识别则全文作为单段处理。

**采样输出**：将选定文本拼接后写入临时文件（路径记为 `{采样路径}`），供 Step 3 测量使用。

### Step 3：确定性测量

跨平台 Python 统计（先探测可用解释器——**勿直接用 `python3`**，Windows 上它会触发 Microsoft Store 占位程序、exit 49 失败）：

```bash
for PYBIN in python3 python py; do "$PYBIN" -c "" 2>/dev/null && break; done
"$PYBIN" <<'PYEOF'
import re
with open(r'{采样路径}', 'r', encoding='utf-8') as f:
    text = f.read()
# 句长分布
sents = [s for s in re.split(r'[。！？]+', text) if s.strip()]
total = max(len(sents), 1)
short = sum(1 for s in sents if len(s) < 15)
mid   = sum(1 for s in sents if 15 <= len(s) <= 30)
lng   = sum(1 for s in sents if len(s) > 30)
# 标点密度
chars = max(sum(1 for c in text if not c.isspace()), 1)
puncts = sum(1 for c in text if c in '，。！？；：、…—""\'\'')
avg = sum(len(s) for s in sents) // total
print(f'sentences={total}; short_lt15={100*short//total}%; mid_15to30={100*mid//total}%; long_gt30={100*lng//total}%; avg_len={avg}; punct_density={100*puncts//chars}%')
PYEOF
```

记录输出数值备用。

### Step 4：定性观察

基于已读文本，分析并记录以下维度（每项标注 confidence: high / med / low）：

| 维度 | 观察内容 |
|------|---------|
| 标点习惯 | 破折号/省略号/感叹号/分号的使用频率和用途。附 2-3 个原文短片段 |
| 段落节奏 | 平均段长、单段单动作 vs 多动作堆叠、断行习惯 |
| 对话潜台词模式 | 2-3 种典型手法（问非所答/语气反差/信息隐瞒等），附原文示例 |
| 对话标签习惯 | 说话动词多样性、动作替代标签的频率、对话与动作的穿插比例 |
| 角色语气区分 | 主角和 1-2 个核心配角的语言差异，引用原文样本句 |
| 情绪基调分布 | 文本整体基调偏向（紧张/轻松/悲伤/热血/压抑等），是否频繁切换 |
| 典型句式特征 | 是否有高频句式模式（长句/短句/排比/反问等） |

**参考工具**：上述维度的详细分析方法见 `story-long-analyze/references/style-profile-generator.md`（Step 2-5），但不强制加载——主线程直接根据已读文本分析即可。

### Step 5：抽取原文锚点片段

从已读文本中选 4-6 段 300-500 字原文，每段覆盖一种基调。每个锚点标注基调类型 + 示范点。

| 基调 | 优先选 | 缺样本则 |
|------|--------|---------|
| 紧张/对峙 | 对话+动作交织段落 | 跳过该基调 |
| 悲伤/压抑 | 安静细节+内心流露段落 | 跳过 |
| 轻松/日常 | 日常互动+轻松对话 | 跳过 |
| 热血/爽点 | 冲突释放+情绪高潮 | 跳过 |
| 温馨/甜 | 感情互动+细节刻画 | 跳过 |
| 悬念/铺垫 | 信息差+伏笔段落 | 跳过 |

锚点必须是原文连续切片，禁止改写/缩写/跳段/拼接。

### Step 6：输出文风文件

按 [references/extract-protocol.md](references/extract-protocol.md) 模板填写。

**输出位置规则**：
- 用户指定输出路径 → 写入指定位置
- 未指定且输入是目录 → 写入输入目录下的 `文风.md`
- 未指定且输入是单文件 → 写入文件同目录下的 `文风.md`

输出后向用户确认：
> 「文风已提取并写入 `{输出路径}`。
> - 写作时引用：设置写项目的 `对标/{书别名}/文风.md`
> - 直接读取方式：story-long-write 日更时在 Step 2.3 读取对标书文风；如果你想用本文风约束自己的书，将本文风放在项目根下，在 `追踪/上下文.md` 中注明 `文风路径：{路径}`」

---

## 参考资料

按需加载以下文件：

| 文件 | 何时加载 |
|------|----------|
| [references/extract-protocol.md](references/extract-protocol.md) | Step 6 填写输出模板时 |
| `story-long-analyze/references/style-profile-generator.md` | Step 3-4 测量和分析方法需要更详细指引时 |

---

## 失败模式与降级

| 场景 | 处理 |
|------|------|
| 路径无效或文件不存在 | 提示用户重新提供路径 |
| 文本不足 5000 字 | 输出句段，所有 confidence 标 low，提示样本不足 |
| 章节分隔符无法识别 | 全文作为一段处理，锚点和句长统计可用，情绪交替和节奏分析置信度标 low |
| 纯对话无叙述 | 可正常提取对话标签习惯和潜台词模式，句长分布仍可测量 |