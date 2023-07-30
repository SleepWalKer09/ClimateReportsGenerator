import streamlit as st
import httpx
import pandas as pd
import plotly.express as px
import threading
import time
from datetime import datetime, timedelta


# Definir la URL base de la API
base_url = "http://localhost:8000/weather/"
# URL base para obtener los íconos de OpenWeather
icon_base_url = "https://openweathermap.org/img/wn/"

# Configuración de la página
st.set_page_config(page_title="Reportes climáticos", page_icon="🌤️")

# Título de la interfaz
st.title("Generador de Reportes Climáticos 🌪️")


# Función para obtener datos climáticos de la API
def get_weather_data(city):
    url = base_url + city
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()

# Función para mostrar TODA la información climática en la interfaz
def mostrar_info_climatica(weather_data):
    # Mostrar la información climática
    st.write(
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
    st.dataframe(df)

    # Mostrar las gráficas
    timezone_offset = weather_data["timezone"]
    timezone = datetime.utcnow() + timedelta(seconds=timezone_offset)
    timezone_str = timezone.strftime("%H:%M:%S")

    # Mostrar gráficas
    # Crear gráficas de Temperatura en el Tiempo
    temp_time_df = pd.DataFrame({
        "Tiempo": [timezone_str],
        "Temperatura": [weather_data["main"]["temp"]]
    })
    temp_time_chart = px.line(temp_time_df, x="Tiempo", y="Temperatura", title="Variación de Temperatura en el Tiempo")

    # Mostrar gráfica de Temperatura Mínima y Máxima (gráfico de barras)
    temp_min_max_df = pd.DataFrame({
        "Temperatura": ["Temperatura Mínima", "Temperatura Máxima"],
        "Valor": [weather_data["main"]["temp_min"], weather_data["main"]["temp_max"]]
    })

    temp_min_max_chart = px.bar(temp_min_max_df, x="Temperatura", y="Valor", title="Temperatura Mínima y Máxima")

    # Crear gráficas de Presión Atmosférica en el Tiempo
    pressure_time_df = pd.DataFrame({
        "Tiempo": [timezone_str],
        "Presión Atmosférica": [weather_data["main"]["pressure"]]
    })

    pressure_time_chart = px.line(pressure_time_df, x="Tiempo", y="Presión Atmosférica", title="Variación de Presión Atmosférica en el Tiempo")

    # Crear gráficas de Humedad en el Tiempo
    humidity_time_df = pd.DataFrame({
        "Tiempo": [timezone_str],
        "Humedad": [weather_data["main"]["humidity"]]
    })

    humidity_time_chart = px.line(humidity_time_df, x="Tiempo", y="Humedad", title="Variación de Humedad en el Tiempo")

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

# Variable para controlar el hilo de actualización
seguir_actualizando = False
# Variable para almacenar los datos climáticos
weather_data = None
# Estructuras de datos para almacenar datos históricos
temperatura_historica = []
presion_historica = []
humedad_historica = []

# Función para actualizar los datos climáticos y mostrar la información climática
def update_weather_data(city):
    global weather_data, temperatura_historica, presion_historica, humedad_historica

    try:
        # Obtener el clima actual de la ciudad ingresada
        weather_data = get_weather_data(city)

        # Actualizar datos históricos
        if weather_data:
            temperatura_historica.append({
                "Tiempo": datetime.utcnow().strftime("%H:%M:%S"),
                "Temperatura": weather_data["main"]["temp"]
            })

            presion_historica.append({
                "Tiempo": datetime.utcnow().strftime("%H:%M:%S"),
                "Presión Atmosférica": weather_data["main"]["pressure"]
            })

            humedad_historica.append({
                "Tiempo": datetime.utcnow().strftime("%H:%M:%S"),
                "Humedad": weather_data["main"]["humidity"]
            })

    except httpx.HTTPError as e:
        st.error(f"Error al obtener los datos climáticos: {e}")

# Función para mostrar las gráficas con los datos históricos actualizados
def mostrar_graficas():
    # Crear DataFrame para la variación de Temperatura en el Tiempo
    temp_time_df = pd.DataFrame(temperatura_historica, columns=["Tiempo", "Temperatura"])
    temp_time_chart = px.line(temp_time_df, x="Tiempo", y="Temperatura", title="Variación de Temperatura en el Tiempo")

    # Crear DataFrame para la Temperatura Mínima y Máxima
    temp_min_max_df = pd.DataFrame(presion_historica, columns=["Tiempo", "Presión Atmosférica"])
    temp_min_max_chart = px.line(temp_min_max_df, x="Tiempo", y="Presión Atmosférica", title="Variación de Presión Atmosférica en el Tiempo")

    # Crear DataFrame para la variación de Humedad en el Tiempo
    humidity_time_df = pd.DataFrame(humedad_historica, columns=["Tiempo", "Humedad"])
    humidity_time_chart = px.line(humidity_time_df, x="Tiempo", y="Humedad", title="Variación de Humedad en el Tiempo")

    # Dividir el espacio en dos columnas para los gráficos interactivos
    fig_col1, fig_col2 = st.columns(2)
    fig_col3, fig_col4 = st.columns(2)

    # Mostrar los gráficos interactivos en las columnas respectivas
    with fig_col1:
        st.plotly_chart(temp_time_chart)

    with fig_col2:
        st.plotly_chart(temp_min_max_chart)

    with fig_col3:
        st.plotly_chart(humidity_time_chart)

# Widget para obtener la ciudad del usuario
city = st.text_input("Ingrese el nombre de la ciudad:")
# Widget para iniciar el seguimiento
start_update = st.button("Iniciar seguimiento")
# Widget para detener el seguimiento
stop_update_button = st.button("Detener seguimiento")

# Verificar si se ha ingresado una ciudad válida y se ha hecho clic en el botón "Iniciar seguimiento"
if city and start_update and not seguir_actualizando:
    seguir_actualizando = True
    # Crear un contenedor vacío para mostrar la información climática
    info_climatica_container = st.empty()
    # Realizar una llamada inicial para mostrar los datos climáticos antes de iniciar el intervalo de actualización
    update_weather_data(city)

while seguir_actualizando:
    # Actualizar los datos climáticos cada 10 segundos
    update_weather_data(city)

    # Mostrar la información climática en el contenedor
    if weather_data:
        # Actualizar el contenedor con la información climática
        info_climatica_container.subheader("Información climática actual (última actualización)")
        mostrar_info_climatica(weather_data)
        # Mostrar las gráficas con los datos históricos actualizados
        mostrar_graficas()
        
    # Pequeño retraso para evitar llamadas excesivamente rápidas a la API
    time.sleep(10)

    # Detener el seguimiento si se ha hecho clic en el botón "Detener seguimiento"
    if stop_update_button:
        seguir_actualizando = False
        # Mostrar mensaje cuando el seguimiento en tiempo real ha sido detenido
        st.warning("Seguimiento en tiempo real está detenido. Ingrese una ciudad para continuar.")


# Mostrar la información climática actual congelada
if weather_data:
    st.subheader("Información climática actual (última actualización)")
    mostrar_info_climatica(weather_data)
