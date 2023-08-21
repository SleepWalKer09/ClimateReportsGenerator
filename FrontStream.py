"""
Módulo principal de la aplicación Streamlit para el generador de reportes climáticos.
Permite a los usuarios ingresar una ciudad, iniciar y detener el seguimiento del clima en tiempo real, 
y ver el pronóstico de 5 días.
"""
import streamlit as st
import httpx
import pandas as pd
import plotly.express as px
import threading
import time
import regex
from forecastFront import show_forecast,get_forecast
from datetime import datetime, timedelta

#https://openweathermap.org/forecast5

# Definir la URL base de la API
base_url = "http://localhost:8000/weather/"
# URL base para obtener los íconos de OpenWeather
icon_base_url = "https://openweathermap.org/img/wn/"

# Configuración de la página
st.set_page_config(page_title="Reportes climáticos", page_icon="🌤️",layout="wide")


st.title("Generador de Reportes Climáticos 🌪️")
st.sidebar.title("Instrucciones")
st.sidebar.write(
    "1. Ingresa el nombre de la ciudad que quieras monitorear.\n"
    "2. Presiona 'Iniciar Seguimiento' para comenzar el monitoreo en tiempo real.\n"
    "3. Para conocer el pronóstico de los proximos 5 dias, presiona 'Mostrar forecast'.\n"
    "4. Presiona 'Detener Seguimiento' para detener todo el monitoreo.\n"
    "5. Recomiendo recargar la página para consultar el clima de otra ciudad luego de detener el seguimiento.\n"
)
forecast_message_marker = st.empty()

# Función para obtener datos climáticos de la API
def get_weather_data(city):
    """
    Obtiene los datos climáticos para una ciudad específica desde la API.

    La función valida el nombre de la ciudad para asegurar que contenga solo letras Unicode y espacios.
    Si la API devuelve un error o no se encuentra información para la ciudad proporcionada, 
    se muestra un mensaje de error en Streamlit y se restablece el estado de seguimiento.

    Parámetros:
    - city (str): Nombre de la ciudad para la cual obtener los datos climáticos.

    Devuelve:
    - dict: Diccionario con información del clima para la ciudad especificada.
            Si hay un problema o no se encuentra información para la ciudad, devuelve None.
    """
    if not regex.match("^\\p{L}[\\p{L}\\s]*$", city):
        st.error(f"'{city}' no es un nombre de ciudad válido. Por favor, introduce un nombre de ciudad correcto.")
        st.session_state.start_update = False  # Reset tracking state
        return None

    url = base_url + city
    response = httpx.get(url)
    
    if response.status_code == 404:
        st.error(f"No se encontró información climática para la ciudad: {city}. Por favor, intenta con otra ciudad.")
        st.session_state.start_update = False  # Reset tracking state
        return None
    elif response.status_code != 200:
        st.error("Hubo un problema al obtener los datos del clima. Por favor, intenta nuevamente.")
        st.session_state.start_update = False  # Reset tracking state
        return None

    weather_data = response.json()
    st.session_state.weather_data = response.json()
    
    essential_keys = ['name', 'weather', 'main', 'sys', 'coord', 'wind']
    for key in essential_keys:
        if key not in weather_data:
            st.error(f"No se encontró información del clima para la ciudad: {city}. Por favor, intenta con otra ciudad.")
            st.session_state.start_update = False  # Reset tracking state
            return None

    return weather_data

