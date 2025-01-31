import serial
import time
import random

class BluetoothHandler:
    """ESP-32와 블루투스 시리얼 통신을 처리하는 클래스"""

    def __init__(self, port="/dev/rfcomm0", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None

    def connect(self):
        """블루투스 연결 시도"""
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"Connected to ESP-32 on {self.port} at {self.baudrate} baud.")
        except serial.SerialException as e:
            print(f"Bluetooth connection failed: {e}")

    def send_command(self, command):
        """ESP-32로 명령 전송"""
        if self.serial_conn:
            self.serial_conn.write(f"{command}\n".encode('utf-8'))
            print(f"Sent command: {command}")

    def receive_response(self):
        """ESP-32에서 응답 수신"""
        if self.serial_conn:
            response = self.serial_conn.readline().decode('utf-8').strip()
            return response if response else None

    def close(self):
        """블루투스 연결 종료"""
        if self.serial_conn:
            self.serial_conn.close()
            print("Bluetooth connection closed.")

class RandomValueGenerator:
    """랜덤 값(A, B, C) 생성 클래스"""

    def generate(self):
        return random.choice(["A", "B", "C"])

class SignalProcessor:
    """랜덤 값을 생성하고 ESP-32로 전송하는 클래스"""

    def __init__(self, bluetooth_handler, value_generator):
        self.bluetooth_handler = bluetooth_handler
        self.value_generator = value_generator

    def process_signal(self):
        """랜덤 값을 생성하고 ESP-32로 전송"""
        command = self.value_generator.generate()
        self.bluetooth_handler.send_command(command)
        print(f"Sent to ESP-32: {command}")



# # --- main.py에서 사용할 코드 ---
# if __name__ == "__main__":
#     # 블루투스 핸들러 초기화
#     bluetooth_handler = BluetoothHandler()
#     bluetooth_handler.connect()

#     # 랜덤 값 생성기 초기화 (기본 확률 사용)
#     value_generator = RandomValueGenerator()

#     # 신호 프로세서 초기화
#     signal_processor = SignalProcessor(bluetooth_handler, value_generator)

#     try:
#         print("Waiting for signals. Press Ctrl+C to stop.")
#         while True:
#             # 시뮬레이션: 신호 감지 (여기서는 5초마다 신호가 발생한다고 가정)
#             time.sleep(5)
#             signal_processor.process_signal()

#     except KeyboardInterrupt:
#         print("Program stopped by user.")

#     finally:
#         bluetooth_handler.close()
