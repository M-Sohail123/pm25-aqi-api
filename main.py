import os
import pandas as pd
import pickle
from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Multi-City PM2.5 & AQI Forecasting API",
    version="2.1",
    description=(
        "API for air quality forecasting across Karachi, Lahore, Islamabad,"
        " and Multan using city-specific datasets."
    ),
)

# Supported cities aur unki respective result pickle files ki mapping
CITY_FILES = {
    "karachi": "karachi_results.pkl",
    "lahore": "lahore_results.pkl",
    "islamabad": "islamabad_results.pkl",
    "multan": "multan_results.pkl",
}


# Helper function: City ke mutabiq uski specific results file load karne ke liye
def load_city_results(city: str):
  city_key = city.lower().strip()
  if city_key not in CITY_FILES:
    return None

  file_name = CITY_FILES[city_key]

  # Check karein ke file server par mojood hai ya nahi
  if not os.path.exists(file_name):
    return None

  try:
    df = pd.read_pickle(file_name)
    # Yakeen kar lein ke 'date' column datetime format mein ho
    if "date" in df.columns:
      df["date"] = pd.to_datetime(df["date"])
    return df
  except Exception as e:
    return None


@app.get("/")
def read_root():
  return {
      "status": "Online",
          "message": "Welcome to Multi-City Air Quality Forecasting API."
          " Supported cities: karachi, lahore, islamabad, multan"
  }


# 1. Poora data city ke lehaz se dekhne ke liye
@app.get("/api/forecast/{city}/all")
def get_all_by_city(city: str):
  df_results = load_city_results(city)
  if df_results is None:
    raise HTTPException(
        status_code=404,
        detail=(
            f"Dataset for city '{city}' not found or pickle file is missing on"
            " server."
        ),
    )
  return df_results.to_dict(orient="records")


# 2. Specific Date wise filter (Misal: /api/forecast/karachi/date/2026-10-15)
@app.get("/api/forecast/{city}/date/{target_date}")
def get_by_city_and_date(city: str, target_date: str):
  df_results = load_city_results(city)
  if df_results is None:
    raise HTTPException(
        status_code=404, detail=f"Dataset for city '{city}' not found."
    )

  filtered = df_results[
      df_results["date"].dt.strftime("%Y-%m-%d") == target_date
  ]
  if filtered.empty:
    raise HTTPException(
        status_code=404,
        detail=(
            f"No data found for {city.capitalize()} on date {target_date}"
        ),
    )
  return filtered.to_dict(orient="records")


# 3. Month wise filter (Misal: /api/forecast/lahore/month/2026/10)
@app.get("/api/forecast/{city}/month/{year}/{month}")
def get_by_city_and_month(city: str, year: int, month: int):
  df_results = load_city_results(city)
  if df_results is None:
    raise HTTPException(
        status_code=404, detail=f"Dataset for city '{city}' not found."
    )

  filtered = df_results[
      (df_results["date"].dt.year == year)
      & (df_results["date"].dt.month == month)
  ]
  if filtered.empty:
    raise HTTPException(
        status_code=404,
        detail=(
            f"No data found for {city.capitalize()} in {year}-{month:02d}"
        ),
    )
  return filtered.to_dict(orient="records")


# 4. Year wise filter (Misal: /api/forecast/islamabad/year/2026)
@app.get("/api/forecast/{city}/year/{year}")
def get_by_city_and_year(city: str, year: int):
  df_results = load_city_results(city)
  if df_results is None:
    raise HTTPException(
        status_code=404, detail=f"Dataset for city '{city}' not found."
    )

  filtered = df_results[df_results["date"].dt.year == year]
  if filtered.empty:
    raise HTTPException(
        status_code=404,
        detail=f"No data found for {city.capitalize()} in year {year}",
    )
  return filtered.to_dict(orient="records")


# 5. Day of the week wise filter (Misal: /api/forecast/multan/day/monday)
@app.get("/api/forecast/{city}/day/{day_name}")
def get_by_city_and_day(city: str, day_name: str):
  df_results = load_city_results(city)
  if df_results is None:
    raise HTTPException(
        status_code=404, detail=f"Dataset for city '{city}' not found."
    )

  filtered = df_results[
      df_results["date"].dt.day_name().str.lower() == day_name.lower()
  ]
  if filtered.empty:
    raise HTTPException(
        status_code=404,
        detail=f"No data found for {city.capitalize()} on {day_name}",
    )
  return filtered.to_dict(orient="records")