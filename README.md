# Secure Raspberry Pi-Based IoT System for Sensor Data Acquisition and Integrity Assurance


🔐 Secure IoT Sensor Node with Video Integrity Verification
This project presents the design and implementation of a secure, Raspberry Pi–based IoT sensor node for real-time environmental and motion monitoring. The system integrates multiple sensors:

🟢 PIR Motion Sensor for detecting movement

🌡️ AHT20 Temperature & Humidity Sensor via I2C

📷 USB Camera for capturing short video clips when motion is detected

Data is transmitted using the MQTT protocol secured with TLS 1.3 and mutual certificate-based authentication. All sensor readings are formatted in JSON and sent to a central MQTT broker (hosted on a laptop), where they are logged in real time.

To ensure the integrity of video recordings, the Raspberry Pi computes a SHA-256 hash for each motion-triggered video file. This hash is included in the MQTT payload, allowing the receiver to verify the authenticity of the video after it’s transferred via SCP.

The system is designed to be modular and scalable, supporting future extensions to a multi-node network. It also lays the groundwork for integration with neuromorphic computing models or anomaly detection algorithms for intelligent IoT and smart grid security applications.







