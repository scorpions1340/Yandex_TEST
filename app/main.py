import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import router
from app.models.mock_classifier import mock_classifier as classifier
from app.core.config import settings
from app.db.database import engine
from app.db import models
from app.auth.routes import router as auth_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск приложения
    logger.info("Запуск приложения...")
    
    # Создание таблиц в базе данных
    try:
        models.Base.metadata.create_all(bind=engine)
        logger.info("База данных инициализирована")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        raise
    
    # Загрузка модели
    try:
        classifier.load_model()
        logger.info("Модель успешно загружена")
    except Exception as e:
        logger.error(f"Ошибка при загрузке модели: {e}")
        raise
    
    yield
    
    # Завершение работы приложения
    logger.info("Завершение работы приложения...")


# Создание FastAPI приложения
app = FastAPI(
    title="Sentiment Analyzer API",
    description="API для классификации тональности отзывов на основе многоязычной модели XLM-RoBERTa",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене следует указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(router, prefix="/api")
app.include_router(auth_router, prefix="/auth", tags=["authentication"])


@app.get("/")
async def root():
    """
    Корневой эндпоинт
    """
    return {
        "message": "Sentiment Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "web_interface": "/",
        "authentication": {
            "register": "/auth/register",
            "login": "/auth/login",
            "me": "/auth/me"
        },
        "endpoints": {
            "classify": "/api/classify",
            "classify_batch": "/api/classify-batch",
            "upload_file": "/api/upload-file",
            "model_info": "/api/model-info",
            "health": "/api/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )