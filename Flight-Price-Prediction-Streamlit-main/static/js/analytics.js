// Analytics functionality
async function loadAnalytics() {
    try {
        const response = await fetch('/analytics');
        const analytics = await response.json();
        
        // Update price trends chart
        updatePriceTrendsChart(analytics.price_trends);
        
        // Update best deals section
        updateBestDeals(analytics.best_deals);
        
        // Update alerts summary
        updateAlertsSummary(analytics.alerts_summary);
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

async function loadRouteAnalytics(source, destination) {
    try {
        const response = await fetch(`/route-analytics?source=${source}&destination=${destination}`);
        const analytics = await response.json();
        
        // Update route statistics
        updateRouteStats(analytics.route_stats);
        
        // Update best booking time
        updateBestBookingTime(analytics.best_booking_time);
        
        // Update airline comparison chart
        updateAirlineComparison(analytics.airline_comparison);
    } catch (error) {
        console.error('Error loading route analytics:', error);
    }
}

function updatePriceTrendsChart(trends) {
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    if (window.priceChart) {
        window.priceChart.destroy();
    }
    
    window.priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: trends.map(t => new Date(t.date).toLocaleDateString()),
            datasets: [{
                label: 'Average Price',
                data: trends.map(t => t.avg_price),
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }, {
                label: 'Minimum Price',
                data: trends.map(t => t.min_price),
                borderColor: 'rgb(54, 162, 235)',
                tension: 0.1
            }, {
                label: 'Maximum Price',
                data: trends.map(t => t.max_price),
                borderColor: 'rgb(255, 99, 132)',
                tension: 0.1
            }]
        },
        options: UserPreferences.get_chart_options('line')
    });
}

function updateBestDeals(deals) {
    const dealsContainer = document.getElementById('bestDeals');
    dealsContainer.innerHTML = '';
    
    deals.forEach(deal => {
        const dealCard = document.createElement('div');
        dealCard.className = 'card mb-2';
        dealCard.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">${deal.source} → ${deal.destination}</h5>
                <p class="card-text">
                    <strong>Airline:</strong> ${deal.airline}<br>
                    <strong>Deal Price:</strong> ${UserPreferences.format_price(deal.deal_price)}<br>
                    <strong>Regular Price:</strong> ${UserPreferences.format_price(deal.avg_price)}<br>
                    <strong>Savings:</strong> ${UserPreferences.format_price(deal.savings)}
                </p>
            </div>
        `;
        dealsContainer.appendChild(dealCard);
    });
}

function updateAlertsSummary(summary) {
    const summaryContainer = document.getElementById('alertsSummary');
    summaryContainer.innerHTML = `
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Alerts Summary</h5>
                <p class="card-text">
                    <strong>Total Alerts:</strong> ${summary.total_alerts}<br>
                    <strong>Active Alerts:</strong> ${summary.active_alerts}<br>
                    <strong>Average Target Price:</strong> ${UserPreferences.format_price(summary.avg_target_price)}
                </p>
                <h6>Most Watched Routes:</h6>
                <ul>
                    ${Object.entries(summary.most_watched_routes)
                        .map(([route, count]) => `<li>${route}: ${count} alerts</li>`)
                        .join('')}
                </ul>
            </div>
        </div>
    `;
}

function updateRouteStats(stats) {
    const statsContainer = document.getElementById('routeStats');
    statsContainer.innerHTML = `
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Route Statistics</h5>
                <p class="card-text">
                    <strong>Average Price:</strong> ${UserPreferences.format_price(stats.avg_price)}<br>
                    <strong>Price Range:</strong> ${UserPreferences.format_price(stats.min_price)} - ${UserPreferences.format_price(stats.max_price)}<br>
                    <strong>Total Predictions:</strong> ${stats.total_predictions}
                </p>
                <h6>Airlines Distribution:</h6>
                ${createAirlinesChart(stats.airlines)}
            </div>
        </div>
    `;
}

function updateBestBookingTime(bookingTime) {
    const timeContainer = document.getElementById('bestBookingTime');
    timeContainer.innerHTML = `
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Best Booking Time</h5>
                <p class="card-text">
                    <strong>Best Time to Book:</strong> ${bookingTime.best_time}<br>
                    <strong>Best Price:</strong> ${UserPreferences.format_price(bookingTime.best_price)}<br>
                    <strong>Avoid Booking At:</strong> ${bookingTime.worst_time}<br>
                    <strong>Potential Savings:</strong> ${UserPreferences.format_price(bookingTime.savings_potential)}
                </p>
            </div>
        </div>
    `;
}

function updateAirlineComparison(airlines) {
    const ctx = document.getElementById('airlineChart').getContext('2d');
    
    if (window.airlineChart) {
        window.airlineChart.destroy();
    }
    
    window.airlineChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: airlines.map(a => a.airline),
            datasets: [{
                label: 'Average Price',
                data: airlines.map(a => a.avg_price),
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
                borderColor: 'rgb(75, 192, 192)',
                borderWidth: 1
            }]
        },
        options: UserPreferences.get_chart_options('bar')
    });
}

// Load analytics when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadAnalytics();
    
    // Load route analytics when source/destination changes
    const sourceSelect = document.getElementById('source');
    const destSelect = document.getElementById('destination');
    
    function updateRouteAnalytics() {
        const source = sourceSelect.value;
        const destination = destSelect.value;
        if (source && destination) {
            loadRouteAnalytics(source, destination);
        }
    }
    
    sourceSelect.addEventListener('change', updateRouteAnalytics);
    destSelect.addEventListener('change', updateRouteAnalytics);
});