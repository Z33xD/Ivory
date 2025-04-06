/**
 * Calendar.js - Transaction Calendar Functionality
 * Handles calendar rendering and random transaction generation
 */

// Global variables
let currentDate = new Date();
let currentMonth = currentDate.getMonth();
let currentYear = currentDate.getFullYear();

// Add notification function to window object if not already present
if (!window.addNotification) {
    window.addNotification = function(title, message) {
        // Get notifications from localStorage
        let notifications = JSON.parse(localStorage.getItem('notifications') || '[]');
        
        // Create new notification
        const notification = {
            id: Date.now(),
            title: title,
            message: message,
            timestamp: new Date().toISOString(),
            read: false
        };
        
        // Add to notifications
        notifications.unshift(notification);
        
        // Save to localStorage
        localStorage.setItem('notifications', JSON.stringify(notifications));
        
        // Update badge if present
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            const unreadCount = notifications.filter(n => !n.read).length;
            badge.textContent = unreadCount;
            badge.style.display = unreadCount > 0 ? 'flex' : 'none';
        }
        
        // Render notification in panel if it exists
        const notificationsList = document.querySelector('.notifications-list');
        if (notificationsList) {
            renderNotifications();
        }
        
        return notification;
    };
}

// Render notifications helper
function renderNotifications() {
    const notificationsList = document.querySelector('.notifications-list');
    if (!notificationsList) return;
    
    // Get notifications from localStorage
    const notifications = JSON.parse(localStorage.getItem('notifications') || '[]');
    
    // Clear notifications list
    notificationsList.innerHTML = '';
    
    if (notifications.length === 0) {
        notificationsList.innerHTML = '<div class="notification-item">No notifications yet.</div>';
        return;
    }
    
    // Add notifications to list
    notifications.forEach(notification => {
        const notificationItem = document.createElement('div');
        notificationItem.className = 'notification-item' + (notification.read ? ' read' : '');
        
        const timestamp = new Date(notification.timestamp);
        const formattedTime = timestamp.toLocaleString();
        
        notificationItem.innerHTML = `
            <div class="notification-title">${notification.title}</div>
            <div class="notification-message">${notification.message}</div>
            <div class="notification-time">${formattedTime}</div>
        `;
        
        notificationItem.addEventListener('click', function() {
            // Mark as read
            notification.read = true;
            localStorage.setItem('notifications', JSON.stringify(notifications));
            
            // Update badge
            updateNotificationBadge();
            
            // Update class
            notificationItem.classList.add('read');
        });
        
        notificationsList.appendChild(notificationItem);
    });
}

// Update notification badge
function updateNotificationBadge() {
    const badge = document.getElementById('notificationBadge');
    if (!badge) return;
    
    const notifications = JSON.parse(localStorage.getItem('notifications') || '[]');
    const unreadCount = notifications.filter(n => !n.read).length;
    
    badge.textContent = unreadCount;
    badge.style.display = unreadCount > 0 ? 'flex' : 'none';
}

// Transaction categories
const transactionCategories = [
    'Groceries', 'Rent', 'Utilities', 'Entertainment', 'Eating_Out',
    'Transport', 'Shopping', 'Health', 'Education', 'Salary', 'Income',
    'Investment', 'Clothing', 'Subscriptions', 'Fitness', 'Travel'
];

// Transaction titles by category
const transactionTitles = {
    'Groceries': ['Supermarket', 'Local Market', 'Organic Store', 'Grocery Delivery'],
    'Rent': ['Monthly Rent', 'Rent Payment'],
    'Utilities': ['Electricity Bill', 'Water Bill', 'Gas Bill', 'Internet Bill'],
    'Entertainment': ['Movie Tickets', 'Concert Tickets', 'Game Purchase', 'Streaming Service'],
    'Eating_Out': ['Restaurant Dinner', 'Lunch with Friends', 'Coffee Shop', 'Fast Food'],
    'Transport': ['Fuel', 'Public Transport', 'Cab Ride', 'Car Maintenance'],
    'Shopping': ['Clothing Purchase', 'Electronics', 'Home Goods', 'Online Shopping'],
    'Health': ['Doctor Visit', 'Pharmacy', 'Health Insurance', 'Gym Membership'],
    'Education': ['Course Fee', 'Books', 'Online Course', 'School Supplies'],
    'Salary': ['Monthly Salary', 'Paycheck'],
    'Income': ['Freelance Work', 'Side Gig', 'Consulting Fee', 'Rental Income'],
    'Investment': ['Stock Purchase', 'Mutual Fund Investment', 'Cryptocurrency'],
    'Clothing': ['New Shirt', 'Jeans', 'Shoes', 'Accessories'],
    'Subscriptions': ['Netflix', 'Spotify', 'Amazon Prime', 'Magazine Subscription'],
    'Fitness': ['Gym Membership', 'Fitness Equipment', 'Sports Gear'],
    'Travel': ['Flight Tickets', 'Hotel Booking', 'Vacation Expenses']
};

