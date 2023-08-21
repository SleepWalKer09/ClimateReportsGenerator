"""
Módulo que contiene la lógica de presentación para mostrar el pronóstico del clima en Streamlit.
Utiliza datos obtenidos de la API de OpenWeather para mostrar el pronóstico de 5 días.
"""

import streamlit as st
import httpx
import datetime

# URL de tu FastAPI
#BASE_URL = "http://localhost:8000/forecast_weather/"

"""
Asíncronamente recupera datos de pronóstico del clima basados en la latitud y longitud proporcionadas.

    Esta función consulta una API local en `localhost:8000/forecast` para obtener el pronóstico del clima
    para una ubicación específica (latitud y longitud). Antes de hacer la consulta, verifica si la 
    latitud y longitud ya están almacenadas en el `session_state` de Streamlit y, en caso afirmativo, 
    utiliza esos valores en lugar de los proporcionados.

    Parámetros:
    - lat (float): Latitud de la ubicación para la que se debe obtener el pronóstico.
    - lon (float): Longitud de la ubicación para la que se debe obtener el pronóstico.

    Devuelve:
    - dict or None: Datos de pronóstico del clima si la consulta es exitosa, o None si no se encuentra 
                    información en el `session_state` o si ocurre algún otro error.
"""
async def fetch_forecast_data(lat, lon):

    if "lat" in st.session_state and "lon" in st.session_state:
        lat = st.session_state.lat
        lon = st.session_state.lon
        response = httpx.get(f"http://localhost:8000/forecast?lat={lat}&lon={lon}")
        data = response.json()
        return data
    return None

    """
    Obtiene datos de pronóstico del clima basados en la latitud y longitud proporcionadas.

    Esta función utiliza la función asincrónica `fetch_forecast_data` para recuperar el pronóstico del clima
    para una ubicación específica (latitud y longitud). Internamente, hace uso de asyncio para ejecutar 
    la función asincrónica y obtener el resultado.

    Parámetros:
    - lat (float): Latitud de la ubicación para la que se debe obtener el pronóstico.
    - lon (float): Longitud de la ubicación para la que se debe obtener el pronóstico.

    Devuelve:
    - dict or None: Datos de pronóstico del clima si la consulta es exitosa, o None si ocurre algún error.
    """
def get_forecast(lat, lon):

    import asyncio
    return asyncio.run(fetch_forecast_data(lat, lon))

# Lógica para Streamlit
    """
    show_forecast
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

    forecast_message_marker.success(f"Mostrando pronóstico de los próximos **5 días**")
    
    # Filtrar los datos para que solo se incluyan las entradas de "15:00:00" horas
    filtered_data = [entry for entry in st.session_state.forecast_data["list"] if "15:00:00" in entry["dt_txt"]]

    if 'forecast_marker' not in st.session_state:
        st.session_state.forecast_marker = st.empty()

    forecast_container = st.session_state.forecast_marker.container()
    
    # Iterar sobre los datos filtrados y mostrar en el contenedor general
    for day_data in filtered_data:
        
        date_only = day_data["dt_txt"].split()[0]
        temp = day_data["main"]["temp"]
        description = day_data["weather"][0]["description"]
        icon_url = f"https://openweathermap.org/img/wn/{day_data['weather'][0]['icon']}@2x.png"

        col1, col2, col3, col4 = forecast_container.columns(4)
        col1.metric(label="Fecha", value=date_only)
        col2.metric(label="Temperatura Promedio", value=f"{temp} °C")
        col3.metric(label="Pronóstico", value=description)
        col4.image(icon_url, caption="Clima", width=60)

# Para probarlo
if __name__ == "__main__":
    show_forecast()