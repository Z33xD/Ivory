const ctx = document.getElementById('expenseChart').getContext('2d');
let expenseChart;

// API Configuration
const API_BASE_URL = 'https://my.api.mockaroo.com/expenditures_and_savings.json'; // Replace with your actual API base URL

// Chart configuration
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                padding: 20,
                font: {
                    size: 12
                }
            }
        },
        title: {
            display: true,
            text: 'Monthly Expenses',
            font: {
                size: 18
            },
            padding: {
                top: 10,
                bottom: 20
            }
        }
    }
};

// Initialize chart with empty data
function initializeChart() {
    expenseChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#FF6384', // Groceries
                    '#36A2EB', // Transport
                    '#FFCE56', // Eating Out
                    '#4BC0C0', // Entertainment
                    '#9966FF', // Utilities
                    '#FF9F40', // Healthcare
                    '#45B7D1', // Education
                    '#C9CBCF'  // Miscellaneous
                ],
                borderWidth: 1
            }]
        },
        options: chartOptions
    });
}

// Function to update chart with transaction data
function updateExpenseChart(expenses) {
    if (!expenseChart) {
        initializeChart();
    }
    
    const variable = window.location.pathname !== "/frontend/page/opt_out.html";
    
    // Format category labels and calculate totals
    const labels = variable ? Object.keys(expenses).map(key => 
        key.split('_')
           .map(word => word.charAt(0).toUpperCase() + word.slice(1))
           .join(' ')
    ) : [];
    const values = variable ? Object.values(expenses) : [];

    // Update chart data
    expenseChart.data.labels = labels;
    expenseChart.data.datasets[0].data = values;
    
    // Update chart title with total expenses
    const totalExpenses = values.reduce((a, b) => a + b, 0);
    expenseChart.options.plugins.title.text = `Monthly Expenses: ₹${totalExpenses.toLocaleString()}`;
    
    if (variable) {
        expenseChart.update();
    }
}

// Category icons mapping
const categoryIcons = {
    groceries: '🛒',
    transport: '🚗',
    eating_out: '🍔',
    entertainment: '🎬',
    utilities: '⚡',
    healthcare: '🏥',
    education: '📚',
    miscellaneous: '📦'
};

