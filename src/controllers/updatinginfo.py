import requests
import time
import json
import re


def get_dht():
    try:
        print("Getting information from the DHT Sensor, please wait.")
        dht_request = requests.get("http://192.168.1.100/readweather").text
        print(dht_request)


        cleaned_response = dht_request.replace('Â', '')


        pattern = r'Temperature: ([\d.]+)°C, Humidity: ([\d.]+)%'


        match = re.search(pattern, cleaned_response)


        if match:

            temperature = float(match.group(1))
            humidity = float(match.group(2))
            print("Temperature:", temperature)
            print("Humidity:", humidity)


            return temperature, humidity
        else:
            print("Unable to extract temperature and humidity from the response.")

            return None
    except requests.RequestException as e:
        print(f"Error during HTTP request: {e}")

        return None


def get_soilmoisture():
    try:
        print("Getting soil moisture information, please wait.")
        moisture_request = requests.get("http://192.168.1.100/readmoisture").text
        print(moisture_request)


        cleaned_response = moisture_request.strip()  

        try:
            moisture_str = cleaned_response.split(":")[1].strip().rstrip('%')
            moisture = int(moisture_str)
            print("Moisture:", moisture)

            return moisture
        except (IndexError, ValueError) as e:
            print(f"Error extracting moisture value: {e}")
            return None
    except requests.RequestException as e:
        print(f"Error during HTTP request: {e}")
        return None

# Define the URL for updating weather information
#update_weather_url = 'http://127.0.0.1:8080/update_weather'

# Example weather data
#weather_data = {
#    "Temperature": 25,
#    "Precipitation By MM": 5,
#    "WindSpeed": 10,
#    "Chance Of Rain": 30
#}

# Send a POST request to update weather information
#response_weather = requests.post(update_weather_url, json=weather_data)

# Print the response
#print("Update Weather Response:", response_weather.json())


# Define the URL for updating soil moisture
#update_moisture_url = 'http://127.0.0.1:8080/update_moisture'

# Example moisture data
#moisture_data = {
#    "Moisture": 40
#}

# Send a POST request to update soil moisture
#response_moisture = requests.post(update_moisture_url, json=moisture_data)

# Print the response
#print("Update Moisture Response:", response_moisture.json())

while True:
    temperature, humidity = get_dht()
    soil_moisture = get_soilmoisture()
    moisture_data = {
        "Moisture": soil_moisture
    }
    
    weather_data = {
        "Temperature": temperature,
        "Precipitation By MM": 5,
        "WindSpeed": 10,
        "Chance Of Rain": 30

    }
    #updating moisture
    update_moisture_url = 'http://127.0.0.1:8080/update_moisture'
    response_moisture = requests.post(update_moisture_url, json=moisture_data)
    print("Update Moisture Response:", response_moisture.json())
    #updating weather
    update_weather_url = 'http://127.0.0.1:8080/update_weather'
    response_weather = requests.post(update_weather_url, json=weather_data)
    print("Update Weather Response:", response_weather.json())
    time.sleep(120)







    

