import requests
import json
import time

# Базовый URL API
BASE_URL = "http://localhost:8000"

def test_register():
    """Тест регистрации пользователя"""
    try:
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        print(f"Register: {response.status_code}")
        if response.status_code == 201:
            print(f"User registered: {response.json()}")
        else:
            print(f"Error: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"Register failed: {e}")
        return False

def test_login():
    """Тест входа пользователя"""
    try:
        data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", data=data)
        print(f"Login: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            print(f"Token received: {token_data['access_token'][:20]}...")
            return token_data['access_token']
        else:
            print(f"Error: {response.json()}")
            return None
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def test_me(token):
    """Тест получения информации о текущем пользователе"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"Me: {response.status_code}")
        print(f"User info: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Me failed: {e}")
        return False

def test_classify_without_token():
    """Тест классификации без токена (должен завершиться ошибкой)"""
    try:
        data = {"text": "This is a test"}
        response = requests.post(f"{BASE_URL}/api/classify", json=data)
        print(f"Classify without token: {response.status_code}")
        if response.status_code == 403:
            print("✅ Correctly rejected without token")
            return True
        else:
            print("❌ Should have been rejected without token")
            return False
    except Exception as e:
        print(f"Classify without token failed: {e}")
        return False

def test_classify_with_token(token):
    """Тест классификации с токеном"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"text": "This is a wonderful product!"}
        response = requests.post(f"{BASE_URL}/api/classify", json=data, headers=headers)
        print(f"Classify with token: {response.status_code}")
        print(f"Result: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Classify with token failed: {e}")
        return False

def test_batch_classify_with_token(token):
    """Тест пакетной классификации с токеном"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "texts": [
                "Great product!",
                "Terrible service",
                "It's okay"
            ]
        }
        response = requests.post(f"{BASE_URL}/api/classify-batch", json=data, headers=headers)
        print(f"Batch classify with token: {response.status_code}")
        result = response.json()
        print(f"Total processed: {result.get('total')}")
        return response.status_code == 200
    except Exception as e:
        print(f"Batch classify with token failed: {e}")
        return False

def test_health():
    """Тест проверки состояния API (должен работать без токена)"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_model_info():
    """Тест получения информации о модели (должен работать без токена)"""
    try:
        response = requests.get(f"{BASE_URL}/api/model-info")
        print(f"Model info: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Model info failed: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("Начало тестирования API с аутентификацией...")
    print("-" * 50)
    
    # Ждем запуска сервера
    print("Ожидание запуска сервера...")
    time.sleep(5)
    
    # Тесты без аутентификации
    print("\n--- Тесты без аутентификации ---")
    health_ok = test_health()
    model_info_ok = test_model_info()
    classify_no_token_ok = test_classify_without_token()
    
    # Регистрация и вход
    print("\n--- Тесты аутентификации ---")
    register_ok = test_register()
    token = test_login()
    
    if token:
        me_ok = test_me(token)
        
        # Тесты с аутентификацией
        print("\n--- Тесты с аутентификацией ---")
        classify_ok = test_classify_with_token(token)
        batch_ok = test_batch_classify_with_token(token)
        
        # Итоги
        print("\n" + "=" * 50)
        print("Итоги тестирования:")
        print(f"Health Check: {'✅ Успешно' if health_ok else '❌ Ошибка'}")
        print(f"Model Info: {'✅ Успешно' if model_info_ok else '❌ Ошибка'}")
        print(f"Classify without token: {'✅ Правильно отклонено' if classify_no_token_ok else '❌ Ошибка'}")
        print(f"Register: {'✅ Успешно' if register_ok else '❌ Ошибка'}")
        print(f"Login: {'✅ Успешно' if token else '❌ Ошибка'}")
        print(f"Get User Info: {'✅ Успешно' if me_ok else '❌ Ошибка'}")
        print(f"Classify with token: {'✅ Успешно' if classify_ok else '❌ Ошибка'}")
        print(f"Batch Classify: {'✅ Успешно' if batch_ok else '❌ Ошибка'}")
        
        all_passed = all([
            health_ok, 
            model_info_ok, 
            classify_no_token_ok, 
            register_ok, 
            bool(token), 
            me_ok, 
            classify_ok, 
            batch_ok
        ])
        
        print(f"\nОбщий результат: {'✅ Все тесты пройдены' if all_passed else '❌ Некоторые тесты не пройдены'}")
        
        if all_passed:
            print("\n🎉 API с аутентификацией готов к использованию!")
            print(f"Документация API: {BASE_URL}/docs")
    else:
        print("\n❌ Не удалось получить токен, тесты с аутентификацией пропущены")

if __name__ == "__main__":
    main()