# 🎓 AI School MVP Platform

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red.svg)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green.svg)
![BeyondPresence](https://img.shields.io/badge/AI-Beyond_Presence-purple.svg)

**Адаптивная обучающая платформа с интеграцией 3D ИИ-репетиторов в реальном времени.**

Это MVP версия системы для демонстрации функционала заказчику. Приложение объединяет фронтенд и бэкенд в единый запускаемый модуль для простоты деплоя.

---

## 🚀 Основной функционал

### 1. 🤖 Real-time AI Tutors
*   Полноценная видео-связь с 3D аватаром.
*   Минимальная задержка (<500мс) благодаря WebRTC.
*   **VAD (Voice Activity Detection):** Аватар слушает и отвечает автоматически, нажимать кнопки не нужно.

### 2. 🔐 Secure Auth Proxy (Bypass Login)
*   Бэкенд выступает посредником между клиентом и Beyond Presence.
*   Генерирует уникальные **приватные ссылки** через API.
*   Пользователь попадает на урок сразу, **без авторизации Google** и ввода паролей.

### 3. ⏳ Система очереди (Smart Queue)
*   Лимит: **10 одновременных сессий** (согласно ТЗ).
*   11-й пользователь автоматически видит экран очереди с позицией.
*   Автоматическое освобождение слота при завершении урока.

### 4. ⏱️ Биллинг и Интерфейс
*   Интерактивный таймер обратного отсчета (JS).
*   Учет баланса пользователя (Mock Database).
*   Заметки и инструкции внутри урока.

---

## 🛠 Установка и Запуск

### Предварительные требования
*   Python 3.9 или выше.
*   Ключ API от Beyond Presence.

### 1. Клонирование репозитория
```bash
git clone https://github.com/PavelMenshikov/ai_school_mvp
cd ai_school_mvp