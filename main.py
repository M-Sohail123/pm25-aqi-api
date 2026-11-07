import os
import pickle
import pandas as pd
from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Multi-City PM2.5 & AQI Forecasting API",
    version="2.0",
    description=(
        "API for PM2.5 and Air Quality forecasting across Karachi, Lahore,"
        " Islamabad, and Multan."
    ),
)


# City ke naam ke mutabiq data load karne ka helper function
def load_city_data(city_name: str):
  city_name = city_name.lower().strip()

  # City ke mutabiq file ka naam select karna
  if city_name == "karachi":
    file_path = "karachi_results.pkl"
  elif city_name == "lahore":
    file_path = "lahore_results.pkl"
  elif city_name == "islamabad":
    file_path = "islamabad_results.pkl"
  elif city_name == "multan":
    file_path = "multan_results.pkl"
  else:
    return None

  # Check karna ke file server par mojood hai ya nahi
  if not os.path.exists(file_path):
    return None

  try:
    df = pd.read_pickle(file_path)
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
          "message": "Welcome to Multi-City Air Quality Forecasting API"
          " (Karachi, Lahore, Islamabad, Multan)"
  }


# 1. Poora data city ke lehaz se dekhne ke liye
@app.get("/api/forecast/{city}/all")
def get_all_forecasts(city: str):
  df_results = load_city_data(city)
  if df_results is None:
    raise HTTPException(
        status_code=404,
        detail=(
            f"Dataset for city '{city}' not found or file is missing on server."
        ),
    )
  return df_results.to_dict(orient="records")


# 2. Specific Date wise filter (Misal: /api/forecast/karachi/date/2026-10-15)
@app.get("/api/forecast/{city}/date/{target_date}")
def get_by_date(city: str, target_date: str):
  df_results = load_city_data(city)
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
        detail=f"No data found for {city.capitalize()} on date {target_date}",
    )
  return filtered.to_dict(orient="records")


# 3. Month wise filter (Misal: /api/forecast/lahore/month/2026/10)
@app.get("/api/forecast/{city}/month/{year}/{month}")
def get_by_month(city: str, year: int, month: int):
  df_results = load_city_data(city)
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
def get_by_year(city: str, year: int):
  df_results = load_city_data(city)
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
def get_by_day_name(city: str, day_name: str):
  df_results = load_city_data(city)
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