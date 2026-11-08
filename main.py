import os
import pandas as pd
import pickle
from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

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

# Current directory aur absolute path check karne ke liye
  current_dir = os.getcwd()
  full_path = os.path.join(current_dir, file_name)

  print(f"Checking file at: {full_path}")  # Railway logs mein nazar aayega

  # Check karein ke file server par mojood hai ya nahi
  if not os.path.exists(file_name):
    print(f"File NOT found at {full_path}")
    return None

  try:
    df = pd.read_pickle(full_path)
    if "date" in df.columns:
      df["date"] = pd.to_datetime(df["date"])
    return df
  except Exception as e:
    print(f"Error loading pickle: {e}")
    return None

# Aapki nayi MapData class ke mutabiq Pydantic model
class MapDataResponse(BaseModel):
    latitude: float
    longitude: float
    pm25: float
    date: str
    level: str
    color: str
    advice: str
    aqi: float

@app.get("/")
def read_root():
  return {
      "status": "Online",
          "message": "Welcome to Multi-City Air Quality Forecasting API."
          " Supported cities: karachi, lahore, islamabad, multan"
  }


@app.get("/api/forecast/{city}/analytics")
def get_filtered_city_analytics(
    city: str,
    filter_type: Optional[str] = Query(None, description="e.g., 'weekly', 'monthly', or specific date 'YYYY-MM-DD'"),
    start_date: Optional[str] = Query(None, description="Format: YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Format: YYYY-MM-DD")
):
    df = load_city_results(city)
    
    if df is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Dataset for city '{city}' not found or pickle file is missing on server."
        )
    
    # Column name detect karna (aqi ya predicted_pm25)
    val_col = 'aqi' if 'aqi' in df.columns else ('predicted_pm25' if 'predicted_pm25' in df.columns else df.columns[-1])
    
    if 'date' in df.columns:
        df = df.sort_values('date')
        
        # 1. Custom Date Range Filter (Agar start_date aur end_date di gayi ho)
        if start_date and end_date:
            df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]
        
        # 2. Specific Filter Type (Jaise Spinner ya dropdown ki value ke mutabiq)
        elif filter_type:
            filter_lower = filter_type.lower().strip()
            if filter_lower == "last 7 days" or filter_lower == "weekly":
                df = df.tail(7)
            elif filter_lower == "last 30 days" or filter_lower == "monthly":
                df = df.tail(30)
            elif len(filter_lower) == 10:  # Agar koi exact date pass ki ho e.g., "2026-11-08"
                df = df[df['date'].dt.strftime('%Y-%m-%d') == filter_lower]

        if df.empty:
            raise HTTPException(status_code=404, detail="No records found for the given filter criteria.")
            
        dates_list = df['date'].dt.strftime('%Y-%m-%d').tolist()
    else:
        dates_list = [str(i) for i in range(len(df))]
        
    aqi_values = df[val_col].astype(float).tolist()
    
    # Statistics calculations on filtered data
    avg_aqi = float(df[val_col].mean())
    max_aqi = float(df[val_col].max())
    min_aqi = float(df[val_col].min())
    
    return {
        "average_aqi": round(avg_aqi, 2),
        "max_aqi": round(max_aqi, 2),
        "min_aqi": round(min_aqi, 2),
        "aqi_values": aqi_values,
        "dates": dates_list
    }


