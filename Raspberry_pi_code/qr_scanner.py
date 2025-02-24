from picamera2 import Picamera2
import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar

class QRScanner:
    """PiCamera2를 이용한 QR 코드 스캐너"""

    def __init__(self, width=640, height=480, show_display=True):
        """
        카메라 및 전처리 설정 초기화
        :param width: 카메라 해상도 (기본값 640x480)
        :param height: 카메라 해상도
        :param show_display: 디스플레이 출력 여부 (True = 출력, False = 미출력)
        """
        self.picam2 = Picamera2()
        self.picam2.preview_configuration.main.size = (width, height)
        self.picam2.preview_configuration.main.format = "RGB888"
        self.picam2.configure("preview")
        self.picam2.start()

        self.show_display = show_display  # ✅ 디스플레이 출력 여부 설정

        # ✅ QR 인식률을 높이기 위한 전처리 설정 (튜닝 가능)
        self.preprocess_settings = {
            "brightness": 0.6,   # 밝기 조정 (1.0 = 기본값, 1.2 = 밝게)
            "contrast": 1.0,     # 대비 조정 (1.0 = 기본값, 1.5 = 강한 대비)
            "blur_kernel": (3, 3),  # 가우시안 블러 크기 (홀수 값만 가능)
            "adaptive_block_size": 101,  # ✅ 적응형 이진화 블록 크기 (홀수)
            "adaptive_C": 6  # ✅ 적응형 이진화 상수 (값이 클수록 더 밝게)
        }

        if self.show_display:
            # OpenCV 창 생성 (디스플레이 ON일 경우만)
            cv2.namedWindow("QR Code Scanner", cv2.WINDOW_NORMAL)
            # cv2.setWindowProperty("QR Code Scanner", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    def get_frame(self):
        """
        카메라에서 프레임을 가져와서 전처리 수행 후 반환
        :return: 전처리된 프레임 (이미지)
        """
        frame = self.picam2.capture_array()
        return self.preprocess_frame(frame)  # 전처리 적용 후 반환

    def preprocess_frame(self, frame):
        """
        QR 코드 인식을 위한 이미지 전처리 (밝기, 대비, 블러링, 적응형 이진화 적용)
        :param frame: 원본 이미지
        :return: 전처리된 이미지
        """
        settings = self.preprocess_settings

        # 🔵 1. 밝기 및 대비 조정
        adjusted = cv2.convertScaleAbs(frame, alpha=settings["contrast"], beta=settings["brightness"] * 50)

        # 🔵 2. 그레이스케일 변환
        gray = cv2.cvtColor(adjusted, cv2.COLOR_RGB2GRAY)

        # 🔵 3. 가우시안 블러 적용 (노이즈 제거)
        blurred = cv2.GaussianBlur(gray, settings["blur_kernel"], 0)

        # 🔵 4. 적응형 이진화 적용 (기존 고정값 이진화 → ✅ 적응형으로 개선)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
            settings["adaptive_block_size"], settings["adaptive_C"]
        )

        return thresh  # QR 코드 검출을 위해 이진화된 이미지 반환

    def decode_qr(self, frame):
        """
        QR 코드를 디코딩
        :param frame: 입력 프레임 (전처리된 이미지)
        :return: 디코딩된 QR 코드 객체 리스트
        """
        return pyzbar.decode(frame)

    def display_frame(self, frame, decoded_objects):
        """
        QR 코드를 화면에 출력 (show_display가 True일 때만)
        :param frame: 입력 프레임 (이미지)
        :param decoded_objects: 디코딩된 QR 코드 객체 리스트
        """
        if not self.show_display:  
            return  # 🔴 디스플레이 출력 OFF일 경우 생략

        for obj in decoded_objects:
            points = obj.polygon
            if len(points) > 4:
                hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                hull = list(map(tuple, np.squeeze(hull)))
            else:
                hull = points

            # QR 코드 경계선 그리기
            n = len(hull)
            for j in range(n):
                cv2.line(frame, hull[j], hull[(j + 1) % n], (255, 0, 0), 3)

            # QR 코드 데이터 화면 출력
            qr_data = obj.data.decode('utf-8')
            top_left = hull[0]
            cv2.putText(frame, qr_data, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)

        # ✅ 디스플레이에 프레임 출력 (show_display가 True일 경우만)
        cv2.imshow("QR Code Scanner", frame)
        cv2.waitKey(1)

    def release(self):
        """
        카메라 및 OpenCV 창 자원 해제
        """
        self.picam2.close()
        if self.show_display:
            cv2.destroyAllWindows()

# ✅ **단독 실행 테스트 모드**
if __name__ == "__main__":
    scanner = QRScanner(show_display=True)  # 🔵 디스플레이 ON/OFF 설정 가능

    print("📷 QR 코드 스캐너 실행 중... (ESC 키를 눌러 종료)")

    while True:
        frame = scanner.get_frame()
        if frame is None:
            print("🚨 카메라 프레임을 가져오지 못했습니다.")
            break

        decoded_objects = scanner.decode_qr(frame)

        if decoded_objects:
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                print(f"✅ 인식된 QR 코드: {qr_data}")

        scanner.display_frame(frame, decoded_objects)  # 🔵 디스플레이 출력 여부 확인

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC 키로 종료
            print("🛑 QR 스캐너 종료")
            break

    scanner.release()
