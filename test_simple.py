import requests

def test_system():
    base_url = "http://localhost:5000"
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ СИСТЕМЫ УРОВНЕЙ")
    print("=" * 60)
    
    try:
        # 1. Тест здоровья системы
        print("\n1. Проверка здоровья системы:")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   Статус: {health['status']}")
            print(f"   Сообщение: {health['message']}")
        else:
            print(f"   Ошибка: {response.status_code}")
        
        # 2. Тест API уровней
        print("\n2. Тест API уровней:")
        response = requests.get(f"{base_url}/api/levels")
        if response.status_code == 200:
            levels = response.json()
            print(f"   Уровней найдено: {len(levels.get('levels', {}))}")
            for level_id, level in levels.get('levels', {}).items():
                print(f"   Уровень {level_id}: {level['name']} ({level['tasks_count']} задач)")
        else:
            print(f"   Ошибка: {response.status_code}")
        
        # 3. Тест задач по уровням
        print("\n3. Тест задач по уровням:")
        for level in range(1, 6):
            response = requests.get(f"{base_url}/api/tasks/{level}")
            if response.status_code == 200:
                task = response.json()
                print(f"   Уровень {level}: Задача загружена")
                print(f"     Вопрос: {task.get('question', '')[:50]}...")
                print(f"     Очки: {task.get('points', 0)}")
            else:
                print(f"   Уровень {level}: Ошибка {response.status_code}")
        
        # 4. Тест статистики игры
        print("\n4. Тест статистики игры:")
        response = requests.get(f"{base_url}/api/game/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   Счет: {stats.get('score', 0)}")
            print(f"   Текущий уровень: {stats.get('current_level', 1)}")
            print(f"   Решено задач: {stats.get('total_tasks', 0)}")
            
            # Проверка прогресса по уровням
            levels_progress = stats.get('levels_progress', {})
            print(f"   Прогресс по уровням:")
            for level_id, progress in levels_progress.items():
                print(f"     Уровень {level_id}: {progress.get('completed', 0)}/{progress.get('required', 2)} задач")
        else:
            print(f"   Ошибка: {response.status_code}")
        
        # 5. Тест проверки ответа
        print("\n5. Тест проверки ответа:")
        test_data = {
            "answer": "1.0",
            "task_id": "level_1_task_1"
        }
        response = requests.post(f"{base_url}/api/check", json=test_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   Результат: {'Правильно' if result.get('correct') else 'Неправильно'}")
            print(f"   Сообщение: {result.get('message', '')}")
        else:
            print(f"   Ошибка: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Ошибка подключения. Убедитесь, что сервер запущен:")
        print(f"   python app.py")
        print(f"   Сервер должен быть доступен по адресу: {base_url}")

if __name__ == "__main__":
    test_system()°)"))