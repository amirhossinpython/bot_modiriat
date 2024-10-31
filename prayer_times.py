import requests

def get_prayer_times(city):
    url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=IR"
    response = requests.get(url)
    
    if response.status_code == 200:
        timings = response.json()['data']['timings']
        return timings
    else:
        return None


