// Category colors matching the main dashboard
const categoryColors = {
    groceries: '#FF6384',
    transport: '#36A2EB',
    eating_out: '#FFCE56',
    entertainment: '#4BC0C0',
    utilities: '#9966FF',
    healthcare: '#FF9F40',
    education: '#45B7D1',
    miscellaneous: '#C9CBCF'
};

// Load and display statistics
function loadStatistics() {
    const profileData = JSON.parse(localStorage.getItem('profileData') || '{}');
    if (!profileData.expenses) return;

    updateOverviewStats(profileData);
    updateExpenseTable(profileData);
    updateKeyMetrics(profileData);
}

function updateOverviewStats(profileData) {
    // Update income
    document.getElementById('totalIncome').textContent = `₹${profileData.income.toLocaleString()}`;
    
    // Calculate total expenses
    const totalExpenses = Object.values(profileData.expenses).reduce((a, b) => a + b, 0);
    document.getElementById('totalExpenses').textContent = `₹${totalExpenses.toLocaleString()}`;
    
    // Calculate net savings
    const netSavings = profileData.income - totalExpenses;
    document.getElementById('netSavings').textContent = `₹${netSavings.toLocaleString()}`;
    
    // Calculate savings progress
    const savingsProgress = (netSavings / profileData.savings_goal * 100).toFixed(1);
    document.getElementById('savingsProgress').textContent = `${savingsProgress}%`;
    
    const remaining = profileData.savings_goal - netSavings;
    document.getElementById('goalRemaining').textContent = 
        remaining > 0 ? `₹${remaining.toLocaleString()} remaining` : 'Goal Achieved!';
}

function updateExpenseTable(profileData) {
    const expenseTable = document.getElementById('expenseTable');
    const totalExpenses = Object.values(profileData.expenses).reduce((a, b) => a + b, 0);
    
    // Clear existing rows
    expenseTable.innerHTML = '';
    
    // Add a row for each expense category
    Object.entries(profileData.expenses).forEach(([category, amount]) => {
        const percentage = ((amount / totalExpenses) * 100).toFixed(1);
        const budget = getBudgetForCategory(category, profileData.income);
        const status = getStatusForExpense(amount, budget);
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="category-cell">
                <span class="category-indicator" style="background-color: ${categoryColors[category]}"></span>
                ${formatCategoryName(category)}
            </td>
            <td>₹${amount.toLocaleString()}</td>
            <td>${percentage}%</td>
            <td>₹${budget.toLocaleString()}</td>
            <td>${status}</td>
        `;
        expenseTable.appendChild(row);
    });
}

function updateKeyMetrics(profileData) {
    // Calculate needs vs wants ratio
    const needsCategories = ['groceries', 'utilities', 'transport', 'healthcare', 'education'];
    const totalExpenses = Object.values(profileData.expenses).reduce((a, b) => a + b, 0);
    
    const needsTotal = needsCategories.reduce((sum, category) => 
        sum + (profileData.expenses[category] || 0), 0);
    const wantsTotal = totalExpenses - needsTotal;
    
    const needsPercentage = ((needsTotal / totalExpenses) * 100).toFixed(0);
    const wantsPercentage = ((wantsTotal / totalExpenses) * 100).toFixed(0);
    
    document.getElementById('needsWantsRatio').textContent = `${needsPercentage}:${wantsPercentage}`;
    document.getElementById('needsWantsStatus').textContent = 
        needsPercentage <= 50 ? 'On Track' : 'Review Needed';
    
    // Calculate savings rate
    const savingsRate = ((profileData.income - totalExpenses) / profileData.income * 100).toFixed(1);
    document.getElementById('savingsRate').textContent = `${savingsRate}%`;
    document.getElementById('savingsStatus').textContent = 
        savingsRate >= 20 ? 'On Track' : 'Below Target';
    
    // Calculate budget utilization
    const budgetUtilization = (totalExpenses / (profileData.income * 0.7) * 100).toFixed(1);
    document.getElementById('budgetUtilization').textContent = `${budgetUtilization}%`;
    document.getElementById('budgetStatus').textContent = 
        budgetUtilization <= 100 ? 'On Track' : 'Over Budget';
}

// Helper functions
function formatCategoryName(category) {
    return category.split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function getBudgetForCategory(category, income) {
    const budgetPercentages = {
        groceries: 0.15,
        transport: 0.10,
        eating_out: 0.10,
        entertainment: 0.05,
        utilities: 0.10,
        healthcare: 0.10,
        education: 0.10,
        miscellaneous: 0.05
    };
    
    return income * (budgetPercentages[category] || 0.05);
}

function getStatusForExpense(amount, budget) {
    const ratio = amount / budget;
    if (ratio <= 0.8) return '✓ Under Budget';
    if (ratio <= 1) return '⚠️ Near Limit';
    return '❌ Over Budget';
}

// Handle time range changes
document.getElementById('timeRange').addEventListener('change', function(e) {
    // In a real application, this would fetch data for the selected time range
    loadStatistics();
});

// Load statistics when page loads
document.addEventListener('DOMContentLoaded', loadStatistics); 