@app.get("/api/forecast/{city}/map-data", response_model=List[MapDataResponse])
def get_filtered_city_map_data(
    city: str,
    filter_type: Optional[str] = Query(None, description="e.g., 'weekly', 'monthly', or specific date 'YYYY-MM-DD'"),
    start_date: Optional[str] = Query(None, description="Format: YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Format: YYYY-MM-DD")
):
    city_key = city.lower().strip()
    if city_key not in CITY_FILES:
        raise HTTPException(status_code=404, detail=f"City '{city}' is not supported.")
    
    df = load_city_results(city_key)  # Cached function
    if df is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Dataset for city '{city}' not found or pickle file is missing on server."
        )
    
    filtered_df = df.copy()
    
    # Date & Filter Logic (Analytics ki tarah same filtering)
    if 'date' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('date')
        
        if start_date and end_date:
            filtered_df = filtered_df[
                (filtered_df['date'] >= pd.to_datetime(start_date)) & 
                (filtered_df['date'] <= pd.to_datetime(end_date))
            ]
        elif filter_type:
            filter_lower = filter_type.lower().strip()
            if filter_lower == "last 7 days" or filter_lower == "weekly":
                filtered_df = filtered_df.tail(7)
            elif filter_lower == "last 30 days" or filter_lower == "monthly":
                filtered_df = filtered_df.tail(30)
            elif len(filter_lower) == 10:  # Exact date format like "2026-11-08"
                filtered_df = filtered_df[filtered_df['date'].dt.strftime('%Y-%m-%d') == filter_lower]

        if filtered_df.empty:
            raise HTTPException(status_code=404, detail="No map records found for the given filter criteria.")
    
    # Default coordinates agar dataframe mein lat/lon na hon
    default_coords = {
        "karachi": (24.8607, 67.0011),
        "lahore": (31.5497, 74.3436),
        "islamabad": (33.6844, 73.0479),
        "multan": (30.1575, 71.5249)
    }
    
    lat_val = float(filtered_df['original_latitude'].iloc[0]) if 'original_latitude' in filtered_df.columns else default_coords.get(city_key, (0.0, 0.0))[0]
    lon_val = float(filtered_df['original_longitude'].iloc[0]) if 'original_longitude' in filtered_df.columns else default_coords.get(city_key, (0.0, 0.0))[1]
    
    # PM2.5 column detection
    pm_col = next((col for col in ['pm25', 'predicted_pm25', 'value'] if col in filtered_df.columns), filtered_df.columns[-1])
    
    response_list = []
    for _, row in filtered_df.iterrows():
        pm_val = float(row.get(pm_col, 0.0))
        
        # DataFrame ke apne columns se values uthana (agar column mojood na ho toh fallback values)
        level_val = str(row.get('level', 'Moderate'))
        color_val = str(row.get('color', '#FFC107'))
        advice_val = str(row.get('advice', 'Standard air quality precautions apply.'))
        aqi_val = float(row.get('aqi', 0.0))

            
        date_str = row['date'].strftime('%Y-%m-%d') if 'date' in filtered_df.columns and pd.notnull(row['date']) else "N/A"
        
        response_list.append({
            "latitude": lat_val,
            "longitude": lon_val,
            "pm25": round(pm_val, 2),
            "date": date_str,
            "level": level_val,
            "color": color_val,
            "advice": advice_val,
            "aqi": aqi_val
        })
        
    return response_list


class AirRequest(BaseModel):
    pm25: float

class AirResponse(BaseModel):
    date: str
    country: str
    city: str
    latitude: float
    longitude: float
    pm25: float
    level: str
    color: str
    advice: str



@app.post("/api/predict", response_model=AirResponse)
def predict_air_quality(request: AirRequest):
    pm25_val = request.pm25
    
    # EPA Breakpoints ke mutabiq AQI category, color aur advice determine karna
    if pm25_val <= 12.0:
        level = "Good"
        color = "#4CAF50"
        advice = "Air quality is satisfactory, and air pollution poses little or no risk."
    elif pm25_val <= 35.4:
        level = "Moderate"
        color = "#FFC107"
        advice = "Acceptable air quality; sensitive individuals may experience minor irritation."
    elif pm25_val <= 55.4:
        level = "Unhealthy for Sensitive Groups"
        color = "#FF9800"
        advice = "Sensitive groups may experience health effects. General public is less likely to be affected."
    elif pm25_val <= 150.4:
        level = "Unhealthy"
        color = "#F44336"
        advice = "Everyone may begin to experience health effects; sensitive groups may experience severe effects."
    elif pm25_val <= 250.4:
        level = "Very Unhealthy"
        color = "#9C27B0"
        advice = "Health alert: everyone may experience more serious health effects."
    elif pm25_val <= 350.4:
        level = "Hazardous"
        color = "#795548"
        advice = "Health warnings of emergency conditions. The entire population is likely to be affected."
    else:
        level = "Hazardous"
        color = "#7E0023"
        advice = "Serious health alert: stay indoors."

    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "latitude": 24.8607,
        "longitude": 67.0011,
        "pm25": round(float(pm25_val), 2),
        "level": level,
        "color": color,
        "advice": advice
    }


@app.get("/api/forecast/{city}/all")
def get_all_by_city(city: str):
  df_results = load_city_results(city)
  if df_results is None:
    raise HTTPException(
        status_code=404,
        detail=(
            f"Dataset for city '{city}' not found or pickle file is missing on"
            f" server. Current dir: {os.getcwd()}"
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