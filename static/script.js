// static/script.js
// Разработчик Б: Улучшенная логика

let currentTransactions = [];
let charts = {};

document.addEventListener('DOMContentLoaded', function() {
    loadCategories();
    loadData();
    setupTheme();
    setupPeriodSelector();
    setupModal();
});

// Загрузка категорий
function loadCategories() {
    fetch('/api/categories')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('category');
            select.innerHTML = '<option value="">Выберите категорию</option>';
            
            // Доходы
            const incomeGroup = document.createElement('optgroup');
            incomeGroup.label = '💰 Доходы';
            data.income.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.name;
                option.textContent = `${cat.icon} ${cat.name}`;
                incomeGroup.appendChild(option);
            });
            select.appendChild(incomeGroup);
            
            // Расходы
            const expenseGroup = document.createElement('optgroup');
            expenseGroup.label = '💸 Расходы';
            data.expense.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.name;
                option.textContent = `${cat.icon} ${cat.name}`;
                expenseGroup.appendChild(option);
            });
            select.appendChild(expenseGroup);
        });
}

// Загрузка всех данных
function loadData() {
    Promise.all([
        fetch('/api/transactions').then(r => r.json()),
        fetch('/api/balance').then(r => r.json())
    ]).then(([transactions, balanceData]) => {
        currentTransactions = transactions;
        updateBalance(balanceData.balance);
        updateStats(transactions);
        renderTransactions(transactions);
        updateCharts(transactions);
    });
}

// Обновление баланса
function updateBalance(balance) {
    const balanceElement = document.getElementById('balance');
    balanceElement.textContent = formatMoney(balance) + ' ₽';
    balanceElement.style.color = balance >= 0 ? 'var(--income-color)' : 'var(--expense-color)';
}

// Обновление статистики
function updateStats(transactions) {
    const income = transactions
        .filter(t => t.type === 'income')
        .reduce((sum, t) => sum + t.amount, 0);
    
    const expense = transactions
        .filter(t => t.type === 'expense')
        .reduce((sum, t) => sum + t.amount, 0);
    
    document.getElementById('totalIncome').textContent = formatMoney(income) + ' ₽';
    document.getElementById('totalExpense').textContent = formatMoney(expense) + ' ₽';
    document.getElementById('totalTransactions').textContent = transactions.length;
}

// Форматирование денег
function formatMoney(amount) {
    return amount.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

// Отрисовка транзакций
function renderTransactions(transactions) {
    const list = document.getElementById('transactionsList');
    const recent = transactions.slice(0, 10);
    
    if (recent.length === 0) {
        list.innerHTML = '<p class="empty-state">📭 Пока нет операций</p>';
        return;
    }
    
    list.innerHTML = recent.map(t => `
        <div class="transaction-item" data-id="${t.id}">
            <div class="transaction-main">
                <span class="transaction-icon">${t.type === 'income' ? '💰' : '💸'}</span>
                <div class="transaction-details">
                    <div class="transaction-category">${t.category}</div>
                    <div class="transaction-description">${t.description || 'Без описания'}</div>
                    <div class="transaction-date">${t.date}</div>
                </div>
            </div>
            <div class="transaction-amount ${t.type}">
                ${t.type === 'income' ? '+' : '-'}${formatMoney(t.amount)} ₽
            </div>
            <div class="transaction-actions">
                <button onclick="editTransaction(${t.id})" class="edit-btn">✏️</button>
                <button onclick="deleteTransaction(${t.id})" class="delete-btn">🗑️</button>
            </div>
        </div>
    `).join('');
}

// Удаление транзакции
function deleteTransaction(id) {
    if (confirm('Удалить операцию?')) {
        fetch(`/api/delete/${id}`, { method: 'POST' })
            .then(() => loadData());
    }
}

// Редактирование транзакции
function editTransaction(id) {
    const transaction = currentTransactions.find(t => t.id === id);
    if (!transaction) return;
    
    const modal = document.getElementById('editModal');
    const form = document.getElementById('editForm');
    
    form.innerHTML = `
        <input type="hidden" name="id" value="${transaction.id}">
        
        <div class="form-group">
            <label>Тип</label>
            <div class="type-selector">
                <label class="type-option income-option">
                    <input type="radio" name="type" value="income" 
                        ${transaction.type === 'income' ? 'checked' : ''}>
                    <span>💰 Доход</span>
                </label>
                <label class="type-option expense-option">
                    <input type="radio" name="type" value="expense"
                        ${transaction.type === 'expense' ? 'checked' : ''}>
                    <span>💸 Расход</span>
                </label>
            </div>
        </div>
        
        <div class="form-group">
            <label>Сумма</label>
            <input type="number" step="0.01" name="amount" value="${transaction.amount}" required>
        </div>
        
        <div class="form-group">
            <label>Категория</label>
            <select name="category" required>
                <option value="${transaction.category}">${transaction.category}</option>
            </select>
        </div>
        
        <div class="form-group">
            <label>Описание</label>
            <input type="text" name="description" value="${transaction.description || ''}">
        </div>
        
        <button type="submit" class="btn btn-primary">Сохранить</button>
    `;
    
    form.action = `/api/update/${id}`;
    modal.style.display = 'block';
}

// Настройка темы
function setupTheme() {
    const themeToggle = document.getElementById('themeToggle');
    themeToggle.addEventListener('click', () => {
        const isDark = document.body.getAttribute('data-theme') === 'dark';
        document.body.setAttribute('data-theme', isDark ? 'light' : 'dark');
        themeToggle.textContent = isDark ? '🌙 Темная тема' : '☀️ Светлая тема';
    });
}

// Настройка переключателя периода
function setupPeriodSelector() {
    const select = document.getElementById('periodSelect');
    select.addEventListener('change', () => {
        const period = select.value;
        fetch(`/api/statistics?period=${period}`)
            .then(r => r.json())
            .then(stats => updateChartsWithStats(stats));
    });
}

// Настройка модального окна
function setupModal() {
    const modal = document.getElementById('editModal');
    const span = document.getElementsByClassName('close')[0];
    
    span.onclick = () => modal.style.display = 'none';
    
    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };
}

// Автообновление
setInterval(loadData, 10000);