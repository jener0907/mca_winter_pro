#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>

// 📌 Wi-Fi AP 모드 설정
const char* apSSID = "SOJU_Dispenser";
const char* apPassword = "12345678";

// 📌 웹 서버 객체 생성
AsyncWebServer server(80);

// 📌 모터 드라이버 핀 설정
#define MOTOR_IN1 14  
#define MOTOR_IN2 15  

bool isMotorRunning = false;  // ✅ 모터 실행 여부
bool isContinuousMode = false; // ✅ 연속 추출 모드 여부

// 📌 모터 실행 Task (비동기 방식으로 실행)
void motorTask(void *pvParameters) {
    int duration = *(int*)pvParameters;
    delete (int*)pvParameters; // ✅ 동적 할당 해제

    isMotorRunning = true;
    Serial.println("🚀 모터 시작...");
    digitalWrite(MOTOR_IN1, HIGH);
    digitalWrite(MOTOR_IN2, LOW);

    vTaskDelay(duration / portTICK_PERIOD_MS); // ✅ 비동기 대기 (Watchdog 보호)

    digitalWrite(MOTOR_IN1, LOW);
    digitalWrite(MOTOR_IN2, LOW);
    Serial.println("🛑 모터 정지.");

    isMotorRunning = false;
    vTaskDelete(NULL); // ✅ Task 종료
}

// 📌 모터 작동 함수 (RTOS Task 기반 비동기 실행)
void startMotor(int duration) {
    if (isMotorRunning || isContinuousMode) return;
    xTaskCreatePinnedToCore(motorTask, "MotorTask", 2048, new int(duration), 1, NULL, 1);
}

// 📌 연속 추출 모드 실행 (버튼을 누르면 계속 작동)
void startContinuousMotor() {
    if (isMotorRunning) return;
    isMotorRunning = true;
    isContinuousMode = true;

    Serial.println("🚀 연속 추출 시작...");
    digitalWrite(MOTOR_IN1, HIGH);
    digitalWrite(MOTOR_IN2, LOW);
}

// 📌 정지 버튼 → 모든 동작 강제 정지
void stopAllMotors() {
    Serial.println("🛑 모든 동작 중지.");
    digitalWrite(MOTOR_IN1, LOW);
    digitalWrite(MOTOR_IN2, LOW);
    isMotorRunning = false;
    isContinuousMode = false;
}

