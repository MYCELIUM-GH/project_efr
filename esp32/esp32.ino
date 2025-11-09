/*
Small programme, which is connecting ESP32 to Flask server hosted on RPI and publish
topics with DHT11 sensor's readings where Flask app handles them and push to web page.

Whole code follows logic "sensor->wifi->mqtt", so it should be easy to read.
=====================================================================================
Made by Oleh
*/
// ==== ==== IMPORTS ==== ==== 
#include "DHT.h" // library for sensor
#include <WiFi.h> // library for wifi connection
#include <PubSubClient.h> // library for MQTT (God, i love programming - just use libraries, that's all)
// ==== ==== SENSOR CONF ==== ====
// sensor's data pin connected to D4 on ESP32
#define DHTPIN 4 
// type of sensor, because the library supports several
#define DHTTYPE DHT11
// it defines dht as DHT type variable with pin4 and DHT11 macros which i created above
DHT dht(DHTPIN, DHTTYPE);
// ==== ==== WIFI CONF ==== ==== 
// name of network, password, server address and credits to login. i used mobile hotspot because my home network is wild
const char WIFI_SSID[] = "Arch";
const char WIFI_PASS[] = "bhfbkchwj";
const char MQTT_BROKER[] = "10.19.14.156";
const char MQTT_TOPIC[] = "esp32/dht11";
const char* MQTT_USER = "esp32user";
const char* MQTT_PASS = "1337";
// ==== ==== MQTT CONF ==== ==== 
// basic declarations, don't know much, just used guide. but probably defines espClient as macro
WiFiClient espClient;
// same as dht: new variable
PubSubClient client(espClient);
// initialisation of var for data messege
unsigned long lastMsg = 0;
// was neccecary to prevent server from storing too much data
#define MSG_BUFFER_SIZE  (50)
char msg[MSG_BUFFER_SIZE];
// ==== ==== WIFI FUNCTION ==== ==== 
void setup_wifi()
// separate function for wireless connection
{
    delay(2000);
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(WIFI_SSID);
    // starts connection with defined creditations
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    // sort of stop until esp connects to wifi, added mostly for debugging (and it's also fancy)
    while(WiFi.status() != WL_CONNECTED) 
    {
        delay(1000);
        Serial.print(".");
    }

    Serial.println();
    Serial.println("Connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    // if successful - assigns integrated LED to output mode, i'll explain later
    pinMode(2, OUTPUT);
}
// ==== ==== MQTT RECONNECT FUNCTION ==== ==== 
void reconnect_mqtt()
// mainly checks for successful connection to broker
{
    while(!client.connected())
    // starts loop similar to what you've seen for wifi
    {
        Serial.println();
        Serial.print("Attempting MQTT connection...");
        String clientId = "ESP32Client-";
        // assigns random suffix to ESP board, cool feature - i think
        clientId += String(random(0xffff), HEX);
        // check for successful connection, takes ID from above as parameter
        if(client.connect(clientId.c_str(), MQTT_USER, MQTT_PASS)) 
        {
            Serial.println("Connected!");
        }
        // in case connection is faled - will display error with code. debugging!
        else 
        {
            Serial.println();
            Serial.print("MQTT connction failed. Error code: ");
            Serial.print(client.state());
            delay(5000);
        }
    }
}
// ==== ==== MICS FUNCTION ==== ==== 
void setup() 
{
    // shows all the text on band 9600
    Serial.begin(9600);
    // invokes the function from sensor's lib
    dht.begin();
    // and wifi setup
    setup_wifi();
    // defines server's address and port 
    client.setServer(MQTT_BROKER, 1883);
}
// ==== ==== MAIN LOOP ==== ==== 
void loop() 
{
    // waits 2 seconds between assigning readings from sensor to variables
    delay(2000);
    // that's simple
    float h = dht.readHumidity();
    float t = dht.readTemperature();
    // in case of wrong readings shows error
    if(isnan(h) || isnan(t)) 
    {
        Serial.println(F("Failed to read from DHT sensor!"));
        return;
    }
    // debugging again, shows readings in serial monitor
    Serial.println();
    Serial.print(F("Humidity: "));
    Serial.print(h);
    Serial.print(F("%  Temperature: "));
    Serial.print(t);
    Serial.print(F("°C "));
    // my favourite part - if esp connected to wifi - it'll light blue LED. FANCY:D
    if(WiFi.status() == WL_CONNECTED)
    {
        digitalWrite(2,HIGH);
    }
    // invoke function for reconnection to server
    if (!client.connected())
    {
        reconnect_mqtt();
    }
    // invokes the function from mqtt's lib
    client.loop();
    // creates json payload
    snprintf(msg, MSG_BUFFER_SIZE, "{\"temperature\":%.1f, \"humidity\":%.1f}", t, h);
    // and some debugging again
    Serial.println();
    Serial.print("Sending message: ");
    Serial.println(msg);
    // finally, it sends messege to the server
    client.publish(MQTT_TOPIC, msg);
}
