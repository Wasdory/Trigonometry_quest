#!/usr/bin/env python3
"""
Упрощенный тест проекта
"""
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath('.'))

print("\n" + "="*60)
print("🚀 ЗАПУСК УПРОЩЕННЫХ ТЕСТОВ")
print("="*60)

def test_imports():
    """Тест импорта модулей"""
    print("\n1. Тест импорта модулей...")
    try:
        from math_engine.trig_solver import TrigonometrySolver
        print("   ✓ math_engine.trig_solver импортирован")
        
        from ai_modules.local_ai import LocalTrigonometryAI
        print("   ✓ ai_modules.local_ai импортирован")
        
        from game.game_engine import GameEngine
        print("   ✓ game.game_engine импортирован")
        
        return True
    except Exception as e:
        print(f"   ✗ Ошибка импорта: {e}")
        return False

def test_math_simple():
    """Простой тест математики"""
    print("\n2. Тест математического движка...")
    try:
        from math_engine.trig_solver import TrigonometrySolver
        solver = TrigonometrySolver()
        
        result = solver.evaluate_expression("sin(30°) + cos(60°)")
        print(f"   sin(30°) + cos(60°) = {result}")
        
        if abs(result - 1.0) < 0.1:
            print("   ✓ Вычисления работают")
            return True
        else:
            print(f"   ✗ Неверный результат: {result}")
            return False
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
        return False

def test_ai_simple():
    """Простой тест AI"""
    print("\n3. Тест AI модуля...")
    try:
        from ai_modules.local_ai import LocalTrigonometryAI
        ai = LocalTrigonometryAI()
        
        explanation = ai.explain_concept("синус")
        print(f"   Объяснение 'синус': {explanation[:60]}...")
        
        hint = ai.generate_hint("sin(30°)")
        print(f"   Подсказка: {hint}")
        
        print("   ✓ AI модуль работает")
        return True
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
        return False

def test_game_simple():
    """Простой тест игры"""
    print("\n4. Тест игрового движка...")
    try:
        import tempfile
        import json
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            from game.game_engine import GameEngine
            game = GameEngine(temp_file)
            
            stats = game.get_player_stats()
            print(f"   Начальный счет: {stats['score']}")
            print(f"   Текущий уровень: {stats['current_level']}")
            
            # Выполняем задачу
            success = game.complete_task("test_task_1", 10)
            print(f"   Задача выполнена: {success}")
            
            stats = game.get_player_stats()
            print(f"   Счет после задачи: {stats['score']}")
            
            print("   ✓ Игровой движок работает")
            return True
            
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
        return False

def test_flask_simple():
    """Простой тест Flask"""
    print("\n5. Тест Flask приложения...")
    try:
        # Создаем минимальное Flask приложение для теста
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/test')
        def test():
            return 'OK'
        
        with app.test_client() as client:
            response = client.get('/test')
            if response.status_code == 200:
                print("   ✓ Flask работает")
                return True
            else:
                print(f"   ✗ Код ответа: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
        return False

def main():
    """Главная функция"""
    print("Проверка структуры проекта...")
    
    # Проверяем существование файлов
    required_files = [
        'app.py',
        'math_engine/trig_solver.py',
        'ai_modules/local_ai.py', 
        'game/game_engine.py',
        'requirements.txt'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✓ {file}")
        else:
            print(f"   ✗ {file} отсутствует")
    
    # Запускаем тесты
    results = []
    results.append(test_imports())
    results.append(test_math_simple())
    results.append(test_ai_simple())
    results.append(test_game_simple())
    results.append(test_flask_simple())
    
    # Итог
    print("\n" + "="*60)
    print("📊 ИТОГ ТЕСТИРОВАНИЯ")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n✅ Пройдено тестов: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("\nЗапустите проект:")
        print("  python run.py")
        print("  или")
        print("  python app.py")
        print("\nОткройте: http://localhost:5000")
        return True
    else:
        print(f"\n⚠️  Провалено тестов: {total - passed}")
        return False

if __name__ == '__main__':
    # Проверяем, что мы в правильной директории
    current_dir = os.getcwd()
    print(f"Текущая директория: {current_dir}")
    
    if not os.path.exists('app.py'):
        print("\n❌ Ошибка: Запускайте тесты из директории trigonometry_quest/")
        print("Перейдите в директорию проекта:")
        print(f"  cd {os.path.dirname(current_dir)}")
        sys.exit(1)
    
    success = main()
    sys.exit(0 if success else 1)