void setup() {
    Serial.begin(115200);

    pinMode(MOTOR_IN1, OUTPUT);
    pinMode(MOTOR_IN2, OUTPUT);
    digitalWrite(MOTOR_IN1, LOW);
    digitalWrite(MOTOR_IN2, LOW);

    WiFi.mode(WIFI_AP);
    WiFi.softAP(apSSID, apPassword);
    WiFi.setSleep(false);  // 절전 모드 해제
    
    Serial.print("🌍 AP Mode IP: ");
    Serial.println(WiFi.softAPIP());

    // 📌 HTTP GET 요청을 통한 모터 제어
    server.on("/motor", HTTP_GET, [](AsyncWebServerRequest *request) {
        if (request->hasParam("cup")) {
            String cupSize = request->getParam("cup")->value();
            Serial.print("📩 받은 요청: ");
            Serial.println(cupSize);

            if (cupSize == "A") startMotor(3000);
            else if (cupSize == "B") startMotor(4000);
            else if (cupSize == "C") startMotor(4900);
            else if (cupSize == "D") startContinuousMotor();
            else if (cupSize == "STOP") stopAllMotors();
        }
        request->send(200, "text/plain", "OK");
    });


    // 📌 웹 UI 제공 (setup() 내부로 이동)
    server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send_P(200, "text/html; charset=UTF-8", R"rawliteral(
            <!DOCTYPE html>
            <html lang="ko">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
                <meta name="theme-color" content="#f5f6fa">
                <title>MCA 소주 디스펜서</title>
                <style>
                    :root {
                        --primary-color: #00a8ff;
                        --secondary-color: #273c75;
                        --accent-color: #e84118;
                        --light-color: #f5f6fa;
                        --dark-color: #2f3640;
                        --random-color: #9b59b6;
                        --background-gradient: linear-gradient(135deg, #f5f6fa, #dcdde1);
                    }
                    
                    /* 배경색 명시적 지정 */
                    html, body {
                        background-color: var(--light-color);
                        background: var(--background-gradient);
                        margin: 0;
                        padding: 0;
                        min-height: 100vh;
                        width: 100%;
                    }
                    
                    body {
                        font-family: 'Helvetica Neue', Arial, sans-serif;
                        color: var(--dark-color);
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                    }
                    
                    .page-wrapper {
                        background-color: var(--light-color);
                        background: var(--background-gradient);
                        min-height: 100vh;
                        width: 100%;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        padding: 20px 0;
                        box-sizing: border-box;
                    }
                    
                    .container {
                        max-width: 500px;
                        width: 90%;
                        background-color: white;
                        border-radius: 15px;
                        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
                        padding: 25px;
                        margin: 20px 0;
                    }
                    
                    h1 {
                        color: var(--secondary-color);
                        text-align: center;
                        margin-bottom: 5px;
                        font-size: 2.2rem;
                    }
                    
                    .subtitle {
                        color: var(--dark-color);
                        text-align: center;
                        margin-top: 0;
                        margin-bottom: 25px;
                        font-size: 1rem;
                        opacity: 0.7;
                    }
                    
                    .status-container {
                        background-color: var(--light-color);
                        border-radius: 8px;
                        padding: 12px;
                        margin: 15px 0;
                        text-align: center;
                    }
                    
                    .status {
                        font-size: 1.2rem;
                        font-weight: bold;
                        color: var(--secondary-color);
                        margin: 0;
                    }
                    
                    .btn-container {
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 15px;
                        margin-top: 20px;
                    }
                    
                    .btn {
                        font-size: 1.1rem;
                        padding: 15px 10px;
                        border: none;
                        border-radius: 10px;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        font-weight: bold;
                        text-align: center;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                    }
                    
                    .btn-small {
                        background-color: #ff7979;
                        color: white;
                    }
                    
                    .btn-medium {
                        background-color: #f0932b;
                        color: white;
                    }
                    
                    .btn-large {
                        background-color: #eb4d4b;
                        color: white;
                    }
                    
                    .btn-random {
                        background-color: var(--random-color);
                        color: white;
                    }
                    
                    .btn-extra {
                        background-color: var(--primary-color);
                        color: white;
                        grid-column: span 2;
                    }
                    
                    .btn-stop {
                        background-color: var(--dark-color);
                        color: white;
                        grid-column: span 2;
                    }
                    
                    .btn:hover:not(.disabled) {
                        transform: translateY(-3px);
                        box-shadow: 0 5px 10px rgba(0,0,0,0.2);
                    }
                    
                    .btn .emoji {
                        font-size: 1.8rem;
                        margin-bottom: 5px;
                    }
                    
                    .disabled {
                        opacity: 0.5;
                        cursor: not-allowed !important;
                        transform: none !important;
                        box-shadow: none !important;
                        pointer-events: none;
                    }
                    
                    /* 모바일 특정 스타일 */
                    @media (max-width: 400px) {
                        .btn-container {
                            grid-template-columns: 1fr;
                        }
                        
                        .btn-extra, .btn-stop {
                            grid-column: auto;
                        }
                        
                        html, body, .page-wrapper {
                            background-color: var(--light-color) !important;
                            background: var(--background-gradient) !important;
                        }
                    }
                    
                    /* 다크 모드 대응 */
                    @media (prefers-color-scheme: dark) {
                        html, body, .page-wrapper {
                            background-color: var(--light-color) !important;
                            background: var(--background-gradient) !important;
                        }
                    }
                </style>
            </head>
            <body>
                <div class="page-wrapper">
                    <div class="container">
                        <h1>MCA 소주 디스펜서</h1>
                        <p class="subtitle">원하는 양만큼 소주를 따르세요</p>
                        
                        <div class="status-container">
                            <p class="status" id="statusText">🟢 준비 완료</p>
                        </div>
                        
                        <div class="btn-container">
                            <button id="btnSmall" class="btn btn-small" onclick="handleButtonClick('A', '반잔 따르는 중...')">
                                <span class="emoji">🥃</span>
                                <span>반잔</span>
                            </button>
                            <button id="btnMedium" class="btn btn-medium" onclick="handleButtonClick('B', '한잔 따르는 중...')">
                                <span class="emoji">🍶</span>
                                <span>한잔</span>
                            </button>
                            <button id="btnLarge" class="btn btn-large" onclick="handleButtonClick('C', '풀잔 따르는 중...')">
                                <span class="emoji">🍾</span>
                                <span>풀잔</span>
                            </button>
                            <button id="btnRandom" class="btn btn-random" onclick="handleRandomClick()">
                                <span class="emoji">🎲</span>
                                <span>랜덤</span>
                            </button>
                            <button id="btnContinuous" class="btn btn-extra" onclick="handleContinuousClick()">
                                <span class="emoji">🔄</span>
                                <span>연속 추출</span>
                            </button>
                            <button id="btnStop" class="btn btn-stop" onclick="handleStopClick()">
                                <span class="emoji">⛔</span>
                                <span>정지</span>
                            </button>
                        </div>
                    </div>
                </div>

                <script>
                    // 전역 변수로 작업 상태 관리
                    let isWorking = false;
                    
                    // 버튼 클릭 핸들러 - 모든 클릭은 이 함수들을 통해 처리
                    function handleButtonClick(cup, text) {
                        if (isWorking) return; // 이미 작동 중이면 무시
                        
                        isWorking = true;
                        disableAllButtons(true);
                        document.getElementById("statusText").innerText = "🔴 " + text;
                        
                        // 서버에 요청 보내기
                        var xhr = new XMLHttpRequest();
                        xhr.open("GET", "/motor?cup=" + cup, true);
                        xhr.send();
                        
                        // 타이머 설정 (작업 시간에 따라 조정)
                        let duration = 0;
                        if (cup === 'A') duration = 3000;      // 반잔
                        else if (cup === 'B') duration = 4000; // 한잔
                        else if (cup === 'C') duration = 4900; // 풀잔
                        
                        setTimeout(() => {
                            document.getElementById("statusText").innerText = "🟢 준비 완료";
                            disableAllButtons(false);
                            isWorking = false;
                        }, duration);
                    }
                    
                    function handleRandomClick() {
                        if (isWorking) return; // 이미 작동 중이면 무시
                        
                        // 랜덤으로 A(반잔), B(한잔), C(풀잔) 중 하나 선택
                        const options = ['A', 'B', 'C'];
                        const texts = ['반잔 따르는 중...', '한잔 따르는 중...', '풀잔 따르는 중...'];
                        const durations = [3000, 4000, 4900];
                        
                        // 0-2 사이의 랜덤 인덱스 생성
                        const randomIndex = Math.floor(Math.random() * 3);
                        const selectedOption = options[randomIndex];
                        const selectedText = texts[randomIndex];
                        const selectedDuration = durations[randomIndex];
                        
                        isWorking = true;
                        disableAllButtons(true);
                        document.getElementById("statusText").innerText = "🔴 랜덤: " + selectedText;
                        
                        // 서버에 요청 보내기
                        var xhr = new XMLHttpRequest();
                        xhr.open("GET", "/motor?cup=" + selectedOption, true);
                        xhr.send();
                        
                        setTimeout(() => {
                            document.getElementById("statusText").innerText = "🟢 준비 완료";
                            disableAllButtons(false);
                            isWorking = false;
                        }, selectedDuration);
                    }
                    
                    function handleContinuousClick() {
                        if (isWorking) return; // 이미 작동 중이면 무시
                        
                        isWorking = true;
                        disableAllButtons(true);
                        // 정지 버튼은 활성화 상태로 유지
                        document.getElementById("btnStop").classList.remove("disabled");
                        document.getElementById("statusText").innerText = "🔴 연속 추출 중...";
                        
                        // 서버에 요청 보내기
                        var xhr = new XMLHttpRequest();
                        xhr.open("GET", "/motor?cup=D", true);
                        xhr.send();
                        
                        // 연속 모드에서는 타이머를 설정하지 않음 (정지 버튼으로만 중단)
                    }
                    
                    function handleStopClick() {
                        document.getElementById("statusText").innerText = "🟢 준비 완료";
                        disableAllButtons(false);
                        isWorking = false;
                        
                        // 서버에 정지 요청 보내기
                        var xhr = new XMLHttpRequest();
                        xhr.open("GET", "/motor?cup=STOP", true);
                        xhr.send();
                    }
                    
                    // 모든 버튼 비활성화/활성화 함수
                    function disableAllButtons(disable) {
                        const buttons = document.querySelectorAll(".btn");
                        buttons.forEach(btn => {
                            if (disable) {
                                // 정지 버튼은 항상 활성 상태 유지
                                if (!btn.classList.contains("btn-stop")) {
                                    btn.classList.add("disabled");
                                }
                            } else {
                                btn.classList.remove("disabled");
                            }
                        });
                    }
                </script>
            </body>
            </html>
        )rawliteral");
    });

    server.begin();
}

void loop() {
    vTaskDelay(10 / portTICK_PERIOD_MS);
}
