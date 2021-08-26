import requests
import json
import os, sys


WEATHER_API_TOKEN = os.getenv('WEATHER_API_TOKEN')



def weatherMainInfo(weather_info):
    result = {
    'country': weather_info['sys']['country'],
    'city': weather_info['name'],
    'description': weather_info['weather'][0]['description'],
    'temp': weather_info['main']['temp'],
    'temp_feels': weather_info['main']['feels_like'],
    'humidity': weather_info['main']['humidity'],
    'wind_speed': weather_info['wind']['speed']
    }

    return result


def weatherParser(weather_info):
    result = f"""
{weather_info['country']}, {weather_info['city']}:

<b>{weather_info['description'].upper()}</b>

Температура: {weather_info['temp']} °C
Ощущается как: {weather_info['temp_feels']} °C

Влажность: {weather_info['humidity']}%

Скорость ветра: {weather_info['wind_speed']} м/с
"""
    return result


def getCurrentWeather(country, city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&cnt={country}&units=metric&appid={WEATHER_API_TOKEN}&lang=ru"
    response = requests.get(url)

    weather_info = json.loads(response.text)
    return weatherParser(weatherMainInfo(weather_info))