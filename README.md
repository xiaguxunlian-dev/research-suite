# PaperTools — 科研助手

[![Release](https://img.shields.io/github/v/release/xiaguxunlian-dev/PaperTools)](https://github.com/xiaguxunlian-dev/PaperTools/releases)
[![License](https://img.shields.io/github/license/xiaguxunlian-dev/PaperTools)](LICENSE)

多功能文献研究工具包：多源文献检索、证据质量评估、Meta 分析、知识图谱构建，零 API Key 即可上手。

**GitHub**: https://github.com/xiaguxunlian-dev/PaperTools

---

## 🚀 快速开始（推荐）

### 方式一：GUI 图形界面（ easiest ）

下载 `PaperTools.exe`，双击即可运行，无需安装 Python！

📥 **[下载 PaperTools.exe](https://github.com/xiaguxunlian-dev/PaperTools/releases/latest/download/PaperTools.exe)**

#### 使用流程

```
┌─────────────────────────────────────────────────────────────┐
│  1. 下载 PaperTools.exe                                     │
│     ↓                                                       │
│  2. 双击运行（无需安装）                                     │
│     ↓                                                       │
│  3. 输入检索词（如：COVID-19 vaccine）                       │
│     ↓                                                       │
│  4. 点击「🔍 开始检索」                                      │
│     ↓                                                       │
│  5. 查看右侧结果列表                                         │
│     ↓                                                       │
│  6. 点击「📊 生成表格」或「✍️ 写综述」                        │
└─────────────────────────────────────────────────────────────┘
```

#### GUI 界面特性

| 特性 | 说明 |
|------|------|
| 🎨 **超大字体** | 3倍放大，对笔记本和老年人友好 |
| 🔘 **大圆角设计** | 16-24px 圆角，现代化视觉体验 |
| 🌙 **暗色主题** | 护眼的深色玻璃拟态界面 |
| 📐 **三栏布局** | 左侧导航 \| 中间工作区 \| 右侧结果面板 |
| ⚡ **一键流转** | 检索结果直接生成表格/综述 |

#### 系统要求

- Windows 10/11
- 屏幕分辨率建议 1920×1080 或更高

---

## 📦 功能总览

| 模块 | 命令 | 说明 |
|------|------|------|
| 🔍 **多源检索** | `search` | PubMed / arXiv / Semantic Scholar / OpenAlex / CrossRef 并发搜索 |
| 📊 **质量评估** | `assess` | RoB 2 / ROBINS-I / GRADE / JBI 标准化评估 |
| 📋 **PICO 提取** | `pico` | 自动从文本提取 Population / Intervention / Comparison / Outcome |
| 📝 **证据表格** | `table` | 生成 Markdown / CSV / JSON 证据汇总表 |
| 🌲 **PRISMA 流程图** | `prisma` | 生成系统综述 PRISMA 流程图数据 |
| 📖 **综述写作** | `review` | IMRAD 格式综述草稿生成 |
| 📚 **参考文献** | `refs` | BibTeX / Vancouver / RIS 多格式参考文献 |
| 🔬 **Meta 分析** | `meta` | 效应量提取 + 异质性计算 + 森林图 |
| 🌲 **森林图** | `forest` | ASCII / Plotly / RevMan / Stata 森林图 |
| 🕸️ **知识图谱** | `kg-build` | 本地文件或论文构建 KG，Neo4j / JSON / NetworkX 导出 |
| 📈 **研究趋势** | `kg-trends` | 实体时间线 + 热点分析 + Gap 发现 |
| ⚙️ **配置管理** | `config` | API Key 存储与配置 |

---

## 💻 命令行安装（开发者）

### 方式二：一键安装

```powershell
# 1. 安装 Python 3.12+
winget install Python.Python.3.12
# 或从 https://python.org 下载安装包（安装时勾选 Add to PATH）

# 2. 克隆本仓库
git clone https://github.com/xiaguxunlian-dev/PaperTools.git
cd PaperTools

# 3. 安装依赖
pip install -r requirements.txt

# 4. 验证安装
python scripts/paper_tools.py --help
```

### 方式三：便携使用（无需安装）

```powershell
# 只需 Python，直接运行主脚本
python scripts/paper_tools.py search "CRISPR cancer" --database pubmed --limit 3
```

---

## 📖 使用教程

### 1. 文献检索

```powershell
# PubMed 检索（无需 API Key）
python scripts/paper_tools.py search "CRISPR cancer" --database pubmed --limit 5

# arXiv 检索
python scripts/paper_tools.py search "machine learning healthcare" --database arxiv --limit 5

# 多数据库并发检索
python scripts/paper_tools.py search "PD-1 immunotherapy" --database pubmed,semantic --limit 3

# JSON 输出（方便程序处理）
python scripts/paper_tools.py search "metformin diabetes" --database pubmed --json
```

### 2. 证据质量评估

```powershell
# GRADE 评估（输入检索词，自动分析）
python scripts/paper_tools.py assess --tool grade --query "Aspirin cardiovascular prevention"

# RoB 2 评估（评估 RCT 偏倚风险）
python scripts/paper_tools.py assess --tool rob2 --papers paper1.txt paper2.txt

# JBI 评估
python scripts/paper_tools.py assess --tool jbi --papers paper.txt
```

### 3. PICO 框架提取

```powershell
python scripts/paper_tools.py pico --text "Aspirin for cardiovascular disease prevention in adults with diabetes mellitus"
```

### 4. Meta 分析

```powershell
# 从 JSON 文件加载研究数据
python scripts/paper_tools.py meta --studies studies.json --model random --output result.json

# 直接从文献文本提取效应量
python scripts/paper_tools.py meta --extract paper_abstract.txt --model random
```

**studies.json 格式**：
```json
[
  {
    "name": "Smith 2020",
    "type": "OR",
    "effect": 0.65,
    "ci_lower": 0.48,
    "ci_upper": 0.88,
    "year": 2020
  },
  {
    "name": "Johnson 2021",
    "type": "OR",
    "effect": 0.72,
    "ci_lower": 0.55,
    "ci_upper": 0.95,
    "year": 2021
  }
]
```

### 5. 森林图

```powershell
# ASCII 森林图（无需任何依赖）
python scripts/paper_tools.py forest --format ascii

# JSON 格式（用于程序处理）
python scripts/paper_tools.py forest --format json --output forest.json

# Plotly HTML（可交互图表）
python scripts/paper_tools.py forest --format plotly --output forest.html
```

**ASCII 森林图示例**：
```
Forest Plot OR
                      0.72        100%
---------------------------------------------------------------
Smith 2020            0.65  [0.48-0.88]  25.0%
Johnson 2021          0.72  [0.55-0.95]  30.0%
Williams 2022        0.58  [0.40-0.84]  20.0%
Brown 2023           0.69  [0.50-0.95]  25.0%

I2=42.5%  Q=6.8  p=0.034
```

### 6. 知识图谱构建

```powershell
# 从本地文本文件构建知识图谱
python scripts/paper_tools.py kg-build --texts ./test_corpus --format json

# 从 PubMed 检索结果构建
python scripts/paper_tools.py search "TP53 cancer" --database pubmed --limit 20 --json > papers.json
python scripts/paper_tools.py kg-build --papers papers.json --format neo4j --output kg.cypher

# 研究趋势分析
python scripts/paper_tools.py kg-trends --kg kg.json --output trends.json
```

### 7. 综述写作

```powershell
# 生成 IMRAD 格式综述草稿
python scripts/paper_tools.py review --topic "CRISPR gene editing cancer therapy" --output review.md

# 指定章节
python scripts/paper_tools.py review --topic "Immunotherapy melanoma" --sections background,methods,results,discussion
```

---

## 🔧 API Key 配置（可选）

以下数据库可免费申请 API Key，提升检索频率限制：

| 数据库 | 申请地址 | 用途 |
|--------|---------|------|
| PubMed (NCBI) | https://ncbi.nlm.nih.gov/account |
| Semantic Scholar | https://api.semanticscholar.org |
| OpenAlex | https://dev.openalex.org |
| CrossRef | https://crossref.org |

```powershell
# 配置 API Key
python scripts/paper_tools.py config --set-key pubmed=YOUR_KEY
python scripts/paper_tools.py config --set-key semantic=YOUR_KEY

# 查看已配置的 Key
python scripts/paper_tools.py config --list-keys
```

---

## 📁 项目结构

```
PaperTools/
├── dist/
│   └── PaperTools.exe          # 🎉 GUI 可执行文件（Windows）
├── scripts/
│   ├── paper_tools.py          # 主 CLI 入口
│   ├── config.py               # 配置管理
│   ├── search/                # 多源检索适配器
│   │   ├── federated.py      # 联邦检索引擎
│   │   ├── pubmed.py         # PubMed / Europe PMC
│   │   ├── arxiv.py          # arXiv
│   │   ├── semantic.py        # Semantic Scholar
│   │   ├── openalex.py      # OpenAlex
│   │   ├── crossref.py      # CrossRef
│   │   └── bgpt.py          # BGPT 医学数据库
│   ├── assess/               # 质量评估工具
│   │   ├── rob2.py         # RoB 2 (Cochrane)
│   │   ├── robins.py         # ROBINS-I
│   │   ├── grade.py          # GRADE
│   │   └── jbi.py            # JBI 清单
│   ├── synthesize/            # 证据合成
│   │   ├── pico.py           # PICO 框架
│   │   ├── evidence_table.py # 证据表格
│   │   └── prisma.py        # PRISMA 流程图
│   ├── write/                 # 写作辅助
│   │   ├── imrad.py          # IMRAD 综述
│   │   └── references.py     # 参考文献格式化
│   ├── meta/                 # Meta 分析
│   │   ├── effect_size.py   # 效应量提取
│   │   ├── heterogeneity.py  # 异质性统计
│   │   ├── forest_plot.py   # 森林图
│   │   └── analyzer.py       # Meta 流水线
│   └── kg/                   # 知识图谱
│       ├── extractor.py        # 实体/关系抽取
│       └── builder.py         # KG 构建 + 趋势分析
├── main_gui.py                 # GUI 界面源码
├── PaperTools.spec             # PyInstaller 打包配置
├── SKILL.md                  # OpenClaw Skill 定义
├── requirements.txt           # Python 依赖
└── README.md              # 本文件
```

---

## 📋 依赖说明

| 依赖包 | 用途 |
|--------|------|
| `requests` | HTTP 请求 |
| `aiohttp` | 异步并发检索 |
| `feedparser` | PubMed XML 解析 |
| `matplotlib` | 森林图可视化（可选） |
| `networkx` | 图网络分析（可选） |

> **零依赖运行**：核心模块完全独立，仅需 Python 3.10+，无任何第三方依赖即可运行检索和评估功能。

---

## ❓ 常见问题

**Q: 下载的 PaperTools.exe 无法运行？**
A: 请确保：
1. 从 [Releases](https://github.com/xiaguxunlian-dev/PaperTools/releases) 页面下载最新版本
2. Windows 10/11 系统
3. 屏幕分辨率至少 1600×900

**Q: GUI 界面字体太小？**
A: 当前版本已优化为 3 倍大字体，如仍需调整，请提交 Issue。

**Q: PubMed 检索返回 0 结果？**
A: 确认网络可访问外网。PubMed API 地址为 `https://eutils.ncbi.nlm.nih.gov`，无需 VPN。

**Q: 出现 `SSL` 相关错误？**
A: 公司网络可能拦截 HTTPS 请求。可尝试：
```powershell
set SSL_CERT_FILE=C:\Python312\Lib\site-packages\certifi\cacert.pem
python scripts/paper_tools.py search "your query" --database pubmed
```

**Q: arXiv 检索超时？**
A: arXiv 已切换至 HTTPS，确保网络可访问 `https://export.arxiv.org`。

**Q: 如何批量处理多篇论文？**
A: 将论文保存为文本文件放入目录，用 `--texts` 参数批量处理：
```powershell
python scripts/paper_tools.py kg-build --texts ./papers/ --format json
```

---

## 📄 许可证

MIT License

如有帮助，欢迎 ⭐ Star！

---

## 🙏 致谢

感谢以下开源项目：
- [PubMed E-utilities](https://www.ncbi.nlm.nih.gov/home/develop/api/)
- [arXiv API](https://arxiv.org/help/api)
- [Semantic Scholar API](https://api.semanticscholar.org/)
- [OpenAlex](https://openalex.org/)
