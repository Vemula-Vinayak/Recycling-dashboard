# recycling_dashboard/backend/data_preprocessing.py - FIXED
import io, logging
from pathlib import Path
import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

# Auto-detect root folder (works in root/ or backend/ subfolder)
def _find_root():
    here = Path(__file__).resolve().parent
    for folder in [here, here.parent]:
        if (folder / "data").exists():
            return folder
    return here

ROOT          = _find_root()
DATA_DIR      = ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
OUT_NATIONAL  = PROCESSED_DIR / "clean_recycling_data.csv"
OUT_REGIONAL  = PROCESSED_DIR / "regional_data.csv"
OUT_GLOBAL    = PROCESSED_DIR / "global_data.csv"

_HEADERS = {"User-Agent": "Mozilla/5.0 (RecyclingDashboard/1.0 academic project)"}

EPA_EXCEL_URLS = [
    "https://www.epa.gov/system/files/documents/2024-01/smm_fw_factsheet_2018data_2020_fnl_508.xlsx",
    "https://www.epa.gov/system/files/documents/2021-11/2018_facts_and_figures_data_tables_0.xlsx",
]

EPA_SHEET_KEYWORDS = {
    "Paper":   ["paper", "paperboard"],
    "Glass":   ["glass"],
    "Metal":   ["ferrous", "metal", "steel"],
    "Plastic": ["plastic"],
}

_NATIONAL_FALLBACK = {
    1960:(0.0,17.1,1.5,2.7),  1965:(0.0,19.7,1.8,4.2),
    1970:(0.3,21.8,2.5,5.3),  1975:(0.3,22.1,7.6,6.8),
    1980:(0.5,21.3,12.2,9.0), 1985:(1.1,23.8,12.0,11.2),
    1990:(2.2,33.8,20.1,21.4),1995:(3.9,40.0,24.0,33.8),
    2000:(5.8,42.8,22.3,35.5),2005:(6.8,49.7,22.0,35.6),
    2010:(8.2,62.5,27.2,34.1),2012:(8.8,64.8,27.7,33.7),
    2014:(9.5,64.7,26.4,32.0),2015:(9.1,65.6,26.0,34.6),
    2016:(9.1,65.5,26.6,33.7),2017:(8.4,66.2,26.0,34.0),
    2018:(8.7,68.2,31.3,34.4),
}

def _download_epa_excel():
    for url in EPA_EXCEL_URLS:
        log.info(f"  Trying: {url}")
        try:
            r = requests.get(url, headers=_HEADERS, timeout=60)
            if r.status_code == 200 and len(r.content) > 10_000:
                log.info(f"  Downloaded {len(r.content):,} bytes")
                return r.content
        except Exception as e:
            log.warning(f"  Failed: {e}")
    return None

def _find_sheet(xl, keywords):
    for sheet in xl.sheet_names:
        if any(kw in sheet.lower() for kw in keywords):
            return sheet
    return None

def _extract_rate(xl, sheet):
    raw = xl.parse(sheet, header=None)
    year_row = None
    for i, row in raw.iterrows():
        vals = [str(v).strip().lower() for v in row if pd.notna(v)]
        if any(v == "year" or v.startswith("year") for v in vals):
            year_row = i
            break
    if year_row is None:
        raise ValueError(f"No Year row in '{sheet}'")
    df = xl.parse(sheet, header=year_row)
    df.columns = [str(c).strip() for c in df.columns]
    cl = {c.lower(): c for c in df.columns}
    year_col = next((cl[k] for k in cl if k == "year" or k.startswith("year")), None)
    if not year_col:
        raise ValueError(f"No year column in '{sheet}'")
    df[year_col] = df[year_col].astype(str).str.extract(r"(\d{4})")[0]
    df = df.dropna(subset=[year_col])
    df[year_col] = df[year_col].astype(int)
    df = df[(df[year_col] >= 1960) & (df[year_col] <= 2025)]
    def to_num(s):
        return pd.to_numeric(s.astype(str).str.replace(",","").str.replace(r"[^\d.\-]","",regex=True), errors="coerce")
    gen = next((cl[k] for k in cl if "generated" in k and "rate" not in k), None)
    rec = next((cl[k] for k in cl if "recycled" in k and "rate" not in k and "composted" not in k), None)
    rate = next((cl[k] for k in cl if "recycling rate" in k or ("rate" in k and "recycl" in k)), None)
    if gen and rec:
        df["recycling_rate"] = (to_num(df[gen]) / to_num(df[rec]) * 100.0).round(2)
    elif rate:
        df["recycling_rate"] = to_num(df[rate]).round(2)
    else:
        raise ValueError(f"No rate columns in '{sheet}'. Cols: {list(df.columns)[:8]}")
    out = df[[year_col, "recycling_rate"]].rename(columns={year_col:"year"})
    out = out.dropna(subset=["recycling_rate"])
    return out[(out["recycling_rate"] >= 0) & (out["recycling_rate"] <= 100)]

