# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import requests
# import streamlit as st

# app = FastAPI()

# #llamada a clima actual en ciudad elegida
# @app.get("/weather/{city}")
# async def get_weather(city: str):
#     try:
#         api_key=st.secrets["api_key"]
#         url_weather = f"https://api.openweathermap.org/data/2.5/weather?q={city}&APPID={api_key}&units=metric"
#         response = requests.get(url_weather)
#         weather_data = response.json()
#         return weather_data
#     except requests.RequestException:
#         raise HTTPException(status_code=404, detail="City not found")        

# @app.get("/forecast/")
# async def get_forecast(lat: float, lon: float):
#     try:
#         api_key=st.secrets["api_key"]
#         url_forecast = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}"
#         response = requests.get(url_forecast)
#         weather_forecast = response.json()
#         return weather_forecast
#     except requests.RequestException:
#         raise HTTPException(status_code=404, detail="Forecast data not found for provided coordinates")

from fastapi import FastAPI, HTTPException
import httpx
import streamlit as st

app = FastAPI()

API_KEY = st.secrets["api_key"]
CURRENT_WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}"
FORECAST_WEATHER_URL = "http://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&units=metric&appid={}"


@app.get("/weather/{city}")
async def get_current_weather(city: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(CURRENT_WEATHER_URL.format(city, API_KEY))
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        raise HTTPException(status_code=404, detail="City not found")
    else:
        raise HTTPException(status_code=500, detail="API call failed")


@app.get("/forecast")
async def get_forecast_weather(lat: float, lon: float):
    async with httpx.AsyncClient() as client:
        response = await client.get(FORECAST_WEATHER_URL.format(lat, lon, API_KEY))
    
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=500, detail="API call failed")