---
name: paper-tools
description: |
  Scientific Literature & Evidence Assistant — 从文献检索到 Meta 分析，知识图谱构建，
  全流程自动化。覆盖多源联邦检索（PubMed/arXiv/Semantic Scholar/OpenAlex）、
  质量评估（RoB2/ROBINS-I/GRADE/JBI）、证据合成（PICO/证据表格/PRISMA）、
  综述写作（IMRAD）、Meta 分析（效应量提取/森林图/异质性统计）和
  知识图谱（实体关系抽取/Neo4j 导出/趋势分析）。
metadata:
  openclaw:
    emoji: "🔬"
    requires:
      bins: ["python3"]
---

# 🔬 PaperTools — 论文工具

多源检索 → 质量评估 → 证据合成 → 综述写作 → **Meta 分析** → **知识图谱**

---

## 使用场景

当你需要：
- 撰写系统综述 / Meta 分析
- 追踪某领域最新研究进展
- 构建领域知识图谱
- 自动化循证医学文献工作流
- 多数据库并发检索（PubMed / arXiv / Semantic Scholar / OpenAlex）

---

## ⚡ 快速开始

```bash
cd scripts/
pip install -r requirements.txt

# 配置 API Keys（可选）
python paper_tools.py config --set-key pubmed=YOUR_KEY

# 多源检索
python paper_tools.py search "CRISPR gene editing" --database pubmed,arxiv,semantic --limit 30

# 质量评估
python paper_tools.py assess --tool rob2 --papers paper1.pdf

# 生成证据表格
python paper_tools.py table --query "CAR-T hematologic malignancies" --format markdown

# 生成综述草稿
python paper_tools.py review --topic "Immunotherapy solid tumors" --output draft.md
```

---

## 📋 完整命令参考

### 多源检索

```bash
# 并发检索多个数据库
paper_tools search "<query>" --database pubmed,arxiv,semantic,openalex,crossref --limit 50 --json

# 示例
paper_tools search "PD-1 checkpoint inhibitor efficacy" --database pubmed,arxiv --limit 30
```

### 质量评估

```bash
# RoB 2 — 随机对照试验
paper_tools assess --tool rob2 --papers paper1.pdf paper2.pdf

# ROBINS-I — 非随机化研究
paper_tools assess --tool robins --papers cohort_study.pdf

# GRADE — 证据质量分级
paper_tools assess --tool grade --query "Statins cardiovascular prevention"

# JBI — 批判性评价
paper_tools assess --tool jbi --papers study.pdf
```

### 证据合成

```bash
# PICO 框架解析
paper_tools pico --query "他汀类药物对心血管二级预防"

# 证据表格
paper_tools table --query "CAR-T therapy lymphoma" --format markdown
paper_tools table --query "CAR-T therapy lymphoma" --format csv --output evidence.csv

# PRISMA 流程图数据
paper_tools prisma --query "Systematic review question"
```

### 综述写作

```bash
# 生成 IMRAD 综述草稿
paper_tools review --topic "Role of immunotherapy in solid tumors" \
    --sections background,methods,results \
    --output review.md

# 格式化参考文献
paper_tools refs --style bibtex --papers papers.json --output refs.bib
```

### Meta 分析

```bash
# 从 JSON 数据执行 Meta 分析
paper_tools meta --studies meta_data.json --model random --output meta_results.json

# 从文本提取效应量
paper_tools meta --extract paper.txt

# 森林图（多格式）
paper_tools forest --type RR --model random --format ascii          # ASCII 预览
paper_tools forest --type OR --format json                          # JSON (Plotly)
paper_tools forest --type RR --format revman --output forest.xml     # Cochrane RevMan
paper_tools forest --type OR --format stata --output forest.do      # Stata
```

### 知识图谱

