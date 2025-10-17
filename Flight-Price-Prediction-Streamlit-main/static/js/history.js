// Initialize price chart with enhanced styling
let priceChart = new Chart(document.getElementById('priceChart'), {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Predicted Prices',
            data: [],
            borderColor: '#667eea',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            borderWidth: 3,
            tension: 0.4,
            pointBackgroundColor: '#667eea',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 6,
            pointHoverRadius: 8,
            fill: true
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { 
                position: 'top',
                labels: {
                    usePointStyle: true,
                    padding: 20,
                    font: {
                        size: 14,
                        weight: '600'
                    }
                }
            },
            title: { 
                display: true, 
                text: 'Your Flight Price Predictions Over Time',
                font: {
                    size: 16,
                    weight: '600'
                },
                color: '#2c3e50'
            }
        },
        scales: {
            y: { 
                beginAtZero: true, 
                title: { 
                    display: true, 
                    text: 'Price (₹)',
                    font: {
                        size: 14,
                        weight: '600'
                    },
                    color: '#6c757d'
                },
                grid: {
                    color: 'rgba(0, 0, 0, 0.1)'
                },
                ticks: {
                    font: {
                        size: 12
                    },
                    color: '#6c757d'
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Date',
                    font: {
                        size: 14,
                        weight: '600'
                    },
                    color: '#6c757d'
                },
                grid: {
                    color: 'rgba(0, 0, 0, 0.1)'
                },
                ticks: {
                    font: {
                        size: 12
                    },
                    color: '#6c757d'
                }
            }
        },
        interaction: {
            intersect: false,
            mode: 'index'
        }
    }
});

// Enhanced stats calculation
function calculateStats(history) {
    const totalPredictions = history.length;
    const totalSpent = history.reduce((sum, record) => sum + record.price, 0);
    const avgPrice = totalSpent / totalPredictions;
    const uniqueRoutes = new Set(history.map(record => `${record.source}-${record.destination}`)).size;
    
    return {
        totalPredictions,
        totalSpent,
        avgPrice,
        uniqueRoutes
    };
}

// Animate number counting
function animateNumber(element, start, end, duration, prefix = '') {
    const startTime = performance.now();
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const current = Math.floor(start + (end - start) * progress);
        
        element.textContent = prefix + current.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

async function loadHistory() {
    try {
        const response = await fetch('/history');
        const history = await response.json();

        const tableBody = document.getElementById('historyTableBody');
        tableBody.innerHTML = '';

        // Update stats
        const stats = calculateStats(history);
        
        animateNumber(document.getElementById('totalPredictions'), 0, stats.totalPredictions, 1000);
        animateNumber(document.getElementById('totalSpent'), 0, Math.round(stats.totalSpent), 1000, '₹');
        animateNumber(document.getElementById('avgPrice'), 0, Math.round(stats.avgPrice), 1000, '₹');
        animateNumber(document.getElementById('uniqueRoutes'), 0, stats.uniqueRoutes, 1000);

        // Clear chart data
        priceChart.data.labels = [];
        priceChart.data.datasets[0].data = [];

        if (history.length === 0) {
            // Show empty state
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center">
                        <div class="empty-state">
                            <i class="fas fa-search"></i>
                            <h5>No predictions yet</h5>
                            <p>Start making predictions to see your history here!</p>
                            <a href="/predict-page" class="btn btn-primary">
                                <i class="fas fa-plus"></i> Make First Prediction
                            </a>
                        </div>
                    </td>
                </tr>
            `;
        } else {
            // Populate table with animations
            history.forEach((record, index) => {
                setTimeout(() => {
                    const row = tableBody.insertRow();
                    row.style.opacity = '0';
                    row.style.transform = 'translateX(-20px)';
                    row.innerHTML = `
                        <td>
                            <div class="d-flex align-items-center">
                                <i class="fas fa-calendar-alt text-primary me-2"></i>
                                ${new Date(record.timestamp).toLocaleDateString()}
                            </div>
                        </td>
                        <td>
                            <div class="d-flex align-items-center">
                                <i class="fas fa-route text-success me-2"></i>
                                <strong>${record.source}</strong> 
                                <i class="fas fa-arrow-right mx-2 text-muted"></i> 
                                <strong>${record.destination}</strong>
                            </div>
                        </td>
                        <td>
                            <div class="d-flex align-items-center">
                                <i class="fas fa-plane text-info me-2"></i>
                                ${record.airline}
                            </div>
                        </td>
                        <td>
                            <span class="badge bg-${record.stops === 0 ? 'success' : record.stops === 1 ? 'warning' : 'danger'}">
                                ${record.stops} stop${record.stops !== 1 ? 's' : ''}
                            </span>
                        </td>
                        <td>
                            <div class="d-flex align-items-center">
                                <i class="fas fa-clock text-warning me-2"></i>
                                ${record.duration}
                            </div>
                        </td>
                        <td>
                            <div class="d-flex align-items-center">
                                <i class="fas fa-rupee-sign text-success me-2"></i>
                                <strong class="text-success">₹${record.price}</strong>
                            </div>
                        </td>
                    `;
                    
                    // Animate row entrance
                    setTimeout(() => {
                        row.style.transition = 'all 0.3s ease';
                        row.style.opacity = '1';
                        row.style.transform = 'translateX(0)';
                    }, 50);
                }, index * 100);
            });

            // Update chart with enhanced data
            const chartData = history.map(record => ({
                x: new Date(record.timestamp).toLocaleDateString(),
                y: record.price
            })).reverse();

            priceChart.data.labels = chartData.map(d => d.x);
            priceChart.data.datasets[0].data = chartData.map(d => d.y);
        }

        priceChart.update();
        
        // Add fade-in animation to cards
        document.querySelectorAll('.stats-overview, .history-card, .chart-card').forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            setTimeout(() => {
                card.style.transition = 'all 0.6s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 200);
        });
        
    } catch (error) {
        console.error('Error loading history:', error);
        // Show error state
        document.getElementById('historyTableBody').innerHTML = `
            <tr>
                <td colspan="6" class="text-center">
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle"></i>
                        <strong>Error loading history:</strong> ${error.message}
                    </div>
                </td>
            </tr>
        `;
    }
}

function exportHistory() {
    // Add loading animation to export button
    const btn = event.target.closest('button');
    const originalText = btn.innerHTML;
    
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exporting...';
    btn.disabled = true;
    
    // Simulate export delay
    setTimeout(() => {
        window.location.href = '/export';
        btn.innerHTML = originalText;
        btn.disabled = false;
    }, 500);
}

// Add hover effects to table rows
document.addEventListener('DOMContentLoaded', function() {
    // Load initial history
    loadHistory();
    
    // Add click animation to export button
    document.querySelector('.btn-export').addEventListener('click', function() {
        this.style.transform = 'scale(0.95)';
        setTimeout(() => {
            this.style.transform = 'scale(1)';
        }, 150);
    });
    
    // Add periodic refresh for real-time updates
    setInterval(() => {
        loadHistory();
    }, 30000); // Refresh every 30 seconds
});


