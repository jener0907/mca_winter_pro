from playsound import playsound
import os

# 재생할 오디오 파일 경로 설정
audio_file_path = "/home/pi/Desktop/jener/winter_project/game_sounds/Way_Back_then.mp3"

# 🔍 파일이 존재하는지 확인
if os.path.exists(audio_file_path):
    print(f"🎵 Playing: {audio_file_path}")
    playsound(audio_file_path)
else:
    print(f"⚠️ Warning: Audio file not found: {audio_file_path}")
