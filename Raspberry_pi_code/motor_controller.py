# motor_controller.py 구조
import RPi.GPIO as GPIO
import time

class MotorController:
    """L9110 모터 드라이버를 사용한 DC 모터 제어 클래스"""
    
    def __init__(self, pin_a=17, pin_b=18):
        """
        모터 컨트롤러 초기화
        :param pin_a: L9110의 A 입력 핀 (GPIO 번호)
        :param pin_b: L9110의 B 입력 핀 (GPIO 번호)
        """
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.current_speed = 0  # 현재 속도 (0-100)
        self.is_running = False
        self.setup_gpio()
        
    def setup_gpio(self):
        """GPIO 핀 설정"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_a, GPIO.OUT)
        GPIO.setup(self.pin_b, GPIO.OUT)
        
        # PWM 객체 생성 (주파수 1000Hz)
        self.pwm_a = GPIO.PWM(self.pin_a, 1000)
        self.pwm_b = GPIO.PWM(self.pin_b, 1000)
        
        # PWM 시작 (초기 듀티 사이클 0)
        self.pwm_a.start(0)
        self.pwm_b.start(0)
        
    def set_direction(self, direction, speed=50):
        """
        모터 방향 및 속도 설정
        :param direction: 'clockwise' 또는 'counterclockwise'
        :param speed: 모터 속도 (0-100)
        """
        self.current_speed = min(max(0, speed), 100)  # 속도 범위 제한 (0-100)
        self.is_running = self.current_speed > 0
        
        if direction == 'clockwise':
            self.pwm_a.ChangeDutyCycle(self.current_speed)
            self.pwm_b.ChangeDutyCycle(0)
        elif direction == 'counterclockwise':
            self.pwm_a.ChangeDutyCycle(0)
            self.pwm_b.ChangeDutyCycle(self.current_speed)
        else:
            self.stop()
    
    def adjust_for_qr_position(self, qr_x, frame_width):
        """
        QR 코드 위치에 따라 모터 방향 및 속도 조정
        :param qr_x: QR 코드의 X 좌표
        :param frame_width: 프레임 너비
        """
        # 프레임 중앙 계산
        center_x = frame_width / 2
        
        # 중앙으로부터의 거리 계산
        distance_from_center = qr_x - center_x
        
        # 거리에 따른 방향 결정
        if abs(distance_from_center) < 50:  # 중앙 근처에 있으면 정지
            self.stop()
            return
            
        # 거리에 따른 속도 계산 (거리가 멀수록 빠르게, 최대 70%)
        speed = min(30 + abs(distance_from_center) / 5, 70)
        
        if distance_from_center > 0:  # QR 코드가 오른쪽에 있음
            self.set_direction('clockwise', speed)
        else:  # QR 코드가 왼쪽에 있음
            self.set_direction('counterclockwise', speed)
    
    def stop(self):
        """모터 정지"""
        self.pwm_a.ChangeDutyCycle(0)
        self.pwm_b.ChangeDutyCycle(0)
        self.is_running = False
        self.current_speed = 0
    
    def cleanup(self):
        """GPIO 자원 해제"""
        self.stop()
        self.pwm_a.stop()
        self.pwm_b.stop()
        # GPIO.cleanup()  # 전체 GPIO 정리는 호출하지 않음 (다른 모듈에 영향)
