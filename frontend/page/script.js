const ctx = document.getElementById('expenseChart').getContext('2d');
let expenseChart;

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

    // Format category labels and calculate totals
    const labels = Object.keys(expenses).map(key => 
        key.split('_')
           .map(word => word.charAt(0).toUpperCase() + word.slice(1))
           .join(' ')
    );
    const values = Object.values(expenses);

    // Update chart data
    expenseChart.data.labels = labels;
    expenseChart.data.datasets[0].data = values;
    expenseChart.update();

    // Update chart title with total expenses
    const totalExpenses = values.reduce((a, b) => a + b, 0);
    expenseChart.options.plugins.title.text = `Monthly Expenses: ₹${totalExpenses.toLocaleString()}`;
    expenseChart.update();
}

// Load and display user profile data
async function loadUserProfile() {
    try {
        const profileData = JSON.parse(localStorage.getItem('profileData') || '{}');
        const username = localStorage.getItem('username');

        // Update header
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

            // Update expense chart with real data
            updateExpenseChart(profileData.expenses);
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

// Initialize chart and load profile when page loads
document.addEventListener('DOMContentLoaded', () => {
    initializeChart();
    loadUserProfile();
});

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

function sendMessage() {
    const message = chatInput.value.trim();
    if (message === '') return;

    // Add user message
    addMessage(message, 'user');
    chatInput.value = '';

    // Simulate bot response
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

// Notification cycling
const notifications = [
    "You've spent ₹2000 on food delivery this week!",
    "Save ₹100 more this week to unlock rewards!",
    "Your electricity bill is due in 3 days.",
    "You've saved ₹5000 this month. Great job!"
];

const notificationEl = document.getElementById('notification');
let notificationIndex = 0;

setInterval(() => {
    notificationIndex = (notificationIndex + 1) % notifications.length;
    notificationEl.style.opacity = 0;
    
    setTimeout(() => {
        notificationEl.textContent = notifications[notificationIndex];
        notificationEl.style.opacity = 1;
    }, 500);
}, 5000);

// Simulate dynamic data updates
function updateChartData() {
    // Randomly adjust expense percentages
    expenseChart.data.datasets[0].data = expenseChart.data.datasets[0].data.map(value => {
        const change = Math.random() * 2 - 1; // Random value between -1 and 1
        return Math.max(1, value + change); // Ensure no value goes below 1
    });
    
    expenseChart.update();
    
    // Update needs/wants bars
    const newNeeds = Math.floor(60 + Math.random() * 10);
    const newWants = 100 - newNeeds;
    
    document.getElementById('needsBar').style.width = `${newNeeds}%`;
    document.getElementById('needsValue').textContent = `${newNeeds}%`;
    
    document.getElementById('wantsBar').style.width = `${newWants}%`;
    document.getElementById('wantsValue').textContent = `${newWants}%`;
}

// Update data every 10 seconds
setInterval(updateChartData, 10000);