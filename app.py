#!/usr/bin/env python3
"""
Trigonometry Quest - Полноценный сервер с графиками и AI
"""

import os
import json
import random
import math
import re
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, static_folder='static', template_folder='templates')

# ========== ПРОВЕРКА НАЛИЧИЯ MATPLOTLIB ДЛЯ ГРАФИКОВ ==========
try:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io
    import base64
    MATPLOTLIB_AVAILABLE = True
    print("✅ Matplotlib доступен, графики работают")
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️ Matplotlib не установлен, графики недоступны. Установите: pip install matplotlib numpy")

# ========== УМНАЯ ПРОВЕРКА ОТВЕТОВ ==========
def normalize_math(expr):
    expr = expr.strip().lower().replace('пи', 'pi').replace('π', 'pi').replace('√', 'sqrt')
    expr = re.sub(r'\s+', '', expr)
    expr = re.sub(r'(\d)([a-z])', r'\1*\2', expr)
    expr = re.sub(r'([a-z])(\d)', r'\1*\2', expr)
    expr = re.sub(r'sqrt(\d+)', r'sqrt(\1)', expr)
    expr = expr.replace('^', '**').replace('²', '**2')
    return expr

def safe_eval(expr):
    allowed = {'pi': math.pi, 'e': math.e,
               'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
               'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
               'sqrt': math.sqrt, 'abs': abs}
    try:
        res = eval(expr, {"__builtins__": {}}, allowed)
        return round(res, 10) if isinstance(res, (int, float)) else None
    except:
        return None

def compare_answers(user, correct, eps=1e-7):
    if re.sub(r'\s+', '', user.lower()) == re.sub(r'\s+', '', correct.lower()):
        return True
    uv = safe_eval(normalize_math(user))
    cv = safe_eval(normalize_math(correct))
    if uv is not None and cv is not None:
        return abs(uv - cv) < eps
    return normalize_math(user) == normalize_math(correct)

# ========== БАЗА ДАННЫХ ЗАДАЧ ==========
TASKS = {
    1: [
        {"id": "level_1_task_1", "question": "sin(30°) = ?", "answer": "1/2", "points": 10},
        {"id": "level_1_task_2", "question": "cos(60°) = ?", "answer": "1/2", "points": 10},
        {"id": "level_1_task_3", "question": "tg(45°) = ?", "answer": "1", "points": 10}
    ],
    2: [
        {"id": "level_2_task_1", "question": "sin(x) = 0.5, наименьший положительный x (в радианах):", "answer": "π/6", "points": 15},
        {"id": "level_2_task_2", "question": "cos(x) = √2/2, x (в радианах):", "answer": "π/4", "points": 15},
        {"id": "level_2_task_3", "question": "tg(x) = 1, x (в радианах):", "answer": "π/4", "points": 15}
    ],
    3: [
        {"id": "level_3_task_1", "question": "Период функции y = sin(2x):", "answer": "π", "points": 20},
        {"id": "level_3_task_2", "question": "Область значений y = 3cos(x) + 1 (в формате [min; max]):", "answer": "[-2;4]", "points": 20},
        {"id": "level_3_task_3", "question": "Чему равно sin(π/2)?", "answer": "1", "points": 20}
    ],
    4: [
        {"id": "level_4_task_1", "question": "Упростите: (1 - sin²(x)) / cos²(x) = ?", "answer": "1", "points": 25},
        {"id": "level_4_task_2", "question": "Упростите: tg(x) * cos(x) = ?", "answer": "sin(x)", "points": 25},
        {"id": "level_4_task_3", "question": "Формула приведения: sin(π/2 - x) = ?", "answer": "cos(x)", "points": 25}
    ],
    5: [
        {"id": "level_5_task_1", "question": "Формула двойного угла для sin(2x):", "answer": "2sin(x)cos(x)", "points": 30},
        {"id": "level_5_task_2", "question": "Формула двойного угла для cos(2x) (через sin² и cos²):", "answer": "cos²(x)-sin²(x)", "points": 30},
        {"id": "level_5_task_3", "question": "sin(15°)cos(15°) = ? (дробь)", "answer": "1/2", "points": 30}
    ]
}

