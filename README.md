# 📊 Sellers.json Analyzer

**Explore, filter and compare `sellers.json` files from programmatic advertising platforms.**

*Built by Ogury's Supply team · Powered by Streamlit*

![Python](https://img.shields.io/badge/Python-3.10+-005959?style=flat-square&logo=python&logoColor=C3EA76)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-005959?style=flat-square&logo=streamlit&logoColor=C3EA76)
![Plotly](https://img.shields.io/badge/Plotly-5.18+-0A9999?style=flat-square&logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/Internal-Ogury-C3EA76?style=flat-square)

</div>

---

## What it does

The web-app fetches `sellers.json` files **live** from adtech platforms and lets you explore and compare them interactively — no manual JSON parsing, no SQL joins required.

**Supported sources** *(configurable)*

| Platform | URL |
|---|---|
| **Ogury** | `https://sellers.ogury.com/` |
| **Pubmatic** | `https://cdn.pubmatic.com/sellers/data/sellers.json` |
| **Teads** | `https://sellers.teads.tv/sellers.json` |

---

## Features

### 📈 Overview
- Seller type distribution — Publisher / Intermediary / Both — as pie and bar charts
- Top N domains by seller count *(configurable)*

### 🔍 Search & Filter
- Full-text search by seller name, domain, or seller ID
- Filter by seller type · Sort by any field
- Download filtered results as CSV

### 🌐 Domain Analysis
- Top-level domain (TLD) distribution and breakdown by seller type
- Domains with multiple seller IDs *(configurable threshold)*

### 📋 Raw Data
- Full table view of all sellers
- Download the complete dataset as CSV

### 🆚 Compare Mode *(toggle in sidebar)*
- Side-by-side KPI comparison between two platforms
- Delta summary table with absolute and percentage differences
- Seller type distribution chart grouped by source
- Domain overlap — shared domains, platform-exclusive domains
- Seller ID overlap — shared IDs, IDs only in one platform, with detail drill-down
- Download comparison summary as CSV

---

## Tech stack

| Library | Purpose |
|---|---|
| `streamlit` | Web app framework |
| `pandas` | Data manipulation |
| `plotly` | Interactive charts |
| `requests` | Live HTTP fetching of sellers.json files |

> Data is cached for **1 hour** to avoid repeated fetches on every interaction.

---

## Getting started

**1. Clone the repo**
```bash
git clone https://github.com/joaquimfrancalanci/Sellers.json-Analyzer.git
cd Sellers.json-Analyzer
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
streamlit run sellers_app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## Adding a new source

Edit the `SOURCES` dictionary in `sellers_app.py`:

```python
SOURCES = {
    "Ogury":    "https://sellers.ogury.com/",
    "Pubmatic": "https://cdn.pubmatic.com/sellers/data/sellers.json",
    "Teads":    "https://sellers.teads.tv/sellers.json",
    "YourSSP":  "https://yourplatform.com/sellers.json",  # add here
}
```

---

## Feedback

A feedback form and in-app star rating are available directly in the sidebar.
For questions or issues: **joaquim.francalanci@ogury.co**

---
