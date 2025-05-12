
#!/usr/bin/env python3

import os
import time
import json
import ssl
import board
import busio
import subprocess
import adafruit_ahtx0
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from datetime import datetime
import hashlib

# === GPIO PIR Setup ===
PIR_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# === AHT20 Sensor Setup ===
i2c = busio.I2C(board.SCL, board.SDA)
aht20 = adafruit_ahtx0.AHTx0(i2c)

# === MQTT Config ===
broker_address = "rpibroker"
broker_port = 8883
topic = "sensors/motion"

# TLS certificate paths
ca_cert = "/home/shine/mqtt-certs/ca.crt"
client_cert = "/home/shine/mqtt-certs/rpi1.crt"
client_key = "/home/shine/mqtt-certs/rpi1.key"

# === TLS Setup ===
client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
client_context.minimum_version = ssl.TLSVersion.TLSv1_3
client_context.maximum_version = ssl.TLSVersion.TLSv1_3
client_context.load_verify_locations(cafile=ca_cert)
client_context.load_cert_chain(certfile=client_cert, keyfile=client_key)
client_context.check_hostname = True

client = mqtt.Client()
client.tls_set_context(client_context)

# MQTT Broker Connection
try:
    client.connect(broker_address, broker_port)
    print("Connected to MQTT broker with TLS 1.3")
except Exception as e:
    print("MQTT connection failed:", e)
    GPIO.cleanup()
    exit(1)

# === Video Directory ===
video_dir = "/home/shine/videos"
os.makedirs(video_dir, exist_ok=True)

# === SHA-256 Hash Function ===
def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None

print("System running...")

try:
    while True:
        temperature = round(aht20.temperature, 2)
        humidity = round(aht20.relative_humidity, 2)
        motion = GPIO.input(PIR_PIN) == GPIO.HIGH
        video_filename = None
        video_hash = None

        if motion:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_filename = f"motion_{timestamp}.mp4"
            video_path = os.path.join(video_dir, video_filename)

            print(f"Motion detected! Recording to {video_filename}")

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

            # SHA-256 hash after video is saved
            video_hash = compute_sha256(video_path)

        # === JSON Payload ===
        payload = {
            "timestamp": datetime.now().isoformat(),
            "temperature_C": temperature,
            "humidity_percent": humidity,
            "motion_detected": motion,
            "video_filename": video_filename if video_filename else None,
            "video_hash": video_hash if video_hash else None
        }

        client.publish(topic, json.dumps(payload))
        print("Published:", json.dumps(payload, indent=2))

        # Sleep to reduce load
        time.sleep(5 if motion else 2)

except KeyboardInterrupt:
    print("Shutting down...")

finally:
    GPIO.cleanup()
    client.disconnect()
