# Part of the small programme, which is connecting ESP32 to Flask server hosted on RPI and publish
# topics with DHT11 sensor's readings where Flask app handles them and push to web page.
# to talk to the ESP32 sensor device.
#
# ===============================================
# Made by Oleh
# ==== ==== ==== ==== IMPORTS ==== ==== ==== ====
from flask import Flask, render_template, jsonify    # imports stuff we need for the web server
                                                     # Flask is the main web framework
                                                     # render_template lets us see HTML
                                                     # jsonify helps turn data from the sensor into json (i found it easy enough)
import paho.mqtt.client as mqtt                      # the library to connect to the MQTT broker/server
import json                                          # the library to work with json format data
import threading                                     # the library to safely handle shared data between different parts of the programme

# ==== ==== ==== ==== GLOBAL VARIABLES ==== ==== ==== ====
sensor_data = {
    'temperature': 'N/A',                       # dictionary to hold the latest temperature value. 'N/A' for placeholder if there is no data
    'humidity': 'N/A'                           # the same for humidity
}
data_lock = threading.Lock()                    # 'lock' object. found it fun to use, not neccessary here, but i love it
                                                # it makes sure only one part of the program - web or MQTT is changing it at a time,
                                                # preventing errors if both try to do it simultaneously
MQTT_BROKER = "localhost"                       # address of my server. i used 'localhost', but 127.0.0.1 is also fine
MQTT_TOPIC = "esp32/dht11"                      # topic name, kind of channel. don't know much, but this should be the same for all devices
MQTT_USER = "esp32user"                         # username
MQTT_PASS = "1337"                              # password

# ==== ==== ==== ==== APP NAME ==== ==== ==== ====
app = Flask(__name__)                           # creates the Flask web application instance

# ==== ==== ==== ==== MQTT CONF ==== ==== ==== ====
def on_connect(client, userdata, flags, rc):
    # this function will run right after successfull connection to the MQTT broker
    print(f"Connected to MQTT with result code {rc}")
    client.subscribe(MQTT_TOPIC)                      # connect to the topic/channel

def on_message(client, userdata, msg):
    # this function runs every time when new data arrives
    global sensor_data                              # should be global because it has to change initial global var
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}") # prints the raw message for debugging
    try:
        data = json.loads(msg.payload.decode())     # tries to convert the received text from the ESP32 into a python dictionary
        with data_lock:                             # it ensures the programme will access sensor_data for only one thread
            # updates global variables with the new values from the message
            # .get() is used to grab the values, providing placeholders if data is missing
            sensor_data['temperature'] = data.get('temperature', 'N/A') 
            sensor_data['humidity'] = data.get('humidity', 'N/A')
            # the lock is automatically released when we exit the 'with' block
    except json.JSONDecodeError:
        print("Failed to decode JSON")              # if the message wasn't valid JSON it prints an error
    except Exception as e:
        print(f"Error code: {e}")                   # in case of other errors - shows them
# ==== ==== ==== ==== WEB ROUTES ==== ==== ==== ====
@app.route('/')
def index():
    # this function shows index.html when user goes to the main URL
    return render_template('index.html')
@app.route('/data')
def get_data():
    # function to access recieved data, uses lock as explained above
    with data_lock:
        return jsonify(sensor_data)                 # sends the latest json with sensor data back to the browser

# ==== ==== ==== ==== START MQTT ==== ==== ==== ====
mqtt_client = mqtt.Client()                         # MQTT client object
mqtt_client.username_pw_set(username=MQTT_USER, password=MQTT_PASS) # sets username and password defined above
mqtt_client.on_connect = on_connect                 # tells the client which function to run after connecting
mqtt_client.on_message = on_message                 # tells the client which function to run when a message arrives
mqtt_client.connect(MQTT_BROKER, 1883, 5000)        # tries to connect to the broker
mqtt_client.loop_start()                            # it's just monitoring for new messeges

# ==== ==== ==== ==== START THE APP ==== ==== ==== ====
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) # must-have part. just runs whole programme. host 0.0.0.0 for accessability from other devices
