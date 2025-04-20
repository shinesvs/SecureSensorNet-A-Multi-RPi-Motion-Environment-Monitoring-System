import RPi.GPIO as GPIO
import time
import ssl
import paho.mqtt.client as mqtt
import subprocess
from datetime import datetime
import os
import board
import busio
import adafruit_ahtx0

# GPIO
PIR_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Humidity and Temperatuer Sensor
i2c = busio.I2C(board.SCL, board.SDA)
aht20 = adafruit_ahtx0.AHTx0(i2c)

# MQTT Config
broker_address = "rpibroker"
broker_port = 8883
topic = "test"
# MQTT TLS Certs
ca_cert = "/home/shine/mqtt-certs/ca.crt"
client_cert = "/home/shine/mqtt-certs/rpi1.crt"
client_key = "/home/shine/mqtt-certs/rpi1.key"

client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
client_context.minimum_version = ssl.TLSVersion.TLSv1_3
client_context.maximum_version = ssl.TLSVersion.TLSv1_3

client_context.load_verify_locations(cafile=ca_cert)
client_context.load_cert_chain(certfile=client_cert, keyfile=client_key)
client_context.check_hostname = True

client = mqtt.Client()
client.tls_set_context(client_context)

try:
    client.connect(broker_address, broker_port)
    print("Connected to MQTT broker over TLSv1.3")
except Exception as e:
    print("MQTT connection failed:", e)
    GPIO.cleanup()
    exit(1)

# Video with Camera - Currently saves locally on RPi1
video_dir = "/home/shine/videos"
os.makedirs(video_dir, exist_ok=True)

print("Publishing sensor data every 2s. Recording video on motion detected...")

# Main loop
try:
    while True:
        # Read sensors
        temperature = round(aht20.temperature, 2)
        humidity = round(aht20.relative_humidity, 2)
        motion = GPIO.input(PIR_PIN) == GPIO.HIGH
        video_path = None

        # Record video if motion detected
        if motion:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_path = os.path.join(video_dir, f"motion_{timestamp}.mp4")
            print(f"Motion detected! Recording video to: {video_path}")

            subprocess.run([
                "ffmpeg",
                "-f", "v4l2",
                "-input_format", "mjpeg",
                "-video_size", "1024x768",
                "-i", "/dev/video0",
                "-t", "10",
                "-vcodec", "libx264",
                "-preset", "ultrafast",
                "-y",
                video_path
            ])

        # Compose and send MQTT payload
        payload = f"""
        Temperature: {temperature}°C \nHumidity: {humidity}% \nMotion: {'Detected' if motion else 'None'}
        """
        if video_path:
            payload += f"\nVideo saved to: {video_path}"

        # Print and publish
        print(payload.strip())
        client.publish(topic, payload.strip())

        # Delay
        time.sleep(5 if motion else 2)

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
    client.disconnect()
