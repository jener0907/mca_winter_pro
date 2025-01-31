import random

class QRDataManager:
    """QR 코드 데이터를 관리하는 클래스"""

    def __init__(self):
        """QR 데이터 리스트 초기화"""
        self.qr_data_list = []

    def add_data(self, data):
        """
        QR 데이터를 리스트에 추가 (중복 제외)
        :param data: QR 코드에서 읽은 데이터
        """
        if data not in self.qr_data_list:
            self.qr_data_list.append(data)

    def get_random_data(self):
        """
        QR 데이터 리스트에서 랜덤으로 데이터 하나를 선택
        :return: 선택된 데이터, 데이터가 없으면 None 반환
        """
        if self.qr_data_list:
            return random.choice(self.qr_data_list)
        return None

    def clear_data(self):
        """QR 데이터 리스트 초기화"""
        self.qr_data_list = []
