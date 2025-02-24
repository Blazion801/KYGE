import network
import time
import ujson
import machine
import dht
import ntptime
import urequests  # For sending HTTP requests to Flask server
from umqtt.robust import MQTTClient  # For sending data to Ubidots

# 🔹 WiFi Configuration
SSID = "Edward's Galaxy S22+"  # Change this to your WiFi name
PASSWORD = "foundthe14me"       # Change this to your WiFi password

# 🔹 Flask Server (Change IP to your PC's IP)
server_url = "http://192.168.173.101:5000/insert"  

# 🔹 Ubidots MQTT Configuration
UBIDOTS_TOKEN = "BBUS-ZA0nAU03WX6SQ7c1GjFuaStZzRreom"
DEVICE_LABEL = "esp32_sensor"
VARIABLE_TEMP = "temperature"
VARIABLE_HUMID = "humidity"

BROKER = "industrial.api.ubidots.com"
PORT = 1883
CLIENT_ID = "ESP32_" + str(machine.unique_id())
PUB_TOPIC = f"/v1.6/devices/{DEVICE_LABEL}"

# 🔹 Sync ESP32 Time with NTP
try:
    ntptime.settime()
except:
    print("NTP sync failed!")

def get_timestamp():
    year, month, day, hour, minute, second, _, _ = time.localtime()
    return f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

# 🔹 Connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Connecting to WiFi", end="")

    while not wlan.isconnected():
        print(".", end="")
        time.sleep(1)

    print("\nConnected to WiFi:", wlan.ifconfig())

# 🔹 Connect to Ubidots MQTT
def connect_mqtt():
    client = MQTTClient(CLIENT_ID, BROKER, PORT, user=UBIDOTS_TOKEN, password=UBIDOTS_TOKEN)
    client.connect()
    print("Connected to Ubidots MQTT!")
    return client

# 🔹 Send Data to Flask Server
def send_to_server(temperature, humidity):
    data = {
        "temp": temperature,
        "humidity": humidity,
        "timestamp": get_timestamp()
    }
    
    try:
        response = urequests.post(server_url, json=data)
        print("Server Response:", response.text)
        response.close()
    except Exception as e:
        print("Failed to send data to server:", e)

# 🔹 Send Data to Ubidots
def send_to_ubidots(client, temperature, humidity):
    data = ujson.dumps({
        VARIABLE_TEMP: {"value": temperature},
        VARIABLE_HUMID: {"value": humidity}
    })

    try:
        print(f"Sending to Ubidots: {data}")
        client.publish(PUB_TOPIC.encode(), data)
    except Exception as e:
        print(f"Ubidots Error: {e}")

# 🔹 Initialize DHT11 Sensor (Connected to GPIO5)
sensor = dht.DHT11(machine.Pin(5))

# 🔹 Main Loop (Collect & Send Data)
def main():
    connect_wifi()
    mqtt_client = connect_mqtt()

    while True:
        try:
            sensor.measure()
            temperature = sensor.temperature()
            humidity = sensor.humidity()

            print(f"\nTemperature: {temperature}°C, Humidity: {humidity}%")
            
            # Send to Flask server
            send_to_server(temperature, humidity)

            # Send to Ubidots
            send_to_ubidots(mqtt_client, temperature, humidity)

        except Exception as e:
            print(f"Sensor Error: {e}")

        time.sleep(5)  # Send data every 5 seconds

# 🔹 Run Main Program
main()
