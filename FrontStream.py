import streamlit as st
import httpx
import time
import matplotlib.pyplot as plt
import pandas as pd
import requests
import plotly.graph_objects as go

from datetime import datetime, timedelta
from PIL import Image
from io import BytesIO
from st_aggrid import AgGrid, GridOptionsBuilder


'''
Pendientes:
Hacer que se actualicen las tablas en lugar de que se repita todo al final cada 5 seg
Poner wallpapers dinamicos de acueerdo al clima actual de la ciudad (encontrar imagenes de noche y dia)
Endpoint para pronostico de proximos dias (investigar si es posible en la API)
pruebas unitarias
'''


# Definir la URL base de la API
base_url = "http://localhost:8000/weather/"
# URL base para obtener los íconos de OpenWeather
icon_base_url = "https://openweathermap.org/img/wn/"
# Configuración de la página
st.set_page_config(page_title="Reportes climáticos", page_icon="🌤️")

# Título de la interfaz
st.title("Generador de :blue[reportes climáticos]🌪️")

# Bandera para controlar el ciclo de actualización
seguir_actualizando = True

@st.cache(ttl=60)  # Cachear los resultados durante 60 segundos
def get_weather_data(city):
    url = base_url + city
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()

# Obtener la ciudad del usuario
city = st.text_input("Ingrese el nombre de la ciudad:")
# Crear un botón para detener la actualización de los datos
stop_update = st.button("Detener seguimiento")