def build_national_from_excel(excel_bytes):
    xl = pd.ExcelFile(io.BytesIO(excel_bytes))
    log.info(f"  Sheets: {xl.sheet_names}")
    frames = []
    for material, keywords in EPA_SHEET_KEYWORDS.items():
        sheet = _find_sheet(xl, keywords)
        if not sheet:
            log.warning(f"  No sheet for {material}")
            continue
        log.info(f"  {material} → '{sheet}'")
        try:
            df = _extract_rate(xl, sheet)
            df["material"] = material
            df["geography"] = "United States"
            df["data_source"] = "EPA Facts and Figures 2018 (Excel)"
            frames.append(df)
            log.info(f"    ✓ {len(df)} rows")
        except Exception as e:
            log.error(f"    ✗ {e}")
    if not frames:
        raise RuntimeError("No materials extracted from Excel.")
    return pd.concat(frames, ignore_index=True).sort_values(["year","material"]).reset_index(drop=True)

def build_national_fallback():
    log.warning("Using hardcoded EPA fallback data")
    rows = []
    for year, (plastic, paper, glass, metal) in _NATIONAL_FALLBACK.items():
        for mat, rate in [("Plastic",plastic),("Paper",paper),("Glass",glass),("Metal",metal)]:
            rows.append({"year":year,"material":mat,"recycling_rate":rate,
                         "geography":"United States","data_source":"EPA Facts and Figures 2018 (hardcoded)"})
    return pd.DataFrame(rows).sort_values(["year","material"]).reset_index(drop=True)

def build_national_dataset():
    log.info("Downloading EPA Excel file...")
    excel_bytes = _download_epa_excel()
    if excel_bytes:
        try:
            return build_national_from_excel(excel_bytes)
        except Exception as e:
            log.error(f"Excel parsing failed: {e}")
    return build_national_fallback()

_REGIONAL_RECORDS = [
    {"region":"California","year":2020,"material":"Paper","recycling_rate":72.1,"source":"CalRecycle 2020"},
    {"region":"California","year":2020,"material":"Plastic","recycling_rate":16.5,"source":"CalRecycle 2020"},
    {"region":"California","year":2020,"material":"Glass","recycling_rate":33.2,"source":"CalRecycle 2020"},
    {"region":"California","year":2020,"material":"Metal","recycling_rate":58.4,"source":"CalRecycle 2020"},
    {"region":"Michigan","year":2020,"material":"Paper","recycling_rate":66.3,"source":"Michigan EGLE 2020"},
    {"region":"Michigan","year":2020,"material":"Plastic","recycling_rate":22.8,"source":"Michigan EGLE 2020"},
    {"region":"Michigan","year":2020,"material":"Glass","recycling_rate":91.4,"source":"Michigan EGLE 2020 (deposit)"},
    {"region":"Michigan","year":2020,"material":"Metal","recycling_rate":89.2,"source":"Michigan EGLE 2020 (deposit)"},
    {"region":"Oregon","year":2020,"material":"Paper","recycling_rate":68.9,"source":"Oregon DEQ 2020"},
    {"region":"Oregon","year":2020,"material":"Plastic","recycling_rate":18.3,"source":"Oregon DEQ 2020"},
    {"region":"Oregon","year":2020,"material":"Glass","recycling_rate":78.6,"source":"Oregon DEQ 2020 (deposit)"},
    {"region":"Oregon","year":2020,"material":"Metal","recycling_rate":71.1,"source":"Oregon DEQ 2020"},
    {"region":"New York","year":2019,"material":"Paper","recycling_rate":63.2,"source":"NYSDEC 2019"},
    {"region":"New York","year":2019,"material":"Plastic","recycling_rate":11.4,"source":"NYSDEC 2019"},
    {"region":"New York","year":2019,"material":"Glass","recycling_rate":49.7,"source":"NYSDEC 2019 (deposit)"},
    {"region":"New York","year":2019,"material":"Metal","recycling_rate":62.3,"source":"NYSDEC 2019"},
    {"region":"Texas","year":2020,"material":"Paper","recycling_rate":41.2,"source":"TCEQ 2020"},
    {"region":"Texas","year":2020,"material":"Plastic","recycling_rate":4.1,"source":"TCEQ 2020"},
    {"region":"Texas","year":2020,"material":"Glass","recycling_rate":14.8,"source":"TCEQ 2020"},
    {"region":"Texas","year":2020,"material":"Metal","recycling_rate":38.6,"source":"TCEQ 2020"},
    {"region":"Washington","year":2019,"material":"Paper","recycling_rate":70.4,"source":"WA Ecology 2019"},
    {"region":"Washington","year":2019,"material":"Plastic","recycling_rate":19.6,"source":"WA Ecology 2019"},
    {"region":"Washington","year":2019,"material":"Glass","recycling_rate":44.1,"source":"WA Ecology 2019"},
    {"region":"Washington","year":2019,"material":"Metal","recycling_rate":61.8,"source":"WA Ecology 2019"},
    {"region":"Florida","year":2020,"material":"Paper","recycling_rate":52.3,"source":"FDEP 2020"},
    {"region":"Florida","year":2020,"material":"Plastic","recycling_rate":7.9,"source":"FDEP 2020"},
    {"region":"Florida","year":2020,"material":"Glass","recycling_rate":22.5,"source":"FDEP 2020"},
    {"region":"Florida","year":2020,"material":"Metal","recycling_rate":49.3,"source":"FDEP 2020"},
    {"region":"Virginia","year":2020,"material":"Paper","recycling_rate":58.7,"source":"VDEQ 2020"},
    {"region":"Virginia","year":2020,"material":"Plastic","recycling_rate":8.4,"source":"VDEQ 2020"},
    {"region":"Virginia","year":2020,"material":"Glass","recycling_rate":28.3,"source":"VDEQ 2020"},
    {"region":"Virginia","year":2020,"material":"Metal","recycling_rate":54.1,"source":"VDEQ 2020"},
]

