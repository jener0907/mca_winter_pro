# import requests
# import time
# import random
# import subprocess

# class WiFiHandler:
#     """ESP-32 AP에 자동 연결"""

#     def __init__(self, esp32_ip="192.168.4.1", ssid="SOJU_Dispenser", password="12345678"):
#         self.esp32_ip = esp32_ip
#         self.ssid = ssid
#         self.password = password

#     def is_already_connected(self):
#         """현재 ESP32 Wi-Fi에 연결되어 있는지 확인"""
#         try:
#             result = subprocess.run(["nmcli", "-t", "-f", "active,ssid", "connection", "show", "--active"], capture_output=True, text=True)
#             active_connections = result.stdout.strip().split("\n")

#             for conn in active_connections:
#                 if conn.startswith("yes:") and self.ssid in conn:
#                     print(f"📡 Already connected to {self.ssid}")
#                     return True
#             return False
#         except Exception as e:
#             print(f"⚠️ Error checking Wi-Fi connection: {e}")
#             return False

#     def connect_to_esp32(self):
#         """ESP-32 AP에 자동 연결 (이미 연결되어 있으면 건너뜀)"""
#         if self.is_already_connected():
#             return True  # 이미 연결됨, 추가 연결 필요 없음

#         try:
#             print(f"🔄 Trying to connect to ESP32 Wi-Fi: {self.ssid}")
#             result = subprocess.run(["nmcli", "dev", "wifi", "connect", self.ssid, "password", self.password], capture_output=True, text=True)
            
#             if result.returncode == 0:
#                 print(f"✅ Successfully connected to {self.ssid}")
#                 return True
#             else:
#                 print(f"⚠️ Connection failed: {result.stderr}")
#                 return False
#         except Exception as e:
#             print(f"🚨 Wi-Fi connection error: {e}")
#             return False

#     def send_command(self, command):
#         """ESP-32로 HTTP 요청을 보내는 함수"""
#         try:
#             url = f"http://{self.esp32_ip}/motor?cup={command}"
#             response = requests.get(url, timeout=2)  # 요청 타임아웃 추가
#             if response.status_code == 200:
#                 print(f"✅ Sent command: {command}")
#             else:
#                 print(f"⚠️ Failed to send command {command}: {response.status_code}")
#         except requests.exceptions.RequestException as e:
#             print(f"🚨 Error sending command: {e}")

# class RandomValueGenerator:
#     """랜덤 값(A, B, C) 생성 클래스"""

#     def generate(self):
#         return random.choice(["A", "B", "C"])

# class SignalProcessor:
#     """랜덤 값을 생성하고 ESP-32로 전송하는 클래스"""

#     def __init__(self, wifi_handler, value_generator):
#         self.wifi_handler = wifi_handler
#         self.value_generator = value_generator

#     def process_signal(self):
#         """랜덤 값을 생성하고 ESP-32로 전송"""
#         command = self.value_generator.generate()
#         self.wifi_handler.send_command(command)
#         print(f"📡 Sent to ESP-32: {command}")


import subprocess
import time

SSID = "SOJU_Dispenser"
PASSWORD = "12345678"

def get_current_wifi():
    """현재 연결된 Wi-Fi SSID 확인"""
    try:
        result = subprocess.run(["nmcli", "-t", "-f", "active,ssid", "connection", "show", "--active"],
                                capture_output=True, text=True)
        active_connections = result.stdout.strip().split("\n")

        for conn in active_connections:
            if conn.startswith("yes:"):
                ssid = conn.split(":")[1]
                return ssid
    except Exception as e:
        print(f"🚨 Wi-Fi 조회 오류: {e}")
    return None  # 연결된 Wi-Fi 없음

def connect_to_wifi():
    """SOJU_Dispenser에 연결 시도"""
    print(f"🔄 연결 시도 중... ({SSID})")

    # 기존 연결 제거 (필요할 경우)
    subprocess.run(["sudo", "nmcli", "connection", "down", SSID], capture_output=True, text=True)
    subprocess.run(["sudo", "nmcli", "connection", "delete", SSID], capture_output=True, text=True)

    connect_result = subprocess.run(
        ["sudo", "nmcli", "dev", "wifi", "connect", SSID, "password", PASSWORD],
        capture_output=True, text=True, timeout=10
    )

    if connect_result.returncode == 0:
        print(f"✅ 연결 완료! ({SSID})")
        return True
    else:
        print(f"⚠️ 연결 실패: {connect_result.stderr}")
        return False

# 현재 Wi-Fi 확인 후 연결
current_wifi = get_current_wifi()

if current_wifi == SSID:
    print(f"📡 OK - 이미 {SSID}에 연결됨!")
else:
    print(f"⚠️ {SSID}에 연결되지 않음. 연결을 시도합니다...")
    if connect_to_wifi():
        print(f"🎉 석세스! {SSID}에 연결됨!")
    else:
        print("🚨 연결 실패. 다시 시도하세요.")
