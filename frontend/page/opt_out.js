document.addEventListener('DOMContentLoaded', () => {
    const optOutBtn = document.getElementById('optOutBtn');
    const optInBtn = document.getElementById('optInBtn');
    const trackingStatus = document.getElementById('trackingStatus');
    const trackingStatusIndicator = document.getElementById('trackingStatusIndicator');
    
    // Check if user has already opted out
    const isOptedOut = localStorage.getItem('financialTrackingOptOut') === 'true';
    
    // Update UI based on current opt-out status
    updateOptOutUI(isOptedOut);
    
    // Add event listeners to buttons
    if (optOutBtn) {
        optOutBtn.addEventListener('click', () => {
            optOutOfTracking();
        });
    }
    
    if (optInBtn) {
        optInBtn.addEventListener('click', () => {
            optInToTracking();
        });
    }
    
    // Function to opt out of tracking
    function optOutOfTracking() {
        // Set opt-out flag in localStorage
        localStorage.setItem('financialTrackingOptOut', 'true');
        
        // Reset all financial data to zero
        const profileData = JSON.parse(localStorage.getItem('profileData') || '{}');
        
        if (profileData && profileData.expenses) {
            // Set all expense categories to zero
            Object.keys(profileData.expenses).forEach(category => {
                profileData.expenses[category] = 0;
            });
            
            // Update localStorage with zeroed data
            localStorage.setItem('profileData', JSON.stringify(profileData));
        }
        
        // Update UI
        updateOptOutUI(true);
        
        // Show confirmation message
        alert('You have successfully opted out of financial tracking. All tracking values have been set to zero.');
    }
    
    // Function to opt back in to tracking
    function optInToTracking() {
        // Remove opt-out flag
        localStorage.removeItem('financialTrackingOptOut');
        
        // Update UI
        updateOptOutUI(false);
        
        // Clear cached profile data to force reload from API
        localStorage.removeItem('profileData');
        
        // Show confirmation message
        alert('Financial tracking has been re-enabled. Your dashboard will now show your financial data again.');
        
        // Redirect to dashboard after short delay
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1000);
    }
    
    // Function to update UI based on opt-out status
    function updateOptOutUI(isOptedOut) {
        if (isOptedOut) {
            if (trackingStatus) trackingStatus.textContent = 'Disabled';
            if (trackingStatusIndicator) trackingStatusIndicator.querySelector('.status-dot').classList.remove('active');
            if (trackingStatusIndicator) trackingStatusIndicator.querySelector('.status-dot').classList.add('inactive');
            if (optOutBtn) optOutBtn.style.display = 'none';
            if (optInBtn) optInBtn.style.display = 'block';
        } else {
            if (trackingStatus) trackingStatus.textContent = 'Active';
            if (trackingStatusIndicator) trackingStatusIndicator.querySelector('.status-dot').classList.add('active');
            if (trackingStatusIndicator) trackingStatusIndicator.querySelector('.status-dot').classList.remove('inactive');
            if (optOutBtn) optOutBtn.style.display = 'block';
            if (optInBtn) optInBtn.style.display = 'none';
        }
    }
});