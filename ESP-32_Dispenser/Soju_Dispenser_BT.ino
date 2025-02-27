#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

void setup() {
    Serial.begin(115200);             // 디버깅용 시리얼 포트
    SerialBT.begin("ESP32_BT");       // 블루투스 이름 설정
    Serial.println("ESP32 Bluetooth is ready!");
    pinMode(2, OUTPUT);               // 모터 제어 핀 설정 (GPIO2 사용)
}

void loop() {
    // 라즈베리파이에서 데이터 수신
    if (SerialBT.available()) {
        char received = SerialBT.read();  // 한 글자 데이터 수신
        Serial.print("Received: ");
        Serial.println(received);

        // 수신 데이터에 따른 동작
        int motor_duration = 0;
        if (received == 'a') {
            motor_duration = 2000;  // 2초
        } else if (received == 'b') {
            motor_duration = 3000;  // 3초
        } else if (received == 'c') {
            motor_duration = 4000;  // 4초
        }

        if (motor_duration > 0) {
            Serial.println("Motor ON");
            digitalWrite(2, HIGH);      // 모터 ON
            delay(motor_duration);     // 지정된 시간 동안 동작
            digitalWrite(2, LOW);      // 모터 OFF
            Serial.println("Motor OFF");
        }

        // 응답 전송
        SerialBT.print("ACK:");
        SerialBT.println(received);
    }
}