// Month names
const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
];

// Initialize the calendar when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM content loaded - initializing calendar page");
    
    // Log available elements to debug
    console.log("Menu button:", document.getElementById('menuBtn'));
    console.log("Side menu:", document.getElementById('sideMenu'));
    console.log("Menu close button:", document.getElementById('menuClose'));
    console.log("Overlay:", document.getElementById('overlay'));
    
    // Initialize menu and notification functionality
    initializeUI();
    
    // Initialize calendar
    initializeCalendar();
    
    // Generate transactions if none exist or if coming from landing page
    checkAndGenerateTransactions();
});

// Initialize UI elements
function initializeUI() {
    // Get DOM elements
    const menuBtn = document.getElementById('menuBtn');
    const sideMenu = document.getElementById('sideMenu');
    const overlay = document.getElementById('overlay');
    const menuClose = document.getElementById('menuClose');
    const notificationsBtn = document.getElementById('notificationsBtn');
    const notificationsPanel = document.getElementById('notificationsPanel');
    const chatbotBubble = document.getElementById('chatbotBubble');
    const clearAllNotificationsBtn = document.getElementById('clearAllNotificationsBtn');
    
    // Initialize menu functionality
    if (menuBtn && sideMenu && overlay) {
        console.log("Initializing menu functionality");
        menuBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log("Menu button clicked");
            sideMenu.classList.toggle('open');
            overlay.classList.toggle('active');
        });
        
        if (menuClose) {
            menuClose.addEventListener('click', function() {
                console.log("Close menu button clicked");
                sideMenu.classList.remove('open');
                overlay.classList.remove('active');
            });
        }
        
        if (overlay) {
            overlay.addEventListener('click', function() {
                console.log("Overlay clicked");
                sideMenu.classList.remove('open');
                overlay.classList.remove('active');
                if (notificationsPanel) notificationsPanel.classList.remove('show');
            });
        }
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (sideMenu && 
                sideMenu.classList.contains('open') && 
                !sideMenu.contains(e.target) && 
                !menuBtn.contains(e.target)) {
                console.log("Clicked outside menu");
                sideMenu.classList.remove('open');
                if (overlay) overlay.classList.remove('active');
            }
        });
    } else {
        console.error("Menu elements not found", { menuBtn, sideMenu, overlay });
    }
    
    // Initialize notification badge
    updateNotificationBadge();
    
    // Initialize notifications panel
    if (notificationsBtn && notificationsPanel) {
        // Render notifications in panel
        renderNotifications();
        
        notificationsBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            notificationsPanel.classList.toggle('show');
            console.log("Notification button clicked, panel visible:", notificationsPanel.classList.contains('show'));
        });
        
        // Close notifications panel when clicking outside
        document.addEventListener('click', function(e) {
            if (notificationsPanel && 
                notificationsPanel.classList.contains('show') && 
                !notificationsPanel.contains(e.target) && 
                !notificationsBtn.contains(e.target)) {
                notificationsPanel.classList.remove('show');
            }
        });
        
        // Clear all notifications button
        if (clearAllNotificationsBtn) {
            clearAllNotificationsBtn.addEventListener('click', function() {
                // Clear notifications
                localStorage.setItem('notifications', '[]');
                
                // Update badge
                updateNotificationBadge();
                
                // Render notifications
                renderNotifications();
                
                // Hide panel
                notificationsPanel.classList.remove('show');
            });
        }
    } else {
        console.error("Notification elements not found", { notificationsBtn, notificationsPanel });
    }
    
    // Initialize chatbot functionality if exists
    if (chatbotBubble && window.initChatbot) {
        window.initChatbot();
    } else if (chatbotBubble) {
        chatbotBubble.addEventListener('click', function() {
            console.log('Chatbot clicked, but initChatbot function not found');
            // Add fallback behavior or notification
            window.addNotification && window.addNotification(
                'Chatbot Available', 
                'The finance assistant is ready to help you with your questions.'
            );
        });
    }
}

