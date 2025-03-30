import requests
from deep_translator import GoogleTranslator

API_KEY = '15320ac32ad3ebbd83caafb64b1311f4'  # اینجا باید کلید API خود را وارد کنید

# تابع برای دریافت وضعیت آب و هوا از OpenWeatherMap
def get_weather(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&lang=fa&units=metric"
    response = requests.get(url)
    data = response.json()

    if data['cod'] != 200:
        return f"شهر '{city_name}' یافت نشد."

    location = data['name']
    status = data['weather'][0]['description']
    temperature = data['main']
    wind = data['wind']
    pressure = data['main']['pressure']
    humidity = data['main']['humidity']
    clouds = data['clouds']['all']

    # بررسی بارش باران
    rain = data.get('rain', {}).get('1h', 'ندارد')

    # بررسی شاخص حرارت
    heat_index = 'ندارد'  # اگر اطلاعات شاخص حرارت موجود نباشد
    if 'main' in data and 'heat_index' in data['main']:
        heat_index = data['main']['heat_index']

    # بازگشت تمام اطلاعات
    weather_info = f'''
    اطلاعات آب و هوا در {location}:
    وضعیت: {status}
    دمای فعلی: {temperature['temp']}°C (کمینه: {temperature['temp_min']}°C, بیشینه: {temperature['temp_max']}°C)
    رطوبت: {humidity}%
    باد: {wind['speed']} متر بر ثانیه، جهت: {wind['deg']} درجه
    فشار هوا: {pressure} hPa
    ابرها: {clouds}%
    باران: {rain}
    شاخص حرارت: {heat_index}
    '''
    return weather_info

# تابع برای ترجمه متن به زبان انگلیسی با استفاده از GoogleTranslator
def translate_text(text, target_language='en'):
    translator = GoogleTranslator(source='auto', target=target_language)
    translated = translator.translate(text)
    return translated



