#!/usr/bin/env python3
"""
Trigonometry Quest - Основной Flask сервер
"""

import os
import json
import random
import math
from flask import Flask, render_template, request, jsonify

# Инициализация Flask
app = Flask(__name__, 
           static_folder='static',
           template_folder='templates')

# Проверка наличия matplotlib
try:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')  # Для работы без GUI
    import matplotlib.pyplot as plt
    import io
    import base64
    MATPLOTLIB_AVAILABLE = True
    print("✅ Matplotlib доступен")
except ImportError as e:
    print(f"⚠️  Matplotlib не установлен: {e}")
    print("Установите: pip install matplotlib numpy")
    MATPLOTLIB_AVAILABLE = False

# ========== БЕЗОПАСНЫЙ EVAL ДЛЯ ГРАФИКОВ ==========

def safe_eval_function(func_str, x_values):
    """Безопасное вычисление математических выражений"""
    if not MATPLOTLIB_AVAILABLE:
        raise ValueError("Matplotlib не установлен")
    
    # Разрешенные функции
    ALLOWED = {
        'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
        'pi': math.pi, 'e': math.e
    }
    
    # Заменяем синтаксис
    func_str = func_str.replace('^', '**')
    func_str = func_str.replace('π', 'pi')
    
    # Проверка безопасности
    forbidden = ['__', 'import', 'eval', 'exec', 'open', 'os', 'sys', ';']
    for word in forbidden:
        if word in func_str.lower():
            raise ValueError(f"Запрещенное выражение: {word}")
    
    try:
        # Создаем безопасное окружение
        safe_env = {'x': x_values}
        safe_env.update(ALLOWED)
        
        # Вычисляем
        return eval(func_str, {"__builtins__": None}, safe_env)
    except Exception as e:
        raise ValueError(f"Ошибка вычисления '{func_str}': {str(e)}")

# ========== API ДЛЯ ГРАФИКОВ ==========

@app.route('/api/plot/simple', methods=['POST'])
def plot_simple_function():
    """Простой построитель графиков"""
    if not MATPLOTLIB_AVAILABLE:
        return jsonify({
            "success": False,
            "error": "Matplotlib не установлен. Установите: pip install matplotlib numpy",
            "suggestion": "Используйте предопределенные функции через кнопки в лаборатории"
        })
    
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "Нет данных"})
    
    func_str = data.get('function', 'sin(x)')
    
    try:
        # Генерируем данные
        x = np.linspace(-2 * np.pi, 2 * np.pi, 1000)
        y = None
        
        # Предопределенные функции для надежности
        predefined_functions = {
            'sin(x)': np.sin(x),
            'cos(x)': np.cos(x),
            'tan(x)': np.tan(x),
            'sin(2*x)': np.sin(2 * x),
            'cos(2*x)': np.cos(2 * x),
            'sin(x) + cos(x)': np.sin(x) + np.cos(x),
            '2*sin(x)': 2 * np.sin(x),
            'sin(x)*cos(x)': np.sin(x) * np.cos(x)
        }
        
        if func_str in predefined_functions:
            y = predefined_functions[func_str]
            if func_str == 'tan(x)':
                y = np.clip(y, -10, 10)  # Ограничиваем тангенс
        else:
            # Пробуем безопасное вычисление
            y = safe_eval_function(func_str, x)
        
        # Создаем график
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(x, y, color='#4CAF50', linewidth=3, label=func_str)
        ax.axhline(y=0, color='black', linewidth=0.5, alpha=0.5)
        ax.axvline(x=0, color='black', linewidth=0.5, alpha=0.5)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('x')
        ax.set_ylabel('f(x)')
        ax.set_title(f'График: {func_str}')
        ax.legend()
        
        # Настройка делений
        x_ticks = np.arange(-2 * np.pi, 2.5 * np.pi, np.pi / 2)
        x_labels = []
        for val in x_ticks:
            if val == 0:
                x_labels.append('0')
            elif val == np.pi:
                x_labels.append('π')
            elif val == -np.pi:
                x_labels.append('-π')
            elif val == np.pi / 2:
                x_labels.append('π/2')
            elif val == -np.pi / 2:
                x_labels.append('-π/2')
            elif val == 2 * np.pi:
                x_labels.append('2π')
            elif val == -2 * np.pi:
                x_labels.append('-2π')
            else:
                x_labels.append(f'{val / np.pi:.1f}π')
        
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_labels)
        ax.set_xlim(-2 * np.pi, 2 * np.pi)
        
        # Сохраняем
        img = io.BytesIO()
        plt.tight_layout()
        plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close(fig)
        
        return jsonify({
            "success": True,
            "plot": f"data:image/png;base64,{plot_url}",
            "function": func_str
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Не удалось построить график: {str(e)}",
            "suggestion": "Попробуйте: sin(x), cos(x), tan(x), sin(2*x), cos(2*x), sin(x)+cos(x), 2*sin(x), sin(x)*cos(x)"
        })

