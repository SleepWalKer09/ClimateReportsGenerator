import requests
from fastapi import FastAPI

app = FastAPI()

#llamada a clima actual en ciudad elegida
@app.get("/weather/{city}")
def get_weather(city: str):
    api_key = "!!!SECRET!!!"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&APPID={api_key}&units=metric"
    
    response = requests.get(url)
    weather_data = response.json()
    
    return weather_data


#pronostico de clima de proximos 5 dias (se actualiza cada 3 horas)
