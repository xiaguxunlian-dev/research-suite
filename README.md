# 🔬 Research Suite

> AI 加速的科研文献综述工具 — 从检索到写作，全流程自动化

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)

## ✨ 功能特性

### 🔍 多源联邦检索
并发查询 6+ 主流学术数据库，统一去重返回结构化结果：

| 数据库 | 特色 | API 需要 |
|--------|------|---------|
| **PubMed** | 医学/生命科学最大库 | 可选 API Key |
| **arXiv** | 预印本，最新研究 | 无 |
| **Semantic Scholar** | AI 摘要 + 引用图谱 | 可选 |
| **OpenAlex** | 开放知识图谱 | 可选 |
| **CrossRef** | DOI 元数据 | 无 |
| **BGPT** | 结构化实验数据 | 可选 |

### 📊 质量评估
标准化循证医学质量评估工具：

- **RoB 2** — 随机对照试验偏倚风险
- **ROBINS-I** — 非随机化研究偏倚风险
- **GRADE** — 证据质量综合分级
- **JBI Critical Appraisal** — 批判性评价清单

### 📋 证据合成
- **PICO 框架** — 系统综述问题标准化
- **证据表格** — Markdown / CSV / JSON 多格式导出
- **PRISMA 流程图** — 系统综述流程数据

### 📝 综述写作
- **IMRAD 格式** — 自动生成 Introduction / Methods / Results / Discussion
- **参考文献格式化** — BibTeX / RIS / Vancouver / EndNote

## 🚀 快速开始

### 安装

```bash
# 克隆本仓库
git clone https://github.com/YOUR_NAME/research-suite.git
cd research-suite

# 安装依赖
pip install -r requirements.txt

# 配置 API Keys（可选）
python scripts/research.py config --set-key pubmed=YOUR_KEY
python scripts/research.py config --set-key semanticscholar=YOUR_KEY
```

### 检索文献

```bash
python scripts/research.py search "CRISPR gene editing efficiency" \
    --db pubmed,arxiv,semantic \
    --limit 30
```

### 质量评估

```bash
# RoB 2 评估 RCT
python scripts/research.py assess --tool rob2 --papers paper1.pdf paper2.pdf

# GRADE 评估
python scripts/research.py assess --tool grade \
    --query "Statins for cardiovascular prevention"
```

### 生成证据表格

```bash
python scripts/research.py table \
    --query "CAR-T therapy hematologic malignancies" \
    --format markdown
```

### 生成综述草稿

```bash
python scripts/research.py review \
    --topic "Immunotherapy in solid tumors" \
    --sections background,methods,results \
    --output review_draft.md
```

### 生成 PRISMA 流程图数据

```bash
python scripts/research.py prisma \
    --query "Your systematic review question"
```

## 📁 项目结构

```
research-suite/
├── SKILL.md                          # OpenClaw Skill 定义
├── README.md
├── LICENSE
├── requirements.txt
├── scripts/
│   ├── research.py                   # CLI 主入口
│   ├── config.py                     # 配置管理
│   ├── search/
│   │   ├── federated.py              # 联邦检索引擎
│   │   ├── pubmed.py                 # PubMed 适配器
│   │   ├── arxiv.py                  # arXiv 适配器
│   │   ├── semantic.py               # Semantic Scholar 适配器
│   │   ├── openalex.py               # OpenAlex 适配器
│   │   ├── crossref.py               # CrossRef 适配器
│   │   └── bgpt.py                   # BGPT 适配器
│   ├── assess/
│   │   ├── rob2.py                   # RoB 2 评估器
│   │   ├── robins.py                 # ROBINS-I 评估器
│   │   ├── grade.py                  # GRADE 评估器
│   │   └── jbi.py                    # JBI 评估器
│   ├── synthesize/
│   │   ├── pico.py                   # PICO 提取器
│   │   ├── evidence_table.py          # 证据表格生成器
│   │   └── prisma.py                 # PRISMA 流程图生成器
│   └── write/
│       ├── imrad.py                  # IMRAD 综述生成器
│       └── references.py             # 参考文献格式化
```

## 🔧 API Key 申请

| 服务 | 申请地址 | 免费限制 |
|------|---------|---------|
| PubMed | [NCBI](https://www.ncbi.nlm.nih.gov/home/develop/api/) | 无 Key: 3 req/s |
| Semantic Scholar | [API Portal](https://api.semanticscholar.org/) | 100 req/5min |
| OpenAlex | [openalex.org](https://docs.openalex.org/) | 10 req/sec |
| BGPT | [bgpt.pro](https://bgpt.pro/mcp) | 50 req/网络 |

## 📖 文档

详细文档见 [SKILL.md](SKILL.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)
