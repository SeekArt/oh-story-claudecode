# 电视猫剧情抓取技能

从电视猫（tvmao.com）抓取电视剧/电影的分集剧情。

## 快速开始

### 安装依赖

```bash
pip install requests beautifulsoup4
```

### 基本用法

```bash
# 使用剧集ID抓取全部
python scripts/tvmao_scraper.py --id ai4vJS8=

# 搜索剧名并抓取
python scripts/tvmao_scraper.py --search "神盾局特工"

# 抓取单集
python scripts/tvmao_scraper.py --id ai4vJS8= --episode 1

# 抓取指定范围
python scripts/tvmao_scraper.py --id ai4vJS8= --start 1 --end 10

# 使用Markdown格式保存
python scripts/tvmao_scraper.py --id ai4vJS8= --format markdown
```

### 剧集ID获取方式

剧集ID是URL中的加密字符串，例如：
- URL: `https://www.tvmao.com/drama/ai4vJS8=/episode`
- ID: `ai4vJS8=`

可以通过以下方式获取：
1. 使用 `--search` 参数搜索剧名
2. 从浏览器地址栏复制URL中的ID部分

## 输出结构

```
episodes/
└── 神盾局特工第一季/
    ├── 第01集.txt
    ├── 第02集.txt
    ├── 第03集.txt
    └── ...
```

## 参数说明

| 参数 | 简写 | 说明 |
|------|------|------|
| `--search` | `-s` | 按剧名搜索 |
| `--id` | `-i` | 指定剧集ID |
| `--episode` | `-e` | 抓取指定集数 |
| `--start` | | 起始集数（默认：1） |
| `--end` | | 结束集数 |
| `--output` | `-o` | 输出目录（默认：./episodes） |
| `--format` | `-f` | 输出格式：txt/markdown |
| `--delay` | `-d` | 请求延迟秒数（默认：1.0） |

## 注意事项

1. 请遵守网站使用条款，适度抓取
2. 剧情内容版权归电视猫所有
3. 如遇访问限制，可适当增加延迟时间
4. 仅供个人学习和研究使用
