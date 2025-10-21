import csv
import json
import io
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class FileHandler:
    """Класс для обработки файлов с отзывами"""
    
    @staticmethod
    def process_csv_file(file_content: bytes) -> Tuple[List[str], str]:
        """
        Обработка CSV файла
        Возвращает список текстов и имя колонки
        """
        try:
            content = file_content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content))
            
            # Поиск колонки с текстом
            text_column = None
            possible_columns = ['text', 'review', 'comment', 'feedback', 'message', 'content']
            
            for column in csv_reader.fieldnames:
                if column.lower() in possible_columns:
                    text_column = column
                    break
            
            if not text_column:
                # Если не нашли подходящую колонку, берем первую
                text_column = csv_reader.fieldnames[0] if csv_reader.fieldnames else None
            
            if not text_column:
                raise ValueError("Не удалось найти колонку с текстом в CSV файле")
            
            texts = []
            for row in csv_reader:
                if text_column in row and row[text_column].strip():
                    texts.append(row[text_column].strip())
            
            return texts, text_column
            
        except Exception as e:
            logger.error(f"Ошибка при обработке CSV файла: {e}")
            raise
    
    @staticmethod
    def process_json_file(file_content: bytes) -> List[str]:
        """
        Обработка JSON файла
        Поддерживаемые форматы:
        - [{"text": "..."}, {"review": "..."}]
        - {"texts": ["...", "..."]}
        - {"reviews": ["...", "..."]}
        """
        try:
            content = file_content.decode('utf-8')
            data = json.loads(content)
            
            texts = []
            
            if isinstance(data, list):
                # Массив объектов
                for item in data:
                    if isinstance(item, dict):
                        # Поиск поля с текстом
                        for key in ['text', 'review', 'comment', 'feedback', 'message', 'content']:
                            if key in item and isinstance(item[key], str) and item[key].strip():
                                texts.append(item[key].strip())
                                break
                    elif isinstance(item, str) and item.strip():
                        # Массив строк
                        texts.append(item.strip())
            
            elif isinstance(data, dict):
                # Объект с массивом текстов
                for key in ['texts', 'reviews', 'comments', 'feedbacks', 'messages', 'content']:
                    if key in data and isinstance(data[key], list):
                        for item in data[key]:
                            if isinstance(item, str) and item.strip():
                                texts.append(item.strip())
                        break
            
            return texts
            
        except Exception as e:
            logger.error(f"Ошибка при обработке JSON файла: {e}")
            raise
    
    @staticmethod
    def process_txt_file(file_content: bytes) -> List[str]:
        """
        Обработка TXT файла
        Каждый отзыв на новой строке
        """
        try:
            content = file_content.decode('utf-8')
            lines = content.split('\n')
            
            texts = []
            for line in lines:
                line = line.strip()
                if line:
                    texts.append(line)
            
            return texts
            
        except Exception as e:
            logger.error(f"Ошибка при обработке TXT файла: {e}")
            raise
    
    @staticmethod
    def validate_file_size(file_content: bytes, max_size_mb: int = 10) -> bool:
        """
        Проверка размера файла
        """
        max_size_bytes = max_size_mb * 1024 * 1024
        return len(file_content) <= max_size_bytes
    
    @staticmethod
    def get_file_stats(texts: List[str]) -> dict:
        """
        Получение статистики по текстам
        """
        if not texts:
            return {
                "total": 0,
                "avg_length": 0,
                "min_length": 0,
                "max_length": 0
            }
        
        lengths = [len(text) for text in texts]
        
        return {
            "total": len(texts),
            "avg_length": sum(lengths) / len(lengths),
            "min_length": min(lengths),
            "max_length": max(lengths)
        }