#!/bin/bash

ESP32_MAC="3C:61:05:17:81:A2"  # 🔹 여기에 ESP32의 실제 MAC 주소 입력

echo "Connecting to $ESP32_MAC..."
bluetoothctl trust $ESP32_MAC
bluetoothctl pair $ESP32_MAC
bluetoothctl connect $ESP32_MAC

# RFCOMM 바인딩을 설정
sudo rfcomm bind 0 $ESP32_MAC
