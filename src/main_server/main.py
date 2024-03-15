from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
from datetime import datetime
import joblib
import pandas as pd
import requests

app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')

loaded_model = joblib.load("decision_tree_model.sav")


latest_weather_data = {}


@app.route('/')
def home():
  return redirect('/dashboard')

def toggle_relay():
    toggle_request = requests.get("http://192.168.1.100/toggle")

    if toggle_request.status_code == 200:
        print("Relay Toggled")
    else:
        print(f'Error: {toggle_request.status_code}')


@app.route('/predict', methods=['POST'])
def predicti():

  data = request.get_json()


  temperature = float(data['temperature'])
  humidity = float(data['humidity'])
  soil_moisture = float(data['soil_moisture'])
  rainfall = float(data['rainfall'])


  new_data = pd.DataFrame({
      'Temperature': [temperature],
      'Humidity': [humidity],
      'Soil Moisture': [soil_moisture],
      'Rainfall': [rainfall]
  })


  y_pred = loaded_model.predict(new_data)

  # Convert the NumPy array to a Python list
  y_pred_list = y_pred.tolist()


  return jsonify({'prediction': y_pred_list})


latest_moisture = None


@app.route('/dashboard', methods=['GET'])
def dashboard():

  try:
    with open('history.json', 'r') as file:
      history_data = json.load(file)
  except FileNotFoundError:
    history_data = []

  history_data.reverse()

  return render_template('dashboard.html',
                         moisture=30,
                         history_data=history_data)


@app.route('/update_history', methods=['POST'])
def update_history():
  try:

    data = request.json
    if not isinstance(data, dict):
      return jsonify({"error": "Invalid JSON format"}), 400


    required_fields = [
        "WateringNumber", "StartTime", "MoistureBefore", "MoistureAfter",
        "Temperature", "RainingStatus"
    ]
    if not all(field in data for field in required_fields):
      return jsonify({"error": "Invalid data format"}), 400


    data["Timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


    try:
      with open('history.json', 'r') as file:
        history_data = json.load(file)
    except FileNotFoundError:
      history_data = []


    if not isinstance(history_data, list):
      history_data = []


    history_data.append(data)


    with open('history.json', 'w') as file:
      json.dump(history_data, file, indent=2)

    return jsonify({"success": True}), 201

  except FileNotFoundError:
    return jsonify({"error": "File not found"}), 500

  except json.JSONDecodeError:
    return jsonify({"error": "Invalid JSON format"}), 400

  except Exception as e:
    return jsonify({"error": str(e)}), 500


@app.route('/update_weather', methods=['POST'])
def update_weather():
  try:
    data = request.json
    if not isinstance(data, dict):
      return jsonify({"error": "Invalid JSON format"}), 400


    required_fields = [
        "Temperature", "Precipitation By MM", "WindSpeed", "Chance Of Rain"
    ]
    if not all(field in data for field in required_fields):
      return jsonify({"error": "Invalid weather data format"}), 400


    data["Timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


    latest_weather_data.update(data)

    return jsonify({"success": True})

  except Exception as e:
    return jsonify({"error": str(e)}), 500


@app.route('/update_moisture', methods=['POST'])
def update_moisture():
  try:

    data = request.json
    if not isinstance(data, dict):
      return jsonify({"error": "Invalid JSON format"}), 400


    required_fields = ["Moisture"]
    if not all(field in data for field in required_fields):
      return jsonify({"error": "Invalid moisture data format"}), 400


    global latest_moisture
    latest_moisture = data["Moisture"]

    return jsonify({"success": True})

  except Exception as e:
    return jsonify({"error": str(e)}), 500


@app.route('/get_latest_data', methods=['GET'])
def get_latest_data():
  try:

    latest_weather = latest_weather_data

    return jsonify({
        "latest_moisture": latest_moisture,
        "latest_weather": latest_weather
    })

  except Exception as e:
    return jsonify({"error": str(e)}), 500
  

@app.route('/toggle_water_pump', methods=['GET'])
def toggle_water_pump():
    try:
        toggle_relay()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

  


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)
