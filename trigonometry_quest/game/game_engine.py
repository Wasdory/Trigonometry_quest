import json
import os
from datetime import datetime
import sys

class GameEngine:
    def __init__(self, save_file="game_data.json"):
        self.save_file = save_file
        self.player_data = self.load_game_data()
    
    def load_game_data(self):
        """Загружает данные игры"""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Проверяем структуру данных
                    if isinstance(data, dict):
                        return data
            else:
                # Создаем файл с начальными данными
                initial_data = self.get_initial_data()
                self.save_game_data(initial_data)
                return initial_data
                
        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка загрузки данных игры: {e}")
            # Возвращаем начальные данные при ошибке
            return self.get_initial_data()
    
    def get_initial_data(self):
        """Возвращает начальные данные игры"""
        return {
            "score": 0,
            "current_level": 1,
            "completed_tasks": [],
            "unlocked_achievements": [],
            "daily_stats": {},
            "level_progress": {
                "1": {"completed": 0, "required": 2, "unlocked": True},
                "2": {"completed": 0, "required": 2, "unlocked": False},
                "3": {"completed": 0, "required": 2, "unlocked": False},
                "4": {"completed": 0, "required": 2, "unlocked": False},
                "5": {"completed": 0, "required": 2, "unlocked": False}
            }
        }
    
    def save_game_data(self, data=None):
        """Сохраняет данные игры"""
        try:
            if data is None:
                data = self.player_data
                
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"Ошибка сохранения данных игры: {e}")
            return False
    
    def complete_task(self, task_id, score_earned=10):
        """Отмечает выполнение задачи"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Проверяем, не решали ли уже эту задачу
            if task_id not in self.player_data["completed_tasks"]:
                # Добавляем задачу в список выполненных
                self.player_data["completed_tasks"].append(task_id)
                
                # Увеличиваем счет
                self.player_data["score"] += score_earned
                
                # Обновляем ежедневную статистику
                if today not in self.player_data["daily_stats"]:
                    self.player_data["daily_stats"][today] = 0
                self.player_data["daily_stats"][today] += 1
                
                # Определяем уровень задачи
                task_level = self._extract_level_from_task_id(task_id)
                
                if task_level:
                    # Обновляем прогресс по уровню
                    level_key = str(task_level)
                    if level_key in self.player_data["level_progress"]:
                        self.player_data["level_progress"][level_key]["completed"] += 1
                        
                        # Проверяем, завершен ли уровень
                        if self.player_data["level_progress"][level_key]["completed"] >= self.player_data["level_progress"][level_key]["required"]:
                            # Уровень завершен, разблокируем следующий
                            next_level = task_level + 1
                            if next_level <= 5:
                                next_level_key = str(next_level)
                                self.player_data["level_progress"][next_level_key]["unlocked"] = True
                                self.player_data["current_level"] = next_level
                
                # Проверяем достижения
                self._check_achievements()
                
                # Сохраняем изменения
                self.save_game_data()
                return True
                
            return False  # Задача уже была выполнена
            
        except Exception as e:
            print(f"Ошибка при завершении задачи: {e}")
            return False
    
    def _extract_level_from_task_id(self, task_id):
        """Извлекает номер уровня из ID задачи"""
        try:
            # Формат: level_X_task_Y
            if task_id.startswith("level_") and "_task_" in task_id:
                parts = task_id.split("_")
                if len(parts) >= 2:
                    return int(parts[1])
        except:
            pass
        return None
    
    def _check_achievements(self):
        """Проверяет и разблокирует достижения"""
        try:
            total_tasks = len(self.player_data["completed_tasks"])
            today = datetime.now().strftime("%Y-%m-%d")
            
            achievements = {
                "first_step": {"unlocked": False, "condition": total_tasks >= 1},
                "fast_learner": {"unlocked": False, "condition": self.player_data["daily_stats"].get(today, 0) >= 3},
                "level_master": {"unlocked": False, "condition": self.player_data["level_progress"]["1"]["completed"] >= 2},
                "persistent": {"unlocked": False, "condition": total_tasks >= 5},
                "math_master": {"unlocked": False, "condition": all(
                    self.player_data["level_progress"][str(i)]["completed"] >= 2 for i in range(1, 6)
                )}
            }
            
            # Проверяем каждое достижение
            for ach_id, ach_data in achievements.items():
                if ach_data["condition"] and ach_id not in self.player_data["unlocked_achievements"]:
                    self.player_data["unlocked_achievements"].append(ach_id)
                    
        except Exception as e:
            print(f"Ошибка при проверке достижений: {e}")
    
    def get_player_stats(self):
        """Возвращает статистику игрока"""
        try:
            # Достижения
            achievements_data = {
                "first_step": {"name": "Первые шаги", "description": "Решите первую задачу", "icon": "🥇"},
                "fast_learner": {"name": "Быстрый ученик", "description": "Решите 3 задачи за один день", "icon": "⚡"},
                "level_master": {"name": "Мастер уровня", "description": "Завершите первый уровень", "icon": "🎯"},
                "persistent": {"name": "Упорный ученик", "description": "Решите 5 задач", "icon": "💪"},
                "math_master": {"name": "Мастер математики", "description": "Завершите все уровни", "icon": "👑"}
            }
            
            unlocked_achievements = []
            for ach_id in self.player_data.get("unlocked_achievements", []):
                if ach_id in achievements_data:
                    unlocked_achievements.append(achievements_data[ach_id])
            
            # Прогресс по уровням
            levels_progress = {}
            for level_id in range(1, 6):
                level_key = str(level_id)
                if level_key in self.player_data.get("level_progress", {}):
                    progress = self.player_data["level_progress"][level_key]
                    levels_progress[level_id] = {
                        "completed": progress.get("completed", 0),
                        "required": progress.get("required", 2),
                        "unlocked": progress.get("unlocked", level_id == 1)
                    }
            
            return {
                "score": self.player_data.get("score", 0),
                "current_level": self.player_data.get("current_level", 1),
                "total_tasks": len(self.player_data.get("completed_tasks", [])),
                "unlocked_achievements": unlocked_achievements,
                "levels_progress": levels_progress,
                "daily_stats": self.player_data.get("daily_stats", {})
            }
            
        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
            return self.get_initial_data()
    
    def reset_game(self):
        """Сбрасывает игру"""
        try:
            self.player_data = self.get_initial_data()
            self.save_game_data()
            return True
        except Exception as e:
            print(f"Ошибка при сбросе игры: {e}")
            return False