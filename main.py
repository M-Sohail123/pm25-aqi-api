import pickle
import pandas as pd
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Karachi PM2.5 & AQI Forecasting API", version="1.0")

# Server start hotay hi saved dataframe ko load karna
try:
  df_results = pd.read_pickle("df_gbr_forecast_results.pkl")
except Exception as e:
  df_results = None

# Model load karna (agar future mein live single-point prediction ki zaroorat paray)
# try:
#   with open("pm25_gbr_model.pkl", "rb") as f:
#     loaded_model = pickle.load(f)
# except Exception as e:
#   loaded_model = None

# Yakeen kar lein ke 'date' column datetime format mein ho
df_results["date"] = pd.to_datetime(df_results["date"])

@app.get("/")
def read_root():
  return {
      "status": "Online",
      "message": "Welcome to Karachi Air Quality Forecasting API",
  }


@app.get("/api/forecast/all")
def get_all_forecasts():
  """Android app ke liye poora historical aur predicted dataset return karta hai

  jismein date, PM2.5, AQI level, color aur advice shamil hain.
  """
  if df_results is None:
    raise HTTPException(status_code=404, detail="Dataset not found on server.")

  # DataFrame ko JSON list of dictionaries mein convert karna
  return df_results.to_dict(orient="records")


# @app.get("/api/forecast/date/{target_date}")
# def get_forecast_by_date(target_date: str):
#   """Kisi specific date ke liye PM2.5 aur AQI details filter karke deta hai"""
#   if df_results is None:
#     raise HTTPException(status_code=404, detail="Dataset not found on server.")

#   # Date column ke mutabiq filter karna
#   filtered_df = df_results[df_results["date"].astype(str) == target_date]

#   if filtered_df.empty:
#     raise HTTPException(
#         status_code=404, detail=f"No data found for date: {target_date}"
#     )

#   return filtered_df.to_dict(orient="records")


# 1. Specific Date wise filter (Misal: 2026-10-15)
@app.get("/api/forecast/date/{target_date}")
def get_by_date(target_date: str):
  if df_results is None:
    raise HTTPException(status_code=404, detail="Dataset not found on server.")

  filtered = df_results[
      df_results["date"].dt.strftime("%Y-%m-%d") == target_date
  ]
  if filtered.empty:
    raise HTTPException(
        status_code=404, detail=f"No data found for date {target_date}"
    )
  return filtered.to_dict(orient="records")


# 2. Month wise filter (Misal: Year 2026 aur Month 10)
@app.get("/api/forecast/month/{year}/{month}")
def get_by_month(year: int, month: int):
  if df_results is None:
    raise HTTPException(status_code=404, detail="Dataset not found on server.")

  filtered = df_results[
      (df_results["date"].dt.year == year)
      & (df_results["date"].dt.month == month)
  ]
  if filtered.empty:
    raise HTTPException(
        status_code=404, detail=f"No data found for {year}-{month:02d}"
    )
  return filtered.to_dict(orient="records")


# 3. Year wise filter (Misal: 2026)
@app.get("/api/forecast/year/{year}")
def get_by_year(year: int):
  if df_results is None:
    raise HTTPException(status_code=404, detail="Dataset not found on server.")
  
  filtered = df_results[df_results["date"].dt.year == year]
  if filtered.empty:
    raise HTTPException(
        status_code=404, detail=f"No data found for year {year}"
    )
  return filtered.to_dict(orient="records")


# 4. Day of the week wise filter (Misal: 'Monday', 'Friday')
@app.get("/api/forecast/day/{day_name}")
def get_by_day_name(day_name: str):
  if df_results is None:
    raise HTTPException(status_code=404, detail="Dataset not found on server.")
  
  # day_name jaise 'Monday', 'Tuesday'
  filtered = df_results[
      df_results["date"].dt.day_name().str.lower() == day_name.lower()
  ]
  if filtered.empty:
    raise HTTPException(
        status_code=404, detail=f"No data found for day {day_name}"
    )
  return filtered.to_dict(orient="records")