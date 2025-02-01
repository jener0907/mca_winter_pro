from playsound import playsound
import os

class AudioPlayer:
    """오디오 파일 재생을 담당하는 클래스"""

    def __init__(self, audio_files):
        """
        오디오 파일 매핑 초기화
        :param audio_files: QR 데이터와 매핑된 오디오 파일 딕셔너리
        """
        self.audio_files = audio_files  # 🔄 오디오 파일 매핑 저장

    def play_audio(self, data):
        """
        데이터에 매핑된 오디오 파일 재생
        :param data: QR 데이터
        """
        if data in self.audio_files:
            audio_file_path = self.audio_files[data]

            # 🔍 디버깅: 파일 경로 출력
            print(f"🎵 Attempting to play: {audio_file_path}")

            if os.path.exists(audio_file_path):
                try:
                    playsound(audio_file_path)
                    print("✅ Audio played successfully!")
                except Exception as e:
                    print(f"❌ Error while playing sound: {e}")
            else:
                print(f"⚠️ Warning: Audio file not found: {audio_file_path}")
        else:
            print(f"⚠️ Warning: No audio file mapped for {data}")
