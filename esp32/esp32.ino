// ==== IMPORTS ====
#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"
// ==== VARIABLES ====
const char* WIFI_SSID = "House Admin";
const char* WIFI_PASS = "gr34TWif1!!";
const char* MQTT_BROKER = "192.168.1.104";
const char* MQTT_TOPIC = "sensorbox";
// ==== HARDWARE CONF ====
#define DHTPIN 15
#define DHTTYPE DHT11
// ==== MOSQUITTO SHT ====
WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE  (50)
char msg[MSG_BUFFER_SIZE];
// ==== PREP PART ====
void setup() {
    Serial.begin(115200);
    dht.begin();
    setup_wifi();
    client.setServer(MQTT_BROKER, 1883);
}

void setup_wifi() {
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println(WiFi.localIP());
}
// ==== RECONNECTING - just in case
void reconnect_mqtt() {
    while (!client.connected()) {
        String clientId = "ESP32Client-";
        clientId += String(random(0xffff), HEX);

        if (client.connect(clientId.c_str())) {
            Serial.println("connected");
        } else {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            delay(5000);
        }
    }
}
// ==== MAIN PART ====
void loop() {
    if (!client.connected()) {
        reconnect_mqtt();
    }
    client.loop();

    unsigned long now = millis();
    if (now - lastMsg > 5000) {
        lastMsg = now;

        float h = dht.readHumidity();
        float t = dht.readTemperature();

        snprintf(msg, MSG_BUFFER_SIZE, "{\"temperature\":%.1f, \"humidity\":%.1f}", t, h);

        Serial.print("Publish message: ");
        Serial.println(msg);
        client.publish(MQTT_TOPIC, msg);
    }
}
