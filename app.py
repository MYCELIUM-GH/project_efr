from flask import Flask, render_template, jsonify
import paho.mqtt.client as mqtt
import json
import threading

# --- Global variable to store sensor data ---
sensor_data = {
    'temperature': 'N/A',
    'humidity': 'N/A'
}
data_lock = threading.Lock() # To safely update the data from the MQTT thread

# --- Flask App Setup ---
app = Flask(__name__)

# --- MQTT Client Setup ---
MQTT_BROKER = "localhost"  # Running on the same Pi
MQTT_TOPIC = "esp32/dht11" # Same topic as the ESP32
MQTT_USER = "esp32user"
MQTT_PASS = "1337"

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT with result code {rc}")
    # Subscribe to the topic
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global sensor_data
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
    try:
        # Decode the JSON payload
        data = json.loads(msg.payload.decode())
        
        # Update the global variable safely
        with data_lock:
            sensor_data['temperature'] = data.get('temperature', 'N/A')
            sensor_data['humidity'] = data.get('humidity', 'N/A')
            
    except json.JSONDecodeError:
        print("Failed to decode JSON")
    except Exception as e:
        print(f"An error occurred: {e}")

# Initialize and start the MQTT client
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(username=MQTT_USER, password=MQTT_PASS)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_BROKER, 1883, 5000)
mqtt_client.loop_start() # Start the client loop in a background thread

# --- Web Routes ---

@app.route('/')
def index():
    """Serve the main HTML page."""
    # Renders the template from the 'templates' folder
    return render_template('index.html')

@app.route('/data')
def get_data():
    """API endpoint to get the latest sensor data."""
    with data_lock:
        # Return the current data as JSON
        return jsonify(sensor_data)

# --- Run the Flask App ---
if __name__ == '__main__':
    # Run on host 0.0.0.0 to be accessible from other devices on the network
    app.run(host='0.0.0.0', port=5000, debug=False)
