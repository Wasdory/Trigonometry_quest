/**
 * JavaScript для страницы лаборатории
 */

let functionsList = ['sin(x)'];
let graphHistory = [];

// Построить график функции
async function plotFunction() {
    const functionInput = document.getElementById('function-input');
    const xMinInput = document.getElementById('x-min');
    const xMaxInput = document.getElementById('x-max');
    const plotContainer = document.getElementById('plot-container');
    
    if (!functionInput || !plotContainer) return;
    
    const func = functionInput.value.trim();
    if (!func) {
        alert('Пожалуйста, введите функцию');
        return;
    }
    
    const xMin = xMinInput ? parseFloat(xMinInput.value) || -2 * Math.PI : -2 * Math.PI;
    const xMax = xMaxInput ? parseFloat(xMaxInput.value) || 2 * Math.PI : 2 * Math.PI;
    
    if (xMin >= xMax) {
        alert('Минимальное значение X должно быть меньше максимального');
        return;
    }
    
    // Показываем индикатор загрузки
    plotContainer.innerHTML = `
        <div class="plot-placeholder">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Строим график...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/api/plot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                function: func,
                x_min: xMin,
                x_max: xMax
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Ошибка построения графика');
        }
        
        const result = await response.json();
        
        if (result.plot) {
            plotContainer.innerHTML = `<img src="${result.plot}" alt="График функции ${func}" style="width: 100%; height: auto;">`;
            
            // Добавляем в историю
            addToGraphHistory(func, xMin, xMax, result.plot);
            
            // Добавляем функцию в список, если ее там еще нет
            if (!functionsList.includes(func)) {
                functionsList.push(func);
                updateFunctionsList();
            }
            
        } else if (result.error) {
            throw new Error(result.error);
        }
        
    } catch (error) {
        console.error('Ошибка при построении графика:', error);
        plotContainer.innerHTML = `
            <div class="plot-placeholder">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Ошибка построения графика</p>
                <small>${error.message}</small>
                <p>Проверьте синтаксис функции и попробуйте еще раз.</p>
            </div>
        `;
    }
}

// Добавить функцию в список
function addFunction() {
    const functionInput = document.getElementById('function-input');
    if (!functionInput) return;
    
    const func = functionInput.value.trim();
    if (!func) {
        alert('Пожалуйста, введите функцию');
        return;
    }
    
    if (!functionsList.includes(func)) {
        functionsList.push(func);
        updateFunctionsList();
        
        // Очищаем поле ввода
        functionInput.value = '';
        functionInput.placeholder = 'Введите следующую функцию...';
        
        alert(`Функция "${func}" добавлена в список. Постройте графики, чтобы увидеть все функции вместе.`);
    } else {
        alert('Эта функция уже есть в списке');
    }
}

// Обновить список функций
function updateFunctionsList() {
    const functionsListElement = document.getElementById('functions-list');
    if (!functionsListElement) return;
    
    functionsListElement.innerHTML = '';
    
    functionsList.forEach((func, index) => {
        const li = document.createElement('li');
        li.innerHTML = `
            ${func} 
            <button onclick="removeFunction(${index})">
                <i class="fas fa-times"></i>
            </button>
        `;
        functionsListElement.appendChild(li);
    });
}

// Удалить функцию из списка
function removeFunction(index) {
    if (index >= 0 && index < functionsList.length) {
        functionsList.splice(index, 1);
        updateFunctionsList();
    }
}

// Очистить все графики
function clearGraphs() {
    const plotContainer = document.getElementById('plot-container');
    if (plotContainer) {
        plotContainer.innerHTML = `
            <div class="plot-placeholder">
                <i class="fas fa-chart-area"></i>
                <p>График появится здесь</p>
                <small>Введите функцию и нажмите "Построить график"</small>
            </div>
        `;
    }
    
    functionsList = ['sin(x)'];
    updateFunctionsList();
    
    const functionInput = document.getElementById('function-input');
    if (functionInput) {
        functionInput.value = 'sin(x)';
    }
}

// Добавить в историю графиков
function addToGraphHistory(func, xMin, xMax, plotUrl) {
    const historyItem = {
        func: func,
        xMin: xMin,
        xMax: xMax,
        plotUrl: plotUrl,
        timestamp: new Date().toLocaleTimeString()
    };
    
    graphHistory.unshift(historyItem);
    
    // Ограничиваем историю 10 элементами
    if (graphHistory.length > 10) {
        graphHistory = graphHistory.slice(0, 10);
    }
    
    updateGraphHistory();
}

// Обновить историю графиков
function updateGraphHistory() {
    const historyContainer = document.getElementById('graph-history');
    if (!historyContainer) return;
    
    if (graphHistory.length === 0) {
        historyContainer.innerHTML = '<p class="empty-history">Нет сохраненных графиков</p>';
        return;
    }
    
    historyContainer.innerHTML = '';
    
    graphHistory.forEach((item, index) => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <div class="history-preview">
                <img src="${item.plotUrl}" alt="График ${item.func}" style="width: 100%; height: 60px; object-fit: cover; border-radius: 4px;">
            </div>
            <div class="history-info">
                <p><strong>${item.func}</strong></p>
                <small>X: [${item.xMin.toFixed(2)}, ${item.xMax.toFixed(2)}]</small>
                <small>${item.timestamp}</small>
            </div>
            <button onclick="loadFromHistory(${index})" class="history-load-btn">
                <i class="fas fa-redo"></i>
            </button>
        `;
        
        historyContainer.appendChild(historyItem);
    });
}

