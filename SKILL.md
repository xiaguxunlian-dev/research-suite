---
name: research-suite
description: |
  AI-Accelerated Scientific Research Assistant — 从文献检索到 Meta 分析，知识图谱构建，
  全流程自动化。覆盖多源联邦检索（PubMed/arXiv/Semantic Scholar/OpenAlex）、
  质量评估（RoB2/ROBINS-I/GRADE/JBI）、证据合成（PICO/证据表格/PRISMA）、
  综述写作（IMRAD）以及 Phase 3 的 Meta 分析（效应量提取/森林图/异质性统计）和
  知识图谱（实体关系抽取/Neo4j 导出/趋势分析）。
metadata:
  openclaw:
    emoji: "🔬"
    requires:
      bins: ["python3"]
---

# 🔬 Research Suite — AI 科研加速助手

多源检索 → 质量评估 → 证据合成 → 综述写作 → **Meta 分析** → **知识图谱**

---

## 使用场景

当你需要：
- 撰写系统综述 / Meta 分析
- 追踪某领域最新研究进展
- 构建领域知识图谱
- 对比多家 LLM API 的价格和性能
- 自动化循证医学文献工作流

---

## ⚡ 快速开始

```bash
cd scripts/
pip install -r requirements.txt

# 配置 API Keys（可选）
python research.py config --set-key pubmed=YOUR_KEY

# 多源检索
python research.py search "CRISPR gene editing" --db pubmed,arxiv,semantic --limit 30

# 质量评估
python research.py assess --tool rob2 --papers paper1.pdf

# 生成证据表格
python research.py table --query "CAR-T hematologic malignancies" --format markdown

# 生成综述草稿
python research.py review --topic "Immunotherapy solid tumors" --output draft.md
```

---

## 📋 完整命令参考

### Phase 1 — 多源联邦检索

```bash
# 并发检索多个数据库
research search "<query>" --db pubmed,arxiv,semantic,openalex,crossref --limit 50 --json

# 示例
research search "PD-1 checkpoint inhibitor efficacy" --db pubmed,arxiv --limit 30
```

### Phase 1 — 质量评估

```bash
# RoB 2 — 随机对照试验
research assess --tool rob2 --papers paper1.pdf paper2.pdf

# ROBINS-I — 非随机化研究
research assess --tool robins --papers cohort_study.pdf

# GRADE — 证据质量分级
research assess --tool grade --query "Statins cardiovascular prevention"

# JBI — 批判性评价
research assess --tool jbi --papers study.pdf
```

### Phase 2 — 证据合成

```bash
# PICO 框架解析
research pico --query "他汀类药物对心血管二级预防"

# 证据表格
research table --query "CAR-T therapy lymphoma" --format markdown
research table --query "CAR-T therapy lymphoma" --format csv --output evidence.csv

# PRISMA 流程图数据
research prisma --query "Systematic review question"
```

### Phase 2 — 综述写作

```bash
# 生成 IMRAD 综述草稿
research review --topic "Role of immunotherapy in solid tumors" \
    --sections background,methods,results \
    --output review.md

# 格式化参考文献
research refs --style bibtex --papers papers.json --output refs.bib
```

### Phase 3 — Meta 分析

```bash
# 从 JSON 数据执行 Meta 分析
research meta --studies meta_data.json --model random --output meta_results.json

# JSON 格式示例（studies 输入）:
# [
#   {"name": "Smith 2020", "type": "RR", "effect": 0.75, "ci_lower": 0.55, "ci_upper": 1.02, "year": 2020},
#   {"name": "Johnson 2021", "type": "RR", "effect": 0.68, "ci_lower": 0.50, "ci_upper": 0.92, "year": 2021}
# ]

# 从文本提取效应量
research meta --extract paper.txt

# 森林图（多格式）
research forest --type RR --model random --format ascii          # ASCII 预览
research forest --type OR --format json                          # JSON (Plotly)
research forest --type RR --format revman --output forest.xml     # Cochrane RevMan
research forest --type OR --format stata --output forest.do      # Stata
```

### Phase 3 — 知识图谱

```bash
# 构建知识图谱（从论文 JSON）
research kg-build --papers papers.json --format json --output kg.json

# 从文本文件构建
research kg-build --texts ./texts/ --format neo4j --output kg.cypher

# 研究趋势分析
research kg-trends --kg kg.json --output trends.json
```

---

## 🔧 API Key 配置

```bash
# 设置
research config --set-key pubmed=YOUR_PUBMED_KEY
research config --set-key semanticscholar=YOUR_SS_KEY
research config --set-key openalex=YOUR_OPENALEX_KEY
research config --set-key bgpt=YOUR_BGPT_KEY

# 查看状态
research config --list-keys
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
├── research.py              # CLI 主入口
├── config.py                # 配置管理
├── search/
│   ├── federated.py         # 联邦检索引擎（并发+去重）
│   ├── pubmed.py            # PubMed E-utilities
│   ├── arxiv.py             # arXiv API
│   ├── semantic.py          # Semantic Scholar API
│   ├── openalex.py         # OpenAlex API
│   ├── crossref.py         # CrossRef API
│   └── bgpt.py             # BGPT MCP
├── assess/
│   ├── rob2.py              # RoB 2 (RCT)
│   ├── robins.py           # ROBINS-I (非随机化)
│   ├── grade.py            # GRADE 分级
│   └── jbi.py              # JBI 批判性评价
├── synthesize/
│   ├── pico.py              # PICO 框架
│   ├── evidence_table.py    # 证据表格
│   └── prisma.py           # PRISMA 流程图
├── write/
│   ├── imrad.py            # IMRAD 综述生成
│   └── references.py       # 参考文献格式化
├── meta/                    # ─── Phase 3 ───
│   ├── effect_size.py       # 效应量提取与标准化
│   ├── heterogeneity.py     # I² / Q / τ² 统计
│   ├── forest_plot.py       # 森林图数据生成
│   └── analyzer.py          # Meta 分析编排器
└── kg/                      # ─── Phase 3 ───
    ├── extractor.py         # 实体/关系抽取
    ├── builder.py           # 图谱构建与趋势分析
    └── extractor.py          # (续)
```

---

## 📊 Phase 3 核心功能

### 效应量提取

支持从文本自动识别：RR、OR、HR、MD、SMD，自动 log 转换，自动计算标准误。

### Meta 分析

完整流水线：异质性检验（I²/Q/τ²）→ 模型选择（固定/随机）→ 效应量合并 → 森林图数据 → 导出 RevMan/Stata。

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

本 Skill 可与以下工具配合使用：

| 工具 | 用途 |
|------|------|
| `clawhub install arxiv-watcher` | 追踪 ArXiv 新论文 |
| `clawhub install literature-review` | 结构化文献综述 |
| `clawhub install citation-management` | 引用管理 |
| `clawhub install bgpt-paper-search` | 结构化实验数据提取 |
