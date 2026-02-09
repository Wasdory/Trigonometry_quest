/**
 * JavaScript для игровой страницы
 */

// Глобальные переменные
let currentTask = null;
let currentLevel = null;

// Получение параметра из URL
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// Загрузка статистики игры
async function loadGameStats() {
    try {
        const response = await fetch('/api/game/stats');
        if (!response.ok) {
            throw new Error('Ошибка загрузки статистики');
        }
        
        const stats = await response.json();
        updateUI(stats);
        
        // Проверяем уровень из URL
        const urlLevel = getUrlParameter('level');
        if (urlLevel) {
            const levelNum = parseInt(urlLevel);
            if (!isNaN(levelNum) && levelNum >= 1 && levelNum <= 5) {
                // Проверяем, доступен ли уровень
                const levelProgress = stats.levels_progress?.[levelNum];
                if (levelProgress && levelProgress.unlocked) {
                    startLevel(levelNum);
                } else {
                    showError('Этот уровень заблокирован. Завершите предыдущие уровни.');
                }
            }
        }
        
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
        showError('Не удалось загрузить статистику игры');
    }
}

// Обновление интерфейса
function updateUI(stats) {
    // Обновляем счет
    const scoreElement = document.getElementById('score');
    if (scoreElement) scoreElement.textContent = stats.score;
    
    // Обновляем общее количество задач
    const totalTasksElement = document.getElementById('total-tasks');
    if (totalTasksElement) totalTasksElement.textContent = stats.total_tasks;
    
    // Обновляем текущий уровень
    const levelDisplayElement = document.getElementById('level-display');
    if (levelDisplayElement) levelDisplayElement.textContent = stats.current_level;
    
    const currentLevelElement = document.getElementById('current-level');
    if (currentLevelElement) currentLevelElement.textContent = stats.current_level;
    
    // Обновляем количество достижений
    const achievementsCountElement = document.getElementById('achievements-count');
    if (achievementsCountElement) achievementsCountElement.textContent = stats.unlocked_achievements.length;
    
    // Обновляем достижения
    loadAchievements(stats.unlocked_achievements);
    
    // Обновляем уровни
    loadLevels(stats.levels_progress);
}

