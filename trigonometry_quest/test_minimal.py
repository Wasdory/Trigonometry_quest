python
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("МИНИМАЛЬНЫЙ ТЕСТ ПРОЕКТА")
print("="*60)

try:
    # 1. Тест импорта модулей
    print("\n1. Тест импорта модулей...")
    from math_engine.trig_solver import TrigonometrySolver
    print("   ✓ math_engine.trig_solver импортирован")
    
    from ai_modules.local_ai import LocalTrigonometryAI
    print("   ✓ ai_modules.local_ai импортирован")
    
    from game.game_engine import GameEngine
    print("   ✓ game.game_engine импортирован")
    
    from math_engine.plotter import FunctionPlotter
    print("   ✓ math_engine.plotter импортирован")
    
    # 2. Тест создания объектов
    print("\n2. Тест создания объектов...")
    solver = TrigonometrySolver()
    print("   ✓ TrigonometrySolver создан")
    
    ai = LocalTrigonometryAI()
    print("   ✓ LocalTrigonometryAI создан")
    
    game_engine = GameEngine("test_game_data.json")
    print("   ✓ GameEngine создан")
    
    plotter = FunctionPlotter()
    print("   ✓ FunctionPlotter создан")
    
    # 3. Простой тест вычислений
    print("\n3. Тест вычислений...")
    result = solver.evaluate_expression("sin(30°) + cos(60°)")
    print(f"   sin(30°) + cos(60°) = {result}")
    
    # 4. Тест AI
    print("\n4. Тест AI...")
    explanation = ai.explain_concept("синус")
    print(f"   Объяснение 'синус': {explanation[:50]}...")
    
    # 5. Тест игры
    print("\n5. Тест игры...")
    stats = game_engine.get_player_stats()
    print(f"   Начальный счет: {stats['score']}")
    
    print("\n" + "="*60)
    print("✅ ВСЕ МОДУЛИ РАБОТАЮТ КОРРЕКТНО!")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()
    
    # Удаляем временный файл
    if os.path.exists("test_game_data.json"):
        os.remove("test_game_data.json")