# status_manager.py
import time
import cv2
import numpy as np
import threading
import RPi.GPIO as GPIO
from qr_scanner import QRScanner
from qr_data_manager import QRDataManager
from audio_player import AudioPlayer
from wifi_processor import WiFiProcessor
from motor_controller import MotorController

class StatusManager:
    """시스템 전체 상태 및 게임 흐름을 관리하는 중앙 제어 장치"""
    
    # 시스템 상태 코드
    STATUS_DISCONNECTED = 0    # ESP32와 연결 안됨
    STATUS_CONNECTED = 1       # ESP32와 연결됨, 게임 대기 중
    STATUS_GAME_RUNNING = 2    # 게임 진행 중
    STATUS_TRACKING = 3        # QR 코드 추적 중
    
    # GPIO 핀 설정
    LED_PIN = 18  # LED 제어용 GPIO 핀 (PWM 지원)
    BUTTON_PIN = 23  # 게임 시작 버튼 GPIO 핀
    
    def __init__(self, show_display=False):
        """
        초기화
        :param show_display: 디스플레이 출력 여부 (개발 모드에서만 True)
        """
        self.current_status = self.STATUS_DISCONNECTED
        self.show_display = show_display
        self.game_mode = "random"
        self.selected_qr = None
        self.led_blinking = False
        self.button_pressed = False
        
        # GPIO 설정
        self.setup_gpio()
        
        # 모듈 초기화
        self.wifi = WiFiProcessor(status_manager=self)
        self.qr_scanner = QRScanner(show_display=self.show_display)
        self.qr_manager = QRDataManager()
        self.motor = MotorController(pin_a=12, pin_b=13)  # PWM 지원 핀 사용
        
        # 오디오 파일 경로 설정
        audio_files = {
            "Player_Number_001": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/001_eliminated.mp3",
            "Player_Number_002": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/002_eliminated.mp3",
            "Player_Number_003": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/003_eliminated.mp3",
            "Player_Number_004": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/004_eliminated.mp3",
            "Player_Number_005": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/005_eliminated.mp3",
            "Player_Number_006": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/006_eliminated.mp3",
            "Player_Number_007": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/007_eliminated.mp3",
            "Player_Number_008": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/008_eliminated.mp3",
            "Player_Number_009": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/009_eliminated.mp3",
            "Player_Number_010": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/010_eliminated.mp3",
            "Player_Number_456": "/home/pi/Desktop/jener/winter_project/Player_eliminated_sound/456_eliminated.mp3",
            
            # 게임 사운드
            "Way_Back_then": "/home/pi/Desktop/jener/winter_project/game_sounds/Way_Back_then.mp3",
            "game_start": "/home/pi/Desktop/jener/winter_project/game_sounds/game_start.mp3",
    
            # 컵 크기 관련 사운드
            "A": "/home/pi/Desktop/jener/winter_project/game_sounds/A.mp3",
            "B": "/home/pi/Desktop/jener/winter_project/game_sounds/B.mp3",
            "C": "/home/pi/Desktop/jener/winter_project/game_sounds/C.mp3",
        }
        self.audio_player = AudioPlayer(audio_files)
        
        # 게임 설정
        self.qr_capture_duration = 20  # QR 코드 인식 지속 시간 (초)
        self.tracking_duration = 10  # QR 코드 추적 지속 시간 (초)
        self.tracking_timeout = 3  # QR 코드가 사라진 후 추적 중단까지의 시간 (초)
        
        # 초기 연결 확인
        self.check_connection()
    
    def setup_gpio(self):
        """GPIO 핀 설정"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # LED 핀 설정
        GPIO.setup(self.LED_PIN, GPIO.OUT)
        GPIO.output(self.LED_PIN, GPIO.LOW)  # 초기 상태: 꺼짐
        
        # 버튼 핀 설정 (풀업 저항 사용)
        GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.BUTTON_PIN, GPIO.FALLING, 
                             callback=self.button_callback, bouncetime=300)
    
    def button_callback(self, channel):
        """버튼 누름 이벤트 처리"""
        if self.current_status == self.STATUS_CONNECTED:
            print("🔘 버튼이 눌렸습니다! 게임을 시작합니다.")
            self.button_pressed = True
            self.start_game()
        elif self.current_status in [self.STATUS_GAME_RUNNING, self.STATUS_TRACKING]:
            print("🔘 버튼이 눌렸습니다! 게임을 중단합니다.")
            self.button_pressed = True
            self.stop_game()
    
    def check_connection(self):
        """ESP32 연결 상태 확인"""
        is_connected = self.wifi.check_connection()
        self.update_status(self.STATUS_CONNECTED if is_connected else self.STATUS_DISCONNECTED)
        return is_connected
    
    def update_status(self, new_status):
        """
        상태 업데이트 및 LED 제어
        :param new_status: 새로운 상태 코드
        """
        if self.current_status == new_status:
            return  # 상태 변경 없음
            
        self.current_status = new_status
        
        # LED 상태 업데이트
        if new_status == self.STATUS_DISCONNECTED:
            self.stop_led_blinking()
            GPIO.output(self.LED_PIN, GPIO.LOW)  # LED 꺼짐
        elif new_status == self.STATUS_CONNECTED:
            self.stop_led_blinking()
            GPIO.output(self.LED_PIN, GPIO.HIGH)  # LED 켜짐
        elif new_status in [self.STATUS_GAME_RUNNING, self.STATUS_TRACKING]:
            self.start_led_blinking()  # LED 깜빡임
    
    def on_connection_established(self):
        """ESP32 연결 수립 시 호출되는 콜백"""
        print("📡 ESP32와 연결되었습니다.")
        self.update_status(self.STATUS_CONNECTED)
    
    def on_connection_lost(self):
        """ESP32 연결 해제 시 호출되는 콜백"""
        print("📡 ESP32와 연결이 끊어졌습니다.")
        self.update_status(self.STATUS_DISCONNECTED)
    
    def start_game(self, mode="random"):
        """
        게임 시작
        :param mode: 게임 모드 ('random')
        """
        if not self.check_connection():
            print("⚠️ ESP32와 연결되지 않아 게임을 시작할 수 없습니다.")
            return False
        
        # 이미 게임이 진행 중인 경우
        if self.current_status in [self.STATUS_GAME_RUNNING, self.STATUS_TRACKING]:
            print("⚠️ 게임이 이미 진행 중입니다.")
            return False
        
        print("🎮 게임을 시작합니다...")
        self.game_mode = mode
        self.update_status(self.STATUS_GAME_RUNNING)
        
        # 컵 크기 선택 (랜덤)
        cup_size = self.wifi.get_random_cup()  # 랜덤 선택
        print(f"🎲 랜덤 선택: {cup_size}")
        
        # 소주 디스펜서 명령 전송
        self.wifi.send_command(cup_size)
        
        # 게임 시퀀스 시작 (별도 스레드로 실행)
        game_thread = threading.Thread(target=self._game_sequence, args=(cup_size,))
        game_thread.daemon = True
        game_thread.start()
        
        return True
    
    def _game_sequence(self, cup_size):
        """
        게임 시퀀스 실행 (별도 스레드)
        :param cup_size: 선택된 컵 크기 ('A', 'B', 'C')
        """
        try:
            # 1. 컵 크기에 해당하는 음성 재생
            if cup_size in self.audio_player.audio_files:
                self.audio_player.play_audio(cup_size)
                time.sleep(2)
            
            # 2. 게임 시작 안내 방송 + 배경 음악
            self.audio_player.play_audio("game_start")
            time.sleep(5)
            self.audio_player.play_background_music("Way_Back_then")
            
            # 3. QR 코드 스캔 시작
            self.qr_manager.clear_data()
            scan_start_time = time.time()
            
            print("📷 QR 코드 스캔 시작...")
            while time.time() - scan_start_time < self.qr_capture_duration:
                # 게임이 중단되었는지 확인
                if self.current_status != self.STATUS_GAME_RUNNING:
                    return
                
                frame = self.qr_scanner.get_frame()
                if frame is None:
                    continue
                
                decoded_objects = self.qr_scanner.decode_qr(frame)
                for obj in decoded_objects:
                    qr_data = obj.data.decode('utf-8')
                    self.qr_manager.add_data(qr_data)
                    print(f"✅ QR 코드 감지: {qr_data}")
                
                if self.show_display:
                    self.qr_scanner.display_frame(frame, decoded_objects)
                
                time.sleep(0.1)  # CPU 사용량 감소
            
            # 4. QR 코드 랜덤 선택
            self.selected_qr = self.qr_manager.get_random_data()
            
            if not self.selected_qr:
                print("⚠️ 감지된 QR 코드가 없습니다.")
                self.stop_game()
                return
            
            print(f"🎯 선택된 타겟: {self.selected_qr}")
            
            # 5. 선택된 QR 코드 추적 시작
            self.start_tracking()
            
        except Exception as e:
            print(f"🚨 게임 시퀀스 오류: {e}")
            self.stop_game()
    
    def start_tracking(self):
        """선택된 QR 코드 추적 시작"""
        if not self.selected_qr:
            print("⚠️ 추적할 QR 코드가 선택되지 않았습니다.")
            self.stop_game()
            return
        
        self.update_status(self.STATUS_TRACKING)
        print(f"🔍 QR 코드 추적 시작: {self.selected_qr}")
        
        # 추적 시작 시 배경 음악 중지
        self.audio_player.stop_background_music()
        
        # 추적 시간 설정
        tracking_start_time = time.time()
        last_detection_time = tracking_start_time
        
        while time.time() - tracking_start_time < self.tracking_duration:
            # 게임이 중단되었는지 확인
            if self.current_status != self.STATUS_TRACKING:
                self.motor.stop()  # 모터 정지
                return
            
            frame = self.qr_scanner.get_frame()
            if frame is None:
                continue
            
            decoded_objects = self.qr_scanner.decode_qr(frame)
            target_found = False
            
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                if qr_data == self.selected_qr:
                    target_found = True
                    last_detection_time = time.time()
                    
                    # QR 코드 위치 정보 얻기 (pyzbar의 polygon 속성 사용)
                    points = obj.polygon
                    if len(points) > 0:
                        # 중심점 계산
                        x_sum = sum(point[0] for point in points)
                        y_sum = sum(point[1] for point in points)
                        center_x = x_sum / len(points)
                        center_y = y_sum / len(points)
                        
                        # 모터 제어
                        self.motor.adjust_for_qr_position(center_x, frame.shape[1])
                    break
            
            # QR 코드가 사라진 후 일정 시간이 지나면 추적 중단
            if not target_found:
                if time.time() - last_detection_time > self.tracking_timeout:
                    print(f"⚠️ 타겟이 {self.tracking_timeout}초 이상 감지되지 않아 추적을 중단합니다.")
                    self.motor.stop()  # 모터 정지
                    break
            
            if self.show_display:
                self.qr_scanner.display_frame(frame, decoded_objects)
            
            time.sleep(0.1)  # CPU 사용량 감소
        
        # 추적 종료, 모터 정지
        self.motor.stop()
        
        # 탈락자 호명 전 배경 음악 중지 (이미 중지되었지만 명확성을 위해)
        self.audio_player.stop_background_music()
        
        # 탈락자 호명
        print(f"🔊 탈락자 호명: {self.selected_qr}")
        self.audio_player.play_audio(self.selected_qr)
        
        # 효과음 재생 완료 대기
        if hasattr(self.audio_player, 'effect_thread') and self.audio_player.effect_thread:
            self.audio_player.effect_thread.join()  # 효과음 재생 완료 대기
        
        # 게임 종료
        self.stop_game()
    
    def stop_game(self):
        """게임 중지"""
        # 이미 게임이 중지된 상태인 경우
        if self.current_status not in [self.STATUS_GAME_RUNNING, self.STATUS_TRACKING]:
            return
        
        print("🛑 게임을 중지합니다...")
        
        # 모터 정지
        self.motor.stop()
        
        # 배경 음악 중지
        self.audio_player.stop_background_music()
        
        # 모터 정지 명령 전송
        self.wifi.send_command('STOP')
        
        # 상태 업데이트
        if self.check_connection():
            self.update_status(self.STATUS_CONNECTED)
        else:
            self.update_status(self.STATUS_DISCONNECTED)
    
    # LED 제어 메서드
    def start_led_blinking(self):
        """LED 깜빡임 시작"""
        if hasattr(self, 'led_blinking') and self.led_blinking:
            return  # 이미 깜빡이는 중
            
        self.led_blinking = True
        self.led_thread = threading.Thread(target=self._blink_led)
        self.led_thread.daemon = True
        self.led_thread.start()
    
    def stop_led_blinking(self):
        """LED 깜빡임 중지"""
        if hasattr(self, 'led_blinking'):
            self.led_blinking = False
            
        if hasattr(self, 'led_thread') and self.led_thread.is_alive():
            self.led_thread.join(timeout=1.0)
    
    def _blink_led(self):
        """LED 깜빡임 스레드 함수"""
        while hasattr(self, 'led_blinking') and self.led_blinking:
            GPIO.output(self.LED_PIN, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(self.LED_PIN, GPIO.LOW)
            time.sleep(0.5)
    
    def run(self):
        """메인 루프 실행"""
        print("🚀 시스템 실행 중... (Ctrl+C로 종료)")
        
        try:
            while True:
                # 버튼 입력 확인은 GPIO 이벤트로 처리되므로 여기서는 생략
                
                # 개발 모드에서 키보드 입력 처리
                if self.show_display:
                    key = cv2.waitKey(1) & 0xFF
                    
                    if key == ord(' '):  # 스페이스바: 게임 시작
                        if self.current_status == self.STATUS_CONNECTED:
                            self.start_game()
                    
                    elif key == ord('s'):  # 's' 키: 게임 중지
                        self.stop_game()
                    
                    elif key == 27:  # ESC: 종료
                        break
                
                time.sleep(0.1)  # CPU 사용량 감소
        
        except KeyboardInterrupt:
            print("\n프로그램 종료...")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """자원 해제"""
        print("🧹 자원을 정리합니다...")
        self.stop_led_blinking()
        self.audio_player.stop_background_music()
        self.motor.cleanup()  # 모터 자원 해제
        self.qr_scanner.release()
        GPIO.cleanup()
