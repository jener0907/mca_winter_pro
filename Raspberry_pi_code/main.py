# source /home/pi/Desktop/jener/winter_project/qr_pro1/bin/activate
# deactivate
# /bin/python /home/pi/Desktop/jener/winter_project/main.py
# https://github.com/jener0907/mca_winter_pro
# https://github.com/jener0907/mca_winter_pro/tree/main/Raspberry%20pi_code

# main.py
import time
import sys
from status_manager import StatusManager

if __name__ == "__main__":
    try:
        # 명령줄 인자로 개발 모드 여부 결정 (기본: 운영 모드)
        show_display = "--dev" in sys.argv
        
        if show_display:
            print("🔧 개발 모드로 실행합니다. (디스플레이 활성화)")
        else:
            print("🚀 운영 모드로 실행합니다. (디스플레이 비활성화)")
        
        # StatusManager 인스턴스 생성 및 실행
        manager = StatusManager(show_display=show_display)
        
        # 시스템 준비 완료 메시지
        print("✅ MCA 소주 디스펜서 시스템이 준비되었습니다.")
        print("🎮 버튼을 눌러 게임을 시작하세요.")
        
        # 메인 루프 실행
        manager.run()
        
    except Exception as e:
        print(f"🚨 오류 발생: {e}")
        
        # 심각한 오류 발생 시 재시작 (선택 사항)
        print("⚠️ 시스템을 재시작합니다...")
        time.sleep(3)
        
        # 프로세스 종료 (systemd 등으로 관리 중이라면 자동 재시작됨)
        sys.exit(1)
