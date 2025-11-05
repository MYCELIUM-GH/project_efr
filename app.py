# ==== IMPORTS ====
from flask import Flask, render_template, jsonify
import mqtt
import json
import threading
# ==== VARIABLES ====
sensor_data = {
    'temperature': 'N/A',
    'humidity': 'N/A'
}
data_lock = threading.Lock()

# ==== FLASK SETUP ====
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    with data_lock:
        return jsonify(sensor_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
# ==== MQTT SHT ====
MQTT_BROKER = "192.168.1.104"
MQTT_TOPIC = "sensorbox"

def on_connect(client, userdata, flags, rc):
    print(f"{rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global sensor_data
    print(f"{msg.topic}: {msg.payload.decode()}")
    try:
        data = json.loads(msg.payload.decode())
        with data_lock:
            sensor_data['temperature'] = data.get('temperature', 'N/A')
            sensor_data['humidity'] = data.get('humidity', 'N/A')
    except json.JSONDecodeError:
        print("JSON decoding error")
    except Exception as e:
        print(f"error code: {e}")

# ==== START CLIENT ====
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, 1883, 60)
mqtt_client.loop_start()