// Загрузка достижений
function loadAchievements(achievements) {
    const achievementsList = document.getElementById('achievements-list');
    if (!achievementsList) return;
    
    if (achievements.length === 0) {
        achievementsList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-star"></i>
                <p>Пока нет достижений</p>
                <small>Решайте задачи, чтобы получить достижения!</small>
            </div>
        `;
        return;
    }
    
    achievementsList.innerHTML = '';
    
    achievements.forEach(achievement => {
        const achievementItem = document.createElement('div');
        achievementItem.className = 'achievement-item';
        achievementItem.innerHTML = `
            <div class="achievement-icon">${achievement.icon}</div>
            <div class="achievement-info">
                <h5>${achievement.name}</h5>
                <p>${achievement.description}</p>
            </div>
        `;
        
        achievementsList.appendChild(achievementItem);
    });
}

// Загрузка уровней
function loadLevels(levelsProgress) {
    const levelsContainer = document.getElementById('levels-container');
    if (!levelsContainer) return;
    
    levelsContainer.innerHTML = '';
    
    for (const levelId in levelsProgress) {
        const levelData = levelsProgress[levelId];
        const progressPercent = (levelData.completed / levelData.required) * 100;
        
        const levelCard = document.createElement('div');
        levelCard.className = `level-card ${levelData.unlocked ? 'unlocked' : 'locked'}`;
        levelCard.innerHTML = `
            <h3><i class="fas fa-layer-group"></i> Уровень ${levelId}</h3>
            <div class="level-progress">
                <div class="level-progress-fill" style="width: ${progressPercent}%"></div>
            </div>
            <div class="level-stats">
                <span>Прогресс: ${levelData.completed}/${levelData.required}</span>
                <span>${Math.round(progressPercent)}%</span>
            </div>
            <div class="level-actions">
                <button class="start-level-btn" 
                        onclick="startLevel(${levelId})"
                        ${!levelData.unlocked ? 'disabled' : ''}>
                    ${levelData.unlocked ? 'Начать уровень' : 'Заблокировано'}
                </button>
            </div>
        `;
        
        levelsContainer.appendChild(levelCard);
    }
}

// Начать уровень
async function startLevel(levelId) {
    try {
        currentLevel = levelId;
        
        const response = await fetch(`/api/tasks/${levelId}`);
        if (!response.ok) {
            throw new Error('Ошибка загрузки задачи');
        }
        
        const task = await response.json();
        currentTask = task;
        
        // Показываем секцию с задачей
        const taskSection = document.getElementById('task-section');
        if (taskSection) {
            taskSection.style.display = 'block';
        }
        
        // Обновляем информацию о задаче
        const taskLevelElement = document.getElementById('task-level');
        if (taskLevelElement) {
            taskLevelElement.textContent = `Уровень ${levelId}`;
            taskLevelElement.style.color = getLevelColor(levelId);
        }
        
        const taskTextElement = document.getElementById('task-text');
        if (taskTextElement) {
            taskTextElement.textContent = task.question;
        }
        
        const taskPointsElement = document.getElementById('task-points');
        if (taskPointsElement) {
            taskPointsElement.innerHTML = `<i class="fas fa-star"></i> <span>${task.points || 10} очков</span>`;
        }
        
        // Очищаем предыдущие результаты
        const resultArea = document.getElementById('result-area');
        if (resultArea) {
            resultArea.innerHTML = '';
            resultArea.className = 'result-area';
        }
        
        const hintDisplay = document.getElementById('hint-display');
        if (hintDisplay) {
            hintDisplay.style.display = 'none';
            hintDisplay.innerHTML = '';
        }
        
        const answerInput = document.getElementById('answer-input');
        if (answerInput) {
            answerInput.value = '';
            answerInput.focus();
        }
        
        // Прокручиваем к задаче
        taskSection?.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error('Ошибка при загрузке задачи:', error);
        showError('Не удалось загрузить задачу. Попробуйте еще раз.');
    }
}

// Получить цвет уровня
function getLevelColor(levelId) {
    const colors = {
        1: '#4CAF50',
        2: '#2196F3', 
        3: '#9C27B0',
        4: '#FF9800',
        5: '#F44336'
    };
    return colors[levelId] || '#4CAF50';
}

// Проверка ответа
async function checkAnswer() {
    const answerInput = document.getElementById('answer-input');
    const resultArea = document.getElementById('result-area');
    
    if (!answerInput || !resultArea || !currentTask) return;
    
    const userAnswer = answerInput.value.trim();
    if (!userAnswer) {
        resultArea.innerHTML = '<i class="fas fa-exclamation-circle"></i> Пожалуйста, введите ответ';
        resultArea.className = 'result-area error';
        return;
    }
    
    // Показываем индикатор загрузки
    resultArea.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Проверяем ответ...';
    resultArea.className = 'result-area';
    
    try {
        const response = await fetch('/api/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                answer: userAnswer,
                task_id: currentTask.id
            })
        });
        
        if (!response.ok) {
            throw new Error('Ошибка проверки ответа');
        }
        
        const result = await response.json();
        
        if (result.correct) {
            // Ответ правильный
            resultArea.innerHTML = `
                <div class="result-success">
                    <i class="fas fa-check-circle"></i> 
                    <div>
                        <strong>${result.message}</strong>
                        <p>${result.explanation || ''}</p>
                        <p class="points-earned">Вы заработали ${result.points || 10} очков!</p>
                    </div>
                </div>
            `;
            resultArea.className = 'result-area success';
            
            // Отмечаем задачу как выполненную
            await completeTask(result.points || 10);
            
            // Очищаем поле ввода
            answerInput.value = '';
            
            // Обновляем статистику через 1 секунду
            setTimeout(() => {
                loadGameStats();
            }, 1000);
            
            // Автоматически загружаем новую задачу через 3 секунды
            setTimeout(() => {
                if (currentLevel) {
                    startLevel(currentLevel);
                }
            }, 3000);
            
        } else {
            // Ответ неправильный
            resultArea.innerHTML = `
                <div class="result-error">
                    <i class="fas fa-times-circle"></i>
                    <div>
                        <strong>${result.message}</strong>
                        <p>${result.explanation || 'Попробуйте еще раз или воспользуйтесь подсказкой.'}</p>
                    </div>
                </div>
            `;
            resultArea.className = 'result-area error';
        }
        
    } catch (error) {
        console.error('Ошибка при проверке ответа:', error);
        resultArea.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Ошибка при проверке ответа. Попробуйте еще раз.';
        resultArea.className = 'result-area error';
    }
}

// Отметить задачу как выполненную
async function completeTask(points = 10) {
    if (!currentTask) return;
    
    try {
        const response = await fetch('/api/game/complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                task_id: currentTask.id,
                score: points
            })
        });
        
        return response.ok;
        
    } catch (error) {
        console.error('Ошибка при завершении задачи:', error);
        return false;
    }
}

// Получить подсказку
async function getHint() {
    if (!currentTask) return;
    
    const hintDisplay = document.getElementById('hint-display');
    if (!hintDisplay) return;
    
    // Показываем индикатор загрузки
    hintDisplay.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Получаем подсказку...';
    hintDisplay.style.display = 'block';
    
    try {
        const response = await fetch('/api/ai/hint', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                task: currentTask.question
            })
        });
        
        if (!response.ok) {
            throw new Error('Ошибка получения подсказки');
        }
        
        const result = await response.json();
        
        if (result.hint) {
            hintDisplay.innerHTML = `
                <div class="hint-content">
                    <strong><i class="fas fa-lightbulb"></i> Подсказка:</strong>
                    <p>${result.hint}</p>
                </div>
            `;
        } else {
            hintDisplay.innerHTML = 'Подсказка временно недоступна';
        }
        
    } catch (error) {
        console.error('Ошибка при получении подсказки:', error);
        hintDisplay.innerHTML = 'Не удалось получить подсказку. Попробуйте позже.';
    }
}

// Объяснить задачу
async function explainTask() {
    if (!currentTask) return;
    
    const resultArea = document.getElementById('result-area');
    if (!resultArea) return;
    
    resultArea.innerHTML = '<i class="fas fa-spinner fa-spin"></i> AI объясняет задачу...';
    resultArea.className = 'result-area';
    
    try {
        const response = await fetch('/api/ai/explain', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                concept: currentTask.question
            })
        });
        
        if (!response.ok) {
            throw new Error('Ошибка получения объяснения');
        }
        
        const result = await response.json();
        
        if (result.explanation) {
            resultArea.innerHTML = `
                <div class="ai-explanation">
                    <strong><i class="fas fa-robot"></i> Объяснение AI:</strong>
                    <p>${result.explanation}</p>
                </div>
            `;
            resultArea.className = 'result-area success';
        } else {
            resultArea.innerHTML = 'Объяснение временно недоступно';
            resultArea.className = 'result-area error';
        }
        
    } catch (error) {
        console.error('Ошибка при получении объяснения:', error);
        resultArea.innerHTML = 'Не удалось получить объяснение. Попробуйте позже.';
        resultArea.className = 'result-area error';
    }
}

// Пропустить задачу
function skipTask() {
    const answerInput = document.getElementById('answer-input');
    const resultArea = document.getElementById('result-area');
    
    if (answerInput) answerInput.value = '';
    if (resultArea) {
        resultArea.innerHTML = '<i class="fas fa-forward"></i> Задача пропущена. Попробуйте другую задачу.';
        resultArea.className = 'result-area';
    }
    
    // Загружаем новую задачу того же уровня
    if (currentLevel) {
        setTimeout(() => {
            startLevel(currentLevel);
        }, 1000);
    }
}

// Закрыть задачу
function closeTask() {
    const taskSection = document.getElementById('task-section');
    if (taskSection) {
        taskSection.style.display = 'none';
    }
    
    currentTask = null;
}

// Сбросить прогресс
async function resetProgress() {
    if (!confirm('Вы уверены, что хотите сбросить весь прогресс? Это действие нельзя отменить.')) {
        return;
    }
    
    try {
        // В реальном проекте здесь был бы API для сброса
        // Пока просто перезагружаем страницу
        localStorage.clear();
        alert('Прогресс сброшен. Страница будет перезагружена.');
        window.location.reload();
        
    } catch (error) {
        console.error('Ошибка при сбросе прогресса:', error);
        showError('Не удалось сбросить прогресс');
    }
}

// Показать ошибку
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        <span>${message}</span>
    `;
    
    // Добавляем в начало страницы
    const container = document.querySelector('.game-main') || document.body;
    container.insertBefore(errorDiv, container.firstChild);
    
    // Убираем через 5 секунд
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    // Добавляем обработчик Enter в поле ввода
    const answerInput = document.getElementById('answer-input');
    if (answerInput) {
        answerInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                checkAnswer();
            }
        });
    }
    
    // Загружаем статистику
    loadGameStats();
    
    console.log('Игровая страница загружена');
});