// Function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const yesterday = new Date(now);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === now.toDateString()) {
        return `Today, ${date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}`;
    } else if (date.toDateString() === yesterday.toDateString()) {
        return `Yesterday, ${date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}`;
    } else {
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// Function to create a transaction element
function createTransactionElement(transaction) {
    const transactionEl = document.createElement('div');
    transactionEl.className = 'history-item';
    
    const amount = parseFloat(transaction.amount);
    const isExpense = amount > 0; // Expenses are positive in our system
    
    transactionEl.innerHTML = `
        <div class="history-item-left">
            <div class="history-item-icon">${categoryIcons[transaction.category] || '📝'}</div>
            <div class="history-item-details">
                <div class="history-item-title">${formatCategoryName(transaction.category)}</div>
                <div class="history-item-date">${formatDate(transaction.timestamp)}</div>
            </div>
        </div>
        <div class="history-item-amount ${isExpense ? 'expense' : 'income'}">
            ${isExpense ? '-' : '+'}₹${Math.abs(amount).toLocaleString()}
        </div>
    `;
    
    return transactionEl;
}

// Function to format category name
function formatCategoryName(category) {
    return category.split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// Function to get auth token
function getAuthToken() {
    return localStorage.getItem('token');
}

// Function to make authenticated API calls
async function fetchWithAuth(endpoint, options = {}) {
    const token = getAuthToken();
    if (!token) {
        console.warn('No authentication token found, proceeding without authentication');
    }

    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    // Add token to headers if available
    if (token) {
        defaultOptions.headers['Authorization'] = `Bearer ${token}`;
    }

    const fullUrl = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
    
    try {
        const response = await fetch(fullUrl, { ...defaultOptions, ...options });
        if (!response.ok) {
            throw new Error(`API call failed: ${response.status} - ${response.statusText}`);
        }
        return response.json();
    } catch (error) {
        console.error(`Error fetching from ${fullUrl}:`, error);
        throw error;
    }
}

// Function to update recent transactions
async function updateRecentTransactions() {
    try {
        const transactionsList = document.getElementById('transactionsList');
        if (!transactionsList) return;

        // Show loading state
        transactionsList.innerHTML = '<div class="loading">Loading transactions...</div>';

        // Get recent transactions from API
        const recentTransactions = await fetchWithAuth('/get_recent_transactions');
        
        // Clear existing transactions
        transactionsList.innerHTML = '';
        
        // Add new transactions
        if (Array.isArray(recentTransactions) && recentTransactions.length > 0) {
            recentTransactions
                .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
                .forEach(transaction => {
                    transactionsList.appendChild(createTransactionElement(transaction));
                });
        } else {
            transactionsList.innerHTML = '<div class="no-data">No recent transactions found</div>';
        }
    } catch (error) {
        console.error('Error updating recent transactions:', error);
        const transactionsList = document.getElementById('transactionsList');
        if (transactionsList) {
            transactionsList.innerHTML = '<div class="error">Failed to load transactions. Try again later.</div>';
        }
    }
}

// Function to fetch all user data from API
async function fetchUserData() {
    try {
        // Show loading state in UI elements
        document.getElementById('needsValue').textContent = 'Loading...';
        document.getElementById('wantsValue').textContent = 'Loading...';
        
        // Fetch user profile data from API
        const profileData = await fetchWithAuth('/get_user_profile');
        
        // Store in localStorage for caching
        if (profileData) {
            localStorage.setItem('profileData', JSON.stringify(profileData));
        }
        
        return profileData;
    } catch (error) {
        console.error('Error fetching user data:', error);
        
        // If API fails, try to get cached data from localStorage
        const cachedData = localStorage.getItem('profileData');
        if (cachedData) {
            return JSON.parse(cachedData);
        }
        
        // Fall back to generating profile if no cached data
        return await generateUserProfile();
    }
}

// Function to generate user profile (fallback if API is not available)
async function generateUserProfile() {
    try {
        // Try the API first
        const response = await fetchWithAuth('/generate_profile');
        if (response.profile) {
            localStorage.setItem('profileData', JSON.stringify(response.profile));
            return response.profile;
        }
    } catch (error) {
        console.error('Error generating user profile from API:', error);
        
        // Fallback to local profile generation if API fails
        // Create a simple default profile
        const defaultProfile = {
            username: localStorage.getItem('username') || 'User',
            income: 40000,
            savings_goal: 10000,
            expenses: {
                groceries: 8000,
                transport: 3000,
                eating_out: 4000,
                entertainment: 2000,
                utilities: 5000,
                healthcare: 2000,
                education: 3000,
                miscellaneous: 1000
            }
        };
        
        localStorage.setItem('profileData', JSON.stringify(defaultProfile));
        return defaultProfile;
    }
}

// Load and display user profile data
async function loadUserProfile() {
    try {
        // Try to fetch from API first
        let profileData = await fetchUserData();
        
        if (!profileData || !profileData.expenses) {
            console.warn('Failed to get profile data from API, using local data');
            // Try to get from localStorage
            const cachedData = localStorage.getItem('profileData');
            if (cachedData) {
                profileData = JSON.parse(cachedData);
            }
            
            // If still no data, generate fallback
            if (!profileData || !profileData.expenses) {
                profileData = await generateUserProfile();
                if (!profileData) {
                    throw new Error('Could not load or generate profile data');
                }
            }
        }

        // Update UI with username
        const username = profileData.username || localStorage.getItem('username') || 'User';
        document.querySelector('.app-title').textContent = `${username}'s Finance Tracker`;

        if (profileData.expenses) {
            const totalExpenses = Object.values(profileData.expenses).reduce((a, b) => a + b, 0);
            
            // Calculate needs vs wants
            const needsCategories = ['groceries', 'utilities', 'transport', 'healthcare', 'education'];
            const needsTotal = needsCategories.reduce((sum, category) => 
                sum + (profileData.expenses[category] || 0), 0);
            const wantsTotal = totalExpenses - needsTotal;

            // Update needs/wants percentages
            const needsPercentage = (needsTotal / totalExpenses * 100).toFixed(0);
            const wantsPercentage = (wantsTotal / totalExpenses * 100).toFixed(0);

            document.getElementById('needsValue').textContent = `${needsPercentage}%`;
            document.getElementById('wantsValue').textContent = `${wantsPercentage}%`;
            document.getElementById('needsBar').style.width = `${needsPercentage}%`;
            document.getElementById('wantsBar').style.width = `${wantsPercentage}%`;

            // Update budget progress
            const monthlyBudget = profileData.income * 0.7; // 70% of income for expenses
            document.querySelector('.progress-container:nth-child(3) .progress-value').textContent = 
                `₹${totalExpenses.toLocaleString()} / ₹${monthlyBudget.toLocaleString()}`;
            document.querySelector('.progress-container:nth-child(3) .progress-fill').style.width = 
                `${Math.min((totalExpenses / monthlyBudget * 100), 100)}%`;

            // Update savings progress
            const currentSavings = profileData.income - totalExpenses;
            document.querySelector('.progress-container:nth-child(4) .progress-value').textContent = 
                `₹${currentSavings.toLocaleString()} / ₹${profileData.savings_goal.toLocaleString()}`;
            document.querySelector('.progress-container:nth-child(4) .progress-fill').style.width = 
                `${Math.min((currentSavings / profileData.savings_goal * 100), 100)}%`;

            // Update expense chart
            updateExpenseChart(profileData.expenses);
        }

        // Update recent transactions
        await updateRecentTransactions();
    } catch (error) {
        console.error('Error loading profile:', error);
        // Display error state in UI
        document.getElementById('needsValue').textContent = 'Error';
        document.getElementById('wantsValue').textContent = 'Error';
    }
}

// Initialize chart and load profile when page loads
document.addEventListener('DOMContentLoaded', () => {
    initializeChart();
    loadUserProfile();
});

// Function to refresh all data
function refreshAllData() {
    // Clear any cached data to force reload from API
    localStorage.removeItem('profileData');
    loadUserProfile();
}

// Update data periodically
setInterval(() => {
    updateRecentTransactions();
}, 30000);

// Refresh all data less frequently
setInterval(() => {
    refreshAllData();
}, 5 * 60 * 1000); // Every 5 minutes

// Toggle chatbot
const chatbot = document.getElementById('chatbot');
const chatToggle = document.getElementById('chatToggle');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');

chatbot.addEventListener('click', function(e) {
    if (!chatbot.classList.contains('expanded') && e.target !== chatInput) {
        chatbot.classList.add('expanded');
        chatToggle.innerHTML = '▼';
        setTimeout(() => {
            chatInput.focus();
        }, 300);
    }
});

chatToggle.addEventListener('click', function(e) {
    e.stopPropagation();
    chatbot.classList.toggle('expanded');
    chatToggle.innerHTML = chatbot.classList.contains('expanded') ? '▼' : '▲';
});

// Handle chat input
sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Send chat message and get response from API
async function sendMessage() {
    const message = chatInput.value.trim();
    if (message === '') return;

    // Add user message
    addMessage(message, 'user');
    chatInput.value = '';

    try {
        // Try to get response from API
        const response = await fetchWithAuth('/chat', {
            method: 'POST',
            body: JSON.stringify({ message }),
        });
        
        if (response && response.reply) {
            addMessage(response.reply, 'bot');
        } else {
            throw new Error('Invalid response format');
        }
    } catch (error) {
        console.error('Error getting chat response:', error);
        
        // Fallback to predefined responses
        setTimeout(() => {
            let response;
            const lowerMessage = message.toLowerCase();
            
            if (lowerMessage.includes('budget') || lowerMessage.includes('spending')) {
                response = "Based on your spending patterns, I recommend allocating 50% for needs, 30% for wants, and 20% for savings. You're currently spending a bit more on wants than the recommended amount.";
            } else if (lowerMessage.includes('save') || lowerMessage.includes('saving')) {
                response = "You're on track to meet your savings goal! Just ₹1,500 more to go. Have you considered setting up automatic transfers to your savings account?";
            } else if (lowerMessage.includes('spend') || lowerMessage.includes('expense')) {
                response = "Your biggest expense categories this month are housing (30%) and food (20%). Your food expenses are 15% higher than last month.";
            } else if (lowerMessage.includes('invest') || lowerMessage.includes('investment')) {
                response = "Based on your risk profile and goals, I'd recommend considering a mix of index funds and fixed deposits. Would you like me to provide more specific recommendations?";
            } else {
                response = "I'm here to help with your financial questions. You can ask me about your spending, budgeting tips, savings goals, or investment advice!";
            }
            
            addMessage(response, 'bot');
        }, 800);
    }
}

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('chat-message', sender);
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Toggle side menu
const menuBtn = document.getElementById('menuBtn');
const menuClose = document.getElementById('menuClose');
const sideMenu = document.getElementById('sideMenu');
const overlay = document.getElementById('overlay');

menuBtn.addEventListener('click', function() {
    sideMenu.classList.add('open');
    overlay.classList.add('active');
});

function closeMenu() {
    sideMenu.classList.remove('open');
    overlay.classList.remove('active');
}

menuClose.addEventListener('click', closeMenu);
overlay.addEventListener('click', closeMenu);

// Remove the updateChartData function that simulates dynamic data changes
// We'll use real API data instead
// Add these functions to your existing script.js file

// Check if the user has opted out of financial tracking
function isOptedOutOfTracking() {
    return localStorage.getItem('financialTrackingOptOut') === 'true';
}

// Modify the fetchUserData function to check for opt-out status
async function fetchUserData() {
    try {
        // Show loading state in UI elements
        document.getElementById('needsValue').textContent = 'Loading...';
        document.getElementById('wantsValue').textContent = 'Loading...';
        
        // Check if user has opted out
        if (isOptedOutOfTracking()) {
            console.log('User has opted out of financial tracking');
            
            // Create zeroed profile data
            const zeroedProfile = {
                username: localStorage.getItem('username') || 'User',
                income: 0,
                savings_goal: 0,
                expenses: {
                    groceries: 0,
                    transport: 0,
                    eating_out: 0,
                    entertainment: 0,
                    utilities: 0,
                    healthcare: 0,
                    education: 0,
                    miscellaneous: 0
                }
            };
            
            return zeroedProfile;
        }
        
        // If not opted out, proceed with normal fetch
        // Fetch user profile data from API
        const profileData = await fetchWithAuth('/get_user_profile');
        
        // Store in localStorage for caching
        if (profileData) {
            localStorage.setItem('profileData', JSON.stringify(profileData));
        }
        
        return profileData;
    } catch (error) {
        console.error('Error fetching user data:', error);
        
        // If user has opted out, return zeroed profile
        if (isOptedOutOfTracking()) {
            return {
                username: localStorage.getItem('username') || 'User',
                income: 0,
                savings_goal: 0,
                expenses: {
                    groceries: 0,
                    transport: 0,
                    eating_out: 0,
                    entertainment: 0,
                    utilities: 0,
                    healthcare: 0,
                    education: 0,
                    miscellaneous: 0
                }
            };
        }
        
        // If API fails, try to get cached data from localStorage
        const cachedData = localStorage.getItem('profileData');
        if (cachedData) {
            return JSON.parse(cachedData);
        }
        
        // Fall back to generating profile if no cached data
        return await generateUserProfile();
    }
}

// Modify the updateExpenseChart function to check for opt-out path
function updateExpenseChart(expenses) {
    if (!expenseChart) {
        initializeChart();
    }
    
    // Check if user has opted out or if we're on the opt-out page
    const isOptedOut = isOptedOutOfTracking() || window.location.pathname.includes('opt_out.html');
    
    // Format category labels and calculate totals
    const labels = isOptedOut ? [] : Object.keys(expenses).map(key => 
        key.split('_')
           .map(word => word.charAt(0).toUpperCase() + word.slice(1))
           .join(' ')
    );
    const values = isOptedOut ? [] : Object.values(expenses);

    // Update chart data
    expenseChart.data.labels = labels;
    expenseChart.data.datasets[0].data = values;
    
    // Update chart title with total expenses or opt-out message
    const totalExpenses = values.reduce((a, b) => a + b, 0);
    expenseChart.options.plugins.title.text = isOptedOut 
        ? 'Financial Tracking Disabled' 
        : `Monthly Expenses: ₹${totalExpenses.toLocaleString()}`;
    
    expenseChart.update();
}

// Add notification for opt-out status on main page
function checkAndNotifyOptOutStatus() {
    if (isOptedOutOfTracking() && !window.location.pathname.includes('opt_out.html')) {
        const notification = document.createElement('div');
        notification.className = 'opt-out-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">🔕</div>
                <div class="notification-text">Financial tracking is currently disabled</div>
                <a href="opt_out.html" class="notification-link">Manage Settings</a>
            </div>
            <button class="notification-close">×</button>
        `;
        
        document.body.appendChild(notification);
        
        // Add event listener to close button
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            notification.classList.add('hiding');
            setTimeout(() => {
                notification.remove();
            }, 500);
        }, 10000);
    }
}

// Add this to your DOMContentLoaded event
document.addEventListener('DOMContentLoaded', () => {
    initializeChart();
    loadUserProfile();
    checkAndNotifyOptOutStatus();
});

// Additional CSS for notification
const style = document.createElement('style');
style.textContent = `
.opt-out-notification {
    position: fixed;
    bottom: 80px;
    right: 20px;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 350px;
    animation: slideIn 0.5s ease;
}

.opt-out-notification.hiding {
    animation: slideOut 0.5s ease;
}

.notification-content {
    display: flex;
    align-items: center;
    gap: 10px;
}

.notification-icon {
    font-size: 1.5rem;
}

.notification-text {
    font-size: 0.9rem;
}

.notification-link {
    margin-left: 10px;
    color: #007bff;
    text-decoration: underline;
    font-size: 0.8rem;
}

.notification-close {
    background: none;
    border: none;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0 5px;
    margin-left: 10px;
}

@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes slideOut {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
}
`;
document.head.appendChild(style);
// Add this code to your script.js file

document.addEventListener('DOMContentLoaded', function() {
    // Existing functionality
    
    // Budget and Savings input handling
    const budgetInput = document.getElementById('budgetInput');
    const savingsInput = document.getElementById('savingsInput');
    const saveBudgetBtn = document.getElementById('saveBudget');
    const saveSavingsBtn = document.getElementById('saveSavings');
    const budgetBar = document.getElementById('budgetBar');
    const savingsBar = document.getElementById('savingsBar');
    
    // Load saved values from localStorage if available
    const savedBudget = localStorage.getItem('monthlyBudget');
    const savedSavings = localStorage.getItem('savingsGoal');
    const spentAmount = localStorage.getItem('spentAmount') || 0; // This would come from your actual data
    const savedAmount = localStorage.getItem('savedAmount') || 0; // This would come from your actual data
    
    // Initialize with saved values if they exist
    if (savedBudget) {
        showBudgetValue(savedBudget);
        updateBudgetProgress(savedBudget, spentAmount);
    }
    
    if (savedSavings) {
        showSavingsValue(savedSavings);
        updateSavingsProgress(savedSavings, savedAmount);
    }
    
    // Event listeners for saving input values
    saveBudgetBtn.addEventListener('click', function() {
        const budgetValue = budgetInput.value.trim();
        
        if (budgetValue && !isNaN(budgetValue) && budgetValue > 0) {
            localStorage.setItem('monthlyBudget', budgetValue);
            showBudgetValue(budgetValue);
            updateBudgetProgress(budgetValue, spentAmount);
            showNotification('Budget updated successfully!');
        } else {
            localStorage.setItem('monthlyBudget', budgetValue);
            showBudgetValue(budgetValue);
            updateBudgetProgress(budgetValue, spentAmount);
            showNotification('Budget updated successfully!');
            
        }
    });
    
    saveSavingsBtn.addEventListener('click', function() {
        const savingsValue = savingsInput.value.trim();
        
        if (savingsValue && !isNaN(savingsValue) && savingsValue > 0) {
            localStorage.setItem('savingsGoal', savingsValue);
            showSavingsValue(savingsValue);
            updateSavingsProgress(savingsValue, savedAmount);
            
            // Notify user
            showNotification('Savings goal updated successfully!');
        } else {
            localStorage.setItem('savingsGoal', savingsValue);
            showSavingsValue(savingsValue);
            updateSavingsProgress(savingsValue, savedAmount);
            
            // Notify user
            showNotification('Savings goal updated successfully!');
        }
    });
    
    // Helper functions
    function showBudgetValue(value) {
        const budgetValueEl = document.getElementById('budgetValue');
        budgetValueEl.innerHTML = `$${value} <button id="editBudget" class="edit-btn">✏️</button>`;
        
        // Add event listener to edit button
        document.getElementById('editBudget').addEventListener('click', function() {
            budgetValueEl.innerHTML = `
                <input type="number" id="budgetInput" placeholder="Enter budget" class="finance-input" value="${value}">
                <button id="saveBudget" class="save-btn">Save</button>
            `;
            
            // Reattach event listeners
            document.getElementById('budgetInput').focus();
            document.getElementById('saveBudget').addEventListener('click', 
                () => saveBudgetBtn.click());
        });
    }
    
    function showSavingsValue(value) {
        const savingsValueEl = document.getElementById('savingsValue');
        savingsValueEl.innerHTML = `$${value} <button id="editSavings" class="edit-btn">✏️</button>`;
        
        // Add event listener to edit button
        document.getElementById('editSavings').addEventListener('click', function() {
            savingsValueEl.innerHTML = `
                <input type="number" id="savingsInput" placeholder="Enter goal" class="finance-input" value="${value}">
                <button id="saveSavings" class="save-btn">Save</button>
            `;
            
            // Reattach event listeners
            document.getElementById('savingsInput').focus();
            document.getElementById('saveSavings').addEventListener('click', 
                () => saveSavingsBtn.click());
        });
    }
    
    function updateBudgetProgress(budget, spent) {
        const percentage = Math.min(100, (spent / budget) * 100);
        budgetBar.style.width = `${percentage}%`;
        
        // Change color if over budget
        if (percentage >= 90) {
            budgetBar.style.backgroundColor = percentage >= 100 ? '#FF5252' : '#FFA726';
        } else {
            budgetBar.style.backgroundColor = '';  // Reset to default color
        }
    }
    
    function updateSavingsProgress(goal, saved) {
        const percentage = Math.min(100, (saved / goal) * 100);
        savingsBar.style.width = `${percentage}%`;
    }
    
    function showNotification(message, type = 'success') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Add to DOM
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 500);
        }, 3000);
    }
    
    // Add some additional CSS for notifications and edit button
    const style = document.createElement('style');
    style.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 4px;
            color: white;
            z-index: 1000;
            animation: slide-in 0.5s ease;
        }
        
        .notification.success {
            background-color: #4CAF50;
        }
        
        .notification.error {
            background-color: #F44336;
        }
        
        .notification.fade-out {
            animation: fade-out 0.5s ease;
        }
        
        .edit-btn {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 14px;
            padding: 0 4px;
        }
        
        @keyframes slide-in {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes fade-out {
            from { opacity: 1; }
            to { opacity: 0; }
        }
    `;
    document.head.appendChild(style);
});