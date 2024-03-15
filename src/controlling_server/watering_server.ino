#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <DHT.h>
#include <ArduinoHttpClient.h>
#include <ArduinoJson.h>

// Replace with your network credentials
const char *ssid = "zain-BB48";
const char *password = "22318421";

// Replace with the actual IP address and port of your Flask server
const char* flaskUrl = "https://59e28af0-17fd-4b8a-9ab5-7d26d29f4c16-00-2bkl7k7e7je2z.riker.replit.dev";
const int flaskPort = 443;

// Create an instance of the ESP8266WebServer class
ESP8266WebServer server(80);

// Define the DHT sensor
#define DHTPIN D3 // Replace with the actual pin connected to the DHT sensor
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Define the pin connected to the relay
const int relayPin = D0; // Replace with the actual pin connected to the relay

#define sensorPin A0


void setup() {
  // Start Serial communication
  Serial.begin(115200);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Print the ESP8266 server IP address
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Initialize the DHT sensor
  dht.begin();

  // Set the relay pin as an output
  pinMode(relayPin, OUTPUT);

  // Define the server endpoints
  server.on("/toggle", HTTP_GET, handleToggle);
  server.on("/readmoisture", HTTP_GET, handleReadMoisture);
  server.on("/readweather", HTTP_GET, handleReadWeather);

  // Start the server
  server.begin();
  Serial.println("Server started");
}

void loop() {
  // Handle client requests
  server.handleClient();


}

void handleToggle() {
  // Toggle the relay
  digitalWrite(relayPin, !digitalRead(relayPin));
  server.send(200, "text/plain", "Relay toggled");
}


void handleReadMoisture() {
  int sensorValue = analogRead(sensorPin);
  sensorValue = map(sensorValue, 0, 1024, 0, 100);
  sensorValue = constrain(sensorValue, 0, 100);

  sensorValue *= 2;

  Serial.print("Moisture Percentage: ");
  Serial.println(sensorValue);


  server.send(200, "text/plain", "Moisture: " + String(sensorValue) + "%");
}

void handleReadWeather() {
  // Read temperature and humidity from DHT sensor
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // Check if readings are valid
  if (isnan(temperature) || isnan(humidity)) {
    server.send(500, "text/plain", "Error reading DHT sensor");
  } else {
    // Send temperature and humidity as response
    server.send(200, "text/plain", "Temperature: " + String(temperature) + "°C, Humidity: " + String(humidity) + "%");
  }
}
