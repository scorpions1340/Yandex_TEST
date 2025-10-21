import requests
import json
import time

# Базовый URL API
BASE_URL = "http://localhost:8000"

def test_health():
    """Тест проверки состояния API"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_model_info():
    """Тест получения информации о модели"""
    try:
        response = requests.get(f"{BASE_URL}/api/model-info")
        print(f"Model info: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Model info failed: {e}")
        return False

def test_single_classification():
    """Тест классификации одного отзыва"""
    try:
        # Тест на русском языке
        data = {"text": "Этот продукт просто замечательный!"}
        response = requests.post(f"{BASE_URL}/api/classify", json=data)
        print(f"Single classification (RU): {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Тест на английском языке
        data = {"text": "This product is amazing!"}
        response = requests.post(f"{BASE_URL}/api/classify", json=data)
        print(f"Single classification (EN): {response.status_code}")
        print(f"Response: {response.json()}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Single classification failed: {e}")
        return False

def test_batch_classification():
    """Тест пакетной классификации"""
    try:
        data = {
            "texts": [
                "Отличный сервис!",
                "Мне не понравилось",
                "Нормально, но могло быть лучше",
                "Amazing product!",
                "Terrible experience"
            ]
        }
        response = requests.post(f"{BASE_URL}/api/classify-batch", json=data)
        print(f"Batch classification: {response.status_code}")
        result = response.json()
        print(f"Total: {result.get('total')}")
        print(f"Positive: {result.get('positive_count')}")
        print(f"Negative: {result.get('negative_count')}")
        print(f"Neutral: {result.get('neutral_count')}")
        return response.status_code == 200
    except Exception as e:
        print(f"Batch classification failed: {e}")
        return False

def test_web_interface():
    """Тест веб-интерфейса"""
    try:
        response = requests.get(BASE_URL)
        print(f"Web interface: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Web interface failed: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("Начало тестирования API...")
    print("-" * 50)
    
    # Ждем запуска сервера
    print("Ожидание запуска сервера...")
    time.sleep(5)
    
    tests = [
        ("Health Check", test_health),
        ("Model Info", test_model_info),
        ("Single Classification", test_single_classification),
        ("Batch Classification", test_batch_classification),
        ("Web Interface", test_web_interface)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- Тест: {test_name} ---")
        result = test_func()
        results.append((test_name, result))
        print(f"Результат: {'✅ Успешно' if result else '❌ Ошибка'}")
    
    print("\n" + "=" * 50)
    print("Итоги тестирования:")
    for test_name, result in results:
        print(f"{test_name}: {'✅ Успешно' if result else '❌ Ошибка'}")
    
    all_passed = all(result for _, result in results)
    print(f"\nОбщий результат: {'✅ Все тесты пройдены' if all_passed else '❌ Некоторые тесты не пройдены'}")
    
    if all_passed:
        print("\n🎉 API готов к использованию!")
        print(f"Веб-интерфейс: {BASE_URL}")
        print(f"Документация API: {BASE_URL}/docs")

if __name__ == "__main__":
    main()