// Initialize calendar functionality
function initializeCalendar() {
    // Get DOM elements
    const calendarGrid = document.getElementById('calendarGrid');
    const currentMonthElement = document.getElementById('currentMonth');
    const prevMonthBtn = document.getElementById('prevMonth');
    const nextMonthBtn = document.getElementById('nextMonth');
    const generateBtn = document.getElementById('generateRandomTransactions');
    const transactionModal = document.getElementById('transactionModal');
    const modalClose = document.getElementById('modalClose');
    const closeModalBtn = document.getElementById('closeModalBtn');
    
    // Event Listeners
    if (prevMonthBtn) {
        prevMonthBtn.addEventListener('click', function() {
            currentMonth--;
            if (currentMonth < 0) {
                currentMonth = 11;
                currentYear--;
            }
            renderCalendar();
        });
    }
    
    if (nextMonthBtn) {
        nextMonthBtn.addEventListener('click', function() {
            currentMonth++;
            if (currentMonth > 11) {
                currentMonth = 0;
                currentYear++;
            }
            renderCalendar();
        });
    }
    
    if (generateBtn) {
        generateBtn.addEventListener('click', generateRandomTransactions);
    }
    
    if (modalClose) {
        modalClose.addEventListener('click', function() {
            transactionModal.classList.remove('show');
        });
    }
    
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', function() {
            transactionModal.classList.remove('show');
        });
    }
    
    if (transactionModal) {
        transactionModal.addEventListener('click', function(e) {
            if (e.target === transactionModal) {
                transactionModal.classList.remove('show');
            }
        });
    }
    
    // Render calendar
    renderCalendar();
}

// Render the calendar with transactions
function renderCalendar() {
    const calendarGrid = document.getElementById('calendarGrid');
    const currentMonthElement = document.getElementById('currentMonth');
    
    if (!calendarGrid || !currentMonthElement) return;
    
    // Update month and year display
    currentMonthElement.textContent = `${monthNames[currentMonth]} ${currentYear}`;
    
    // Clear previous calendar days (after weekday headers)
    const dayElements = calendarGrid.querySelectorAll('.calendar-day');
    dayElements.forEach(day => day.remove());
    
    // Get first day of the month and number of days
    const firstDay = new Date(currentYear, currentMonth, 1).getDay();
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
    
    // Get previous month's days
    const daysInPrevMonth = new Date(currentYear, currentMonth, 0).getDate();
    
    // Get transactions for the month - optimize by filtering first for better performance
    let allTransactions = JSON.parse(localStorage.getItem('transactions') || '[]');
    let monthTransactions = allTransactions.filter(transaction => {
        const transactionDate = new Date(transaction.date);
        return transactionDate.getMonth() === currentMonth && 
               transactionDate.getFullYear() === currentYear;
    });
    
    // Create calendar days
    // Previous month days
    for (let i = 0; i < firstDay; i++) {
        const day = document.createElement('div');
        day.className = 'calendar-day inactive';
        const prevMonthDay = daysInPrevMonth - firstDay + i + 1;
        day.innerHTML = `<div class="calendar-day-number">${prevMonthDay}</div>`;
        calendarGrid.appendChild(day);
    }
    
    // Organize transactions by day for more efficient rendering
    const transactionsByDay = {};
    monthTransactions.forEach(transaction => {
        const date = new Date(transaction.date);
        const day = date.getDate();
        if (!transactionsByDay[day]) {
            transactionsByDay[day] = [];
        }
        transactionsByDay[day].push(transaction);
    });
    
    // Mobile detection
    const isMobile = window.innerWidth <= 768;
    const maxTransactionsToShow = isMobile ? 4 : 8;
    
    // Current month days
    for (let i = 1; i <= daysInMonth; i++) {
        const day = document.createElement('div');
        day.className = 'calendar-day';
        day.innerHTML = `<div class="calendar-day-number">${i}</div>`;
        
        // Add current day indicator
        const today = new Date();
        if (currentMonth === today.getMonth() && currentYear === today.getFullYear() && i === today.getDate()) {
            day.style.borderColor = 'var(--primary-color)';
            day.style.borderWidth = '2px';
            day.style.backgroundColor = 'rgba(107, 92, 255, 0.05)';
        }
        
        // Add transactions for this day
        const dayTransactions = transactionsByDay[i] || [];
        
        // Show limited transactions on mobile
        const transactionsToShow = dayTransactions.slice(0, maxTransactionsToShow);
        const remainingCount = dayTransactions.length - transactionsToShow.length;
        
        // Only render visible transactions (performance optimization)
        transactionsToShow.forEach(transaction => {
            const transactionElement = document.createElement('div');
            const amount = parseFloat(transaction.amount);
            const isExpense = amount < 0;
            
            transactionElement.className = `day-transaction ${isExpense ? 'expense' : 'income'}`;
            transactionElement.textContent = `${transaction.title} (${isExpense ? '-' : '+'}₹${Math.abs(amount).toFixed(2)})`;
            transactionElement.dataset.transaction = JSON.stringify(transaction);
            
            transactionElement.addEventListener('click', function(e) {
                e.stopPropagation();
                showTransactionDetails(transaction);
            });
            
            day.appendChild(transactionElement);
        });
        
        // Add indicator for more transactions
        if (remainingCount > 0) {
            const moreIndicator = document.createElement('div');
            moreIndicator.className = 'day-transaction';
            moreIndicator.style.textAlign = 'center';
            moreIndicator.style.backgroundColor = '#f0f0f0';
            moreIndicator.textContent = `+ ${remainingCount} more`;
            
            moreIndicator.addEventListener('click', function(e) {
                e.stopPropagation();
                showAllDayTransactions(dayTransactions, i);
            });
            
            day.appendChild(moreIndicator);
        }
        
        calendarGrid.appendChild(day);
    }
    
    // Next month days - only show these rows if needed
    const totalDaysShown = firstDay + daysInMonth;
    const rowsNeeded = Math.ceil(totalDaysShown / 7);
    const cellsNeeded = rowsNeeded * 7;
    const remainingCells = cellsNeeded - totalDaysShown;
    
    // Only add next month days if we need to complete the last row
    for (let i = 1; i <= remainingCells; i++) {
        const day = document.createElement('div');
        day.className = 'calendar-day inactive';
        day.innerHTML = `<div class="calendar-day-number">${i}</div>`;
        calendarGrid.appendChild(day);
    }
}