# Función para mostrar TODA la información climática en la interfaz
def mostrar_info_climatica(weather_data, info_container):
    """
    Muestra la información climática en la interfaz de Streamlit.

    Esta función toma los datos climáticos y los muestra en una serie de tarjetas,
    imágenes y gráficos interactivos en la interfaz de Streamlit. Si se encuentra un error
    en los datos proporcionados, muestra un mensaje de error en lugar de la información climática.

    Parámetros:
    - weather_data (dict): Diccionario con la información climática obtenida de la API.
    - info_container (streamlit.delta_generator.DeltaGenerator): Contenedor Streamlit donde se mostrará la información.

    No devuelve nada.
    """
    # Verificar si hay un error en la respuesta
    if 'error' in weather_data:
        info_container.error(weather_data['error'])
        return  # Salir de la función
    # Update the provided container with weather data
    if 'city_name' not in st.session_state:
        st.session_state.city_name = weather_data["name"]

    info_container.write(
        f'<div style="display: flex; align-items: center;">'
        f'<h1 style="margin-right: 10px;">Clima en {st.session_state.city_name}</h1>'
        f'<img src="{icon_base_url}{weather_data["weather"][0]["icon"]}@2x.png" style="width: 180px; height: 120px;">'
        f'</div>',
        unsafe_allow_html=True
    )
    # Dividir el espacio en tres columnas
    kpi1, kpi2, kpi3 = st.columns(3)
    timezone_offset = weather_data["timezone"]
    timezone = datetime.utcnow() + timedelta(seconds=timezone_offset)
    timezone_str = timezone.strftime("%H:%M:%S")
    # Mostrar las tarjetas de resumen
    kpi1.metric(label="Descripción del clima", value=weather_data['weather'][0]['description'])
    kpi2.metric(label="Hora local", value=timezone_str)
    kpi3.metric(label="Temperatura", value=f"{weather_data['main']['temp']} °C")

    # Mostrar imagen según el campo "icon" de "weather"
    weather_icon = weather_data["weather"][0]["icon"]
    weather_main = weather_data["weather"][0]["main"]
    if weather_icon.endswith("d"):
        if weather_main == "Rain":
            st.image("images\\rainy.png", caption="Dia con Lluvia")
        elif weather_main == "Clear":
            st.image("images\clear.jpg", caption="Dia Despejado")
        elif weather_main == "Clouds":
            st.image("images\cloudy.jpg", caption="Dia Nublado")
    else:
        if weather_main == "Rain":
            st.image("images\\rainy_n.jpg", caption="Noche con Lluvia")
        elif weather_main == "Clear":
            st.image("images\clear_n.jpg", caption="Noche Despejada")
        elif weather_main == "Clouds":
            st.image("images\cloudy_n.jpg", caption="Noche Nublada")
        else:
            st.image("images\default_image.jpg", caption="Estado del tiempo desconocido")

    # Mostrar tabla con datos adicionales, incluyendo descripción del clima y el ícono
    st.subheader("Datos adicionales")
    data = {
        "País": [weather_data["sys"]["country"]],
        "Longitud": [weather_data["coord"]["lon"]],
        "Latitud": [weather_data["coord"]["lat"]],
        "Descripción": [weather_data["weather"][0]["description"]],
        "Velocidad del Viento(m/s)": [weather_data["wind"]["speed"]],
        "Hora Amanecer(Hora usuario)": [datetime.fromtimestamp(weather_data["sys"]["sunrise"]).strftime("%Y-%m-%d %H:%M:%S")],
        "Hora Atardecer(Hora usuario)": [datetime.fromtimestamp(weather_data["sys"]["sunset"]).strftime("%Y-%m-%d %H:%M:%S")],
        "Temperatura Actual": [weather_data["main"]["temp"]],
        "Temperatura Máxima": [weather_data["main"]["temp_max"]],
        "Temperatura Mínima": [weather_data["main"]["temp_min"]]
        
    }
    df = pd.DataFrame(data)

    col1 = st.columns(1)[0] 
    col1.dataframe(df)

    # Mostrar gráficas
    timezone_offset = weather_data["timezone"]
    timezone = datetime.utcnow() + timedelta(seconds=timezone_offset)
    timezone_str = timezone.strftime("%H:%M:%S")

    # Verificar si los DataFrames ya existen en el estado de la sesión. Si no, inicializarlos.
    if "temp_time_df" not in st.session_state:
        st.session_state.temp_time_df = pd.DataFrame(columns=["Tiempo", "Temperatura"])
    if "temp_min_max_time_df" not in st.session_state:
        st.session_state.temp_min_max_time_df = pd.DataFrame(columns=["Tipo", "Valor"])
    if "pressure_time_df" not in st.session_state:
        st.session_state.pressure_time_df = pd.DataFrame(columns=["Tiempo", "Presión Atmosférica"])
    if "humidity_time_df" not in st.session_state:
        st.session_state.humidity_time_df = pd.DataFrame(columns=["Tiempo", "Humedad"])

    # Agregar nuevos datos a los DataFrames
    new_temp_data = pd.DataFrame({
        "Tiempo": [timezone_str],
        "Temperatura": [weather_data["main"]["temp"]]
    })
    st.session_state.temp_time_df = pd.concat([st.session_state.temp_time_df, new_temp_data], ignore_index=True)

    new_temp_min_max_data = pd.DataFrame({
        "Tipo": ["Temperatura Máxima", "Temperatura Mínima"],
        "Valor": [weather_data["main"]["temp_max"], weather_data["main"]["temp_min"]]
    })
    st.session_state.temp_min_max_time_df = new_temp_min_max_data
    
    new_pressure_data = pd.DataFrame({
        "Tiempo": [timezone_str],
        "Presión Atmosférica": [weather_data["main"]["pressure"]]
    })
    st.session_state.pressure_time_df = pd.concat([st.session_state.pressure_time_df, new_pressure_data], ignore_index=True)

    new_humidity_data = pd.DataFrame({
        "Tiempo": [timezone_str],
        "Humedad": [weather_data["main"]["humidity"]]
    })
    st.session_state.humidity_time_df = pd.concat([st.session_state.humidity_time_df, new_humidity_data], ignore_index=True)

    # Crear gráficos usando los DataFrames actualizados
    temp_time_chart = px.line(st.session_state.temp_time_df, x="Tiempo", y="Temperatura", title="Variación de Temperatura en el Tiempo")
    temp_min_max_chart = px.bar(
        st.session_state.temp_min_max_time_df, 
        x="Tipo", y="Valor", 
        title="Temperatura Mínima y Máxima", 
        labels={'Valor': 'Temperatura (°C)'},
        color="Tipo",
        color_discrete_map={
            "Temperatura Máxima": "red",
            "Temperatura Mínima": "blue"
        },
        text="Valor"
    )
    temp_min_max_chart.update_traces(texttemplate='%{text} °C', textposition='outside')

    pressure_time_chart = px.line(st.session_state.pressure_time_df, x="Tiempo", y="Presión Atmosférica", title="Variación de Presión Atmosférica en el Tiempo")
    humidity_time_chart = px.line(st.session_state.humidity_time_df, x="Tiempo", y="Humedad", title="Variación de Humedad en el Tiempo")
        
    # Dividir el espacio en dos columnas para los gráficos interactivos
    fig_col1, fig_col2 = st.columns(2)
    fig_col3, fig_col4 = st.columns(2)

    # Mostrar los gráficos interactivos en las columnas respectivas
    with fig_col1:
        st.markdown("### Temperatura Actual")
        st.plotly_chart(temp_time_chart)

    with fig_col2:
        st.markdown("### Temperatura Mínima y Máxima")
        st.plotly_chart(temp_min_max_chart)

    with fig_col3:
        st.markdown("### Presión Atmosférica")
        st.plotly_chart(pressure_time_chart)

    with fig_col4:
        st.markdown("### Humedad")
        st.plotly_chart(humidity_time_chart)

