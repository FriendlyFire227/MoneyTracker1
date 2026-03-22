// static/charts.js
// Разработчик Б: Визуализация данных

function updateCharts(transactions) {
    updateExpenseChart(transactions);
    updateTrendChart(transactions);
}

function updateExpenseChart(transactions) {
    const expenses = transactions.filter(t => t.type === 'expense');
    
    // Группировка по категориям
    const categories = {};
    expenses.forEach(e => {
        categories[e.category] = (categories[e.category] || 0) + e.amount;
    });
    
    const ctx = document.getElementById('expenseChart').getContext('2d');
    
    if (charts.expense) {
        charts.expense.destroy();
    }
    
    charts.expense = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(categories),
            datasets: [{
                data: Object.values(categories),
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', 
                    '#4BC0C0', '#9966FF', '#FF9F40'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function updateTrendChart(transactions) {
    // Группировка по дням
    const last7Days = [];
    const incomeData = [];
    const expenseData = [];
    
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        const dateStr = date.toLocaleDateString('ru-RU', { 
            day: '2-digit', 
            month: '2-digit' 
        });
        
        last7Days.push(dateStr);
        
        const dayTransactions = transactions.filter(t => 
            t.date.startsWith(date.toISOString().split('T')[0])
        );
        
        const dayIncome = dayTransactions
            .filter(t => t.type === 'income')
            .reduce((sum, t) => sum + t.amount, 0);
        
        const dayExpense = dayTransactions
            .filter(t => t.type === 'expense')
            .reduce((sum, t) => sum + t.amount, 0);
        
        incomeData.push(dayIncome);
        expenseData.push(dayExpense);
    }
    
    const ctx = document.getElementById('trendChart').getContext('2d');
    
    if (charts.trend) {
        charts.trend.destroy();
    }
    
    charts.trend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: last7Days,
            datasets: [
                {
                    label: 'Доходы',
                    data: incomeData,
                    borderColor: '#27ae60',
                    backgroundColor: 'rgba(39, 174, 96, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Расходы',
                    data: expenseData,
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function updateChartsWithStats(stats) {
    // Обновление графиков на основе статистики
    console.log('Stats updated:', stats);
}