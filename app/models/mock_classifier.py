import random
from typing import List, Dict
import logging
from app.core.config import settings
from app.models.schemas import SentimentResult, SentimentLabel

logger = logging.getLogger(__name__)


class MockSentimentClassifier:
    """
    Мок-классификатор для демонстрации работы API без загрузки реальной модели
    """
    def __init__(self):
        self.model_name = settings.model_name
        self.loaded = False
        
    def load_model(self):
        """Имитация загрузки модели"""
        try:
            logger.info(f"Имитация загрузки модели {self.model_name}...")
            self.loaded = True
            logger.info("Модель успешно 'загружена'")
        except Exception as e:
            logger.error(f"Ошибка при 'загрузке' модели: {e}")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """Предобработка текста"""
        return text.strip()
    
    def predict_single(self, text: str) -> SentimentResult:
        """Классификация одного текста"""
        if not self.loaded:
            self.load_model()
        
        processed_text = self.preprocess_text(text)
        
        # Имитация классификации
        sentiment = random.choice(list(SentimentLabel))
        confidence = round(random.uniform(0.7, 0.99), 4)
        
        return SentimentResult(
            text=text,
            sentiment=sentiment,
            confidence=confidence
        )
    
    def predict_batch(self, texts: List[str]) -> List[SentimentResult]:
        """Классификация списка текстов"""
        results = []
        for text in texts:
            result = self.predict_single(text)
            results.append(result)
        return results
    
    def get_model_info(self) -> Dict:
        """Получение информации о модели"""
        return {
            "name": self.model_name,
            "description": "Мок-модель для демонстрации работы API",
            "languages": ["Русский", "Английский", "Немецкий", "Французский", "Итальянский", "Испанский", "Португальский", "Нидерландский", "Китайский", "Японский"],
            "max_text_length": settings.max_text_length
        }


# Глобальный экземпляр мок-классификатора
mock_classifier = MockSentimentClassifier()