from fastapi import FastAPI
import requests
import uvicorn
import redis

app = FastAPI()

@app.get("/")
def get_countries_weather():
    url1 = "https://restcountries.com/v3.1/all"
    url_weather = "https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid=f853ff302498c36c45f065e53ab14c00"

    redis_client = redis.Redis()
    response1 = requests.get(url1)

    if response1.status_code == 200:
        data = response1.json()
        countries = []
        for country in data:
            name = country["name"]["common"]
            capital = country.get("capital", "N/A")
            currency = country.get("currencies", "N/A")
            
            weather_url = url_weather.format(city_name=capital[0])
            response2 = requests.get(weather_url)
            # Check if the second API request was successful (status code 200)
            if response2.status_code == 200:
                weather_data = response2.json()
                weather_list = weather_data.get("weather", [])
                weather_description = weather_list[0]["description"]
                    # Add weather information to the country's data
                country_info = {
                        "name": name,
                        "capital": capital,
                        "currencies": currency,
                        "weather": weather_description
                    }
                countries.append(country_info)
            else:
                # Handle error if weather API request fails
                countries.append({
                    "name": name,
                    "capital": capital,
                    "currencies": currency,
                    "weather": "N/A"
                })
        redis_client.set("countries_data", str(countries))
    else:
        return "Something went wrong with the app you provide"

    return countries

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)

