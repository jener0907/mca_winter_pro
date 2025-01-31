from playsound import playsound

class AudioPlayer:
    """오디오 파일 재생을 담당하는 클래스"""

    def __init__(self, audio_files):
        """
        오디오 파일 매핑 초기화
        :param audio_files: QR 데이터와 매핑된 오디오 파일 딕셔너리
        """
        self.audio_files = audio_files

    def play_audio(self, data):
        """
        데이터에 매핑된 오디오 파일 재생
        :param data: QR 데이터
        """
        if data in self.audio_files:
            playsound(self.audio_files[data])
        else:
            print(f"No audio file mapped for {data}")
