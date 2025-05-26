# ESP32-LD2450-SQLite-Integration
Проект «Радарный мониторинг LD2450 + ESP32 + Flask + SQLite + Chart.js»

Этот репозиторий содержит реализацию системы сбора и визуализации данных с радара LD2450 на базе ESP32. Данные передаются по Wi-Fi на Flask-сервер, сохраняются в SQLite и отображаются в реальном времени и по заданным диапазонам в браузере с помощью Chart.js.
📂 Структура проекта

my_flask_project/
├── server.py            # Flask-приложение (API + веб-интерфейс)
├── ld2450.db            # SQLite-база (создаётся автоматически)
└── templates/
    └── index.html       # HTML-шаблон с графиком Chart.js

⚙️ Зависимости

    Python 3.8+

    Flask

    SQLite (встроено в Python)

    ESP32 (Arduino core)

    Arduino-библиотеки: WiFi, HTTPClient

🚀 Установка и запуск сервера

    Клонировать репозиторий:

git clone https://github.com/yourname/my_flask_project.git
cd my_flask_project

Создать виртуальное окружение и установить Flask:

python3 -m venv venv
source venv/bin/activate
pip install Flask

Запустить сервер:

    python server.py

    Сервер стартует на http://0.0.0.0:8000/.

🔌 Подключение и настройка ESP32 + LD2450

    Аппаратные соединения

        LD2450 VCC → 3.3 V ESP32

        LD2450 GND → GND ESP32

        LD2450 TX → GPIO16 (Serial2 RX)

        LD2450 RX → GPIO17 (Serial2 TX)

    Конфигурация скетча
    Откройте sketch_may5a.ino (в Arduino IDE или PlatformIO) и задайте:

    const char* ssid     = "YOUR_SSID";
    const char* password = "YOUR_PASSWORD";
    const char* serverUrl = "http://<IP_Сервера>:8000/add";

    Загрузка на ESP32
    – Установите WiFi.begin(ssid, password); и Serial2.begin(256000, …);
    – Скомпилируйте и залейте скетч.

🌐 Веб-интерфейс

    Мониторинг в реальном времени
    График обновляется каждую секунду по данным из базы (/all).

    Сброс графика
    Кнопка очищает текущие точки и сбрасывает процент активности.

    Chart.js
    Используется CDN-подключение:

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

📋 API

    POST /add
    Принимает JSON { "velocity":…, "angle":…, "distance":… }, записывает в БД.

    GET /all
    Возвращает все точки: [{"frame_ts":…, "velocity":…}, …].

    GET /range?start=<ts>&end=<ts>
    Возвращает точки за указанный UNIX-диапазон.
