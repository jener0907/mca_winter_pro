# BT_processor.py
import time
import subprocess
import os
import threading
import random

class BluetoothSpeakerServer:
    """라즈베리파이를 블루투스 스피커로 설정하는 클래스"""
    
    def __init__(self, device_name="MCA_Soju_Speaker"):
        """
        초기화
        :param device_name: 블루투스 장치 이름
        """
        self.device_name = device_name
        self.is_running = False
        self.is_connected = False
        self.bt_thread = None
        self.connected_device = None
    
    def setup(self):
        """블루투스 설정 초기화"""
        try:
            print("🔧 블루투스 설정 초기화 중...")
            
            # 필요한 패키지 확인
            required_packages = ["bluez", "bluez-tools", "pulseaudio", "pulseaudio-module-bluetooth"]
            self._check_packages(required_packages)
            
            # 블루투스 서비스 재시작
            subprocess.run(["sudo", "systemctl", "restart", "bluetooth"], check=True)
            time.sleep(2)
            
            # 디바이스 이름 설정
            subprocess.run(["sudo", "hciconfig", "hci0", "name", self.device_name], check=True)
            
            # A2DP 싱크 설정
            self._setup_a2dp_sink()
            
            print("✅ 블루투스 설정 완료")
            return True
            
        except Exception as e:
            print(f"⚠️ 블루투스 설정 오류: {e}")
            return False
    
    def _check_packages(self, packages):
        """필요한 패키지가 설치되어 있는지 확인"""
        for package in packages:
            result = subprocess.run(["dpkg", "-s", package], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True)
            if result.returncode != 0:
                print(f"⚠️ {package} 패키지가 설치되어 있지 않습니다. 설치가 필요합니다.")
                # 자동 설치는 하지 않음 (권한 문제 발생 가능)
    
    def _setup_a2dp_sink(self):
        """A2DP 싱크 프로파일 설정"""
        # PulseAudio 설정 파일 경로
        pa_path = "/etc/pulse/default.pa"
        
        # 백업 파일 생성 (처음 실행 시에만)
        if not os.path.exists(pa_path + ".bak"):
            subprocess.run(["sudo", "cp", pa_path, pa_path + ".bak"])
        
        # 설정 확인 및 추가
        with open(pa_path, "r") as f:
            content = f.read()
        
        # 필요한 설정이 없으면 추가
        if "module-bluetooth-discover" not in content:
            with open("/tmp/pulse_config", "w") as f:
                f.write(content + "\nload-module module-bluetooth-discover\n")
            subprocess.run(["sudo", "cp", "/tmp/pulse_config", pa_path])
        
        # PulseAudio 재시작
        subprocess.run(["pulseaudio", "-k"])
        time.sleep(1)
        subprocess.run(["pulseaudio", "--start"])
        time.sleep(2)
        
        # Bluetooth 설정
        self._configure_bluetooth()
    
    def _configure_bluetooth(self):
        """블루투스 가시성 및 페어링 설정"""
        commands = [
            "power on",
            "discoverable on",
            "pairable on",
            "agent on",
            "default-agent"
        ]
        
        for cmd in commands:
            subprocess.run(["bluetoothctl", cmd], check=True)
    
    def start(self):
        """블루투스 스피커 서비스 시작"""
        if self.is_running:
            print("⚠️ 블루투스 스피커 서비스가 이미 실행 중입니다.")
            return
        
        # 설정 초기화
        if not self.setup():
            print("⚠️ 블루투스 설정에 실패했습니다.")
            return
        
        # 블루투스 스피커 서비스 시작
        self.is_running = True
        self.bt_thread = threading.Thread(target=self._bluetooth_service)
        self.bt_thread.daemon = True
        self.bt_thread.start()
        
        print(f"🎵 블루투스 스피커 서비스 시작 ({self.device_name})")
        print("📱 이제 휴대폰에서 블루투스 기기를 검색하고 연결할 수 있습니다.")
        
        # 자동 재시작 비활성화
        self._disable_auto_restart()
    
    def _bluetooth_service(self):
        """블루투스 연결 모니터링 스레드"""
        while self.is_running:
            try:
                # 연결된 기기 확인
                info_process = subprocess.run(
                    ["bluetoothctl", "info"],
                    capture_output=True,
                    text=True
                )
                
                output = info_process.stdout
                was_connected = self.is_connected
                
                # 연결 상태 확인
                if "Connected: yes" in output:
                    # 기기 이름 추출
                    for line in output.split('\n'):
                        if "Name:" in line:
                            device_name = line.split("Name:")[1].strip()
                            self.connected_device = device_name
                            break
                    
                    self.is_connected = True
                    if not was_connected:
                        print(f"🔗 기기가 연결되었습니다: {self.connected_device}")
                else:
                    self.is_connected = False
                    if was_connected:
                        print("🔌 기기 연결이 해제되었습니다.")
                        self.connected_device = None
            
            except Exception as e:
                print(f"⚠️ 블루투스 모니터링 오류: {e}")
            
            time.sleep(5)  # 5초마다 확인
    
    def _disable_auto_restart(self):
        """자동 재시작 비활성화"""
        try:
            # 자동 재시작 스크립트 비활성화 (임시 파일 생성)
            with open("/tmp/bt_speaker_active", "w") as f:
                f.write("1")
            print("🛑 블루투스 스피커 활성화됨 - 자동 재시작 비활성화")
        except Exception as e:
            print(f"⚠️ 자동 재시작 비활성화 오류: {e}")
    
    def stop(self):
        """블루투스 스피커 서비스 중지"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # 연결 해제
        if self.is_connected:
            subprocess.run(["bluetoothctl", "disconnect"])
            self.is_connected = False
        
        # 블루투스 가시성 해제
        subprocess.run(["bluetoothctl", "discoverable", "off"])
        subprocess.run(["bluetoothctl", "pairable", "off"])
        
        # 스레드 종료 대기
        if self.bt_thread and self.bt_thread.is_alive():
            self.bt_thread.join(timeout=2.0)
        
        print("🛑 블루투스 스피커 서비스가 중지되었습니다.")
        
        # 자동 재시작 파일 제거
        if os.path.exists("/tmp/bt_speaker_active"):
            os.remove("/tmp/bt_speaker_active")
    
    def get_status(self):
        """현재 상태 정보 반환"""
        return {
            "running": self.is_running,
            "connected": self.is_connected,
            "device_name": self.device_name,
            "connected_device": self.connected_device
        }

# 기존 클래스들 유지
class RandomValueGenerator:
    """랜덤 값을 생성하는 클래스"""
    
    def generate(self):
        """A, B, C 중 랜덤 값 생성"""
        return random.choice(['A', 'B', 'C'])

class BluetoothHandler:
    """블루투스 통신 처리 클래스 (기존 코드)"""
    
    def __init__(self):
        # 기존 초기화 코드
        pass
        
    def connect(self):
        # 기존 연결 코드
        pass
        
    def close(self):
        # 기존 종료 코드
        pass

class SignalProcessor:
    """신호 처리 클래스 (기존 코드)"""
    
    def __init__(self, bt_handler, value_generator):
        self.bt_handler = bt_handler
        self.value_generator = value_generator
        
    def process_signal(self):
        # 기존 신호 처리 코드
        pass

# 단독 실행 테스트
if __name__ == "__main__":
    try:
        bt_speaker = BluetoothSpeakerServer(device_name="MCA_Soju_Speaker")
        bt_speaker.start()
        
        print("블루투스 스피커 서비스가 실행 중입니다. Ctrl+C로 종료할 수 있습니다.")
        
        while True:
            status = bt_speaker.get_status()
            if status["connected"]:
                print(f"연결된 기기: {status['connected_device']}")
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n프로그램 종료...")
        bt_speaker.stop()
