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
        
        // Form submission animation
        document.getElementById('signup-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Button animation
            document.getElementById('createBtn').innerHTML = 'Creating...';
            
            // Show success message after delay
            setTimeout(() => {
                document.getElementById('successMessage').classList.add('show');
                
                // Hide success message after 3 seconds
                setTimeout(() => {
                    document.getElementById('successMessage').classList.remove('show');
                    document.getElementById('createBtn').innerHTML = 'Create Profile';
                    document.getElementById('username').value = '';
                }, 3000);
            }, 1500);
        });
        function redirectToDashboard() {
            window.location.href = "index.html";
          }