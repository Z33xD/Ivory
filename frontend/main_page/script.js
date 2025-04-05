const ctx = document.getElementById('expenseChart').getContext('2d');
        let expenseChart;

        // Sample data
        const expenseData = {
            labels: ['Housing', 'Food', 'Transportation', 'Utilities', 'Entertainment', 'Shopping', 'Healthcare'],
            datasets: [{
                data: [30, 20, 15, 10, 10, 10, 5],
                backgroundColor: [
                    '#ffdac1', // Soft peach (Needs)
                    '#b5ead7', // Mint green (Wants)
                    '#f4acb7',
                    '#ffe5b4',
                    '#c7f9cc',
                    '#a9def9'
                ],
                borderWidth: 1
            }]
        };

        // Chart options
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

        // Create chart
        window.onload = function() {
            expenseChart = new Chart(ctx, {
                type: 'pie',
                data: expenseData,
                options: chartOptions
            });
        };

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