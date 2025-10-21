import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import List, Dict, Tuple
import logging
from app.core.config import settings
from app.models.schemas import SentimentResult, SentimentLabel

logger = logging.getLogger(__name__)


class SentimentClassifier:
    def __init__(self):
        self.model_name = settings.model_name
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.label_mapping = {
            0: SentimentLabel.NEGATIVE,
            1: SentimentLabel.NEGATIVE,
            2: SentimentLabel.NEUTRAL,
            3: SentimentLabel.POSITIVE,
            4: SentimentLabel.POSITIVE
        }
        
    def load_model(self):
        """Загрузка модели и токенизатора"""
        try:
            logger.info(f"Загрузка модели {self.model_name}...")
            # Используем use_fast=False для избежания проблем с токенизатором
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=False)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"Модель успешно загружена на устройстве {self.device}")
        except Exception as e:
            logger.error(f"Ошибка при загрузке модели: {e}")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """Предобработка текста"""
        # Базовая предобработка - удаление лишних пробелов
        return text.strip()
    
    def predict_single(self, text: str) -> SentimentResult:
        """Классификация одного текста"""
        if not self.model or not self.tokenizer:
            self.load_model()
        
        # Предобработка текста
        processed_text = self.preprocess_text(text)
        
        # Ограничение длины текста
        if len(processed_text) > settings.max_text_length:
            processed_text = processed_text[:settings.max_text_length]
        
        try:
            # Токенизация
            inputs = self.tokenizer(
                processed_text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=settings.max_text_length
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Предсказание
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
                predicted_class = torch.argmax(probabilities, dim=-1).item()
                confidence = probabilities[0][predicted_class].item()
            
            # Преобразование предсказания
            sentiment = self.label_mapping.get(predicted_class, SentimentLabel.NEUTRAL)
            
            return SentimentResult(
                text=text,
                sentiment=sentiment,
                confidence=round(confidence, 4)
            )
            
        except Exception as e:
            logger.error(f"Ошибка при классификации текста: {e}")
            # Возвращаем нейтральный результат в случае ошибки
            return SentimentResult(
                text=text,
                sentiment=SentimentLabel.NEUTRAL,
                confidence=0.0
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
            "description": "Многоязычная модель для анализа тональности на основе BERT",
            "languages": ["Русский", "Английский", "Немецкий", "Французский", "Итальянский", "Испанский", "Португальский", "Нидерландский", "Китайский", "Японский"],
            "max_text_length": settings.max_text_length
        }


# Глобальный экземпляр классификатора
classifier = SentimentClassifier()