# Sentiment Analyzer API

API для классификации тональности отзывов на основе многоязычной модели XLM-RoBERTa.

## Возможности

- Классификация одного отзыва
- Пакетная обработка отзывов
- Загрузка файлов с отзывами (CSV, JSON, TXT)
- Поддержка множества языков (русский, английский и другие)
- Веб-интерфейс для тестирования
- Автоматическая документация API (Swagger/OpenAPI)
- JWT-аутентификация с системой регистрации/входа
- Защищенные эндпоинты для классификации текста

## Структура проекта

```
sentiment-analyzer/
├── app/
│   ├── __init__.py
│   ├── main.py              # Основной файл FastAPI приложения
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py       # Pydantic модели для данных
│   │   └── classifier.py    # Класс для работы с моделью классификации
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py     # Эндпоинты API
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── dependencies.py  # Зависимости для аутентификации
│   │   ├── routes.py        # Эндпоинты аутентификации
│   │   ├── schemas.py       # Pydantic схемы для аутентификации
│   │   └── security.py      # Утилиты безопасности (JWT, хеширование)
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py      # Настройка подключения к SQLite
│   │   ├── models.py        # SQLAlchemy модели
│   │   └── crud.py          # CRUD операции
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Конфигурация приложения
│   └── utils/
│       ├── __init__.py
│       └── file_handler.py  # Утилиты для обработки файлов
├── static/                  # Статические файлы
├── tests/                   # Тесты
├── requirements.txt         # Зависимости
├── .env                     # Переменные окружения
├── test_api.py              # Тесты API без аутентификации
├── test_auth_api.py         # Тесты API с аутентификацией
└── README.md               # Документация
```

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/scorpions1340/Yandex_TEST
cd sentiment-analyzer
```

### 2. Создание и активация виртуального окружения

```bash
# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения (Windows)
.\venv\Scripts\activate

# Активация виртуального окружения (Linux/Mac)
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Создайте файл `.env` в корне проекта со следующим содержимым:

```env
# Модель для анализа тональности
MODEL_NAME=cardiffnlp/twitter-xlm-roberta-base-sentiment

# Настройки сервера
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Максимальная длина текста для анализа
MAX_TEXT_LENGTH=512

# Настройки безопасности
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Настройки базы данных
DATABASE_URL=sqlite:///./sentiment_analyzer.db
```

### 5. Запуск приложения

```bash
python app/main.py
```

Или с использованием uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Использование API

### Веб-интерфейс

Откройте в браузере `http://localhost:8000` для доступа к веб-интерфейсу.

### Документация API

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Аутентификация

#### 1. Регистрация пользователя

```http
POST /auth/register
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}
```

#### 2. Вход пользователя

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=testuser&password=password123
```

**Ответ:**

```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
}
```

#### 3. Получение информации о текущем пользователе

```http
GET /auth/me
Authorization: Bearer <access_token>
```

### Эндпоинты API

#### 1. Классификация одного отзыва (требуется аутентификация)

```http
POST /api/classify
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "text": "Этот продукт просто замечательный!",
    "language": "ru"
}
```

**Ответ:**

```json
{
    "text": "Этот продукт просто замечательный!",
    "sentiment": "positive",
    "confidence": 0.9876
}
```

#### 2. Пакетная классификация отзывов (требуется аутентификация)

```http
POST /api/classify-batch
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "texts": [
        "Отличный сервис!",
        "Мне не понравилось",
        "Нормально, но могло быть лучше"
    ],
    "language": "ru"
}
```

**Ответ:**

```json
{
    "results": [
        {
            "text": "Отличный сервис!",
            "sentiment": "positive",
            "confidence": 0.9543
        },
        {
            "text": "Мне не понравилось",
            "sentiment": "negative",
            "confidence": 0.8765
        },
        {
            "text": "Нормально, но могло быть лучше",
            "sentiment": "neutral",
            "confidence": 0.7654
        }
    ],
    "total": 3,
    "positive_count": 1,
    "negative_count": 1,
    "neutral_count": 1
}
```

#### 3. Загрузка файла с отзывами (требуется аутентификация)

```http
POST /api/upload-file
Content-Type: multipart/form-data
Authorization: Bearer <access_token>