LEVELS_INFO = {
    1: {"name": "Основы", "desc": "Базовые значения sin, cos, tg", "icon": "🔢", "color": "#4CAF50"},
    2: {"name": "Уравнения", "desc": "Решение простых уравнений", "icon": "📐", "color": "#2196F3"},
    3: {"name": "Свойства и графики", "desc": "Период, область значений", "icon": "📊", "color": "#9C27B0"},
    4: {"name": "Тождества", "desc": "Тригонометрические тождества", "icon": "🧮", "color": "#FF9800"},
    5: {"name": "Формулы", "desc": "Формулы двойного угла", "icon": "🎯", "color": "#E91E63"}
}

PROGRESS_FILE = "user_progress.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data.setdefault("score", 0)
                data.setdefault("completed_tasks", [])
                data.setdefault("level_progress", {})
                data.setdefault("unlocked_achievements", [])
                for i in range(1, 6):
                    key = str(i)
                    if key not in data["level_progress"]:
                        data["level_progress"][key] = {"completed": 0, "unlocked": (i == 1)}
                return data
        except:
            pass
    initial = {
        "score": 0,
        "completed_tasks": [],
        "level_progress": {str(i): {"completed": 0, "unlocked": (i == 1)} for i in range(1, 6)},
        "unlocked_achievements": []
    }
    return initial

def save_progress(data):
    try:
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

# ========== ДОСТИЖЕНИЯ (только данные) ==========
ACHIEVEMENTS_DATA = {
    "first_step": {"name": "Первые шаги", "desc": "Решите 1 задачу", "icon": "🥇", "need_tasks": 1},
    "level_1": {"name": "Знаток основ", "desc": "Завершите уровень 1", "icon": "📐", "need_level": 1},
    "level_2": {"name": "Решатель уравнений", "desc": "Завершите уровень 2", "icon": "📏", "need_level": 2},
    "level_3": {"name": "Мастер свойств", "desc": "Завершите уровень 3", "icon": "📊", "need_level": 3},
    "level_4": {"name": "Знаток тождеств", "desc": "Завершите уровень 4", "icon": "🧮", "need_level": 4},
    "level_5": {"name": "Гуру формул", "desc": "Завершите уровень 5", "icon": "🎯", "need_level": 5},
    "task_10": {"name": "Тригонометрический ниндзя", "desc": "Решите 10 задач", "icon": "⚡", "need_tasks": 10},
    "task_25": {"name": "Легенда тригонометрии", "desc": "Решите 25 задач", "icon": "👑", "need_tasks": 25}
}

def check_achievements(progress):
    total_tasks = len(progress["completed_tasks"])
    unlocked = set(progress.get("unlocked_achievements", []))
    changed = False
    for ach_id, ach in ACHIEVEMENTS_DATA.items():
        if ach_id in unlocked:
            continue
        if "need_tasks" in ach and total_tasks >= ach["need_tasks"]:
            unlocked.add(ach_id)
            changed = True
        elif "need_level" in ach:
            level_key = str(ach["need_level"])
            if progress["level_progress"].get(level_key, {}).get("completed", 0) >= 2:
                unlocked.add(ach_id)
                changed = True
    if changed:
        progress["unlocked_achievements"] = list(unlocked)
        save_progress(progress)
    return list(unlocked)

