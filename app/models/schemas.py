from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum


class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class SentimentResult(BaseModel):
    text: str
    sentiment: SentimentLabel
    confidence: float = Field(..., ge=0.0, le=1.0, description="Уверенность модели в предсказании от 0 до 1")
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Уверенность должна быть в диапазоне от 0 до 1')
        return v


class SingleReviewRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=512, description="Текст отзыва для анализа")
    language: Optional[str] = Field(None, description="Язык текста (опционально)")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Текст отзыва не может быть пустым')
        return v.strip()


class BatchReviewRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=100, description="Список текстов отзывов для анализа")
    language: Optional[str] = Field(None, description="Язык текстов (опционально)")
    
    @validator('texts')
    def validate_texts(cls, v):
        if not all(text.strip() for text in v):
            raise ValueError('Все тексты отзывов должны быть непустыми')
        return [text.strip() for text in v]


class BatchReviewResponse(BaseModel):
    results: List[SentimentResult]
    total: int
    positive_count: int
    negative_count: int
    neutral_count: int


class ModelInfo(BaseModel):
    name: str
    description: str
    languages: List[str]
    max_text_length: int


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


class FileUploadResponse(BaseModel):
    filename: str
    size: int
    results: List[SentimentResult]
    total_processed: int
    processing_time: Optional[float] = None