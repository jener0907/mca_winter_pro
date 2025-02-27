import subprocess
import time

SSID = "SOJU_Dispenser"
PASSWORD = "12345678"

# def rescan_wifi():
#     while True:
#         print("Wi-Fi 스캔 실행 중...")
#         subprocess.run(["nmcli", "dev", "wifi", "rescan"], capture_output=True, text=True)
#         time.sleep(10)  # 10초마다 스캔 (필요시 조정)

# rescan_wifi()

def is_wifi_available():
    """SOJU_Dispenser가 Wi-Fi 목록에 있는지 확인"""
    result = subprocess.run(["nmcli", "-t", "-f", "ssid", "dev", "wifi"], capture_output=True, text=True)
    networks = result.stdout.strip().split("\n")
    return SSID in networks

def get_current_wifi():
    """현재 연결된 Wi-Fi SSID 확인"""
    result = subprocess.run(["nmcli", "-t", "-f", "active,ssid", "connection", "show", "--active"],
                            capture_output=True, text=True)
    active_connections = result.stdout.strip().split("\n")

    for conn in active_connections:
        if conn.startswith("yes:"):
            ssid = conn.split(":")[1]
            return ssid
    return None  # 연결된 Wi-Fi 없음

def is_ip_assigned():
    """Wi-Fi 연결 후 실제로 IP를 받았는지 확인"""
    result = subprocess.run(["hostname", "-I"], capture_output=True, text=True)
    return "192.168.4." in result.stdout  # ESP32 AP의 IP 대역인지 확인

def connect_to_wifi():
    """SOJU_Dispenser에 연결 시도"""
    if not is_wifi_available():
        print("SOJU_Dispenser가 감지되지 않음. Wi-Fi 검색을 다시 시도하세요.")
        return False

    print("Wi-Fi 연결 시도 중...")

    # 기존 연결이 끊겨 있으면 재설정 불필요
    subprocess.run(["sudo", "nmcli", "connection", "delete", SSID], capture_output=True, text=True)

    connect_result = subprocess.run(
        ["sudo", "nmcli", "dev", "wifi", "connect", SSID, "password", PASSWORD],
        capture_output=True, text=True, timeout=10
    )

    if connect_result.returncode == 0 and is_ip_assigned():
        print("Wi-Fi 연결 완료.")
        return True
    else:
        print("Wi-Fi 연결 실패.")
        return False

# 현재 Wi-Fi 상태 확인 후 연결 시도
current_wifi = get_current_wifi()

if current_wifi == SSID:
    print("이미 SOJU_Dispenser에 연결됨.")
elif connect_to_wifi():
    print("SOJU_Dispenser에 연결 성공.")
else:
    print("SOJU_Dispenser 연결 실패. 다시 시도하세요.")
import requests
import time
import threading

class WiFiProcessor:
    """ESP32 통신을 관리하는 클래스"""
    
    # ESP32 설정
    ESP32_IP = "192.168.4.1"
    
    def __init__(self, status_manager=None):
        """
        초기화
        :param status_manager: 상태 관리자 인스턴스 (선택 사항)
        """
        self.status_manager = status_manager
        self.is_connected = False
        self.last_command_time = 0
        
    def check_connection(self):
        """
        ESP32와의 연결 상태 확인
        :return: 연결 상태 (True/False)
        """
        try:
            # 간단한 HTTP 요청으로 연결 확인
            response = requests.get(f"http://{self.ESP32_IP}", timeout=2)
            if response.status_code == 200:
                if not self.is_connected:
                    print(f"✅ ESP32 연결 확인됨")
                    self.is_connected = True
                    if self.status_manager:
                        self.status_manager.on_connection_established()
                return True
        except requests.exceptions.RequestException:
            if self.is_connected:
                print("⚠️ ESP32 연결 실패")
                self.is_connected = False
                if self.status_manager:
                    self.status_manager.on_connection_lost()
            return False
            
        return self.is_connected
    
    def send_command(self, command):
        """
        ESP32에 명령 전송
        :param command: 'A'(반잔), 'B'(한잔), 'C'(풀잔), 'D'(연속), 'STOP'(정지)
        :return: 명령 전송 시도 여부
        """
        # 연결 확인 (선택적)
        self.check_connection()
        
        # 명령 전송 시도
        try:
            url = f"http://{self.ESP32_IP}/motor?cup={command}"
            requests.get(url, timeout=3)
            self.last_command_time = time.time()
            print(f"✅ 명령 전송: {command}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"🚨 명령 전송 실패: {e}")
            return False
    
    def get_random_cup(self):
        """
        A, B, C 중 랜덤으로 컵 크기 선택
        :return: 선택된 컵 크기 ('A', 'B', 'C' 중 하나)
        """
        import random
        return random.choice(['A', 'B', 'C'])

# 단독 실행 테스트
if __name__ == "__main__":
    try:
        # 상태 관리자 대신 간단한 콜백 함수 정의
        class SimpleStatusManager:
            def on_connection_established(self):
                print("🔔 연결 수립 이벤트 발생")
                
            def on_connection_lost(self):
                print("🔔 연결 해제 이벤트 발생")
        
        status_manager = SimpleStatusManager()
        wifi = WiFiProcessor(status_manager)
        
        # 초기 연결 확인
        if wifi.check_connection():
            print(f"📡 ESP32에 연결됨!")
        else:
            print(f"⚠️ ESP32에 연결할 수 없습니다.")
        
        print("🚀 WiFi 프로세서 실행 중... (명령어: a, b, c, d, stop, r(랜덤), exit)")
        
        # 간단한 명령 테스트
        while True:
            cmd = input("명령 입력: ").lower()
            
            if cmd == "a":
                wifi.send_command('A')
            elif cmd == "b":
                wifi.send_command('B')
            elif cmd == "c":
                wifi.send_command('C')
            elif cmd == "d":
                wifi.send_command('D')
            elif cmd == "stop":
                wifi.send_command('STOP')
            elif cmd == "r":
                cup = wifi.get_random_cup()
                print(f"🎲 랜덤 선택: {cup}")
                wifi.send_command(cup)
            elif cmd == "exit":
                break
            else:
                print("⚠️ 알 수 없는 명령입니다. (사용 가능: a, b, c, d, stop, r, exit)")
    
    except KeyboardInterrupt:
        print("\n프로그램 종료...")

sudo nano /etc/default/crda