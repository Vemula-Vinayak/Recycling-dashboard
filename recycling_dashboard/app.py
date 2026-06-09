# recycling_dashboard/backend/app.py

import os
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS


# Auto-detect paths — works whether app.py is in backend/ or root folder
 
HERE = Path(__file__).resolve().parent      # folder containing app.py

# Walk up until we find the folder that contains both 'data' and 'frontend'
def _find_root(start: Path) -> Path:
    for folder in [start, start.parent, start.parent.parent]:
        if (folder / "frontend").exists() and (folder / "data").exists():
            return folder
    # fallback: just use parent of app.py
    return start.parent

ROOT = _find_root(HERE)
FRONTEND_DIR = ROOT / "frontend"
DATA_DIR     = ROOT / "data" / "processed"

app = Flask(__name__, template_folder=str(FRONTEND_DIR))
CORS(app)

def _load(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Missing: {path}\n"
            "Run:  python data_preprocessing.py   (from your project folder)"
        )
    return pd.read_csv(path)

national = _load("clean_recycling_data.csv")   # year, material, recycling_rate, geography, data_source
regional = _load("regional_data.csv")           # region, year, material, recycling_rate, source
global_df = _load("global_data.csv")            # country, year, recycling_rate, material, data_source

 
# Home
 
@app.route("/")
def home():
    materials = sorted(national["material"].unique().tolist())
    regions   = sorted(regional["region"].unique().tolist())
    countries = sorted(global_df["country"].unique().tolist())
    return render_template(
        "index.html",
        materials=materials,
        regions=regions,
        countries=countries,
    )


# National endpoints

@app.route("/api/national")
def api_national():
    """All national data, optionally filtered by material."""
    material = request.args.get("material")
    df = national.copy()
    if material:
        df = df[df["material"] == material]
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/national/summary")
def api_national_summary():
    """Average recycling rate per material across all years."""
    summary = (
        national.groupby("material")["recycling_rate"]
        .agg(["mean", "min", "max", "count"])
        .round(2)
        .reset_index()
        .rename(columns={"mean": "avg_rate", "min": "min_rate",
                         "max": "max_rate", "count": "years_available"})
    )
    return jsonify(summary.to_dict(orient="records"))


@app.route("/api/national/trend")
def api_national_trend():
    """
    Year-by-year recycling rates for one or all materials.
    Returns data shaped for Chart.js line charts:
      { labels: [year, ...], datasets: [{label, data}, ...] }
    """
    material = request.args.get("material")  # optional filter
    df = national.copy()
    if material:
        df = df[df["material"] == material]

    years    = sorted(df["year"].unique().tolist())
    datasets = []
    for mat in sorted(df["material"].unique()):
        sub   = df[df["material"] == mat].set_index("year")
        rates = [round(sub.loc[y, "recycling_rate"], 2) if y in sub.index else None
                 for y in years]
        datasets.append({"label": mat, "data": rates})

    return jsonify({"labels": years, "datasets": datasets})


 
# Regional endpoints
 
@app.route("/api/regional")
def api_regional():
    """State-level data, optionally filtered by region and/or material."""
    region   = request.args.get("region")
    material = request.args.get("material")
    df = regional.copy()
    if region:
        df = df[df["region"] == region]
    if material:
        df = df[df["material"] == material]
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/regional/compare")
def api_regional_compare():
    """
    Side-by-side rate per region for a given material.
    Returns data shaped for Chart.js bar chart:
      { labels: [state, ...], datasets: [{label, data}, ...] }
    """
    material = request.args.get("material", "Plastic")
    df = regional[regional["material"] == material].copy()
    df = df.sort_values("recycling_rate", ascending=False)
    return jsonify({
        "labels":   df["region"].tolist(),
        "datasets": [{"label": f"{material} recycling rate (%)",
                      "data": df["recycling_rate"].round(2).tolist()}]
    })


 
# Global endpoints
 
@app.route("/api/global")
def api_global():
    """Country-level data, optionally filtered by country."""
    country = request.args.get("country")
    df = global_df.copy()
    if country:
        df = df[df["country"] == country]
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/global/compare")
def api_global_compare():
    """
    Latest recycling rate per country, sorted descending.
    Returns Chart.js bar chart format.
    """
    # Use each country's most recent year
    latest = (
        global_df.sort_values("year")
        .groupby("country")
        .last()
        .reset_index()
        .sort_values("recycling_rate", ascending=False)
    )
    return jsonify({
        "labels":   latest["country"].tolist(),
        "datasets": [{"label": "Recycling rate (%, most recent year)",
                      "data": latest["recycling_rate"].round(1).tolist()}]
    })


 
# Metadata / health check
 
@app.route("/api/info")
def api_info():
    return jsonify({
        "national_rows":  len(national),
        "regional_rows":  len(regional),
        "global_rows":    len(global_df),
        "materials":      sorted(national["material"].unique().tolist()),
        "states":         sorted(regional["region"].unique().tolist()),
        "countries":      sorted(global_df["country"].unique().tolist()),
        "national_years": f"{int(national['year'].min())}–{int(national['year'].max())}",
    })




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)