"""
Módulo para interactuar con la API de OpenWeather.
"""

from fastapi import FastAPI, HTTPException
import httpx
import streamlit as st

app = FastAPI()

API_KEY = st.secrets["api_key"]
CURRENT_WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}"
FORECAST_WEATHER_URL = "http://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&units=metric&appid={}"


@app.get("/weather/{city}")
async def get_current_weather(city: str):
    """
    Obtiene el clima actual de una ciudad específica usando la API de OpenWeather.

    Parámetros:
    - city (str): Nombre de la ciudad para la cual obtener el clima.

    Devuelve:
    - dict: Diccionario con información del clima actual.
        Si hay un error en la solicitud, devuelve None.
    """
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
    """
    Obtiene el pronóstico del clima para los próximos 5 días basado en la longitud y latitud.

    Parámetros:
    - lon (float): Longitud geográfica para la cual obtener el pronóstico.
    - lat (float): Latitud geográfica para la cual obtener el pronóstico.

    Devuelve:
    - dict: Diccionario con información del pronóstico del clima para los próximos 5 días.
            Si hay un error en la solicitud, devuelve None.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(FORECAST_WEATHER_URL.format(lat, lon, API_KEY))
    
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=500, detail="API call failed")