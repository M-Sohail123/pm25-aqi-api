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