def update_weather_data(city, info_container):
    """
    Actualiza y muestra la información climática para una ciudad dada.

    Esta función obtiene datos climáticos para una ciudad específica utilizando la función
    `get_weather_data`, luego actualiza las coordenadas de la sesión (latitud y longitud) basadas en 
    la respuesta y finalmente utiliza la función `mostrar_info_climatica` para mostrar
    la información climática en la interfaz Streamlit.

    Parámetros:
    - city (str): Nombre de la ciudad para la cual se debe obtener la información climática.
    - info_container (streamlit.delta_generator.DeltaGenerator): Contenedor Streamlit donde se mostrará la información.

    No devuelve nada.
    """
    weather_data = get_weather_data(city)
    # Verificar si weather_data es None (indicando un error)
    if weather_data is None:
        return  # Salir de la función
    st.session_state.lat = weather_data["coord"]["lat"]
    st.session_state.lon = weather_data["coord"]["lon"]

    mostrar_info_climatica(weather_data, info_container)

# Crear containers para contenido dinamico
info_climatica_container = st.empty()
graph_container = st.empty()
forecast_container = st.empty()

if "tracking_city" not in st.session_state:
    st.session_state.tracking_city = ""

if "start_update" not in st.session_state:
    st.session_state.start_update = False

if 'show_forecast' in st.session_state and st.session_state.show_forecast:
    show_forecast(forecast_message_marker)


if __name__ == '__main__':
    city = st.text_input("Ingrese el nombre de la ciudad:", st.session_state.tracking_city)

    col_iniciar, col_detener, col_forecast = st.columns(3)
    with col_iniciar:
        start_update_button = st.button("Iniciar seguimiento", type="primary",disabled=st.session_state.start_update if 'start_update' in st.session_state else False)
        if not city and start_update_button:
            st.error("Debes ingresar una ciudad válida")
            st.session_state.start_update = False
            st.session_state.forecast_data = None
            st.session_state.show_forecast = False
            st.session_state.show_forecast_message = False

    with col_detener:
        stop_update_button = st.button("Detener seguimiento", type="primary",disabled=not st.session_state.start_update if 'start_update' in st.session_state else True)
        if stop_update_button:
            st.session_state.start_update = False
            st.session_state.forecast_data = None
            st.session_state.show_forecast = False
            st.session_state.show_forecast_message = False

    with col_forecast:
        if st.button("Mostrar forecast", type="primary", disabled=not st.session_state.start_update if 'start_update' in st.session_state else True):
            st.session_state.show_forecast = True
            st.session_state.show_forecast_message = True
            st.session_state.forecast_lon = st.session_state.weather_data["coord"]["lon"]
            st.session_state.forecast_lat = st.session_state.weather_data["coord"]["lat"]
            if 'forecast_data' not in st.session_state:
                forecast_data = get_forecast(st.session_state.forecast_lon, st.session_state.forecast_lat)
                st.session_state['forecast_data'] = forecast_data

    if 'show_forecast' in st.session_state and st.session_state.show_forecast:
        show_forecast(forecast_message_marker)

    if start_update_button:
        st.session_state.start_update = not st.session_state.start_update
        st.session_state.tracking_city = city

    if stop_update_button:
        st.session_state.start_update = False
        st.session_state.forecast_data = None
        st.session_state.show_forecast = False
        st.session_state.show_forecast_message = False
        st.warning("Se ha detenido el seguimiento del clima en tiempo real.")

        
    if st.session_state.start_update and st.session_state.tracking_city:
        update_weather_data(st.session_state.tracking_city, info_climatica_container)
        time.sleep(5)  # Refresh data every 5 seconds (can be adjusted as needed)
        st.experimental_rerun()