// Загрузить график из истории
function loadFromHistory(index) {
    if (index >= 0 && index < graphHistory.length) {
        const item = graphHistory[index];
        
        const functionInput = document.getElementById('function-input');
        const xMinInput = document.getElementById('x-min');
        const xMaxInput = document.getElementById('x-max');
        const plotContainer = document.getElementById('plot-container');
        
        if (functionInput) functionInput.value = item.func;
        if (xMinInput) xMinInput.value = item.xMin;
        if (xMaxInput) xMaxInput.value = item.xMax;
        if (plotContainer) {
            plotContainer.innerHTML = `<img src="${item.plotUrl}" alt="График функции ${item.func}" style="width: 100%; height: auto;">`;
        }
    }
}

// Установить пример функции
function setFunctionExample(func) {
    const functionInput = document.getElementById('function-input');
    if (functionInput) {
        functionInput.value = func;
        functionInput.focus();
    }
}

// Отправить сообщение AI
async function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    
    if (!chatInput || !chatMessages) return;
    
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Добавляем сообщение пользователя
    addUserMessage(message);
    
    // Очищаем поле ввода
    chatInput.value = '';
    
    // Показываем индикатор загрузки
    addAIMessage('<i class="fas fa-spinner fa-spin"></i> AI думает...');
    
    try {
        const response = await fetch('/api/ai/explain', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                concept: message
            })
        });
        
        if (!response.ok) {
            throw new Error('Ошибка получения ответа от AI');
        }
        
        const result = await response.json();
        
        // Заменяем индикатор загрузки на ответ
        chatMessages.removeChild(chatMessages.lastChild);
        
        if (result.explanation) {
            addAIMessage(result.explanation);
        } else {
            addAIMessage('Извините, я не могу ответить на этот вопрос прямо сейчас.');
        }
        
    } catch (error) {
        console.error('Ошибка при запросе к AI:', error);
        
        // Заменяем индикатор загрузки на сообщение об ошибке
        chatMessages.removeChild(chatMessages.lastChild);
        
        addAIMessage(`
            Извините, произошла ошибка при подключении к AI.
            Вот что я могу сказать по теме "${message}":
            
            ${getFallbackResponse(message)}
        `);
    }
    
    // Прокручиваем к последнему сообщению
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Добавить сообщение пользователя
function addUserMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-user"></i>
        </div>
        <div class="message-content">
            <p>${message}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
}

// Добавить сообщение AI
function addAIMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai-message';
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            ${formatAIMessage(message)}
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
}

// Форматировать сообщение AI
function formatAIMessage(message) {
    // Заменяем переносы строк на теги <p>
    const paragraphs = message.split('\n').filter(p => p.trim());
    
    if (paragraphs.length === 1) {
        return `<p>${paragraphs[0]}</p>`;
    }
    
    return paragraphs.map(p => `<p>${p}</p>`).join('');
}

// Получить запасной ответ
function getFallbackResponse(question) {
    const lowerQuestion = question.toLowerCase();
    
    if (lowerQuestion.includes('синус')) {
        return 'Синус угла в прямоугольном треугольнике — отношение противолежащего катета к гипотенузе. На единичной окружности — координата y точки.';
    } else if (lowerQuestion.includes('косинус')) {
        return 'Косинус угла — отношение прилежащего катета к гипотенузе. На единичной окружности — координата x точки.';
    } else if (lowerQuestion.includes('тангенс')) {
        return 'Тангенс — отношение синуса к косинусу. Также отношение противолежащего катета к прилежащему.';
    } else if (lowerQuestion.includes('уравнен')) {
        return 'Для решения тригонометрического уравнения используйте единичную окружность или табличные значения. Например, sin(x)=0.5 при x=π/6+2πk или x=5π/6+2πk.';
    } else if (lowerQuestion.includes('график')) {
        return 'График синуса — синусоида, проходит через (0,0), (π/2,1), (π,0), (3π/2,-1). График косинуса — косинусоида, сдвинутая на π/2.';
    } else if (lowerQuestion.includes('радиан') || lowerQuestion.includes('градус')) {
        return 'π радиан = 180°. Чтобы перевести градусы в радианы, умножьте на π/180. Чтобы перевести радианы в градусы, умножьте на 180/π.';
    } else {
        return 'Тригонометрия изучает соотношения между сторонами и углами треугольников. Основные функции: sin, cos, tan. Используйте единичную окружность для наглядного представления.';
    }
}

// Быстрый вопрос
function askQuickQuestion(question) {
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.value = question;
        sendMessage();
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Инициализируем список функций
    updateFunctionsList();
    
    // Добавляем обработчик Enter в поле ввода чата
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    // Добавляем обработчик Enter в поле ввода функции
    const functionInput = document.getElementById('function-input');
    if (functionInput) {
        functionInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                plotFunction();
            }
        });
    }
    
    // Строим начальный график
    setTimeout(() => {
        plotFunction();
    }, 500);
    
    console.log('Лаборатория загружена');
    console.log('Используйте функции: sin(x), cos(x), tan(x), и их комбинации');
});