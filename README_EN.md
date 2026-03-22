# PaperTools — Scientific Literature & Evidence Assistant

A comprehensive literature research toolkit: multi-source search, evidence quality assessment, meta-analysis, and knowledge graph construction — **zero API keys required to start**.

**GitHub**: https://github.com/xiaguxunlian-dev/PaperTools

---

## 🚀 Quick Start (GUI Version Recommended)

Download the standalone executable and double-click to run — no installation required!

| Platform | Download | Size | Requirements |
|----------|----------|------|--------------|
| Windows | [PaperTools.exe](https://github.com/xiaguxunlian-dev/PaperTools/releases/download/v1.0.0/PaperTools.exe) | ~13 MB | Windows 10/11 |

**GUI Features:**
- 🎨 Modern interface with large fonts and rounded corners — ideal for laptops and seniors
- 🔍 Visual search across multiple databases (PubMed, arXiv, Semantic Scholar, etc.)
- 📊 One-click evidence quality assessment
- 📋 PICO framework extraction
- 🌲 Forest plot generation
- 📈 Knowledge graph construction
- 💾 Export results to multiple formats

---

## Features

| Module | Command | Description |
|--------|---------|-------------|
| 🔍 **Search** | `search` | Concurrent search across PubMed / arXiv / Semantic Scholar / OpenAlex / CrossRef |
| 📊 **Assessment** | `assess` | RoB 2 / ROBINS-I / GRADE / JBI standardized quality assessment |
| 📋 **PICO Extraction** | `pico` | Auto-extract Population / Intervention / Comparison / Outcome from text |
| 📝 **Evidence Table** | `table` | Generate Markdown / CSV / JSON evidence summary tables |
| 🌲 **PRISMA Flowchart** | `prisma` | Generate PRISMA systematic review flowchart data |
| 📖 **Review Writer** | `review` | IMRAD-format review article draft generation |
| 📚 **References** | `refs` | BibTeX / Vancouver / RIS multi-format citation export |
| 🔬 **Meta-Analysis** | `meta` | Effect size extraction + heterogeneity calculation + forest plot |
| 🌲 **Forest Plot** | `forest` | ASCII / Plotly / RevMan / Stata forest plots |
| 🕸️ **Knowledge Graph** | `kg-build` | Build KG from local files or papers, export to Neo4j / JSON / NetworkX |
| 📈 **Research Trends** | `kg-trends` | Entity timelines + hotspot analysis + gap discovery |
| ⚙️ **Configuration** | `config` | API key storage and management |

---

## 📥 Download & Installation

### Option 1: GUI Version (Recommended for Most Users)

Download `PaperTools.exe` from the [Releases](https://github.com/xiaguxunlian-dev/PaperTools/releases) page and double-click to run. No installation or Python required!

**System Requirements:**
- Windows 10/11 (64-bit)
- Screen resolution: 1920×1080 or higher recommended
- Internet connection for database search

### Option 2: CLI Version (For Advanced Users)

```powershell
# 1. Install Python 3.12+
winget install Python.Python.3.12
# Or download from https://python.org (check "Add to PATH" during install)

# 2. Clone the repo
git clone https://github.com/xiaguxunlian-dev/PaperTools.git
cd PaperTools

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify
python scripts/paper_tools.py --help
```

### Option 3: Portable Python (No Install Required)

```powershell
# Just Python — run directly
python scripts/paper_tools.py search "CRISPR cancer" --database pubmed --limit 3
```

---

## 📊 Usage Workflow

### GUI Version (PaperTools.exe)

```
┌─────────────────────────────────────────────────────────────┐
│  1. Launch      → Double-click PaperTools.exe               │
│  2. Search      → Enter keywords, select databases          │
│  3. Browse      → View results in the results panel         │
│  4. Assess      → Click "Quality Assessment" for RoB/GRADE  │
│  5. Extract     → Use "PICO Extraction" for framework       │
│  6. Export      → Save results as Markdown/CSV/JSON         │
└─────────────────────────────────────────────────────────────┘
```

**Interface Highlights:**
- 🖥️ **Large Fonts**: 3× enlarged text for comfortable reading on any screen
- 🎨 **Modern Design**: Large rounded corners (R16-R32) for a polished look
- 🖱️ **One-Click Actions**: All major functions accessible via buttons
- 📋 **Copy & Export**: Easy result copying and multi-format export

---

## Tutorial

### 1. Literature Search

```powershell
# PubMed (no API key needed)
python scripts/paper_tools.py search "CRISPR cancer" --database pubmed --limit 5

# arXiv
python scripts/paper_tools.py search "machine learning healthcare" --database arxiv --limit 5

# Multiple databases at once
python scripts/paper_tools.py search "PD-1 immunotherapy" --database pubmed,semantic --limit 3

# JSON output (for programmatic use)
python scripts/paper_tools.py search "metformin diabetes" --database pubmed --json
```

### 2. Evidence Quality Assessment

```powershell
# GRADE assessment (keyword-based auto-analysis)
python scripts/paper_tools.py assess --tool grade --query "Aspirin cardiovascular prevention"

# RoB 2 for RCT bias risk
python scripts/paper_tools.py assess --tool rob2 --papers paper1.txt paper2.txt

# JBI checklist
python scripts/paper_tools.py assess --tool jbi --papers paper.txt
```

### 3. PICO Framework Extraction

```powershell
python scripts/paper_tools.py pico --text "Aspirin for cardiovascular disease prevention in adults with diabetes mellitus"
```

### 4. Meta-Analysis

```powershell
# Load study data from JSON
python scripts/paper_tools.py meta --studies studies.json --model random --output result.json

# Extract effect sizes from paper text
python scripts/paper_tools.py meta --extract paper_abstract.txt --model random
```

**studies.json format**:
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

### 5. Forest Plot

```powershell
# ASCII forest plot (zero dependencies)
python scripts/paper_tools.py forest --format ascii

# JSON format (for programmatic use)
python scripts/paper_tools.py forest --format json --output forest.json

# Interactive HTML with Plotly
python scripts/paper_tools.py forest --format plotly --output forest.html
```

### 6. Knowledge Graph Construction

```powershell
# Build KG from local text files
python scripts/paper_tools.py kg-build --texts ./test_corpus --format json

# Build from PubMed search results
python scripts/paper_tools.py search "TP53 cancer" --database pubmed --limit 20 --json > papers.json
python scripts/paper_tools.py kg-build --papers papers.json --format neo4j --output kg.cypher

# Research trend analysis
python scripts/paper_tools.py kg-trends --kg kg.json --output trends.json
```

### 7. Review Article Writing

```powershell
# Generate IMRAD-format review draft
python scripts/paper_tools.py review --topic "CRISPR gene editing cancer therapy" --output review.md

# Specify sections
python scripts/paper_tools.py review --topic "Immunotherapy melanoma" \
  --sections background,methods,results,discussion
```

---

## API Key Configuration (Optional)

| Database | Sign Up | Use Case |
|----------|---------|----------|
| PubMed (NCBI) | https://ncbi.nlm.nih.gov/account | Higher search limits |
| Semantic Scholar | https://api.semanticscholar.org | Citation data |
| OpenAlex | https://dev.openalex.org | Knowledge graph data |
| CrossRef | https://crossref.org | Metadata |

```powershell
# Set API keys
python scripts/paper_tools.py config --set-key pubmed=YOUR_KEY
python scripts/paper_tools.py config --set-key semantic=YOUR_KEY

# List configured keys
python scripts/paper_tools.py config --list-keys
```

---

## 📁 Project Structure

```
PaperTools/
├── PaperTools.exe           # 🎨 GUI version (Windows executable)
├── scripts/
│   ├── main_gui.py          # GUI entry point (Tkinter)
│   ├── paper_tools.py       # Main CLI entry point
│   ├── config.py            # Configuration management
│   ├── search/              # Multi-source search adapters
│   │   ├── federated.py    # Federated search engine
│   │   ├── pubmed.py      # PubMed / Europe PMC
│   │   ├── arxiv.py       # arXiv
│   │   ├── semantic.py     # Semantic Scholar
│   │   ├── openalex.py   # OpenAlex
│   │   ├── crossref.py   # CrossRef
│   │   └── bgpt.py       # BGPT medical database
│   ├── assess/             # Quality assessment tools
│   │   ├── rob2.py       # RoB 2 (Cochrane)
│   │   ├── robins.py      # ROBINS-I
│   │   ├── grade.py       # GRADE
│   │   └── jbi.py        # JBI checklist
│   ├── synthesize/           # Evidence synthesis
│   │   ├── pico.py       # PICO framework
│   │   ├── evidence_table.py # Evidence table
│   │   └── prisma.py    # PRISMA flowchart
│   ├── write/              # Writing assistance
│   │   ├── imrad.py     # IMRAD review
│   │   └── references.py # Citation formatter
│   ├── meta/              # Meta-analysis
│   │   ├── effect_size.py # Effect size extraction
│   │   ├── heterogeneity.py # Heterogeneity statistics
│   │   ├── forest_plot.py # Forest plot
│   │   └── analyzer.py   # Meta-analysis pipeline
│   └── kg/               # Knowledge graph
│       ├── extractor.py     # Entity/relation extraction
│       └── builder.py      # KG builder + trend analysis
├── SKILL.md              # OpenClaw Skill definition
├── requirements.txt      # Python dependencies
├── README.md            # Chinese documentation
└── README_EN.md         # This file
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `requests` | HTTP requests |
| `aiohttp` | Async concurrent search |
| `feedparser` | PubMed XML parsing |
| `matplotlib` | Forest plot visualization (optional) |
| `networkx` | Graph network analysis (optional) |

> **Zero-dependency mode**: All core modules are fully standalone. Search and assessment work with Python 3.10+ alone — no pip install needed.

---

## ❓ FAQ

**Q: How do I use the GUI version?**
A: Download `PaperTools.exe` from [Releases](https://github.com/xiaguxunlian-dev/PaperTools/releases), double-click to run. No installation needed!

**Q: What are the GUI system requirements?**
A: Windows 10/11 with 1920×1080 resolution recommended. The interface uses large fonts for accessibility.

**Q: PubMed returns 0 results?**
A: Check internet access to `https://eutils.ncbi.nlm.nih.gov`. The API is free and no VPN is needed.

**Q: SSL errors on corporate network?**
A: Try:
```powershell
set SSL_CERT_FILE=C:\Python312\Lib\site-packages\certifi\cacert.pem
python scripts/paper_tools.py search "query" --database pubmed
```

**Q: arXiv times out?**
A: arXiv now requires HTTPS. Ensure network can access `https://export.arxiv.org`.

**Q: How to batch-process multiple papers?**
A: Save papers as `.txt` files in a directory:
```powershell
python scripts/paper_tools.py kg-build --texts ./papers/ --format json
```

---

## 🎨 GUI Features

| Feature | Description |
|---------|-------------|
| 🔍 **Visual Search** | Search across PubMed, arXiv, Semantic Scholar, OpenAlex, CrossRef |
| 📊 **Quality Assessment** | RoB 2, ROBINS-I, GRADE, JBI with visual reports |
| 📋 **PICO Extraction** | Auto-extract Population/Intervention/Comparison/Outcome |
| 🌲 **Forest Plot** | Generate and visualize meta-analysis forest plots |
| 🕸️ **Knowledge Graph** | Build and explore research knowledge graphs |
| 💾 **Multi-format Export** | Markdown, CSV, JSON, BibTeX, RIS |
| 🖥️ **Large Fonts** | 3× enlarged text for accessibility |
| 🎨 **Modern UI** | Large rounded corners, gradient buttons, card-based layout |

---

## License

MIT License

Star the repo if this tool helps your research!
