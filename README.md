# ClimateReportsGenerator
Generate real-time weather reports for different cities around the world. From the OpenWeather API using FastAPI and displays it using Streamlit a Python web framework.

Images courtesy of [Unsplash](https://unsplash.com/)
## Features:

1. **Real-Time Weather Data:** The application retrieves real-time weather data from the OpenWeather API, including temperature, humidity, pressure, weather description, and wind speed.

2. **Dynamic Graphs:** The app generates dynamic line charts using Plotly to visualize the temperature, temperature range, pressure, and humidity trends for the selected city over time.

3. **Weather Icons:** The app displays weather icons corresponding to the current weather conditions, providing a quick visual representation of the weather status.

4. **Timezone Conversion:** The app converts the timezone offset from the API response to the local time of the selected city, making it easy for users to understand the weather data in their local time.

5. **User Interaction:** Users can interact with the application by entering different city names to retrieve weather information. Additionally, they can stop the real-time updates using the "Detener seguimiento" button.

6. **Five day weather forecast** Based on the city chosen by the user, the system is able to display the weather for the next 5 days from the day of inquiry.


********************************

## Steps to run the program:

1. Install libraries and dependencies from the requirements.txt file.

2. In "OpenWeather.py" file you have to put your own Api-key from [OpenWeather](https://openweathermap.org/) by changing this line `API_KEY = st.secrets["api_key"]` to `API_KEY ='YOUR_OPENWEATHER_API'`
   
3. Have the FastAPI server running = `uvicorn OpenWeather:app --reload`.
   
4. Compile the "FrontStream.py" file using streamlit = `streamlit run FrontStream.py`.
   
5. Once the interface is rendered, just enter the name of any desired city and click on the "Start tracking" button to begin real-time weather tracking for that city and then wait a few seconds while the request is processed.
   
6. If you want to see the forecast for the next 5 days, the user should click on the "show forecast" button.
    
7. At any time, you can stop real-time tracking by clicking on "stop tracking"."
