# A part programme, which is connecting ESP32 to Flask server hosted on RPI and publish
# topics with DHT11 sensor's readings where Flask app handles them and push to web page.
#
# =====================================================================================
# Made by Oleh
# ==== ==== ==== ==== IMPORTS ==== ==== ==== ====
from flask import Flask, render_template, jsonify
import paho.mqtt.client as mqtt
import json
import threading
# ==== ==== ==== ==== GLOBAL VARIABLES ==== ==== ==== ====
sensor_data = {
    'temperature': 'N/A',
    'humidity': 'N/A'
}
data_lock = threading.Lock()
MQTT_BROKER = "localhost"
MQTT_TOPIC = "esp32/dht11"
MQTT_USER = "esp32user"
MQTT_PASS = "1337"
# ==== ==== ==== ==== APP NAME ==== ==== ==== ====
app = Flask(__name__)
# ==== ==== ==== ==== MQTT CONF ==== ==== ==== ====
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global sensor_data
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
    try:
        data = json.loads(msg.payload.decode())
        with data_lock:
            sensor_data['temperature'] = data.get('temperature', 'N/A')
            sensor_data['humidity'] = data.get('humidity', 'N/A')
            
    except json.JSONDecodeError:
        print("Failed to decode JSON")
    except Exception as e:
        print(f"Error code: {e}")
# ==== ==== ==== ==== WEB ROUTES ==== ==== ==== ====
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/data')
def get_data():
    with data_lock:
        return jsonify(sensor_data)
# ==== ==== ==== ==== START MQTT ==== ==== ==== ====
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(username=MQTT_USER, password=MQTT_PASS)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, 1883, 5000)
mqtt_client.loop_start()
# ==== ==== ==== ==== START THE APP ==== ==== ==== ====
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
