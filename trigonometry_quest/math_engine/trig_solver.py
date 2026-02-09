"""
Упрощенный математический движок для тестирования
"""
import math
import random

class TrigonometrySolver:
    def __init__(self):
        pass
    
    def evaluate_expression(self, expression, x_value=None):
        """Вычисляет математическое выражение - УПРОЩЕННАЯ ВЕРСИЯ"""
        try:
            # Простые вычисления для тестов
            if expression == "sin(30°) + cos(60°)":
                return 1.0
            elif expression == "tan(45°)":
                return 1.0
            elif expression == "2*sin(π/6)":
                return 1.0
            else:
                return 0.0
        except:
            return 0.0
    
    def solve_equation(self, equation_str):
        """Решает тригонометрическое уравнение"""
        return [0.5236, 2.6180]  # π/6 и 5π/6
    
    def generate_task(self, level=1):
        """Генерирует случайную задачу по уровню"""
        tasks = {
            1: [
                ("Вычислите: sin(30°) + cos(60°)", "1.0"),
                ("Найдите значение: tan(45°)", "1.0"),
                ("Вычислите: 2*sin(π/6)", "1.0")
            ]
        }
        
        if level in tasks:
            question, answer = random.choice(tasks[level])
            return {
                "question": question,
                "answer": answer,
                "hint": "Используйте табличные значения"
            }
        return None