# ========== ГРАФИКИ ==========
@app.route('/api/plot/simple', methods=['POST'])
def plot_simple_function():
    if not MATPLOTLIB_AVAILABLE:
        return jsonify({"success": False, "error": "Matplotlib не установлен. Установите: pip install matplotlib numpy"})

    data = request.json
    if not data:
        return jsonify({"success": False, "error": "Нет данных"})

    compute_func = data.get('function', 'sin(x)')
    display_name = data.get('display_name', compute_func)
    # Для отображения заменяем tan на tg
    display_name = display_name.replace('tan', 'tg')

    try:
        x = np.linspace(-2 * np.pi, 2 * np.pi, 1000)
        # Заменяем tg на tan для вычислений
        compute_func = compute_func.replace('tg', 'tan')

        if compute_func == 'sin(x)':
            y = np.sin(x)
        elif compute_func == 'cos(x)':
            y = np.cos(x)
        elif compute_func == 'tan(x)':
            y = np.tan(x)
            y = np.clip(y, -10, 10)
        elif compute_func == 'sin(2*x)':
            y = np.sin(2 * x)
        elif compute_func == 'cos(2*x)':
            y = np.cos(2 * x)
        elif compute_func == 'sin(x) + cos(x)':
            y = np.sin(x) + np.cos(x)
        elif compute_func == '2*sin(x)':
            y = 2 * np.sin(x)
        elif compute_func == 'sin(x)*cos(x)':
            y = np.sin(x) * np.cos(x)
        else:
            # Безопасное вычисление
            safe_func = compute_func.replace('^', '**').replace('π', 'pi')
            allowed = {'sin': np.sin, 'cos': np.cos, 'tan': np.tan, 'pi': np.pi, 'e': np.e, 'x': x}
            y = eval(safe_func, {"__builtins__": {}}, allowed)
            if 'tan' in safe_func:
                y = np.clip(y, -10, 10)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(x, y, color='#4CAF50', linewidth=3, label=display_name)
        ax.axhline(0, color='black', linewidth=0.5, alpha=0.5)
        ax.axvline(0, color='black', linewidth=0.5, alpha=0.5)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('x')
        ax.set_ylabel('f(x)')
        ax.set_title(f'График: {display_name}')
        ax.legend()

        # Настройка подписей оси X
        x_ticks = np.arange(-2*np.pi, 2.5*np.pi, np.pi/2)
        x_labels = []
        for val in x_ticks:
            if val == 0: x_labels.append('0')
            elif val == np.pi: x_labels.append('π')
            elif val == -np.pi: x_labels.append('-π')
            elif val == np.pi/2: x_labels.append('π/2')
            elif val == -np.pi/2: x_labels.append('-π/2')
            elif val == 2*np.pi: x_labels.append('2π')
            elif val == -2*np.pi: x_labels.append('-2π')
            else: x_labels.append(f'{val/np.pi:.1f}π')
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_labels)
        ax.set_xlim(-2*np.pi, 2*np.pi)
        ax.set_ylim(-3, 3)
        if 'tan' in compute_func:
            ax.set_ylim(-5, 5)

        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plot_url = base64.b64encode(buf.getvalue()).decode()
        plt.close(fig)
        return jsonify({"success": True, "plot": f"data:image/png;base64,{plot_url}", "function": display_name})
    except Exception as e:
        print("Ошибка построения графика:", e)
        return jsonify({"success": False, "error": str(e)})

# ========== AI ПОМОЩНИК (полная версия) ==========
@app.route('/api/ai/hint', methods=['POST'])
def get_hint():
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "Нет данных"})
    question = data.get('question', '').lower()
    hints = {
        "sin(30": "sin(30°) = 1/2 = 0.5",
        "cos(60": "cos(60°) = 1/2 = 0.5",
        "tg(45": "tg(45°) = 1",
        "sin(x) = 0.5": "sin(x) = 0.5 при x = π/6 (30°) или 5π/6 (150°)",
        "cos(x) = √2/2": "cos(x) = √2/2 при x = π/4 (45°) или 7π/4 (315°)",
        "tg(x) = 1": "tg(x) = 1 при x = π/4 (45°)",
        "период sin": "Период sin(x) и cos(x) равен 2π",
        "sin²+cos²": "Основное тригонометрическое тождество: sin²(x) + cos²(x) = 1",
        "1+tg²": "1 + tg²(x) = sec²(x)",
        "sin(π/2 - x)": "Формула приведения: sin(π/2 - x) = cos(x)",
        "sin(2x)": "Формула двойного угла: sin(2x) = 2·sin(x)·cos(x)",
        "cos(2x)": "cos(2x) = cos²(x) - sin²(x) = 2cos²(x) - 1 = 1 - 2sin²(x)"
    }
    for key, hint in hints.items():
        if key in question:
            return jsonify({"success": True, "hint": hint})
    return jsonify({"success": True, "hint": "Попробуйте использовать единичную окружность или табличные значения. Подробнее спросите у AI-помощника на главной странице."})