# ========== БАЗА ДАННЫХ ЗАДАЧ ==========

TASKS = {
    1: [
        {"id": "task_1_1", "question": "sin(30°) + cos(60°) = ?", "answer": "1.0", "points": 10},
        {"id": "task_1_2", "question": "tan(45°) = ?", "answer": "1.0", "points": 10},
        {"id": "task_1_3", "question": "2 * sin(π/6) = ?", "answer": "1.0", "points": 10}
    ],
    2: [
        {"id": "task_2_1", "question": "sin(x) = 0.5, x = ? (укажите в градусах)", "answer": "30, 150", "points": 15},
        {"id": "task_2_2", "question": "cos(x) = √2/2, x = ?", "answer": "45, 315", "points": 15},
        {"id": "task_2_3", "question": "tan(x) = 1, x = ?", "answer": "45, 225", "points": 15}
    ],
    3: [
        {"id": "task_3_1", "question": "Период sin(x) = ?", "answer": "2π", "points": 20},
        {"id": "task_3_2", "question": "sin(60°) = ?", "answer": "√3/2", "points": 20},
        {"id": "task_3_3", "question": "tan не определен при x = ?", "answer": "90°, 270°", "points": 20}
    ],
    4: [
        {"id": "task_4_1", "question": "sin²(x) + cos²(x) = ?", "answer": "1", "points": 25},
        {"id": "task_4_2", "question": "1 + tan²(x) = ?", "answer": "1/cos²(x)", "points": 25},
        {"id": "task_4_3", "question": "sin(π/2 - x) = ?", "answer": "cos(x)", "points": 25}
    ],
    5: [
        {"id": "task_5_1", "question": "sin(2x) = ?", "answer": "2sin(x)cos(x)", "points": 30},
        {"id": "task_5_2", "question": "cos(2x) = ? (формула через sin и cos)", "answer": "cos²(x)-sin²(x)", "points": 30},
        {"id": "task_5_3", "question": "sin(45°) = ?", "answer": "√2/2", "points": 30}
    ]
}

# ИНФОРМАЦИЯ ОБ УРОВНЯХ
LEVELS = {
    1: {"name": "Основы", "desc": "Базовые значения", "icon": "🔢", "color": "#4CAF50"},
    2: {"name": "Уравнения", "desc": "Решение уравнений", "icon": "📐", "color": "#2196F3"},
    3: {"name": "Свойства", "desc": "Свойства функций", "icon": "📊", "color": "#9C27B0"},
    4: {"name": "Тождества", "desc": "Тригонометрические тождества", "icon": "🧮", "color": "#FF9800"},
    5: {"name": "Формулы", "desc": "Формулы сложения", "icon": "🎯", "color": "#E91E63"}
}

# Файл для сохранения прогресса
PROGRESS_FILE = "user_progress.json"

