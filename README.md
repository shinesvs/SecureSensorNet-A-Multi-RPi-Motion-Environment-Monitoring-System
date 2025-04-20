# SecureSensorNet-A-Multi-RPi-Motion-Environment-Monitoring-System

SecureSensorNet is a distributed multi-sensor monitoring system built using Raspberry Pi devices, designed for secure and coordinated data collection at the edge. Each Raspberry Pi node is equipped with different sensors (PIR motion, temperature/humidity, camera) and communicates securely over MQTT using TLS 1.3 encryption.

This system supports:

Real-time environmental sensing (temperature, humidity, motion)

Motion-triggered video recording and coordination across nodes

Secure MQTT communication using custom TLS certificates

Structured data publishing in JSON format

Centralized logging and CSV/JSON storage for ML-ready datasets

The project demonstrates a scalable and intelligent IoT edge solution suitable for smart environments, surveillance systems, or anomaly detection research.

 Hardware Setup
This project uses three Raspberry Pi nodes, each equipped with different sensors and peripherals. All nodes communicate over a shared Wi-Fi network using a secure MQTT protocol.

🧩 Node Configurations:
✅ Node 1: Motion Sensor Node
Device: Raspberry Pi 3B+/4

Sensor: PIR Motion Sensor (connected to GPIO17)

Functionality:

Detects motion and publishes alert messages to MQTT broker.

Triggers video recording on other nodes.

✅ Node 2: Environmental Sensor Node
Device: Raspberry Pi 3B+/4

Sensor: AHT20 (Temperature + Humidity) Sensor via I²C

Functionality:

Reads ambient temperature and humidity periodically.

Publishes environmental data with timestamps.

✅ Node 3: Camera Node
Device: Raspberry Pi with Camera Module or USB Webcam

Peripheral: /dev/video0 (e.g., USB webcam)

Functionality:

Subscribes to motion detection messages.

Records 10-second videos locally when motion is detected.

Publishes metadata about video events to MQTT broker.

🌐 Networking Setup
All Raspberry Pis are connected to the same local Wi-Fi network.

A central MQTT broker (hosted on a laptop or Raspberry Pi) facilitates secure communication.

TLS 1.3 is used for encrypted data exchange.

Devices are authenticated using client-side certificates.