@app.route('/api/ai/explain', methods=['POST'])
def explain_concept():
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "Нет данных"})
    concept = data.get('concept', '').lower()

    explanations = {
        "синус": "**Синус** угла в прямоугольном треугольнике — отношение противолежащего катета к гипотенузе. На единичной окружности синус — это координата Y точки.",
        "sin": "**Синус** — тригонометрическая функция. В прямоугольном треугольнике: sin(α) = противолежащий катет / гипотенуза.",
        "косинус": "**Косинус** угла — отношение прилежащего катета к гипотенузе. На единичной окружности косинус — координата X точки.",
        "cos": "**Косинус** — тригонометрическая функция. cos(α) = прилежащий катет / гипотенуза.",
        "тангенс": "**Тангенс** угла — отношение противолежащего катета к прилежащему, или sin(α)/cos(α). Обозначается tg или tan.",
        "tg": "**Тангенс** (tg) — sin(α)/cos(α). В прямоугольном треугольнике: tg(α) = противолежащий катет / прилежащий.",
        "tan": "**Тангенс** (tan) — то же, что и tg.",
        "котангенс": "**Котангенс** — отношение прилежащего катета к противолежащему, или cos(α)/sin(α). Обозначается ctg или cot.",
        "секанс": "**Секанс** — sec(α) = 1/cos(α).",
        "косеканс": "**Косеканс** — csc(α) = 1/sin(α).",
        "арксинус": "**Арксинус** (arcsin) — обратная функция к синусу. arcsin(x) — угол, синус которого равен x.",
        "арккосинус": "**Арккосинус** (arccos) — обратная функция к косинусу.",
        "арктангенс": "**Арктангенс** (arctg) — обратная функция к тангенсу.",
        "тригонометрия": "**Тригонометрия** — раздел математики, изучающий тригонометрические функции (sin, cos, tg и др.) и их применение в геометрии.",
        "единичная окружность": "**Единичная окружность** — окружность радиусом 1 с центром в начале координат. Используется для определения тригонометрических функций: точка на окружности имеет координаты (cos α, sin α).",
        "радиан": "**Радиан** — единица измерения углов. Угол в 1 радиан — центральный угол, опирающийся на дугу длиной в радиус. π радиан = 180°.",
        "градус": "**Градус** — 1/360 часть полного оборота. 90° = π/2 радиан, 180° = π радиан.",
        "теорема пифагора": "**Теорема Пифагора**: В прямоугольном треугольнике квадрат гипотенузы равен сумме квадратов катетов: a² + b² = c².",
        "основное тригонометрическое тождество": "**sin²α + cos²α = 1** — выполняется для любого угла α.",
        "формулы приведения": "Формулы приведения позволяют выразить sin(π/2 ± α), cos(π ± α) и т.д. через sin α, cos α. Например: sin(π/2 - α) = cos α, cos(π/2 - α) = sin α.",
        "формулы сложения": "sin(α±β) = sinα·cosβ ± cosα·sinβ, cos(α±β) = cosα·cosβ ∓ sinα·sinβ.",
        "формулы двойного угла": "sin(2α) = 2·sinα·cosα, cos(2α) = cos²α - sin²α = 2cos²α - 1 = 1 - 2sin²α, tg(2α) = 2tgα/(1 - tg²α)."
    }
    # Ищем наиболее полное совпадение
    best_key = None
    for key in explanations:
        if key in concept:
            if best_key is None or len(key) > len(best_key):
                best_key = key
    if best_key:
        return jsonify({"success": True, "explanation": explanations[best_key]})
    return jsonify({
        "success": True,
        "explanation": "**Тригонометрия** — раздел математики о связях углов и сторон треугольников. Основные функции: sin, cos, tg. Задайте конкретный вопрос, например: 'Что такое синус?', 'Что такое радиан?', 'Формулы двойного угла'."
    })

# ========== ОСТАЛЬНЫЕ МАРШРУТЫ ==========
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/game')
def game():
    return render_template('game.html')

@app.route('/levels')
def levels_page():
    return render_template('levels.html')

@app.route('/lab')
def lab():
    return render_template('lab.html')