if city:
# Hacer la llamada a la API para obtener los datos del clima
    # url = base_url + city
    # response = httpx.get(url)
    # response.raise_for_status()
    # weather_data = response.json()
    weather_data = get_weather_data(city)

    # Crear contenedores para mostrar las mediciones como gráficas de líneas
    temp_container = st.empty()
    temp_min_container = st.empty()
    temp_max_container = st.empty()
    pressure_container = st.empty()
    humidity_container = st.empty()

    while seguir_actualizando:
        # Obtener el ícono correspondiente según día o noche
        weather_icon = weather_data["weather"][0]["icon"]
        is_day = weather_icon.endswith("d")
        # Definir las URLs de los íconos según día o noche
        day_icon_url = f"{icon_base_url}{weather_icon.replace('n', 'd')}@2x.png"
        night_icon_url = f"{icon_base_url}{weather_icon.replace('d', 'n')}@2x.png"
        # Obtener la descripción del clima con el ícono correspondiente
        weather_description = weather_data["weather"][0]["description"]
        icon_html = day_icon_url if is_day else night_icon_url
        
        
        # Mostrar nombre de la ciudad y el icono en la misma línea utilizando HTML y CSS
        st.write(
            f'<div style="display: flex; align-items: center;">'
            f'<h1 style="margin-right: 10px;">Clima en {weather_data["name"]}</h1>'
            f'<img src="{icon_html}" style="width: 180px; height: 120px;">'
            f'</div>',
            unsafe_allow_html=True
        )
        # Mostrar el caption con la descripción del clima debajo de la imagen
        st.write(f"**Descripción del clima:** {weather_description}")
        
        # if st.button("Detener seguimiento"):
        #     detener_seguimiento()
        # Obtener el campo "main" de "weather"
        weather_main = weather_data["weather"][0]["main"]
        # Mostrar imagen según el campo "main" de "weather"
        if weather_main == "Rain":
            st.image("images\\rainy.png", caption="Lluvia")
        elif weather_main == "Clear":
            st.image("images\sunny.png", caption="Despejado")
        elif weather_main == "Clouds":
            st.image("images\cloudy.png", caption="Nublado")
        else:
            st.image("images\default_image.png", caption="Estado del tiempo desconocido")
        # Convertir el campo "timezone" a formato de 24 horas
        timezone_offset = weather_data["timezone"]
        timezone = datetime.utcnow() + timedelta(seconds=timezone_offset)
        timezone_str = timezone.strftime("%H:%M:%S")
        # Mostrar información del campo "timezone" en formato de 24 horas
        st.subheader("Zona horaria (24 horas)")
        st.markdown(f"Zona horaria: {timezone_str}")
        

        st.subheader("Gráficas")
        # Mostrar la temperatura actual y la sensación térmica en una gráfica de líneas
        temp_df = pd.DataFrame({
            "Tiempo": [timezone_str],
            "Temperatura": [weather_data["main"]["temp"]],
            "Sensación térmica": [weather_data["main"]["feels_like"]]
        })
        temp_chart = go.Figure()
        temp_chart.add_trace(go.Scatter(x=temp_df["Tiempo"], y=temp_df["Temperatura"], mode='lines+markers', name='Temperatura'))
        temp_chart.add_trace(go.Scatter(x=temp_df["Tiempo"], y=temp_df["Sensación térmica"], mode='lines+markers', name='Sensación térmica'))
        temp_chart.update_layout(title="Temperatura y Sensación Térmica")
        temp_container.plotly_chart(temp_chart)

        # Mostrar temperatura mínima y máxima en una gráfica de líneas
        temp_min_max_df = pd.DataFrame({
            "Tiempo": [timezone_str],
            "Temperatura Mínima": [weather_data["main"]["temp_min"]],
            "Temperatura Máxima": [weather_data["main"]["temp_max"]]
        })
        temp_min_max_chart = go.Figure()
        temp_min_max_chart.add_trace(go.Scatter(x=temp_min_max_df["Tiempo"], y=temp_min_max_df["Temperatura Mínima"], mode='lines+markers', name='Temperatura Mínima'))
        temp_min_max_chart.add_trace(go.Scatter(x=temp_min_max_df["Tiempo"], y=temp_min_max_df["Temperatura Máxima"], mode='lines+markers', name='Temperatura Máxima'))
        temp_min_max_chart.update_layout(title="Temperatura Mínima y Máxima")
        temp_min_container.plotly_chart(temp_min_max_chart)

        # Mostrar la presión atmosférica en una gráfica de líneas
        pressure_df = pd.DataFrame({
            "Tiempo": [timezone_str],
            "Presión": [weather_data["main"]["pressure"]]
        })
        pressure_chart = go.Figure()
        pressure_chart.add_trace(go.Scatter(x=pressure_df["Tiempo"], y=pressure_df["Presión"], mode='lines+markers', name='Presión Atmosférica'))
        pressure_chart.update_layout(title="Presión Atmosférica")
        pressure_container.plotly_chart(pressure_chart)

        # Mostrar la humedad en una gráfica de líneas
        humidity_df = pd.DataFrame({
            "Tiempo": [timezone_str],
            "Humedad": [weather_data["main"]["humidity"]]
        })
        humidity_chart = go.Figure()
        humidity_chart.add_trace(go.Scatter(x=humidity_df["Tiempo"], y=humidity_df["Humedad"], mode='lines+markers', name='Humedad'))
        humidity_chart.update_layout(title="Humedad")
        humidity_container.plotly_chart(humidity_chart)

        # Mostrar tabla con datos adicionales, incluyendo descripción del clima y el ícono
        st.subheader("Datos adicionales")
        data = {
            "País": [weather_data["sys"]["country"]],
            "Longitud": [weather_data["coord"]["lon"]],
            "Latitud": [weather_data["coord"]["lat"]],
            "Descripción": [weather_data["weather"][0]["description"]],
            "Velocidad del Viento": [weather_data["wind"]["speed"]],
            "Amanecer": [datetime.fromtimestamp(weather_data["sys"]["sunrise"]).strftime("%Y-%m-%d %H:%M:%S")],
            "Atardecer": [datetime.fromtimestamp(weather_data["sys"]["sunset"]).strftime("%Y-%m-%d %H:%M:%S")]
        }
        df = pd.DataFrame(data)
        st.dataframe(df)
        # Verificar si se ha presionado el botón "Detener seguimiento"
        if stop_update:
            # Detener la ejecución de la aplicación
            st.write("Se ha detenido el seguimiento!!, vuelva a ingresar otra ciudad para consultar el clima")
            break
            st.stop()

        # Esperar 5 segundos antes de hacer la próxima llamada a la API
        time.sleep(5)
