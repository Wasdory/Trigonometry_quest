#!/usr/bin/env python3
"""
Запуск Trigonometry Quest
"""

import os
import sys

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Запуск Trigonometry Quest: AI-лаборатория")
    print("=" * 50)
    print("📖 Документация: http://localhost:5000/api/docs")
    print("🎮 Игра: http://localhost:5000/game")
    print("🔬 Лаборатория: http://localhost:5000/lab")
    print("🛑 Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    except Exception as e:
        print(f"Ошибка при запуске: {e}")
        print("Проверьте установлены ли все зависимости:")
        print("pip install -r requirements.txt")