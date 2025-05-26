# ESP32-LD2450-SQLite-Integration

Система сбора и визуализации данных с радара LD2450 на базе ESP32, Flask и SQLite.  
Простая интеграция: ESP32 передаёт JSON через Wi-Fi → Flask-сервер сохраняет в SQLite → браузер строит график через Chart.js.


## 📥 Клонирование репозитория

```bash
git clone https://github.com/KT-NT/ESP32-LD2450-SQLite-Integration.git

cd ESP32-LD2450-SQLite-Integration
```
**⚙️ Установка и запуск сервера**

Создать виртуальное окружение и активировать
```bash
python3 -m venv venv

source venv/bin/activate
```

Установить Flask
```bash
pip install Flask
```
Запустить сервер
```bash
python3 server.py #    По умолчанию слушает http://0.0.0.0:8000/.
```

## 🔌 Подключение (пины)

- LD2450 VCC → ESP32 3.3V
- LD2450 GND → ESP32 GND
- LD2450 TX  → ESP32 GPIO16 (Serial2 RX)
- LD2450 RX  → ESP32 GPIO17 (Serial2 TX)

**Конфигурация скетча**

 В файле sketch_may5a.ino пропишите свои параметры:

```bash
    const char* ssid     = "ВАШ_SSID"; #Название сити 
    const char* password = "ВАШ_ПАРОЛЬ"; 
    const char* serverUrl = "http://<IP_Сервера>:8000/add"; #Замените <IP_Сервера> на IP вашего сервера
```
    
**Загрузка в ESP32**

- Откройте sketch_may5a.ino в Arduino IDE

- Скомпилируйте и загрузите на плату

## 🌐 Веб-интерфейс

- Главная страница: `GET /`
- Мониторинг в реальном времени:
  - Запрос: `GET /all` раз в секунду
  - Chart.js строит график velocity по frame_ts
  - Кнопка «Сбросить график» очищает старые точки
- Исторический диапазон: `GET /range?start=&end=` (при сохранении старого кода)


## 🗂️ Структура проекта
```
ESP32-LD2450-SQLite-Integration/
├── server.py # Flask-приложение и API
├── ld2450.db # SQLite-база (автосоздание)
├── sketch_may5a.ino # Arduino-скетч для ESP32 + LD2450
└── templates/
    └── index.html # HTML + Chart.js