// Show all transactions for a specific day
function showAllDayTransactions(transactions, dayNumber) {
    const transactionModal = document.getElementById('transactionModal');
    const modalDetails = document.getElementById('modalDetails');
    const modalTitle = document.querySelector('.modal-title');
    
    if (!transactionModal || !modalDetails || !modalTitle) return;
    
    // Update modal title
    modalTitle.textContent = `Transactions for ${monthNames[currentMonth]} ${dayNumber}, ${currentYear}`;
    
    // Clear existing content
    modalDetails.innerHTML = '';
    
    // Add each transaction
    transactions.forEach(transaction => {
        const amount = parseFloat(transaction.amount);
        const isExpense = amount < 0;
        const formattedAmount = `${isExpense ? '-' : '+'}₹${Math.abs(amount).toFixed(2)}`;
        
        const transactionElement = document.createElement('div');
        transactionElement.className = 'modal-transaction';
        transactionElement.style.padding = '10px';
        transactionElement.style.margin = '5px 0';
        transactionElement.style.borderRadius = '5px';
        transactionElement.style.backgroundColor = isExpense ? 'rgba(255, 82, 82, 0.1)' : 'rgba(76, 175, 80, 0.1)';
        transactionElement.style.borderLeft = `3px solid ${isExpense ? '#FF5252' : '#4CAF50'}`;
        
        transactionElement.innerHTML = `
            <div><strong>${transaction.title}</strong></div>
            <div class="transaction-amount ${isExpense ? 'expense' : 'income'}">${formattedAmount}</div>
            <div style="font-size: 0.9rem;">Category: ${transaction.category}</div>
        `;
        
        transactionElement.addEventListener('click', () => {
            showTransactionDetails(transaction);
        });
        
        modalDetails.appendChild(transactionElement);
    });
    
    // Show modal
    transactionModal.classList.add('show');
}