```bash
# 构建知识图谱（从论文 JSON）
paper_tools kg-build --papers papers.json --format json --output kg.json

# 从文本文件构建
paper_tools kg-build --texts ./texts/ --format neo4j --output kg.cypher

# 研究趋势分析
paper_tools kg-trends --kg kg.json --output trends.json
```

---

## 🔧 API Key 配置

```bash
# 设置
paper_tools config --set-key pubmed=YOUR_PUBMED_KEY
paper_tools config --set-key semanticscholar=YOUR_SS_KEY
paper_tools config --set-key openalex=YOUR_OPENALEX_KEY
paper_tools config --set-key bgpt=YOUR_BGPT_KEY

# 查看状态
paper_tools config --list-keys
```

| 数据源 | 必需 | 申请地址 | 免费限制 |
|--------|------|---------|---------|
| PubMed | 否 | [NCBI](https://www.ncbi.nlm.nih.gov/home/develop/api/) | 3 req/s |
| Semantic Scholar | 否 | [API Portal](https://api.semanticscholar.org/) | 100 req/5min |
| OpenAlex | 否 | [openalex.org](https://docs.openalex.org/) | 10 req/sec |
| BGPT | 否 | [bgpt.pro](https://bgpt.pro/mcp) | 50 req/网络 |

---

## 📁 模块架构

```
scripts/
├── paper_tools.py          # CLI 主入口
├── config.py              # 配置管理
├── search/
│   ├── federated.py       # 联邦检索引擎（并发+去重）
│   ├── pubmed.py         # PubMed E-utilities
│   ├── arxiv.py          # arXiv API
│   ├── semantic.py       # Semantic Scholar API
│   ├── openalex.py       # OpenAlex API
│   ├── crossref.py       # CrossRef API
│   └── bgpt.py          # BGPT MCP
├── assess/
│   ├── rob2.py           # RoB 2 (RCT)
│   ├── robins.py         # ROBINS-I (非随机化)
│   ├── grade.py          # GRADE 分级
│   └── jbi.py            # JBI 批判性评价
├── synthesize/
│   ├── pico.py           # PICO 框架
│   ├── evidence_table.py  # 证据表格
│   └── prisma.py         # PRISMA 流程图
├── write/
│   ├── imrad.py          # IMRAD 综述生成
│   └── references.py      # 参考文献格式化
├── meta/
│   ├── effect_size.py    # 效应量提取与标准化
│   ├── heterogeneity.py  # I² / Q / τ² 统计
│   ├── forest_plot.py    # 森林图数据生成
│   └── analyzer.py        # Meta 分析编排器
└── kg/
    ├── extractor.py       # 实体/关系抽取
    └── builder.py         # 图谱构建与趋势分析
```

---

## 📊 Meta 分析核心功能

### 效应量提取
支持从文本自动识别：RR、OR、HR、MD、SMD，自动 log 转换，自动计算标准误。

### 完整流水线
异质性检验（I²/Q/τ²）→ 模型选择（固定/随机）→ 效应量合并 → 森林图数据 → 导出 RevMan/Stata。

### 森林图格式
- **ASCII**: 终端直接预览
- **JSON (Plotly)**: 网页可视化
- **RevMan XML**: Cochrane 综述软件
- **Stata do-file**: 统计分析脚本

### 知识图谱
- 实体类型：基因/疾病/药物/通路/症状/蛋白/细胞
- 关系类型：上调/下调/治疗/因果/相互作用/磷酸化
- 导出格式：Neo4j Cypher / NetworkX JSON / D3.js
- 趋势分析：发表时间线 / 新兴实体 / 热门通路 / Gap 分析

---

## 🔗 配套使用

| 工具 | 用途 |
|------|------|
| `clawhub install arxiv-watcher` | 追踪 ArXiv 新论文 |
| `clawhub install literature-review` | 结构化文献综述 |
| `clawhub install citation-management` | 引用管理 |
| `clawhub install bgpt-paper-search` | 结构化实验数据提取 |
