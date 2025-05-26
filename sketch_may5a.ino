#include <WiFi.h>
#include <HTTPClient.h>

#define RXD2 16
#define TXD2 17
#define NUM_TARGETS 3


const char* ssid     = "ВАШ_SSID";
const char* password = "ВАШ_ПАРОЛЬ";
const char* serverUrl = "http://<IP_Сервера>:8000/add";


uint8_t frameBuf[30];
unsigned long lastSec = 0;

// текущий этап поиска кадра
int fbIndex = 0;

void setup() {
  Serial.begin(115200);
  Serial2.begin(256000, SERIAL_8N1, RXD2, TXD2);
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected, IP: " + WiFi.localIP().toString());
}

// Ищем кадр: заголовок 0xAA,0xFF, затем 28 байт до футера
bool readFrame() {
  while (Serial2.available()) {
    uint8_t b = Serial2.read();
    // state machine
    if (fbIndex == 0) {
      if (b == 0xAA) {
        frameBuf[fbIndex++] = b;
      }
    }
    else if (fbIndex == 1) {
      if (b == 0xFF) {
        frameBuf[fbIndex++] = b;
      } else {
        fbIndex = 0;
      }
    }
    else {
      frameBuf[fbIndex++] = b;
      if (fbIndex == 30) {
        // проверяем футер
        if (frameBuf[28] == 0x55 && frameBuf[29] == 0xCC) {
          fbIndex = 0;
          return true;
        }
        // не то — сдвигаем буфер на 1 и продолжаем искать
        memmove(frameBuf, frameBuf+1, 29);
        fbIndex = 29;
      }
    }
  }
  return false;
}

float toAngle(uint8_t lo, uint8_t hi) {
  return ((hi<<8)|lo) / 100.0;
}
float toDistance(uint8_t lo, uint8_t hi) {
  return ((hi<<8)|lo) / 1000.0;
}
float toVelocity(uint8_t lo, uint8_t hi) {
  int16_t raw = (hi<<8)|lo;
  return raw / 1000.0;
}
uint16_t toAmplitude(uint8_t lo, uint8_t hi) {
  return (hi<<8)|lo;
}

void sendData() {
  unsigned long nowSec = millis() / 1000;
  if (nowSec == lastSec) return;
  lastSec = nowSec;

  Serial.println("Frame received, building JSON...");

  // Формируем JSON
  String js = "{\"ts\":" + String(nowSec) + ",\"targets\":[";
  bool first = true;
  for (int i = 0; i < NUM_TARGETS; i++) {
    int base = 2 + i*8; // после 2-байтного заголовка
    float angle    = toAngle   (frameBuf[base],   frameBuf[base+1]);
    float distance = toDistance(frameBuf[base+2], frameBuf[base+3]);
    float velocity = toVelocity(frameBuf[base+4], frameBuf[base+5]);
    uint16_t amp   = toAmplitude(frameBuf[base+6], frameBuf[base+7]);

    if (distance <= 0) continue;
    if (!first) js += ",";
    first = false;
    js += "{\"angle\":"   + String(angle,2) +
          ",\"distance\":" + String(distance,3) +
          ",\"velocity\":" + String(velocity,2) +
          ",\"amplitude\":" + String(amp) +
          ",\"idx\":"      + String(i+1) +
          "}";
  }
  js += "]}";

  // Логи HTTP
  Serial.println("=== Sending JSON ===");
  Serial.println(js);
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type","application/json");
  int code = http.POST(js);
  Serial.println("--- HTTP Response ---");
  Serial.print("Code: "); Serial.println(code);
  Serial.print("Body: "); Serial.println(http.getString());
  Serial.println("====================");
  http.end();
}

void loop() {
  // heartbeat
  static unsigned long lastBeat = 0;
  unsigned long now = millis();
  if (now - lastBeat >= 1000) {
    lastBeat = now;
    Serial.println("[Loop heartbeat]");
  }

  // показываем, сколько байт в буфере
  int cnt = Serial2.available();
  Serial.printf("Serial2.available(): %d\n", cnt);

  // пытаемся прочитать полный кадр
  if (readFrame()) {
    sendData();
  }

  delay(200);
}