file: [CSV/JSON/TXT файл]
```

**Поддерживаемые форматы файлов:**

- **CSV**: файл должен содержать колонку с текстом (названия: text, review, comment, feedback, message, content)
- **JSON**: поддерживаются форматы:
  - `[{"text": "..."}, {"review": "..."}]`
  - `{"texts": ["...", "..."]}`
  - `{"reviews": ["...", "..."]}`
- **TXT**: каждый отзыв на новой строке

#### 4. Информация о модели

```http
GET /api/model-info
```

**Ответ:**

```json
{
    "name": "cardiffnlp/twitter-xlm-roberta-base-sentiment",
    "description": "Многоязычная модель для анализа тональности на основе XLM-RoBERTa",
    "languages": ["Русский", "Английский", "Испанский", "Французский", "Немецкий", "Итальянский", "Португальский", "Китайский", "Японский", "Корейский"],
    "max_text_length": 512
}
```

#### 5. Проверка состояния API

```http
GET /api/health
```

**Ответ:**

```json
{
    "status": "healthy",
    "message": "API работает нормально"
}
```

## Примеры использования

### Python

```python
import requests

# Регистрация пользователя
register_response = requests.post(
    "http://localhost:8000/auth/register",
    json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
)

# Вход пользователя
login_response = requests.post(
    "http://localhost:8000/auth/login",
    data={"username": "testuser", "password": "password123"}
)
token = login_response.json()["access_token"]

# Заголовок для аутентификации
headers = {"Authorization": f"Bearer {token}"}

# Классификация одного отзыва
response = requests.post(
    "http://localhost:8000/api/classify",
    json={"text": "Отличный продукт!"},
    headers=headers
)
result = response.json()
print(f"Тональность: {result['sentiment']}, Уверенность: {result['confidence']}")

# Пакетная классификация
response = requests.post(
    "http://localhost:8000/api/classify-batch",
    json={"texts": ["Хорошо", "Плохо", "Нормально"]},
    headers=headers
)
results = response.json()
print(f"Всего отзывов: {results['total']}")
print(f"Положительных: {results['positive_count']}")
print(f"Отрицательных: {results['negative_count']}")
print(f"Нейтральных: {results['neutral_count']}")
```

### cURL

```bash
# Регистрация пользователя
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'

# Вход пользователя
TOKEN=$(curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=password123" | jq -r .access_token)

# Классификация одного отзыва
curl -X POST "http://localhost:8000/api/classify" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"text": "Отличный продукт!"}'

# Пакетная классификация
curl -X POST "http://localhost:8000/api/classify-batch" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"texts": ["Хорошо", "Плохо", "Нормально"]}'
```

## Модель

Проект использует модель `cardiffnlp/twitter-xlm-roberta-base-sentiment` - многоязычную модель на основе XLM-RoBERTa, обученную на данных Twitter для анализа тональности.

### Характеристики модели:

- **Архитектура**: XLM-RoBERTa
- **Поддерживаемые языки**: более 40 языков, включая русский и английский
- **Классы**: negative, neutral, positive
- **Максимальная длина текста**: 512 токенов

## Ограничения

- Максимальный размер файла для загрузки: 10 МБ
- Максимальное количество отзывов в пакетной обработке: 100
- Максимальная длина текста: 512 символов

## Разработка

### Запуск тестов

```bash
# Тесты без аутентификации
python test_api.py

# Тесты с аутентификацией
python test_auth_api.py

# Юнит-тесты
python -m pytest tests/
```

### Форматирование кода

```bash
black app/
```

### Проверка типов

```bash
mypy app/
```

## Лицензия

MIT License

## Поддержка


При возникновении проблем или вопросов, пожалуйста, создайте issue в репозитории проекта.