def load_progress():
    """Загрузить прогресс из файла"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Убедимся, что есть все 5 уровней
                if "level_progress" not in data:
                    data["level_progress"] = {}
                
                for level_id in range(1, 6):
                    level_key = str(level_id)
                    if level_key not in data["level_progress"]:
                        data["level_progress"][level_key] = {
                            "completed": 0, 
                            "unlocked": level_id == 1
                        }
                return data
        except:
            pass
    
    # Начальные данные для 5 уровней
    initial = {
        "score": 0,
        "completed_tasks": [],
        "level_progress": {}
    }
    
    for level_id in range(1, 6):
        initial["level_progress"][str(level_id)] = {
            "completed": 0,
            "unlocked": level_id == 1  # Только 1 уровень разблокирован
        }
    
    return initial

def save_progress(data):
    """Сохранить прогресс в файл"""
    try:
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

# ========== МАРШРУТЫ ==========

@app.route('/')
def home():
    """Главная страница"""
    return render_template('index.html')

@app.route('/game')
def game_page():
    """Страница игры"""
    return render_template('game.html')

@app.route('/levels')
def show_levels():
    """Страница всех уровней"""
    return render_template('levels.html')

@app.route('/lab')
def lab_page():
    """Лаборатория графиков"""
    return render_template('lab.html')

# ========== API МАРШРУТЫ ==========

@app.route('/api/levels')
def api_levels():
    """Получить информацию о всех уровнях"""
    progress = load_progress()
    levels_data = {}
    
    for level_id in range(1, 6):
        level_info = LEVELS.get(level_id, {}).copy()
        level_key = str(level_id)
        prog = progress["level_progress"].get(level_key, {"completed": 0, "unlocked": level_id == 1})
        
        # Логика разблокировки: следующий уровень разблокируется при завершении предыдущего
        if level_id > 1:
            prev_level_key = str(level_id - 1)
            prev_prog = progress["level_progress"].get(prev_level_key, {"completed": 0})
            if prev_prog.get("completed", 0) >= 2:
                prog["unlocked"] = True
        
        level_info.update({
            "id": level_id,
            "unlocked": prog["unlocked"],
            "completed": prog.get("completed", 0),
            "total_tasks": len(TASKS.get(level_id, [])),
            "tasks_count": len(TASKS.get(level_id, []))
        })
        levels_data[str(level_id)] = level_info
    
    return jsonify({"success": True, "levels": levels_data})

@app.route('/api/tasks/<int:level_id>')
def get_task(level_id):
    """Получить задачу для уровня"""
    if 1 <= level_id <= 5 and level_id in TASKS and TASKS[level_id]:
        task = random.choice(TASKS[level_id])
        return jsonify({
            "success": True,
            "task": {
                "id": task["id"],
                "question": task["question"],
                "points": task["points"],
                "level": level_id
            }
        })
    return jsonify({"success": False, "error": "Нет задач для этого уровня"})

@app.route('/api/check', methods=['POST'])
def check_answer():
    """Проверить ответ"""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "Нет данных"})
    
    answer = data.get('answer', '').strip()
    task_id = data.get('task_id')
    
    if not task_id:
        return jsonify({"success": False, "error": "Нет ID задачи"})
    
    # Ищем задачу во всех 5 уровнях
    for level in range(1, 6):
        if level in TASKS:
            for task in TASKS[level]:
                if task["id"] == task_id:
                    # Нормализуем ответы
                    user_answer = answer.lower().replace(' ', '')
                    correct_answer = task["answer"].lower().replace(' ', '')
                    
                    # Для ответов с несколькими значениями
                    if ',' in correct_answer:
                        user_answers = [a.strip() for a in user_answer.split(',')]
                        correct_answers = [a.strip() for a in correct_answer.split(',')]
                        user_answers.sort()
                        correct_answers.sort()
                        is_correct = user_answers == correct_answers
                    else:
                        is_correct = user_answer == correct_answer
                    
                    if is_correct:
                        # Обновляем прогресс
                        progress = load_progress()
                        
                        if task_id not in progress["completed_tasks"]:
                            progress["completed_tasks"].append(task_id)
                            progress["score"] += task["points"]
                            
                            # Обновляем уровень
                            if task_id.startswith("task_"):
                                parts = task_id.split("_")
                                if len(parts) >= 2:
                                    level_num = int(parts[1])
                                    level_key = str(level_num)
                                    
                                    if level_key not in progress["level_progress"]:
                                        progress["level_progress"][level_key] = {
                                            "completed": 0,
                                            "unlocked": True
                                        }
                                    
                                    progress["level_progress"][level_key]["completed"] += 1
                                    progress["level_progress"][level_key]["unlocked"] = True
                                    
                                    # Разблокируем следующий уровень при выполнении 2+ задач
                                    if progress["level_progress"][level_key]["completed"] >= 2:
                                        next_level = level_num + 1
                                        if next_level <= 5:
                                            next_key = str(next_level)
                                            progress["level_progress"][next_key]["unlocked"] = True
                            
                            save_progress(progress)
                    
                    return jsonify({
                        "success": True,
                        "correct": is_correct,
                        "message": "✅ Верно!" if is_correct else f"❌ Неверно. Правильный ответ: {task['answer']}",
                        "points": task["points"] if is_correct else 0
                    })
    
    return jsonify({"success": False, "error": "Задача не найдена"})

@app.route('/api/game/stats')
def game_stats():
    """Получить статистику игры"""
    progress = load_progress()
    
    completed_levels = 0
    current_level = 1
    
    # Проверяем все 5 уровней
    for level_id in range(1, 6):
        level_key = str(level_id)
        if level_key in progress["level_progress"]:
            completed = progress["level_progress"][level_key].get("completed", 0)
            unlocked = progress["level_progress"][level_key].get("unlocked", False)
            
            if completed >= 2:
                completed_levels += 1
            
            if unlocked:
                current_level = level_id
            else:
                break
    
    current_level = min(current_level, 5)
    
    return jsonify({
        "success": True,
        "score": progress.get("score", 0),
        "total_tasks": len(progress.get("completed_tasks", [])),
        "level_progress": progress.get("level_progress", {}),
        "current_level": current_level,
        "completed_levels": completed_levels
    })

@app.route('/api/ai/hint', methods=['POST'])
def get_hint():
    """Получить подсказку"""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "Нет данных"})
    
    question = data.get('question', '')
    
    # Простые подсказки
    hints = {
        "sin(30°)": "sin(30°) = 1/2 = 0.5",
        "cos(60°)": "cos(60°) = 1/2 = 0.5",
        "tan(45°)": "tan(45°) = 1",
        "sin(x) = 0.5": "sin(x)=0.5 при x=30° или 150°",
        "cos(x) = √2/2": "cos(x)=√2/2 при x=45° или 315°",
        "период": "Период sin(x) и cos(x) = 2π",
        "π/6": "π/6 радиан = 30°",
        "60°": "sin(60°) = √3/2",
        "sin²": "Основное тригонометрическое тождество: sin²(x) + cos²(x) = 1",
        "tan²": "1 + tan²(x) = 1/cos²(x)",
        "sin(π/2": "Формула приведения: sin(π/2 - x) = cos(x)",
        "sin(2x)": "Формула двойного угла: sin(2x) = 2sin(x)cos(x)",
        "cos(2x)": "cos(2x) = cos²(x) - sin²(x) = 2cos²(x) - 1 = 1 - 2sin²(x)"
    }
    
    for key, hint in hints.items():
        if key.lower() in question.lower():
            return jsonify({"success": True, "hint": hint})
    
    return jsonify({"success": True, "hint": "Используйте тригонометрическую окружность или таблицу значений"})

@app.route('/api/ai/explain', methods=['POST'])
def explain_concept():
    """Объяснить концепт"""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "Нет данных"})
    
    concept = data.get('concept', '')
    
    # Простые объяснения
    explanations = {
        "синус": "Синус угла в прямоугольном треугольнике — отношение противолежащего катета к гипотенузе.",
        "косинус": "Косинус угла — отношение прилежащего катета к гипотенузе.",
        "тангенс": "Тангенс — отношение синуса к косинусу (противолежащего катета к прилежащему).",
        "тригонометрия": "Тригонометрия изучает соотношения между сторонами и углами треугольников.",
        "единичная окружность": "Окружность радиуса 1, используемая для определения тригонометрических функций.",
        "период": "Период функции — наименьший интервал, через который значения функции повторяются.",
        "тождество": "Тригонометрическое тождество — равенство, справедливое для всех значений переменных.",
        "формула двойного угла": "Формулы, выражающие тригонометрические функции двойного угла через функции одинарного угла."
    }
    
    for key, explanation in explanations.items():
        if key.lower() in concept.lower():
            return jsonify({"success": True, "explanation": explanation})
    
    return jsonify({
        "success": True, 
        "explanation": "Тригонометрия изучает соотношения между сторонами и углами треугольников. Основные функции: sin, cos, tan."
    })

@app.route('/api/game/reset', methods=['POST'])
def reset_game():
    """Сбросить игру"""
    initial_data = {
        "score": 0,
        "completed_tasks": [],
        "level_progress": {
            "1": {"completed": 0, "unlocked": True},
            "2": {"completed": 0, "unlocked": False},
            "3": {"completed": 0, "unlocked": False},
            "4": {"completed": 0, "unlocked": False},
            "5": {"completed": 0, "unlocked": False}
        }
    }
    
    save_progress(initial_data)
    return jsonify({"success": True, "message": "Игра сброшена"})

@app.route('/health')
def health_check():
    """Проверка здоровья сервера"""
    return jsonify({
        "status": "healthy",
        "message": "Trigonometry Quest работает",
        "version": "1.0.0"
    })

# ========== ЗАПУСК СЕРВЕРА ==========

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 TRIGONOMETRY QUEST ЗАПУЩЕН!")
    print("=" * 60)
    print("🌐 Главная: http://localhost:5000")
    print("🎮 Игра: http://localhost:5000/game")
    print("📚 Уровни: http://localhost:5000/levels")
    print("🔬 Лаборатория: http://localhost:5000/lab")
    print("🩺 Health: http://localhost:5000/health")
    print("=" * 60)
    
    if MATPLOTLIB_AVAILABLE:
        print("✅ Графики доступны")
    else:
        print("⚠️  Графики НЕ доступны. Установите: pip install matplotlib numpy")
    
    # Создаем начальный файл прогресса, если его нет
    if not os.path.exists(PROGRESS_FILE):
        initial = load_progress()
        save_progress(initial)
        print("✅ Создан файл прогресса с 5 уровнями")
    
    # Запускаем сервер
    app.run(host='0.0.0.0', port=5000, debug=True)