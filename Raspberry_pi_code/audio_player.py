import subprocess
import random
from playsound import playsound
import threading

class AudioPlayer:
    """배경 음악과 효과음을 총괄 관리하는 클래스"""

    def __init__(self, audio_files):
        """
        오디오 파일 매핑 초기화
        :param audio_files: 사운드 파일 매핑 딕셔너리
        """
        self.audio_files = audio_files
        self.music_process = None  # 배경 음악 실행 프로세스
        self.effect_thread = None  # 효과음 실행을 위한 스레드
        
        # 🔹 배경 음악 목록 저장
        self.background_tracks = [key for key in audio_files.keys() if "background" in key]

    def play_audio(self, sound_key):
        """
        효과음 또는 배경 음악을 자동 감지하여 재생
        :param sound_key: 오디오 파일 키 값
        """
        if sound_key not in self.audio_files:
            # print(f"⚠️ Warning: No audio file mapped for '{sound_key}'")
            return

        # 🎵 배경 음악인지 확인
        if sound_key in self.background_tracks:
            self.play_background_music(sound_key)
        else:
            self.play_effect(sound_key)

    def play_effect(self, sound_key):
        """
        효과음 재생 (비동기 실행으로 메인 프로그램 멈추지 않음)
        :param sound_key: 효과음 키 값
        """
        if sound_key in self.audio_files:
            # print(f"🎵 Playing effect: {self.audio_files[sound_key]}")
            
            # 🔹 playsound()를 별도 스레드에서 실행 (메인 프로그램 지연 방지)
            def play():
                playsound(self.audio_files[sound_key])

            self.effect_thread = threading.Thread(target=play)
            self.effect_thread.start()
        else:
            print(f"⚠️ Warning: No audio file mapped for '{sound_key}'")

    def play_background_music(self, sound_key):
        """
        배경 음악을 백그라운드에서 실행 (이미 실행 중이면 중복 실행 방지)
        :param sound_key: 배경 음악 키 값
        """
        if sound_key in self.audio_files:
            if self.music_process and self.music_process.poll() is None:
                # print("🎵 Background music already playing. Stopping previous track.")
                self.stop_background_music()

            # print(f"🎵 Playing background music: {self.audio_files[sound_key]}")
            self.music_process = subprocess.Popen(["mpg123", self.audio_files[sound_key]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print(f"⚠️ Warning: No background music file mapped for '{sound_key}'")

    def play_random_background_music(self):
        """
        배경 음악 리스트에서 랜덤 선택 후 재생
        """
        if self.background_tracks:
            selected_track = random.choice(self.background_tracks)
            # print(f"🎵 Random background music selected: {selected_track}")
            self.play_background_music(selected_track)
        else:
            print("⚠️ Warning: No background music tracks available!")

    def stop_background_music(self):
        """
        실행 중인 배경 음악을 종료
        """
        if self.music_process and self.music_process.poll() is None:
            self.music_process.terminate()
            # print("🛑 Background music stopped.")
