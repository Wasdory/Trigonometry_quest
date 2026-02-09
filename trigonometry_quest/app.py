#!/usr/bin/env python3
"""
Trigonometry Quest - Основной Flask сервер
Упрощенная версия для быстрого запуска
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

# ========== БЕЗОПАСНЫЙ EVAL ==========

def safe_eval_function(func_str, x_values):
    """
    Безопасное вычисление математических выражений
    """
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
    """Простой построитель графиков - предопределенные функции"""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "Нет данных"})
    
    func_str = data.get('function', 'sin(x)')
    
    try:
        import numpy as np
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import io
        import base64
        
        # Генерируем данные
        x = np.linspace(-2 * np.pi, 2 * np.pi, 1000)
        y = None
        
        # Только разрешенные функции
        if func_str == 'sin(x)':
            y = np.sin(x)
        elif func_str == 'cos(x)':
            y = np.cos(x)
        elif func_str == 'tan(x)':
            y = np.tan(x)
            y = np.clip(y, -10, 10)
        elif func_str == 'sin(2*x)':
            y = np.sin(2 * x)
        elif func_str == 'cos(2*x)':
            y = np.cos(2 * x)
        elif func_str == 'sin(x) + cos(x)':
            y = np.sin(x) + np.cos(x)
        elif func_str == '2*sin(x)':
            y = 2 * np.sin(x)
        elif func_str == 'sin(x)*cos(x)':
            y = np.sin(x) * np.cos(x)
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
            "suggestion": "Попробуйте: sin(x), cos(x), tan(x), sin(2*x), cos(2*x), sin(x)+cos(x)"
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
    ]
}

# ИНФОРМАЦИЯ ОБ УРОВНЯХ
LEVELS = {
    1: {"name": "Основы", "desc": "Базовые значения", "icon": "🔢", "color": "#4CAF50"},
    2: {"name": "Уравнения", "desc": "Решение уравнений", "icon": "📐", "color": "#2196F3"},
    3: {"name": "Свойства", "desc": "Свойства функций", "icon": "📊", "color": "#9C27B0"}
}

# Файл для сохранения прогресса
PROGRESS_FILE = "user_progress.json"

def load_progress():
    """Загрузить прогресс из файла"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # Начальные данные
    return {
        "score": 0,
        "completed_tasks": [],
        "level_progress": {
            "1": {"completed": 0, "unlocked": True},
            "2": {"completed": 0, "unlocked": False},
            "3": {"completed": 0, "unlocked": False}
        }
    }

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
    
    for level_id in range(1, 4):
        level_info = LEVELS[level_id].copy()
        level_key = str(level_id)
        prog = progress["level_progress"].get(level_key, {"completed": 0, "unlocked": level_id == 1})
        
        level_info.update({
            "id": level_id,
            "unlocked": prog["unlocked"],
            "completed": prog["completed"],
            "total_tasks": len(TASKS.get(level_id, [])),
            "is_completed": prog["completed"] >= 2,
            "tasks_count": len(TASKS.get(level_id, []))
        })
        levels_data[str(level_id)] = level_info
    
    return jsonify({"success": True, "levels": levels_data})

@app.route('/api/tasks/<int:level_id>')
def get_task(level_id):
    """Получить задачу для уровня"""
    if level_id in TASKS and TASKS[level_id]:
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
    
    # Ищем задачу
    for level in range(1, 4):
        if level in TASKS:
            for task in TASKS[level]:
                if task["id"] == task_id:
                    is_correct = answer.lower() == task["answer"].lower()
                    
                    if is_correct:
                        # Обновляем прогресс
                        progress = load_progress()
                        
                        if task_id not in progress["completed_tasks"]:
                            progress["completed_tasks"].append(task_id)
                            progress["score"] += task["points"]
                            
                            # Обновляем уровень
                            try:
                                if task_id.startswith("task_"):
                                    parts = task_id.split("_")
                                    if len(parts) >= 2:
                                        level_num = int(parts[1])
                                        level_key = str(level_num)
                                        
                                        if level_key in progress["level_progress"]:
                                            progress["level_progress"][level_key]["completed"] += 1
                                            
                                            # Разблокируем следующий уровень
                                            if progress["level_progress"][level_key]["completed"] >= 2:
                                                next_level = level_num + 1
                                                if next_level <= 3:
                                                    next_key = str(next_level)
                                                    progress["level_progress"][next_key]["unlocked"] = True
                            except:
                                pass
                            
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
    
    # Считаем завершенные уровни
    completed_levels = 0
    for level_id in range(1, 4):
        level_key = str(level_id)
        if level_key in progress["level_progress"]:
            if progress["level_progress"][level_key]["completed"] >= 2:
                completed_levels += 1
    
    return jsonify({
        "success": True,
        "score": progress["score"],
        "total_tasks": len(progress["completed_tasks"]),
        "level_progress": progress["level_progress"],
        "current_level": max([1] + [id for id in range(1, 4) 
                                   if progress["level_progress"].get(str(id), {}).get("unlocked", False)]),
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
        "60°": "sin(60°) = √3/2"
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
        "единичная окружность": "Окружность радиуса 1, используемая для определения тригонометрических функций."
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
            "3": {"completed": 0, "unlocked": False}
        }
    }
    
    save_progress(initial_data)
    return jsonify({"success": True, "message": "Игра сброшена"})

@app.route('/api/test')
def test_api():
    """Тестовый эндпоинт"""
    return jsonify({
        "success": True,
        "message": "API работает корректно",
        "endpoints": [
            "/api/game/stats",
            "/api/levels", 
            "/api/tasks/1",
            "/api/check",
            "/api/ai/hint",
            "/api/ai/explain",
            "/api/plot/simple",
            "/api/game/reset"
        ]
    })

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
    print("⚙️ API тест: http://localhost:5000/api/test")
    print("🩺 Health: http://localhost:5000/health")
    print("=" * 60)
    
    # Создаем начальный файл прогресса, если его нет
    if not os.path.exists(PROGRESS_FILE):
        initial = load_progress()
        save_progress(initial)
        print("✅ Создан файл прогресса")
    
    # Запускаем сервер
    app.run(host='0.0.0.0', port=5000, debug=True)