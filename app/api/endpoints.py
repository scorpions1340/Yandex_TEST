import time
import logging
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import HTMLResponse

from app.models.schemas import (
    SingleReviewRequest,
    BatchReviewRequest,
    BatchReviewResponse,
    SentimentResult,
    ModelInfo,
    ErrorResponse,
    FileUploadResponse
)
from app.models.mock_classifier import mock_classifier as classifier
from app.utils.file_handler import FileHandler
from app.auth.dependencies import get_current_active_user
from app.db.models import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/classify", response_model=SentimentResult)
async def classify_review(
    request: SingleReviewRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Классификация одного отзыва
    """
    try:
        result = classifier.predict_single(request.text)
        return result
    except Exception as e:
        logger.error(f"Ошибка при классификации отзыва: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post("/classify-batch", response_model=BatchReviewResponse)
async def classify_reviews_batch(
    request: BatchReviewRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Пакетная классификация отзывов
    """
    try:
        start_time = time.time()
        results = classifier.predict_batch(request.texts)
        processing_time = time.time() - start_time
        
        # Подсчет статистики
        positive_count = sum(1 for r in results if r.sentiment == "positive")
        negative_count = sum(1 for r in results if r.sentiment == "negative")
        neutral_count = sum(1 for r in results if r.sentiment == "neutral")
        
        return BatchReviewResponse(
            results=results,
            total=len(results),
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count
        )
    except Exception as e:
        logger.error(f"Ошибка при пакетной классификации отзывов: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post("/upload-file", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Загрузка файла с отзывами для классификации
    Поддерживаемые форматы: CSV, JSON, TXT
    """
    try:
        # Проверка формата файла
        allowed_extensions = ["csv", "json", "txt"]
        file_extension = file.filename.split(".")[-1].lower() if file.filename else ""
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(allowed_extensions)}"
            )
        
        # Чтение содержимого файла
        file_content = await file.read()
        
        # Проверка размера файла
        if not FileHandler.validate_file_size(file_content):
            raise HTTPException(
                status_code=400,
                detail="Размер файла превышает максимально допустимый (10 МБ)"
            )
        
        # Обработка файла в зависимости от формата
        start_time = time.time()
        
        if file_extension == "csv":
            texts, column_name = FileHandler.process_csv_file(file_content)
        elif file_extension == "json":
            texts = FileHandler.process_json_file(file_content)
        else:  # txt
            texts = FileHandler.process_txt_file(file_content)
        
        if not texts:
            raise HTTPException(
                status_code=400,
                detail="В файле не найдено текстов для анализа"
            )
        
        # Классификация текстов
        results = classifier.predict_batch(texts)
        processing_time = time.time() - start_time
        
        return FileUploadResponse(
            filename=file.filename,
            size=len(file_content),
            results=results,
            total_processed=len(results),
            processing_time=round(processing_time, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обработке файла: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/model-info", response_model=ModelInfo)
async def get_model_info():
    """
    Получение информации о модели
    """
    try:
        info = classifier.get_model_info()
        return ModelInfo(**info)
    except Exception as e:
        logger.error(f"Ошибка при получении информации о модели: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/health")
async def health_check():
    """
    Проверка состояния API
    """
    return {"status": "healthy", "message": "API работает нормально"}


@router.get("/", response_class=HTMLResponse)
async def get_web_interface():
    """
    Веб-интерфейс для тестирования API
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Анализатор тональности отзывов</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background-color: #f8f9fa;
            }
            .container {
                max-width: 1000px;
                margin-top: 30px;
            }
            .card {
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                border: none;
                margin-bottom: 20px;
            }
            .card-header {
                background-color: #0d6efd;
                color: white;
                font-weight: bold;
            }
            .btn-primary {
                background-color: #0d6efd;
                border-color: #0d6efd;
            }
            .result-card {
                margin-top: 20px;
            }
            .sentiment-positive {
                color: #198754;
                font-weight: bold;
            }
            .sentiment-negative {
                color: #dc3545;
                font-weight: bold;
            }
            .sentiment-neutral {
                color: #6c757d;
                font-weight: bold;
            }
            .confidence-bar {
                height: 20px;
                border-radius: 10px;
                background-color: #e9ecef;
                margin-top: 5px;
            }
            .confidence-fill {
                height: 100%;
                border-radius: 10px;
                background-color: #0d6efd;
            }
            .file-upload-area {
                border: 2px dashed #dee2e6;
                border-radius: 10px;
                padding: 30px;
                text-align: center;
                margin-bottom: 20px;
                transition: all 0.3s ease;
            }
            .file-upload-area:hover {
                border-color: #0d6efd;
                background-color: #f8f9ff;
            }
            .loading {
                display: none;
            }
            .batch-results {
                max-height: 400px;
                overflow-y: auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="text-center mb-4">
                <h1 class="display-4">
                    <i class="fas fa-brain text-primary"></i>
                    Анализатор тональности отзывов
                </h1>
                <p class="lead">Многоязычная модель на основе XLM-RoBERTa для классификации отзывов</p>
            </div>

            <!-- Вкладки -->
            <ul class="nav nav-tabs" id="myTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="single-tab" data-bs-toggle="tab" data-bs-target="#single" type="button" role="tab">
                        <i class="fas fa-comment"></i> Один отзыв
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="batch-tab" data-bs-toggle="tab" data-bs-target="#batch" type="button" role="tab">
                        <i class="fas fa-list"></i> Пакетная обработка
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="file-tab" data-bs-toggle="tab" data-bs-target="#file" type="button" role="tab">
                        <i class="fas fa-file-upload"></i> Загрузка файла
                    </button>
                </li>
            </ul>

            <div class="tab-content" id="myTabContent">
                <!-- Вкладка "Один отзыв" -->
                <div class="tab-pane fade show active" id="single" role="tabpanel">
                    <div class="card">
                        <div class="card-header">
                            <i class="fas fa-comment"></i> Анализ одного отзыва
                        </div>
                        <div class="card-body">
                            <form id="single-form">
                                <div class="mb-3">
                                    <label for="single-text" class="form-label">Текст отзыва:</label>
                                    <textarea class="form-control" id="single-text" rows="4" placeholder="Введите текст отзыва..." required></textarea>
                                </div>
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-search"></i> Анализировать
                                </button>
                                <div class="spinner-border text-primary loading" role="status">
                                    <span class="visually-hidden">Загрузка...</span>
                                </div>
                            </form>
                            <div id="single-result" class="result-card"></div>
                        </div>
                    </div>
                </div>

                <!-- Вкладка "Пакетная обработка" -->
                <div class="tab-pane fade" id="batch" role="tabpanel">
                    <div class="card">
                        <div class="card-header">
                            <i class="fas fa-list"></i> Пакетная обработка отзывов
                        </div>
                        <div class="card-body">
                            <form id="batch-form">
                                <div class="mb-3">
                                    <label for="batch-texts" class="form-label">Тексты отзывов (каждый с новой строки):</label>
                                    <textarea class="form-control" id="batch-texts" rows="8" placeholder="Введите тексты отзывов, каждый с новой строки..." required></textarea>
                                </div>
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-search"></i> Анализировать все
                                </button>
                                <div class="spinner-border text-primary loading" role="status">
                                    <span class="visually-hidden">Загрузка...</span>
                                </div>
                            </form>
                            <div id="batch-result" class="result-card"></div>
                        </div>
                    </div>
                </div>

                <!-- Вкладка "Загрузка файла" -->
                <div class="tab-pane fade" id="file" role="tabpanel">
                    <div class="card">
                        <div class="card-header">
                            <i class="fas fa-file-upload"></i> Загрузка файла с отзывами
                        </div>
                        <div class="card-body">
                            <div class="file-upload-area" id="file-drop-area">
                                <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
                                <h5>Перетащите файл сюда или нажмите для выбора</h5>
                                <p class="text-muted">Поддерживаемые форматы: CSV, JSON, TXT (макс. размер: 10 МБ)</p>
                                <input type="file" id="file-input" accept=".csv,.json,.txt" style="display: none;">
                                <button type="button" class="btn btn-outline-primary" onclick="document.getElementById('file-input').click()">
                                    <i class="fas fa-folder-open"></i> Выбрать файл
                                </button>
                            </div>
                            <div id="file-info" class="alert alert-info" style="display: none;"></div>
                            <button id="analyze-file-btn" class="btn btn-primary" style="display: none;" onclick="analyzeFile()">
                                <i class="fas fa-search"></i> Анализировать файл
                            </button>
                            <div class="spinner-border text-primary loading" role="status">
                                <span class="visually-hidden">Загрузка...</span>
                            </div>
                            <div id="file-result" class="result-card"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Информация о модели -->
            <div class="card">
                <div class="card-header">
                    <i class="fas fa-info-circle"></i> Информация о модели
                </div>
                <div class="card-body">
                    <div id="model-info">
                        <div class="text-center">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Загрузка...</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Базовый URL API
            const API_BASE = window.location.origin;

            // Функции для работы с API
            async function analyzeSingleReview(text) {
                const response = await fetch(`${API_BASE}/api/classify`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: text }),
                });
                return await response.json();
            }

            async function analyzeBatchReviews(texts) {
                const response = await fetch(`${API_BASE}/api/classify-batch`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ texts: texts }),
                });
                return await response.json();
            }

            async function uploadFile(file) {
                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch(`${API_BASE}/api/upload-file`, {
                    method: 'POST',
                    body: formData,
                });
                return await response.json();
            }

            async function getModelInfo() {
                const response = await fetch(`${API_BASE}/api/model-info`);
                return await response.json();
            }

            // Функции для отображения результатов
            function displaySingleResult(result) {
                const sentimentClass = `sentiment-${result.sentiment}`;
                const sentimentText = {
                    'positive': 'Положительный',
                    'negative': 'Отрицательный',
                    'neutral': 'Нейтральный'
                }[result.sentiment];

                const html = `
                    <div class="card">
                        <div class="card-header">
                            <i class="fas fa-chart-line"></i> Результат анализа
                        </div>
                        <div class="card-body">
                            <p><strong>Текст:</strong> ${result.text}</p>
                            <p><strong>Тональность:</strong> <span class="${sentimentClass}">${sentimentText}</span></p>
                            <p><strong>Уверенность:</strong> ${(result.confidence * 100).toFixed(2)}%</p>
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: ${result.confidence * 100}%"></div>
                            </div>
                        </div>
                    </div>
                `;
                document.getElementById('single-result').innerHTML = html;
            }

            function displayBatchResult(results) {
                const positiveCount = results.positive_count;
                const negativeCount = results.negative_count;
                const neutralCount = results.neutral_count;
                const total = results.total;

                let resultsHtml = '<div class="batch-results">';
                results.results.forEach((result, index) => {
                    const sentimentClass = `sentiment-${result.sentiment}`;
                    const sentimentText = {
                        'positive': 'Положительный',
                        'negative': 'Отрицательный',
                        'neutral': 'Нейтральный'
                    }[result.sentiment];

                    resultsHtml += `
                        <div class="card mb-2">
                            <div class="card-body">
                                <p class="mb-1"><strong>${index + 1}.</strong> ${result.text}</p>
                                <p class="mb-1"><strong>Тональность:</strong> <span class="${sentimentClass}">${sentimentText}</span> (${(result.confidence * 100).toFixed(2)}%)</p>
                            </div>
                        </div>
                    `;
                });
                resultsHtml += '</div>';

                const html = `
                    <div class="card">
                        <div class="card-header">
                            <i class="fas fa-chart-pie"></i> Статистика
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <h4 class="sentiment-positive">${positiveCount}</h4>
                                        <p>Положительных</p>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <h4 class="sentiment-negative">${negativeCount}</h4>
                                        <p>Отрицательных</p>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <h4 class="sentiment-neutral">${neutralCount}</h4>
                                        <p>Нейтральных</p>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <h4>${total}</h4>
                                        <p>Всего</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    ${resultsHtml}
                `;
                document.getElementById('batch-result').innerHTML = html;
            }

            function displayFileResult(result) {
                const positiveCount = result.results.filter(r => r.sentiment === 'positive').length;
                const negativeCount = result.results.filter(r => r.sentiment === 'negative').length;
                const neutralCount = result.results.filter(r => r.sentiment === 'neutral').length;

                let resultsHtml = '<div class="batch-results">';
                result.results.forEach((item, index) => {
                    const sentimentClass = `sentiment-${item.sentiment}`;
                    const sentimentText = {
                        'positive': 'Положительный',
                        'negative': 'Отрицательный',
                        'neutral': 'Нейтральный'
                    }[item.sentiment];

                    resultsHtml += `
                        <div class="card mb-2">
                            <div class="card-body">
                                <p class="mb-1"><strong>${index + 1}.</strong> ${item.text}</p>
                                <p class="mb-1"><strong>Тональность:</strong> <span class="${sentimentClass}">${sentimentText}</span> (${(item.confidence * 100).toFixed(2)}%)</p>
                            </div>
                        </div>
                    `;
                });
                resultsHtml += '</div>';

                const html = `
                    <div class="card">
                        <div class="card-header">
                            <i class="fas fa-file-alt"></i> Информация о файле
                        </div>
                        <div class="card-body">
                            <p><strong>Имя файла:</strong> ${result.filename}</p>
                            <p><strong>Размер:</strong> ${(result.size / 1024).toFixed(2)} КБ</p>
                            <p><strong>Обработано отзывов:</strong> ${result.total_processed}</p>
                            <p><strong>Время обработки:</strong> ${result.processing_time} сек.</p>
                        </div>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <i class="fas fa-chart-pie"></i> Статистика
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <h4 class="sentiment-positive">${positiveCount}</h4>
                                        <p>Положительных</p>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <h4 class="sentiment-negative">${negativeCount}</h4>
                                        <p>Отрицательных</p>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <h4 class="sentiment-neutral">${neutralCount}</h4>
                                        <p>Нейтральных</p>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <h4>${result.total_processed}</h4>
                                        <p>Всего</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    ${resultsHtml}
                `;
                document.getElementById('file-result').innerHTML = html;
            }

            function displayModelInfo(info) {
                const html = `
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Название модели:</strong> ${info.name}</p>
                            <p><strong>Описание:</strong> ${info.description}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Макс. длина текста:</strong> ${info.max_text_length} символов</p>
                            <p><strong>Поддерживаемые языки:</strong></p>
                            <ul>
                                ${info.languages.map(lang => `<li>${lang}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                `;
                document.getElementById('model-info').innerHTML = html;
            }

            // Обработчики событий
            document.getElementById('single-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const text = document.getElementById('single-text').value;
                
                document.querySelector('#single-form .loading').style.display = 'inline-block';
                document.querySelector('#single-form button[type="submit"]').disabled = true;
                
                try {
                    const result = await analyzeSingleReview(text);
                    displaySingleResult(result);
                } catch (error) {
                    alert('Ошибка при анализе отзыва: ' + error.message);
                } finally {
                    document.querySelector('#single-form .loading').style.display = 'none';
                    document.querySelector('#single-form button[type="submit"]').disabled = false;
                }
            });

            document.getElementById('batch-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const texts = document.getElementById('batch-texts').value.split('\\n').filter(text => text.trim());
                
                if (texts.length === 0) {
                    alert('Пожалуйста, введите хотя бы один отзыв');
                    return;
                }
                
                document.querySelector('#batch-form .loading').style.display = 'inline-block';
                document.querySelector('#batch-form button[type="submit"]').disabled = true;
                
                try {
                    const result = await analyzeBatchReviews(texts);
                    displayBatchResult(result);
                } catch (error) {
                    alert('Ошибка при анализе отзывов: ' + error.message);
                } finally {
                    document.querySelector('#batch-form .loading').style.display = 'none';
                    document.querySelector('#batch-form button[type="submit"]').disabled = false;
                }
            });

            let selectedFile = null;

            // Обработка загрузки файла
            const fileInput = document.getElementById('file-input');
            const fileDropArea = document.getElementById('file-drop-area');

            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    handleFileSelect(file);
                }
            });

            // Drag and drop
            fileDropArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                fileDropArea.classList.add('border-primary');
            });

            fileDropArea.addEventListener('dragleave', () => {
                fileDropArea.classList.remove('border-primary');
            });

            fileDropArea.addEventListener('drop', (e) => {
                e.preventDefault();
                fileDropArea.classList.remove('border-primary');
                
                const file = e.dataTransfer.files[0];
                if (file) {
                    handleFileSelect(file);
                }
            });

            function handleFileSelect(file) {
                const allowedExtensions = ['csv', 'json', 'txt'];
                const fileExtension = file.name.split('.').pop().toLowerCase();
                
                if (!allowedExtensions.includes(fileExtension)) {
                    alert('Неподдерживаемый формат файла. Разрешены: CSV, JSON, TXT');
                    return;
                }
                
                if (file.size > 10 * 1024 * 1024) { // 10 МБ
                    alert('Размер файла превышает максимально допустимый (10 МБ)');
                    return;
                }
                
                selectedFile = file;
                document.getElementById('file-info').innerHTML = `
                    <i class="fas fa-file"></i> Выбран файл: <strong>${file.name}</strong> (${(file.size / 1024).toFixed(2)} КБ)
                `;
                document.getElementById('file-info').style.display = 'block';
                document.getElementById('analyze-file-btn').style.display = 'inline-block';
            }

            async function analyzeFile() {
                if (!selectedFile) {
                    alert('Файл не выбран');
                    return;
                }
                
                document.querySelector('#file .loading').style.display = 'inline-block';
                document.getElementById('analyze-file-btn').disabled = true;
                
                try {
                    const result = await uploadFile(selectedFile);
                    displayFileResult(result);
                } catch (error) {
                    alert('Ошибка при обработке файла: ' + error.message);
                } finally {
                    document.querySelector('#file .loading').style.display = 'none';
                    document.getElementById('analyze-file-btn').disabled = false;
                }
            }

            // Загрузка информации о модели при загрузке страницы
            window.addEventListener('load', async () => {
                try {
                    const info = await getModelInfo();
                    displayModelInfo(info);
                } catch (error) {
                    document.getElementById('model-info').innerHTML = '<p class="text-danger">Ошибка при загрузке информации о модели</p>';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)