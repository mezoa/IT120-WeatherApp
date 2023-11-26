from django.shortcuts import render
from geopy.geocoders import Nominatim

import requests
import datetime

# Create your views here.
def index(request): 
    API_KEY = open("C:\\Users\\Meo Angelo Alcantara\\Documents\\GitHub\\IT120_WeatherApp\\weather_app\\API_KEY", "r").read()
    current_weather_url = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}"
    forecast_url = "https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&exclude=current,minutely,hourly,alerts&appid={}"

    if request.method == "POST":
        geolocator = Nominatim(user_agent="weather_app")
        city1 = request.POST['city1']
        city2 = request.POST.get('city2', None)

        location1 = geolocator.geocode(city1)
        location2 = None

        if city2:
            location2 = geolocator.geocode(city2)

        weather_data1, daily_forecasts1 = None, None
        weather_data2, daily_forecasts2 = None, None

        if location1:
            city1 = {'lat': location1.latitude, 'lon': location1.longitude, 'name': city1}
            weather_data1, daily_forecasts1 = fetch_weather_and_forecast(city1, API_KEY, current_weather_url, forecast_url)

        if location2:
            city2 = {'lat': location2.latitude, 'lon': location2.longitude, 'name': city2}
            weather_data2, daily_forecasts2 = fetch_weather_and_forecast(city2, API_KEY, current_weather_url, forecast_url)

        context = {
            "weather_data1": weather_data1,
            "daily_forecasts1": daily_forecasts1,
            "weather_data2": weather_data2,
            "daily_forecasts2": daily_forecasts2
        }


        return render(request, 'weather_app/index.html', context)
    else: 
        return render(request, 'weather_app/index.html')
    

def fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url):
    try:
        current_response = requests.get(current_weather_url.format(city['lat'], city['lon'], api_key)).json()
        forecast_response = requests.get(forecast_url.format(city['lat'], city['lon'], api_key)).json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None, None

    weather_data = {
        'city': city['name'],
        'temperature': round(current_response['main']['temp'] - 273.15, 2),
        'description': current_response['weather'][0]['description'],
        'icon': current_response['weather'][0]['icon'],
    }

    daily_forecasts = []
    for forecast in forecast_response.get('list', []):
        # Ensure data availability for the chosen time (e.g., 12:00 PM)
        forecast_time = datetime.datetime.strptime(forecast['dt_txt'], '%Y-%m-%d %H:%M:%S').time()
        if forecast_time.hour == 12:
            daily_forecasts.append({
                'day': datetime.datetime.strptime(forecast['dt_txt'], '%Y-%m-%d %H:%M:%S').strftime('%A'),
                'temp_min': round(forecast['main']['temp_min'] - 273.15, 2),
                'temp_max': round(forecast['main']['temp_max'] - 273.15, 2),
                'description': forecast['weather'][0]['description'],
                'icon': forecast['weather'][0]['icon'],
            })
            if len(daily_forecasts) == 5:
                break  # Stop after collecting 5 days' forecast data

    return weather_data, daily_forecasts