const particles = document.querySelector('.particles');
        for (let i = 0; i < 50; i++) {
            let particle = document.createElement('div');
            particle.className = 'particle';
            
            // Random position
            let posX = Math.random() * 100;
            let posY = Math.random() * 100;
            particle.style.left = posX + '%';
            particle.style.top = posY + '%';
            
            // Random size
            let size = Math.random() * 5 + 2;
            particle.style.width = size + 'px';
            particle.style.height = size + 'px';
            
            // Random animation duration
            let duration = Math.random() * 10 + 5;
            particle.style.animationDuration = duration + 's';
            
            // Random delay
            let delay = Math.random() * 5;
            particle.style.animationDelay = delay + 's';
            
            particles.appendChild(particle);
        }
        
        // Currency icon animation
        const icons = document.querySelectorAll('.icon');
        icons.forEach((icon, index) => {
            let delay = index * 0.5;
            let duration = Math.random() * 15 + 10;
            icon.style.animationDelay = delay + 's';
            icon.style.animationDuration = duration + 's';
        });
        
        // Function to fetch user profile data from Mockaroo
        async function fetchUserProfile() {
            try {
                const response = await fetch('https://my.api.mockaroo.com/expenditures_and_savings.json', {
                    method: 'GET',
                    headers: {
                        'X-API-Key': 'a1055fe0'
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch profile data');
                }

                const data = await response.json();
                return data;
            } catch (error) {
                console.error('Error fetching profile data:', error);
                // Return default data in case of error
                return {
                    income: 50000,
                    expenses: {
                        groceries: 5000,
                        transport: 2000,
                        eating_out: 3000,
                        entertainment: 2000,
                        utilities: 4000,
                        healthcare: 2000,
                        education: 3000,
                        miscellaneous: 2000
                    },
                    savings_goal: 10000,
                    disposable_income: 27000
                };
            }
        }

        // Form submission animation and API call
        document.getElementById('signup-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            
            // Button animation
            document.getElementById('createBtn').innerHTML = 'Creating...';
            
            try {
                // Fetch profile data from Mockaroo
                const profileData = await fetchUserProfile();
                
                // Store user data in localStorage
                localStorage.setItem('username', username);
                localStorage.setItem('profileData', JSON.stringify(profileData));
                localStorage.setItem('lastUpdate', new Date().toISOString());
                
                // Show success message
                document.getElementById('successMessage').classList.add('show');
                
                // Redirect to dashboard after 3 seconds
                setTimeout(() => {
                    window.location.href = "index.html";
                }, 3000);
                
            } catch (error) {
                console.error('Error during profile creation:', error);
                document.getElementById('createBtn').innerHTML = 'Create Profile';
                alert('There was an error creating your profile. Please try again.');
            }
        });
        function redirectToDashboard() {
            window.location.href = "index.html";
          }