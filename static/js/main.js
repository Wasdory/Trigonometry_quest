/**
 * Основной JavaScript файл для главной страницы
 */

// Показ/скрытие модального окна AI помощника
function showAIHelp() {
    const modal = document.getElementById('aiModal');
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeModal() {
    const modal = document.getElementById('aiModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Закрытие модального окна при клике вне его
window.onclick = function(event) {
    const modal = document.getElementById('aiModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

// Отправка вопроса AI
async function sendAIQuestion() {
    const questionInput = document.getElementById('aiQuestion');
    const responseDiv = document.getElementById('aiResponse');
    
    if (!questionInput || !responseDiv) return;
    
    const question = questionInput.value.trim();
    if (!question) {
        responseDiv.innerHTML = '<p style="color: #f44336;">Пожалуйста, введите вопрос</p>';
        return;
    }
    
    // Показываем индикатор загрузки
    responseDiv.innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> AI думает...</p>';
    
    try {
        const response = await fetch('/api/ai/explain', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ concept: question })
        });
        
        if (!response.ok) {
            throw new Error('Ошибка сети');
        }
        
        const data = await response.json();
        
        if (data.error) {
            responseDiv.innerHTML = `<p style="color: #f44336;">Ошибка: ${data.error}</p>`;
        } else {
            responseDiv.innerHTML = `
                <div class="ai-response-content">
                    <p><strong>Ваш вопрос:</strong> ${question}</p>
                    <div class="ai-answer">
                        <p><strong>Ответ AI:</strong> ${data.explanation}</p>
                    </div>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Ошибка при запросе к AI:', error);
        responseDiv.innerHTML = `
            <div class="ai-response-content">
                <p><strong>Ваш вопрос:</strong> ${question}</p>
                <div class="ai-answer">
                    <p><strong>Ответ AI (локальный):</strong> Попробуйте использовать табличные значения тригонометрических функций или единичную окружность для решения.</p>
                </div>
            </div>
        `;
    }
    
    // Очищаем поле ввода
    questionInput.value = '';
}

// Быстрый вопрос AI
function askAI() {
    showAIHelp();
}

// Показать информацию о проекте
function showAbout() {
    alert(`
Trigonometry Quest: AI-лаборатория

Образовательный проект для изучения тригонометрии через программирование и AI.

Возможности:
- Интерактивный игровой квест
- AI-помощник для объяснений
- Построение графиков функций
- Система достижений и прогресса

Технологии: Python, Flask, JavaScript, AI

Разработано для образовательных целей.
    `);
}

// Загрузка статистики при загрузке страницы (для будущих улучшений)
document.addEventListener('DOMContentLoaded', function() {
    // Проверка поддержки современных функций браузера
    if (!('fetch' in window)) {
        alert('Ваш браузер устарел. Пожалуйста, обновите его для использования всех функций проекта.');
    }
    
    // Добавляем обработчик Enter в поле вопроса AI
    const aiQuestionInput = document.getElementById('aiQuestion');
    if (aiQuestionInput) {
        aiQuestionInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                sendAIQuestion();
            }
        });
    }
    
    // Анимация карточек при загрузке
    const cards = document.querySelectorAll('.feature-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
    
    console.log('Trigonometry Quest загружен!');
    console.log('Доступные функции:');
    console.log('- Игровой квест: /game');
    console.log('- AI-лаборатория: /lab');
    console.log('- API документация: /api/docs');
});