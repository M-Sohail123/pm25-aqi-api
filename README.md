# 🌍 Karachi PM2.5 & Air Quality (AQI) Forecasting API

A production-ready machine learning backend API built with **FastAPI**, **Gradient Boosting Regressor**, and **Pandas** to provide real-time and historical air quality forecasts for Karachi. Designed for seamless integration with mobile applications (Android).

---

## 🚀 Features

* **High-Performance ML Model:** Powered by an optimized `GradientBoostingRegressor` trained on historical environmental data with advanced feature engineering (Lag features & rolling means).
* **Automated AQI Mapping:** Converts predicted PM2.5 concentrations into standardized AQI levels, color codes, and actionable health advice.
* **FastAPI Endpoints:** Optimized routing for historical dataset retrieval, date-wise filtering, and structured JSON responses.
* **Production-Ready:** Configured for cloud deployment on platforms like Render via Uvicorn ASGI server.

---

## 🛠️ Tech Stack

* **Backend Framework:** FastAPI, Uvicorn
* **Data Science & ML:** Python, Pandas, NumPy, Scikit-Learn
* **Model Serialization:** Pickle (`.pkl`)
* **Deployment:** Render Cloud Platform

---

## 📂 Project Structure

```text
├── main.py                     # FastAPI application and endpoint definitions
├── pm25_gbr_model.pkl          # Trained Gradient Boosting Regressor model
├── df_gbr_forecast_results.pkl # Pre-calculated results dataset with AQI metrics
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation

🔌 API Endpoints
Once the server is running (locally or via your Render public URL), you can access the following endpoints:

Endpoint	Method	Description
/	GET	API health check and welcome message
/api/forecast/all	GET	Retrieves the entire historical and predicted dataset (JSON)
/api/forecast/date/{target_date}	GET	Filters and returns forecast details for a specific date (Format: YYYY-MM-DD)
⚙️ Local Installation & Running Guide
1. Clone the Repository
Bash
git clone [https://github.com/M-Sohail123/pm25-aqi-api.git](https://github.com/M-Sohail123/pm25-aqi-api.git)
cd pm25-aqi-api
2. Install Dependencies
Bash
pip install -r requirements.txt
3. Run the FastAPI Server locally
Bash
uvicorn main:app --reload
Open your browser and navigate to http://127.0.0.1:8000/docs to test the interactive Swagger documentation.

☁️ Deployment on Render
Create a new Web Service on Render and connect your GitHub repository.

Configure the build and start settings:

Runtime: Python 3

Build Command: pip install -r requirements.txt

Start Command: uvicorn main:app --host 0.0.0.0 --port 10000

Click Create Web Service to generate your live public API URL.
