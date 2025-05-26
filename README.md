# ESP32-LD2450-SQLite-Integration

Система сбора и визуализации данных с радара LD2450 на базе ESP32, Flask и SQLite.  
Простая интеграция: ESP32 передаёт JSON через Wi-Fi → Flask-сервер сохраняет в SQLite → браузер строит график через Chart.js.



## 📥 Клонирование репозитория

---
git clone https://github.com/KT-NT/ESP32-LD2450-SQLite-Integration.git
cd ESP32-LD2450-SQLite-Integration
```bash

⚙️ Установка и запуск сервера

    Создать виртуальное окружение и активировать

python3 -m venv venv
source venv/bin/activate

Установить Flask

pip install Flask

Запустить сервер

    python3 server.py

    По умолчанию слушает http://0.0.0.0:8000/.

🔌 Подключение ESP32 + LD2450

    Пины ESP32 ↔ LD2450

        ESP32 GPIO16 (Serial2 RX) ← LD2450 TX

        ESP32 GPIO17 (Serial2 TX) → LD2450 RX

        ESP32 3.3 V ← LD2450 VCC

        ESP32 GND ← LD2450 GND

    Конфигурация скетча
    В файле sketch_may5a.ino пропишите свои параметры:

    const char* ssid     = "ВАШ_SSID";
    const char* password = "ВАШ_ПАРОЛЬ";
    const char* serverUrl = "http://<IP_Сервера>:8000/add";

    Загрузка в ESP32

        Откройте sketch_may5a.ino в Arduino IDE

        Скомпилируйте и загрузите на плату

🌐 Веб-интерфейс

    Главная страница: GET /

    Мониторинг в реальном времени:

        Запрос GET /all раз в секунду

        Chart.js строит график velocity по frame_ts

        Кнопка Сбросить график очищает старые точки

    Исторический диапазон: GET /range?start=<ts>&end=<ts> (при сохранении старого кода)

📋 API

    POST /add
    Принимает JSON:

{
  "velocity": <число>,
  "angle":    <число>,
  "distance": <число>
}

Возвращает 201 Created и {"status":"ok"}.

GET /all
Ответ:

    [
      {"frame_ts": 1620000000, "velocity": 0.12},
      {"frame_ts": 1620000001, "velocity": 0.15},
      ...
    ]

    GET /range?start=<ts>&end=<ts>
    Фильтрация по временным меткам UNIX.

📝 Структура проекта

ESP32-LD2450-SQLite-Integration/
├── server.py          # Flask-приложение и API
├── ld2450.db          # SQLite-база (автосоздание)
├── sketch_may5a.ino   # Arduino-скетч для ESP32 + LD2450
└── templates/
    └── index.html     # HTML + Chart.js
