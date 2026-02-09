"""
Модуль для построения графиков функций
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Для работы без GUI
import matplotlib.pyplot as plt
import io
import base64
import math

class FunctionPlotter:
    def __init__(self):
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    def plot_function(self, func_str, x_range=(-2*np.pi, 2*np.pi), title=None):
        """Создает график функции и возвращает base64 изображение"""
        try:
            # Генерация данных
            x = np.linspace(x_range[0], x_range[1], 1000)
            
            # Вычисление y
            y = self._evaluate_function(func_str, x)
            
            # Создание графика
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(x, y, color=self.colors[0], linewidth=2, label=func_str)
            
            # Настройки графика
            ax.axhline(y=0, color='black', linewidth=0.5, alpha=0.5)
            ax.axvline(x=0, color='black', linewidth=0.5, alpha=0.5)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_xlabel('x', fontsize=12)
            ax.set_ylabel('f(x)', fontsize=12)
            
            # Настройка делений на оси X
            x_ticks = np.arange(-2*np.pi, 2.5*np.pi, np.pi/2)
            x_labels = []
            for val in x_ticks:
                if val == 0:
                    x_labels.append('0')
                elif val == np.pi:
                    x_labels.append('π')
                elif val == -np.pi:
                    x_labels.append('-π')
                elif val == np.pi/2:
                    x_labels.append('π/2')
                elif val == -np.pi/2:
                    x_labels.append('-π/2')
                else:
                    x_labels.append(f'{val/np.pi:.1f}π' if abs(val) > 0.1 else '0')
            
            ax.set_xticks(x_ticks)
            ax.set_xticklabels(x_labels)
            
            if title:
                ax.set_title(title, fontsize=14, pad=20)
            else:
                ax.set_title(f'График функции: {func_str}', fontsize=14, pad=20)
            
            ax.legend()
            ax.set_xlim(x_range)
            
            # Конвертация в base64
            img = io.BytesIO()
            plt.tight_layout()
            plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            plt.close(fig)
            
            return f"data:image/png;base64,{plot_url}"
            
        except Exception as e:
            print(f"Ошибка при построении графика: {e}")
            # Возвращаем пустое изображение при ошибке
            return self._get_error_image(str(e))
    
    def _make_function_safe(self, func_str):
        """Делает функцию безопасной для вычисления"""
        safe = func_str.replace('^', '**')
        safe = safe.replace('sin', 'np.sin')
        safe = safe.replace('cos', 'np.cos')
        safe = safe.replace('tan', 'np.tan')
        safe = safe.replace('π', 'np.pi')
        safe = safe.replace('pi', 'np.pi')
        safe = safe.replace('sqrt', 'np.sqrt')
        return safe
    
    def _evaluate_function(self, func_str, x_values):
        """Безопасное вычисление функции"""
        try:
            # Простые функции
            if func_str == 'sin(x)':
                return np.sin(x_values)
            elif func_str == 'cos(x)':
                return np.cos(x_values)
            elif func_str == 'tan(x)':
                return np.tan(x_values)
            elif func_str == 'sin(2*x)':
                return np.sin(2 * x_values)
            elif func_str == 'cos(2*x)':
                return np.cos(2 * x_values)
            elif func_str == 'sin(x) + cos(x)':
                return np.sin(x_values) + np.cos(x_values)
            elif func_str == '2*sin(x)':
                return 2 * np.sin(x_values)
            elif func_str == 'sin(x)*cos(x)':
                return np.sin(x_values) * np.cos(x_values)
            else:
                # Пробуем безопасное вычисление
                return self._safe_eval_simple(func_str, x_values)
        except:
            return np.zeros_like(x_values)
    
    def _safe_eval_simple(self, expr, x):
        """Простое безопасное вычисление"""
        # Разрешенные функции
        ALLOWED = {
            'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
            'pi': np.pi, 'np': np
        }
        
        # Безопасная замена
        expr = expr.replace('^', '**')
        expr = expr.replace('π', 'pi')
        
        try:
            # Простая проверка
            forbidden = ['__', 'import', 'eval', 'exec', 'open', 'os.', 'sys.']
            for word in forbidden:
                if word in expr.lower():
                    raise ValueError(f"Запрещенное выражение: {word}")
            
            # Создаем безопасное окружение
            safe_env = {'x': x, 'np': np}
            safe_env.update(ALLOWED)
            
            # Вычисляем
            return eval(expr, {"__builtins__": None}, safe_env)
        except Exception as e:
            print(f"Ошибка вычисления {expr}: {e}")
            raise
    
    def _get_error_image(self, error_msg):
        """Создает изображение с сообщением об ошибке"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f'Ошибка построения графика:\n{error_msg}',
                horizontalalignment='center',
                verticalalignment='center',
                transform=ax.transAxes,
                fontsize=12,
                color='red')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        img = io.BytesIO()
        plt.tight_layout()
        plt.savefig(img, format='png', dpi=100)
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close(fig)
        
        return f"data:image/png;base64,{plot_url}"
    
    def plot_multiple(self, functions, x_range=(-2*np.pi, 2*np.pi)):
        """Строит несколько функций на одном графике"""
        try:
            x = np.linspace(x_range[0], x_range[1], 1000)
            
            fig, ax = plt.subplots(figsize=(12, 7))
            
            for i, func_str in enumerate(functions):
                try:
                    y = self._evaluate_function(func_str, x)
                    ax.plot(x, y, color=self.colors[i % len(self.colors)], 
                           linewidth=2, label=func_str)
                except Exception as e:
                    print(f"Ошибка при построении {func_str}: {e}")
                    continue
            
            ax.axhline(y=0, color='black', linewidth=0.5, alpha=0.5)
            ax.axvline(x=0, color='black', linewidth=0.5, alpha=0.5)
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('x', fontsize=12)
            ax.set_ylabel('f(x)', fontsize=12)
            ax.set_title('Сравнение тригонометрических функций', fontsize=14, pad=20)
            ax.legend()
            ax.set_xlim(x_range)
            
            img = io.BytesIO()
            plt.tight_layout()
            plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            plt.close(fig)
            
            return f"data:image/png;base64,{plot_url}"
            
        except Exception as e:
            print(f"Ошибка при построении нескольких графиков: {e}")
            return self._get_error_image(str(e))