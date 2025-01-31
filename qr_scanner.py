import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np

class QRScanner:
    """QR 코드를 스캔하고 데이터를 처리하는 클래스"""

    def __init__(self, camera_index=0, width=640, height=480):
        """
        카메라 초기화 및 기본 설정
        :param camera_index: 사용할 카메라 인덱스 (기본값 0)
        :param width: 카메라 해상도 (너비)
        :param height: 카메라 해상도 (높이)
        """
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def get_frame(self):
        """
        카메라에서 프레임을 가져옵니다.
        :return: 읽은 프레임 (이미지), 실패 시 None 반환
        """
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def decode_qr(self, frame):
        """
        QR 코드를 디코딩합니다.
        :param frame: 입력 프레임 (이미지)
        :return: 디코딩된 QR 코드 객체 리스트
        """
        decoded_objects = pyzbar.decode(frame)
        return decoded_objects

    def display_frame(self, frame, decoded_objects):
        """
        QR 코드를 포함한 프레임을 화면에 표시합니다.
        :param frame: 입력 프레임 (이미지)
        :param decoded_objects: 디코딩된 QR 코드 객체 리스트
        """
        for obj in decoded_objects:
            points = obj.polygon
            # 점이 사각형 형태가 아니면 볼록 껍질(Convex Hull)을 계산
            if len(points) > 4:
                hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                hull = list(map(tuple, np.squeeze(hull)))
            else:
                hull = points
            # QR 코드의 테두리 그리기
            n = len(hull)
            for j in range(0, n):
                cv2.line(frame, hull[j], hull[(j + 1) % n], (255, 0, 0), 3)
            # QR 코드 데이터 화면에 출력
            qr_data = obj.data.decode('utf-8')
            top_left = hull[0]
            cv2.putText(frame, qr_data, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
        cv2.imshow("QR Code Scanner", frame)

    def release(self):
        """
        카메라와 화면 자원을 해제합니다.
        """
        self.cap.release()
        cv2.destroyAllWindows()
