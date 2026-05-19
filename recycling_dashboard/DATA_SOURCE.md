# Data Sources

## 1. US National — EPA Facts and Figures (Primary Dataset)

**File:** `data/processed/clean_recycling_data.csv`  
**Coverage:** United States national, 1960–2018, annual  
**Materials:** Plastic, Paper, Glass, Ferrous Metal  
**Accessed:** April 2026

| Material | EPA Page | Notes |
|----------|----------|-------|
| Plastic  | https://www.epa.gov/facts-and-figures-about-materials-waste-and-recycling/plastics-material-specific-data | Includes all plastic resins |
| Paper    | https://www.epa.gov/facts-and-figures-about-materials-waste-and-recycling/paper-and-paperboard-material-specific-data | Includes paperboard |
| Glass    | https://www.epa.gov/facts-and-figures-about-materials-waste-and-recycling/glass-material-specific-data | Source data from Glass Packaging Institute |
| Metal    | https://www.epa.gov/facts-and-figures-about-materials-waste-and-recycling/ferrous-metals-material-specific-data | Steel/iron only; excludes aluminum |

**How recycling rate is computed:**  
`recycling_rate = (tons_recycled / tons_generated) × 100`  
Both columns are taken directly from the EPA HTML table on each page.

**Backup download (Excel):**  
https://www.epa.gov/facts-and-figures-about-materials-waste-and-recycling/studies-summary-tables-and-data-related  
→ "Summary Yearly Facts and Figures Data by material from 1960–2018 (xlsx)"

**Limitations:**
- Data ends at 2018 (EPA has not published a national update since)
- National aggregate only — does not reflect regional variation
- Plastic rate includes industrial recycling, which inflates the consumer figure slightly

---

## 2. US Regional — State Agency Annual Reports

**File:** `data/processed/regional_data.csv`  
**Coverage:** 8 US states, 2019–2020, 4 materials each  
**Method:** Manually curated from state solid-waste annual reports

| State | Source | Year | URL |
|-------|--------|------|-----|
| California | CalRecycle Annual Report | 2020 | https://www.calrecycle.ca.gov/Publications |
| Michigan | MDEQ Solid Waste Report | 2020 | https://www.michigan.gov/egle/about/organization/Materials-Management/solid-waste |
| Oregon | Oregon DEQ Recycling Rate Report | 2020 | https://www.oregon.gov/deq/mm/Pages/Recycling-Rate-Report.aspx |
| New York | NYSDEC Materials Flow Report | 2019 | https://www.dec.ny.gov/chemical/8751.html |
| Texas | TCEQ Municipal Solid Waste Summary | 2020 | https://www.tceq.texas.gov/agency/data/uploads/rops/msw/msw_summary.pdf |
| Washington | WA Ecology Solid Waste Report | 2019 | https://ecology.wa.gov/Waste-Toxics/Reducing-recycling-waste/Solid-waste-data |
| Florida | FDEP Recycling Rate Report | 2020 | https://floridadep.gov/waste/permitting-compliance-assistance/content/solid-waste-annual-report |
| Virginia | VDEQ Annual Waste Characterization | 2020 | https://www.deq.virginia.gov/programs/waste/solid-waste |

**Notes:**
- Michigan and Oregon have bottle deposit programs, explaining significantly higher Glass and Metal rates
- Texas has no statewide bottle deposit law, producing the lowest rates in this dataset
- Some rates are extracted from PDF tables; verify against the source document before citing in your final report

---

## 3. Global — OECD Municipal Waste Statistics

**File:** `data/processed/global_data.csv`  
**Coverage:** 15 countries, 2010–2022 (varies by country), MSW overall recycling rate  
**Source:** OECD Environment Statistics, served via Our World in Data  
**URL:** https://ourworldindata.org/waste  
**Direct CSV:** https://ourworldindata.org/grapher/municipal-waste-recycling-rates.csv

**Fallback:** If the live URL is unavailable, the script uses a hardcoded 2022 snapshot from:  
OECD (2024). *Municipal Waste Treatment.* OECD Environment Statistics.  
https://stats.oecd.org/Index.aspx?DataSetCode=MUNW

**Limitations:**
- Rates represent total MSW recycling (not material-specific)
- Country methodologies vary — Germany and South Korea use broader definitions that inflate their rates relative to the US
- Data lags by 1–3 years depending on the country

---

## Acknowledgements

This project uses publicly available data from:
- U.S. Environmental Protection Agency (EPA)
- Glass Packaging Institute
- Steel Recycling Institute
- Aluminum Association
- State environmental agencies (CalRecycle, MDEQ, Oregon DEQ, NYSDEC, TCEQ, WA Ecology, FDEP, VDEQ)
- OECD Environment Statistics
- Our World in Data
