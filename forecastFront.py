"""
Módulo que contiene la lógica de presentación para mostrar el pronóstico del clima en Streamlit.
Utiliza datos obtenidos de la API de OpenWeather para mostrar el pronóstico de 5 días.
"""

import streamlit as st
import httpx
import datetime

# URL de tu FastAPI
#BASE_URL = "http://localhost:8000/forecast_weather/"

async def fetch_forecast_data(lat, lon):
    if "lat" in st.session_state and "lon" in st.session_state:
        lat = st.session_state.lat
        lon = st.session_state.lon
        response = httpx.get(f"http://localhost:8000/forecast?lat={lat}&lon={lon}")
        data = response.json()
        return data
    return None

def get_forecast(lat, lon):

    import asyncio
    return asyncio.run(fetch_forecast_data(lat, lon))

# Lógica para Streamlit
    """
    Muestra el pronóstico del clima de los próximos 5 días en Streamlit.

    Parámetros:
    - forecast_message_marker (streamlit.delta_generator.DeltaGenerator): 
        Marcador de posición en Streamlit donde se mostrará el mensaje del pronóstico.

    Devuelve:
    - None: Esta función no devuelve nada. Su propósito es renderizar información en la interfaz de Streamlit.

    Notas:
    - La función espera que los datos del pronóstico estén disponibles en st.session_state.
    """
def show_forecast(forecast_message_marker):
    # Verificar si hay datos de pronóstico en session_state; si no, terminar la función
    if 'forecast_data' not in st.session_state or not st.session_state.forecast_data:
        return

    # Mostrar el mensaje al inicio de la sección de pronóstico utilizando el marcador de posición
    forecast_message_marker.success(f"Mostrando pronóstico de los próximos **5 días**")
    
    # Filtrar los datos para que solo se incluyan las entradas de "15:00:00" horas
    filtered_data = [entry for entry in st.session_state.forecast_data["list"] if "15:00:00" in entry["dt_txt"]]

    # Lugar donde se renderizará el pronóstico
    if 'forecast_marker' not in st.session_state:
        st.session_state.forecast_marker = st.empty()

    # Contenedor general para todo el pronóstico
    forecast_container = st.session_state.forecast_marker.container()
    
    # Iterar sobre los datos filtrados y mostrar en el contenedor general
    for day_data in filtered_data:
        # Extraer solo la fecha (sin la hora) y convertirla a un formato legible
        date_only = day_data["dt_txt"].split()[0]
        
        # Extraer los datos necesarios
        temp = day_data["main"]["temp"]
        description = day_data["weather"][0]["description"]
        icon_url = f"https://openweathermap.org/img/wn/{day_data['weather'][0]['icon']}@2x.png"

        # Crear una fila para este conjunto de datos dentro del contenedor general
        col1, col2, col3, col4 = forecast_container.columns(4)
        col1.metric(label="Fecha", value=date_only)
        col2.metric(label="Temperatura Promedio", value=f"{temp} °C")
        col3.metric(label="Pronóstico", value=description)
        col4.image(icon_url, caption="Clima", width=60)

# Para probarlo
if __name__ == "__main__":
    show_forecast()