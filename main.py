import requests
import json
import time
import re

watering_number = 2


def add_to_history(moisture_before, moisture_after, temperature, raining_status):
    global watering_number

    history_url = 'http://127.0.0.1:8080/update_history'


    history_data = {
        "WateringNumber": watering_number,
        "MoistureBefore": moisture_before,
        "MoistureAfter": moisture_after,
        "Temperature": temperature,
        "RainingStatus": raining_status
    }

    try:

        response = requests.post(history_url, json=history_data)


        if response.status_code == 201:
            print("Data added to history successfully")
            watering_number += 1
        else:

            print(f'Error adding data to history: {response.status_code}')

    except requests.RequestException as e:
        print(f"Error during HTTP request: {e}")


def toggle_relay():
    toggle_request = requests.get("http://192.168.1.100/toggle")

    if toggle_request.status_code == 200:
        print("Relay Toggled")
    else:
        print(f'Error: {toggle_request.status_code}')


def get_rainfall_from_api():
    try:
        response = requests.get(
            "http://api.weatherapi.com/v1/forecast.json?key=b0055fbf2bca4a17b95104217240901&q=Amman&days=1&aqi=no&alerts=no"
        )

        if response.status_code == 200:
            data = response.json()
            closest_hour_data = min(data['forecast']['forecastday'][0]['hour'],
                                    key=lambda x: abs(
                                        int(x['time'].split()[1].split(':')[0]) -
                                        time.localtime().tm_hour))

            rainfall_amount = closest_hour_data.get('precip_mm', None)
            print(rainfall_amount)
            return rainfall_amount

        else:
            print(f"Error: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error occurred while fetching rainfall data: {e}")
        return None


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


def start_watering():
    global watering_number
    print("Start Watering....")
    moisture_before1 = get_soilmoisture()
    temperature1, humidity1 = get_dht()
    watering_number
    start_time = time.strftime("%Y-%m-%dT%H:%M:%S")
    toggle_relay()
    while True:

        soil_moisture = get_soilmoisture()

        if soil_moisture is not None:
            print(f"Soil Moisture: {soil_moisture}")

            if soil_moisture >= 80:
                print("Soil Moisture reached the perfect level. Stoping watering.")
                add_to_history(moisture_before1, soil_moisture, temperature1, "No")
                watering_number += 1
                toggle_relay()
                break

        time.sleep(0.5)


def check_for_watering(temperature, humidity, soil_moisture):

    url = 'http://127.0.0.1:8080/predict'


    rainfall = get_rainfall_from_api()

    # Sample input data
    input_data = {
        'temperature': temperature,
        'humidity': humidity,
        'soil_moisture': soil_moisture,
        'rainfall': rainfall
    }


    response = requests.post(url, json=input_data)


    if response.status_code == 200:

        result = response.json()


        prediction = result['prediction']


        return prediction
    else:

        print(f'Error: {response.status_code}')


while True:
    print("Check for watering.")

    temperature, humidity = get_dht()
    soil_moisture = get_soilmoisture()


    prediction_result = check_for_watering(temperature, humidity, 10)

    if "On" in prediction_result:
        print("Plant Needs Watering, lets start it.")
        start_watering()
        print("Plant Succesfly watered, rechecking in 5 minutes")
    elif "Off" in prediction_result:
        print("Plant does not need watering, rechecking in 5 minutes.")

    time.sleep(300)


