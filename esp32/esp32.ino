/*
Small programme, which is connecting ESP32 to Flask server hosted on RPI and publish
topics with DHT11 sensor's readings where Flask app handles them and push to web page.

Whole code follows logic "sensor->wifi->mqtt", so it should be easy to read.
=====================================================================================
Made by Oleh
*/
#include "DHT.h"
#include <WiFi.h>
#include <PubSubClient.h>
// SENSOR CONFIG
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);
// WIFI CONFIG
const char WIFI_SSID[] = "House Admin";
const char WIFI_PASS[] = "gr34TWif1!!";
const char MQTT_BROKER[] = "192.168.29.104";
const char MQTT_TOPIC[] = "esp32/dht11";
// MQTT CONFIG
WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE  (50)
char msg[MSG_BUFFER_SIZE];

void setup_wifi() 
{
    delay(2000);
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(WIFI_SSID);

    WiFi.begin(WIFI_SSID, WIFI_PASS);

    while(WiFi.status() != WL_CONNECTED) 
    {
        delay(1000);
        Serial.print(".");
    }

    Serial.println();
    Serial.println("Connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    pinMode(2, OUTPUT);
}

void reconnect_mqtt() 
{
    while(!client.connected()) 
    {
        Serial.println();
        Serial.print("Attempting MQTT connection...");
        String clientId = "ESP32Client-";
        clientId += String(random(0xffff), HEX);

        if(client.connect(clientId.c_str())) 
        {
            Serial.println("connected");
        } 
        else 
        {
            Serial.println();
            Serial.print("MQTT connction failed. Error code: ");
            Serial.print(client.state());
            delay(5000);
        }
    }
}

void setup() 
{
    Serial.begin(9600);
    dht.begin();
    setup_wifi();
    client.setServer(MQTT_BROKER, 1883);
}

void loop() 
{
    delay(2000);

    float h = dht.readHumidity();
    float t = dht.readTemperature();

    if(isnan(h) || isnan(t)) 
    {
        Serial.println(F("Failed to read from DHT sensor!"));
        return;
    }
    Serial.println();
    Serial.print(F("Humidity: "));
    Serial.print(h);
    Serial.print(F("%  Temperature: "));
    Serial.print(t);
    Serial.print(F("°C "));

    if(WiFi.status() == WL_CONNECTED)
    {
        digitalWrite(2,HIGH);
    }

    if (!client.connected()) 
    {
        reconnect_mqtt();
    }
    client.loop();

    snprintf(msg, MSG_BUFFER_SIZE, "{\"temperature\":%.1f, \"humidity\":%.1f}", t, h);
    Serial.println();
    Serial.print("Sending message: ");
    Serial.println(msg);
    client.publish(MQTT_TOPIC, msg);
}
