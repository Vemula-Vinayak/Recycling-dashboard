# Recycling Awareness Data Dashboard

A full-stack data analytics web dashboard analyzing US and global recycling rates across **Plastic, Paper, Glass, and Metal** using real government data spanning 1960–2022.

Built as the capstone project for **CSIT 697 – Master's Project** at Montclair State University.

> **Team:** Varshitha Kayithi (MS Computer Science) · Vinayak Vemula (MS Data Science)

---

## Key Findings

| # | Finding |
|---|---------|
| F1 | Plastic has **never exceeded 10%** in 58 years — peaked at 8.7% in 2018 |
| F2 | Paper grew from **16.9% → 68.2%** (+51 pp), the strongest recycling success story |
| F3 | Deposit-law states recycle **2.4× more glass** (73.2% vs 30.4%) |
| F4 | **51 pp gap** between Michigan (67.4%) and Texas (24.7%) — driven entirely by policy |
| F5 | US ranks **7th of 15 OECD nations** at 25% — half the rate of South Korea (54%) and Germany (47%) |

---

## Regression Results

| Material | Slope (pp/yr) | R² | p-value |
|----------|:---:|:---:|:---:|
| Paper | +1.02 | 0.97 | <0.001 |
| Metal | +0.58 | 0.91 | <0.001 |
| Glass | +0.44 | 0.72 | 0.004 |
| Plastic | +0.14 | 0.89 | <0.001 |

---

## Dashboard Sections

- **About** — stat cards and key findings overview
- **US Trends** — interactive line chart with material filter (1960–2018)
- **By State** — bar chart, heatmap, and deposit law comparison (8 states)
- **Global** — horizontal bar chart comparing 15 OECD countries

---

## Project Structure

```
recycling_dashboard/
├── README.md
├── DATA_SOURCE.md
├── recycling_eda.ipynb          # EDA notebook — 22 cells, 12 charts
├── backend/
│   ├── app.py                   # Flask API — 9 endpoints, 193 lines
│   ├── data_preprocessing.py    # Downloads EPA Excel, cleans, exports CSVs
│   └── requirements.txt
├── data/
│   └── processed/
│       ├── clean_recycling_data.csv   # US national, 68 rows (1960–2018)
│       ├── regional_data.csv          # 8 states, 32 rows
│       └── global_data.csv            # 15 OECD countries
├── frontend/
│   └── index.html               # Chart.js dashboard, dark mode, real-time filters
└── charts/
    └── (12 PNG chart files)
```

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/national` | All national data — optional `?material=` filter |
| `GET /api/national/trend` | Chart.js-ready line chart data |
| `GET /api/national/summary` | Average rate per material |
| `GET /api/regional` | State data with filters |
| `GET /api/regional/compare` | States ranked by material |
| `GET /api/global` | Country data |
| `GET /api/global/compare` | Countries ranked by MSW recycling rate |
| `GET /api/info` | Dataset summary |

---

## Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/recycling-dashboard.git
cd recycling-dashboard
pip install -r backend/requirements.txt
```

### Run the data pipeline

```bash
python backend/data_preprocessing.py
```

This downloads the EPA Excel file, cleans the data, and exports the 3 CSV files to `data/processed/`.

### Start the Flask server

```bash
python backend/app.py
```

### Open the dashboard

Open `frontend/index.html` in your browser. The dashboard connects to the Flask API at `http://localhost:5000`.

---

## Data Sources

- **US National (1960–2018):** [EPA Facts and Figures](https://www.epa.gov/facts-and-figures-about-materials-waste-and-recycling)
- **Regional (8 states):** CalRecycle, Michigan EGLE, Oregon DEQ, NYSDEC, TCEQ, WA Ecology, FDEP, VDEQ
- **Global (15 OECD countries):** [Our World in Data](https://ourworldindata.org/waste) via OECD

See `DATA_SOURCE.md` for full citations.

---

## Tech Stack

**Backend:** Python · Flask · Flask-CORS · pandas · numpy · scipy · requests · openpyxl

**Frontend:** HTML5 · CSS3 · JavaScript · Chart.js

**Analysis:** Linear regression · Pearson correlation · box plots · histograms · deposit law analysis

---

## EDA Highlights

The `recycling_eda.ipynb` notebook contains 22 code cells across 8 sections with 12 saved charts:

`chart_national_trends` · `chart_regression` · `chart_boxplot` · `chart_distributions` · `chart_heatmap` · `chart_regional` · `chart_deposit_law` · `chart_global` · `chart_correlation` · `chart_scatter_regional` · `chart_decade_change` · `chart_summary`

---

## Authors

| Name | Program | ID | Contributions |
|------|---------|-----|---------------|
| Vinayak Vemula | MS Data Science | 50124145 | Data pipeline, EDA notebook, statistical analysis, reports |
| Varshitha Kayithi | MS Computer Science | 50123684 | Flask API, Chart.js dashboard, frontend, dark mode, filters |

---

*CSIT 697 – Master's Project · Montclair State University*
