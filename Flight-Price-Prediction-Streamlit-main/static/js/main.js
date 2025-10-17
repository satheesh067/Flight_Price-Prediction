// Initialize datetime pickers with enhanced styling
flatpickr("#departure", {
    enableTime: true,
    dateFormat: "Y-m-d H:i",
    minDate: "today",
    time_24hr: true,
    minuteIncrement: 15
});

flatpickr("#arrival", {
    enableTime: true,
    dateFormat: "Y-m-d H:i",
    minDate: "today",
    time_24hr: true,
    minuteIncrement: 15
});

// Load user stats on page load
async function loadUserStats() {
    try {
        const response = await fetch('/history');
        const history = await response.json();
        
        // Update stats cards
        document.getElementById('totalPredictions').textContent = history.length;
        
        if (history.length > 0) {
            const avgPrice = history.reduce((sum, h) => sum + h.price, 0) / history.length;
            document.getElementById('avgPrice').textContent = `₹${Math.round(avgPrice)}`;
            
            const uniqueRoutes = new Set(history.map(h => `${h.source}-${h.destination}`)).size;
            document.getElementById('uniqueRoutes').textContent = uniqueRoutes;
            
            const lastPrediction = new Date(history[0].timestamp);
            document.getElementById('lastPrediction').textContent = lastPrediction.toLocaleDateString();
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Enhanced form submission with animations
document.getElementById('predictionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const predictButton = document.getElementById('predictButton');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const buttonText = document.getElementById('buttonText');
    const resultDiv = document.getElementById('predictionResult');
    
    // Show loading state with enhanced animation
    loadingSpinner.classList.remove('d-none');
    buttonText.innerHTML = 'Predicting...';
    predictButton.disabled = true;
    predictButton.style.opacity = '0.7';
    
    // Add typing animation effect
    let dots = 0;
    const typingInterval = setInterval(() => {
        dots = (dots + 1) % 4;
        buttonText.innerHTML = 'Predicting' + '.'.repeat(dots);
    }, 500);
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                source: document.getElementById('source').value,
                destination: document.getElementById('destination').value,
                airline: document.getElementById('airline').value,
                departure: document.getElementById('departure').value,
                arrival: document.getElementById('arrival').value,
                stops: parseInt(document.getElementById('stops').value)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Enhanced result display with animations
            resultDiv.innerHTML = `
                <div class="prediction-result">
                    <div class="mb-3">
                        <i class="fas fa-check-circle" style="font-size: 3rem; color: #28a745;"></i>
                    </div>
                    <h4 class="mb-3">Price Prediction Complete!</h4>
                    <div class="price-display">₹${data.price}</div>
                    <div class="duration-display">
                        <i class="fas fa-clock"></i> Duration: ${data.duration.hours}h ${data.duration.minutes}m
                    </div>
                    <div class="mt-3">
                        <small class="opacity-75">
                            <i class="fas fa-info-circle"></i> 
                            Price includes taxes and fees. Actual prices may vary.
                        </small>
                    </div>
                </div>
            `;
            
            // Update stats after successful prediction
            setTimeout(() => {
                loadUserStats();
            }, 1000);
            
            // Show success animation
            resultDiv.style.display = 'block';
            
        } else {
            resultDiv.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>Error:</strong> ${data.error}
                </div>
            `;
        }
    } catch (error) {
        resultDiv.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Error:</strong> ${error.message}
            </div>
        `;
    } finally {
        // Hide loading state
        clearInterval(typingInterval);
        loadingSpinner.classList.add('d-none');
        buttonText.innerHTML = '<i class="fas fa-search"></i> Predict Price';
        predictButton.disabled = false;
        predictButton.style.opacity = '1';
    }
});

// Add form field animations
document.querySelectorAll('.form-control, .form-select').forEach(field => {
    field.addEventListener('focus', function() {
        this.style.transform = 'scale(1.02)';
        this.style.transition = 'all 0.3s ease';
    });
    
    field.addEventListener('blur', function() {
        this.style.transform = 'scale(1)';
    });
});

// Add hover effects to cards
document.querySelectorAll('.stats-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-5px) scale(1.02)';
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0) scale(1)';
    });
});

// Initialize stats on page load
document.addEventListener('DOMContentLoaded', function() {
    loadUserStats();
    
    // Add entrance animations
    const cards = document.querySelectorAll('.stats-card, .prediction-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'all 0.6s ease';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});