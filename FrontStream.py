
import streamlit as st
import httpx
import pandas as pd
import plotly.express as px
import threading
import time
import regex
from datetime import datetime, timedelta

# Definir la URL base de la API
base_url = "http://localhost:8000/weather/"
# URL base para obtener los íconos de OpenWeather
icon_base_url = "https://openweathermap.org/img/wn/"

# Configuración de la página
st.set_page_config(page_title="Reportes climáticos", page_icon="🌤️",layout="wide")

# Título de la interfaz
st.title("Generador de Reportes Climáticos 🌪️")

# Función para obtener datos climáticos de la API
def get_weather_data(city):
    # Validate the city name to contain only Unicode letters and spaces
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
    
    essential_keys = ['name', 'weather', 'main', 'sys', 'coord', 'wind']
    for key in essential_keys:
        if key not in weather_data:
            st.error(f"No se encontró información del clima para la ciudad: {city}. Por favor, intenta con otra ciudad.")
            st.session_state.start_update = False  # Reset tracking state
            return None

    return weather_data

# Función para mostrar TODA la información climática en la interfaz
def mostrar_info_climatica(weather_data, info_container):
    # Verificar si hay un error en la respuesta
    if 'error' in weather_data:
        info_container.error(weather_data['error'])
        return  # Salir de la función
    # Update the provided container with weather data
    info_container.write(
        f'<div style="display: flex; align-items: center;">'
        f'<h1 style="margin-right: 10px;">Clima en {weather_data["name"]}</h1>'
        f'<img src="{icon_base_url}{weather_data["weather"][0]["icon"]}@2x.png" style="width: 180px; height: 120px;">'
        f'</div>',
        unsafe_allow_html=True
    )
    # Dividir el espacio en tres columnas
    kpi1, kpi2, kpi3 = st.columns(3)
    # Mostrar la hora local de la ciudad
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
        # Es de día, usar imágenes sin "_n" para representar el clima
        if weather_main == "Rain":
            st.image("images\\rainy.jpg", caption="Dia con Lluvia")
        elif weather_main == "Clear":
            st.image("images\clear.jpg", caption="Dia Despejado")
        elif weather_main == "Clouds":
            st.image("images\cloudy.jpg", caption="Dia Nublado")
    else:
        # Es de noche, usar imágenes con "_n" para representar el clima
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
        "Hora Amanecer(Hora local)": [datetime.fromtimestamp(weather_data["sys"]["sunrise"]).strftime("%Y-%m-%d %H:%M:%S")],
        "Hora Atardecer(Hora local)": [datetime.fromtimestamp(weather_data["sys"]["sunset"]).strftime("%Y-%m-%d %H:%M:%S")]
    }
    df = pd.DataFrame(data)

    # Create a full-width column and display the dataframe in it
    col1 = st.columns(1)[0]  # Use 1 to take the full width, 0 for an empty space
    col1.dataframe(df)

    # Mostrar las gráficas
    timezone_offset = weather_data["timezone"]
    timezone = datetime.utcnow() + timedelta(seconds=timezone_offset)
    timezone_str = timezone.strftime("%H:%M:%S")

    # Mostrar gráficas
    # Verificar si los DataFrames ya existen en el estado de la sesión. Si no, inicializarlos.
    if "temp_time_df" not in st.session_state:
        st.session_state.temp_time_df = pd.DataFrame(columns=["Tiempo", "Temperatura"])
    if "temp_min_max_df" not in st.session_state:
        st.session_state.temp_min_max_df = pd.DataFrame(columns=["Temperatura", "Valor"])
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
        "Temperatura": ["Temperatura Mínima", "Temperatura Máxima"],
        "Valor": [weather_data["main"]["temp_min"], weather_data["main"]["temp_max"]]
    })
    st.session_state.temp_min_max_df = pd.concat([st.session_state.temp_min_max_df, new_temp_min_max_data], ignore_index=True)

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
    temp_min_max_chart = px.bar(st.session_state.temp_min_max_df, x="Temperatura", y="Valor", title="Temperatura Mínima y Máxima")
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
    weather_data = get_weather_data(city)
    # Verificar si weather_data es None (indicando un error)
    if weather_data is None:
        return  # Salir de la función

    mostrar_info_climatica(weather_data, info_container)

# Create containers for dynamic content
info_climatica_container = st.empty()
graph_container = st.empty()

# Initialize session state if not already done
if "tracking_city" not in st.session_state:
    st.session_state.tracking_city = ""

if "start_update" not in st.session_state:
    st.session_state.start_update = False

# Widget para obtener la ciudad del usuario
city = st.text_input("Ingrese el nombre de la ciudad:", st.session_state.tracking_city)

# Widget para iniciar el seguimiento
start_update_clicked = st.button("Iniciar seguimiento")

# Update session state when button is clicked
if start_update_clicked:
    st.session_state.start_update = not st.session_state.start_update
    st.session_state.tracking_city = city

# Widget para detener el seguimiento
stop_update_button = st.button("Detener seguimiento")

# If stop button is clicked, update session state and display warning
if stop_update_button:
    st.session_state.start_update = False
    st.warning("Seguimiento en tiempo real está detenido. Ingrese una ciudad para continuar.")

# If session state indicates tracking, fetch and display data, then rerun after a delay
if st.session_state.start_update and st.session_state.tracking_city:
    update_weather_data(st.session_state.tracking_city, info_climatica_container)
    time.sleep(5)  # Refresh data every 5 seconds (can be adjusted as needed)
    st.experimental_rerun()