// Show transaction details in modal
function showTransactionDetails(transaction) {
    const transactionModal = document.getElementById('transactionModal');
    const modalDetails = document.getElementById('modalDetails');
    
    if (!transactionModal || !modalDetails) return;
    
    // Format transaction details
    const amount = parseFloat(transaction.amount);
    const isExpense = amount < 0;
    const formattedAmount = `${isExpense ? '-' : '+'}₹${Math.abs(amount).toFixed(2)}`;
    const formattedDate = new Date(transaction.date).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    // Update modal content
    modalDetails.innerHTML = `
        <div class="modal-detail-row">
            <div class="modal-detail-label">Title:</div>
            <div>${transaction.title}</div>
        </div>
        <div class="modal-detail-row">
            <div class="modal-detail-label">Amount:</div>
            <div class="transaction-amount ${isExpense ? 'expense' : 'income'}">${formattedAmount}</div>
        </div>
        <div class="modal-detail-row">
            <div class="modal-detail-label">Category:</div>
            <div>${transaction.category}</div>
        </div>
        <div class="modal-detail-row">
            <div class="modal-detail-label">Date:</div>
            <div>${formattedDate}</div>
        </div>
        ${transaction.description ? `
        <div class="modal-detail-row">
            <div class="modal-detail-label">Description:</div>
            <div>${transaction.description}</div>
        </div>
        ` : ''}
    `;
    
    // Show modal
    transactionModal.classList.add('show');
}

// Generate random transactions for the current month
function generateRandomTransactions() {
    // Get existing transactions
    let transactions = JSON.parse(localStorage.getItem('transactions') || '[]');
    
    // Clear existing transactions for the current month
    transactions = transactions.filter(transaction => {
        const transactionDate = new Date(transaction.date);
        return !(transactionDate.getMonth() === currentMonth && 
               transactionDate.getFullYear() === currentYear);
    });
    
    // Adjust number of transactions based on device for better performance
    const isMobile = window.innerWidth <= 768;
    const minTransactions = isMobile ? 10 : 15;
    const maxTransactions = isMobile ? 20 : 30;
    const numTransactions = Math.floor(Math.random() * (maxTransactions - minTransactions + 1)) + minTransactions;
    
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
    
    // Create batch for better performance
    const newTransactions = [];
    
    for (let i = 0; i < numTransactions; i++) {
        // Random date in current month
        const day = Math.floor(Math.random() * daysInMonth) + 1;
        const date = new Date(currentYear, currentMonth, day);
        
        // Random category
        const category = transactionCategories[Math.floor(Math.random() * transactionCategories.length)];
        
        // Random title based on category
        const titles = transactionTitles[category] || ['Payment'];
        const title = titles[Math.floor(Math.random() * titles.length)];
        
        // Random amount (negative for expenses, positive for income)
        let amount;
        if (category === 'Salary' || category === 'Income' || category === 'Investment') {
            // Income: 10,000 to 50,000
            amount = Math.random() * 40000 + 10000;
        } else {
            // Expense: -100 to -5,000
            amount = -(Math.random() * 4900 + 100);
        }
        
        // Create transaction
        const transaction = {
            id: Date.now() + i,
            title: title,
            amount: amount.toFixed(2),
            date: date.toISOString().split('T')[0],
            category: category
        };
        
        newTransactions.push(transaction);
    }
    
    // Add all transactions at once for better performance
    transactions = transactions.concat(newTransactions);
    
    // Save transactions to localStorage
    localStorage.setItem('transactions', JSON.stringify(transactions));
    
    // Show notification
    if (window.addNotification) {
        window.addNotification(
            'Transactions Generated', 
            `${numTransactions} new transactions have been added to your calendar for ${monthNames[currentMonth]}.`
        );
    }
    
    // Re-render calendar
    renderCalendar();
}

// Check if transactions need to be generated
function checkAndGenerateTransactions() {
    const transactions = JSON.parse(localStorage.getItem('transactions') || '[]');
    const comingFromLanding = sessionStorage.getItem('comingFromLanding');
    
    // Generate transactions if none exist or if coming from landing page
    if (transactions.length === 0 || comingFromLanding === 'true') {
        generateRandomTransactions();
        
        // Clear the flag
        sessionStorage.removeItem('comingFromLanding');
    }
}

// Add event listener for window resize to adapt to screen changes
window.addEventListener('resize', debounce(function() {
    renderCalendar();
}, 250));

// Debounce function to limit resize event handling
function debounce(func, wait) {
    let timeout;
    return function() {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, arguments), wait);
    };
} 