# source /home/pi/Desktop/jener/winter_project/qr_pro1/bin/activate
# deactivate
# /bin/python /home/pi/Desktop/jener/winter_project/main.py
# https://github.com/jener0907/mca_winter_pro

import time
import cv2
import numpy as np
from qr_scanner import QRScanner
from qr_data_manager import QRDataManager
from audio_player import AudioPlayer
from BT_processor import BluetoothHandler, RandomValueGenerator, SignalProcessor

class MainApp:
    """QR 코드 스캔, 데이터 처리, 오디오 재생, 블루투스 통신을 통합 관리"""

    def __init__(self):
        """필요한 클래스 초기화"""
        self.scanner = QRScanner()
        self.data_manager = QRDataManager()
        self.audio_player = AudioPlayer({
            "Player_Number_001": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/001_eliminated.mp3",
            "Player_Number_002": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/002_eliminated.mp3",
            "Player_Number_003": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/003_eliminated.mp3",
            "Player_Number_004": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/004_eliminated.mp3",
        })
        
        # 🔵 블루투스 자동 연결
        self.bluetooth_handler = BluetoothHandler()
        self.bluetooth_handler.connect()
        self.value_generator = RandomValueGenerator()
        self.signal_processor = SignalProcessor(self.bluetooth_handler, self.value_generator)

        # 🔳 OpenCV 창 강제 오픈
        cv2.namedWindow("QR Code Scanner", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("QR Code Scanner", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("QR Code Scanner", 255 * np.ones((480, 640, 3), dtype=np.uint8))
        cv2.waitKey(1)  # 창이 뜨도록 대기

        # 데이터 수집 관련 설정
        self.qr_capture_duration = 5  # QR 코드 인식 지속 시간 (초)
        self.start_time = None

    def run(self):
        """메인 루프 실행"""
        print("Press Spacebar to start the sequence. Press ESC to exit.")
        
        while True:  # 🔄 **무한 루프 (게임 시퀀스 실행)**
            key = cv2.waitKey(1) & 0xFF  # 키 입력 대기

            if key == ord(' '):  # ✅ **스페이스바 입력 시 게임 시작**
                print(" Spacebar pressed! Starting sequence...")

                # 🎲 **랜덤 값 생성 및 ESP-32로 전송**
                self.signal_processor.process_signal()

                # ⏳ **2초 대기 후 해당 음성 파일 재생**
                time.sleep(2)
                # selected_command = self.value_generator.generate()
                # self.audio_player.play_audio(f"/home/pi/Desktop/jener/winter_project/game_sounds/{selected_command}.mp3")

                # 🔊 **게임 시작 알림 + 배경 음악**
                # self.audio_player.play_audio("/home/pi/Desktop/jener/winter_project/game_sounds/game_start.mp3")
                # self.audio_player.play_audio("/home/pi/Desktop/jener/winter_project/game_sounds/background_music.mp3")

                # 🎥 **QR 코드 인식 시작 (20초)**
                self.data_manager.clear_data()
                self.start_time = time.time()

                while time.time() - self.start_time < self.qr_capture_duration:
                    frame = self.scanner.get_frame()
                    if frame is None:
                        break

                    decoded_objects = self.scanner.decode_qr(frame)
                    for obj in decoded_objects:
                        qr_data = obj.data.decode('utf-8')
                        self.data_manager.add_data(qr_data)

                    self.scanner.display_frame(frame, decoded_objects)
                    cv2.waitKey(1)  # 화면 업데이트

                # 🎯 **랜덤으로 QR 코드 선택 & 음성 재생**
                qr_data_list = self.data_manager.qr_data_list
                if qr_data_list:
                    selected_qr = self.data_manager.get_random_data()
                    print(f"📢 Randomly selected player: {selected_qr}")
                    self.audio_player.play_audio(selected_qr)

            if key == 27:  # ✅ **ESC 입력 시 종료**
                print("❌ ESC pressed. Exiting program.")
                break  # 🔄 **while 루프 종료**

        self.scanner.release()  # 카메라 종료
        self.bluetooth_handler.close()  # 블루투스 종료
        cv2.destroyAllWindows()  # 모든 OpenCV 창 닫기

# ✅ **실행 코드**
if __name__ == "__main__":
    app = MainApp()  # 🎮 MainApp 인스턴스 생성
    app.run()  # 🏁 프로그램 실행






# import time
# import cv2
# from qr_scanner import QRScanner
# from qr_data_manager import QRDataManager
# from audio_player import AudioPlayer

# class MainApp:
#     """QR 코드 스캔, 데이터 처리, 오디오 재생을 통합 관리"""

#     def __init__(self):
#         """필요한 클래스 초기화"""
#         self.scanner = QRScanner()
#         self.data_manager = QRDataManager()
#         self.audio_player = AudioPlayer({
#             "Player_Number_001": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/001_eliminated.mp3",
#             "Player_Number_002": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/002_eliminated.mp3",
#             "Player_Number_003": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/003_eliminated.mp3",
#             "Player_Number_004": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/004_eliminated.mp3",
#         })
#         self.capture_duration = 3  # 데이터 수집 시간 (초)
#         self.start_time = None

#     def run(self):
#         """메인 루프 실행"""
#         while True:
#             frame = self.scanner.get_frame()
#             if frame is None:
#                 break

#             decoded_objects = self.scanner.decode_qr(frame)
#             for obj in decoded_objects:
#                 qr_data = obj.data.decode('utf-8')
#                 self.data_manager.add_data(qr_data)

#             self.scanner.display_frame(frame, decoded_objects)

#             key = cv2.waitKey(1) & 0xFF

#             if key == ord(' '):  # 스페이스바로 데이터 수집 시작
#                 # print("Data collection started.")
#                 self.data_manager.clear_data()
#                 self.start_time = time.time()

#             if self.start_time is not None:
#                 elapsed_time = time.time() - self.start_time
#                 if elapsed_time >= self.capture_duration:
#                     # print("Data collection ended.")
#                     qr_data_list = self.data_manager.qr_data_list
#                     # print(f"Collected QR Data: {qr_data_list}")

#                     selected_data = self.data_manager.get_random_data()
#                     if selected_data:
#                         # print(f"Randomly selected data: {selected_data}")
#                         self.audio_player.play_audio(selected_data)

#                     self.start_time = None

#             if key == 27:  # ESC 키로 종료
#                 break

#         self.scanner.release()


# if __name__ == "__main__":
#     app = MainApp()
#     app.run()