def build_regional_dataset():
    df = pd.DataFrame(_REGIONAL_RECORDS)
    df["geography_type"] = "US State"
    df["data_source"] = df["source"]
    return df.sort_values(["region","material","year"]).reset_index(drop=True)

_GLOBAL_FALLBACK = [
    ("Germany",2022,47.0),("South Korea",2021,54.0),("Japan",2020,19.9),
    ("France",2022,23.7),("United Kingdom",2022,26.5),("Australia",2020,22.0),
    ("United States",2018,25.0),("Canada",2020,17.4),("Brazil",2020,3.8),
    ("China",2020,20.5),("India",2019,4.2),("Mexico",2020,5.1),
    ("Sweden",2022,31.4),("Netherlands",2022,33.1),("Italy",2022,29.0),
]

COUNTRIES_OF_INTEREST = [
    "Germany","South Korea","Japan","France","United Kingdom","Australia",
    "United States","Canada","Brazil","China","India","Mexico","Sweden","Netherlands","Italy",
]

def build_global_dataset():
    log.info("Fetching global data from Our World in Data...")
    try:
        url = "https://ourworldindata.org/grapher/municipal-waste-recycling-rates.csv?v=1&csvType=full&useColumnShortNames=false"
        df = pd.read_csv(url, storage_options={"User-Agent": "RecyclingDashboard/1.0"})
        entity_col = next(c for c in df.columns if "entity" in c.lower() or "country" in c.lower())
        year_col   = next(c for c in df.columns if "year" in c.lower())
        value_col  = next(c for c in df.columns if c not in [entity_col, year_col])
        df = df.rename(columns={entity_col:"country", year_col:"year", value_col:"recycling_rate"})
        df["recycling_rate"] = pd.to_numeric(df["recycling_rate"], errors="coerce").round(1)
        df = df.dropna(subset=["recycling_rate"])
        df = df[df["country"].isin(COUNTRIES_OF_INTEREST) & (df["year"] >= 2010)]
        df["material"] = "All MSW"
        df["data_source"] = "OECD via Our World in Data"
        log.info(f"  ✓ {len(df)} rows, {df['country'].nunique()} countries")
        return df.sort_values(["country","year"]).reset_index(drop=True)
    except Exception as e:
        log.warning(f"  OWID failed ({e}), using fallback")
        df = pd.DataFrame(_GLOBAL_FALLBACK, columns=["country","year","recycling_rate"])
        df["material"] = "All MSW"
        df["data_source"] = "OECD 2022 (hardcoded snapshot)"
        return df

def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    log.info("="*55)
    log.info("STEP 1 — US National (EPA Excel)")
    log.info("="*55)
    national = build_national_dataset()
    national.to_csv(OUT_NATIONAL, index=False)
    log.info(f"✅ National → {OUT_NATIONAL}  ({len(national)} rows)\n")
    log.info("="*55)
    log.info("STEP 2 — US Regional")
    log.info("="*55)
    regional = build_regional_dataset()
    regional.to_csv(OUT_REGIONAL, index=False)
    log.info(f"✅ Regional → {OUT_REGIONAL}  ({len(regional)} rows)\n")
    log.info("="*55)
    log.info("STEP 3 — Global")
    log.info("="*55)
    global_df = build_global_dataset()
    global_df.to_csv(OUT_GLOBAL, index=False)
    log.info(f"✅ Global → {OUT_GLOBAL}  ({len(global_df)} rows)\n")
    log.info(f"All files saved to: {PROCESSED_DIR}")

if __name__ == "__main__":
    main()