@app.route('/api/levels')
def api_levels():
    prog = load_progress()
    levels_data = {}
    for i in range(1, 6):
        key = str(i)
        prog_level = prog["level_progress"].get(key, {"completed": 0, "unlocked": i == 1})
        if i > 1 and prog["level_progress"].get(str(i-1), {}).get("completed", 0) >= 2:
            prog_level["unlocked"] = True
        levels_data[key] = {
            "id": i,
            "name": LEVELS_INFO[i]["name"],
            "desc": LEVELS_INFO[i]["desc"],
            "icon": LEVELS_INFO[i]["icon"],
            "color": LEVELS_INFO[i]["color"],
            "unlocked": prog_level["unlocked"],
            "completed": prog_level["completed"],
            "tasks_count": len(TASKS[i])
        }
    return jsonify({"success": True, "levels": levels_data})

@app.route('/api/tasks/<int:level_id>')
def get_task(level_id):
    if level_id not in TASKS:
        return jsonify({"success": False, "error": "Уровень не найден"})
    prog = load_progress()
    completed = prog["completed_tasks"]
    available = [t for t in TASKS[level_id] if t["id"] not in completed]
    task = random.choice(available) if available else random.choice(TASKS[level_id])
    return jsonify({
        "success": True,
        "task": {
            "id": task["id"],
            "question": task["question"],
            "points": task["points"],
            "level": level_id,
            "correct_answer": task["answer"]
        }
    })

@app.route('/api/check', methods=['POST'])
def check_answer():
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "Нет данных"})
    user = data.get('answer', '').strip()
    task_id = data.get('task_id')
    for level, tasks in TASKS.items():
        for t in tasks:
            if t["id"] == task_id:
                correct = compare_answers(user, t["answer"])
                if correct:
                    prog = load_progress()
                    if task_id not in prog["completed_tasks"]:
                        prog["completed_tasks"].append(task_id)
                        prog["score"] += t["points"]
                        lvl = int(task_id.split("_")[1])
                        lk = str(lvl)
                        if lk not in prog["level_progress"]:
                            prog["level_progress"][lk] = {"completed": 0, "unlocked": True}
                        prog["level_progress"][lk]["completed"] += 1
                        if prog["level_progress"][lk]["completed"] >= 2 and lvl < 5:
                            prog["level_progress"][str(lvl+1)]["unlocked"] = True
                        check_achievements(prog)
                        save_progress(prog)
                return jsonify({
                    "success": True,
                    "correct": correct,
                    "message": "✅ Верно!" if correct else f"❌ Неверно. Правильный ответ: {t['answer']}",
                    "points": t["points"] if correct else 0
                })
    return jsonify({"success": False, "error": "Задача не найдена"})

@app.route('/api/game/stats')
def game_stats():
    prog = load_progress()
    unlocked_ids = check_achievements(prog)
    unlocked_list = [ACHIEVEMENTS_DATA[aid] for aid in unlocked_ids if aid in ACHIEVEMENTS_DATA]
    return jsonify({
        "success": True,
        "score": prog["score"],
        "total_tasks": len(prog["completed_tasks"]),
        "level_progress": prog["level_progress"],
        "unlocked_achievements": unlocked_list
    })

@app.route('/api/game/complete', methods=['POST'])
def complete_task():
    data = request.json
    tid = data.get('task_id')
    if not tid:
        return jsonify({"success": False, "error": "Нет ID"})
    prog = load_progress()
    if tid in prog["completed_tasks"]:
        return jsonify({"success": False, "error": "Уже выполнена"})
    prog["completed_tasks"].append(tid)
    prog["score"] += data.get("score", 10)
    check_achievements(prog)
    save_progress(prog)
    return jsonify({"success": True})

@app.route('/api/game/reset', methods=['POST'])
def reset_game():
    initial = {
        "score": 0,
        "completed_tasks": [],
        "level_progress": {str(i): {"completed": 0, "unlocked": (i == 1)} for i in range(1,6)},
        "unlocked_achievements": []
    }
    save_progress(initial)
    return jsonify({"success": True})

@app.route('/health')
def health():
    return jsonify({"status": "ok", "matplotlib": MATPLOTLIB_AVAILABLE})

if __name__ == '__main__':
    if not os.path.exists(PROGRESS_FILE):
        save_progress(load_progress())
    print("🚀 Сервер запущен: http://localhost:5000")
    if MATPLOTLIB_AVAILABLE:
        print("✅ Графики доступны")
    else:
        print("⚠️ Графики недоступны, установите matplotlib и numpy")
    app.run(host='0.0.0.0', port=5000, debug=True)