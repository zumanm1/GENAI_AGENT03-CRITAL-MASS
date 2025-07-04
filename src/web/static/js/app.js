/**
 * Main JavaScript for Network Automation AI Agent
 * Common functionality and utilities
 */

// Global variables
let currentSessionId = null;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    checkSystemHealth();
    setInterval(updateStatusIndicator, 30000); // Update every 30 seconds
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('Network Automation AI Agent - Initializing...');
    
    // Generate or get session ID
    currentSessionId = generateSessionId();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize event listeners
    initializeEventListeners();
    
    console.log('Application initialized successfully');
}

/**
 * Generate a unique session ID
 */
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    // Handle navbar collapse on mobile
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            const navbarCollapse = document.querySelector('.navbar-collapse');
            navbarCollapse.classList.toggle('show');
        });
    }
    
    // Handle form submissions
    const forms = document.querySelectorAll('form[data-ajax="true"]');
    forms.forEach(form => {
        form.addEventListener('submit', handleAjaxForm);
    });
}

/**
 * Check system health
 */
function checkSystemHealth() {
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            updateStatusIndicator(data.status === 'healthy');
        })
        .catch(error => {
            console.error('Health check failed:', error);
            updateStatusIndicator(false);
        });
}

/**
 * Update status indicator
 */
function updateStatusIndicator(isHealthy = null) {
    const indicator = document.getElementById('status-indicator');
    if (!indicator) return;
    
    if (isHealthy === null) {
        // Just update timestamp
        checkSystemHealth();
        return;
    }
    
    if (isHealthy) {
        indicator.className = 'badge bg-success';
        indicator.textContent = 'Online';
    } else {
        indicator.className = 'badge bg-danger';
        indicator.textContent = 'Offline';
    }
}

/**
 * Show health check modal
 */
function checkHealth() {
    const modal = new bootstrap.Modal(document.getElementById('healthModal'));
    modal.show();
    
    // Load health data
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            const content = document.getElementById('health-content');
            content.innerHTML = formatHealthData(data);
        })
        .catch(error => {
            const content = document.getElementById('health-content');
            content.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Failed to load health data: ${error.message}
                </div>
            `;
        });
}

/**
 * Format health data for display
 */
function formatHealthData(data) {
    const statusClass = data.status === 'healthy' ? 'success' : 'danger';
    const statusIcon = data.status === 'healthy' ? 'check-circle' : 'times-circle';
    
    return `
        <div class="text-center mb-3">
            <i class="fas fa-${statusIcon} fa-3x text-${statusClass}"></i>
            <h4 class="mt-2 text-${statusClass}">${data.status.toUpperCase()}</h4>
        </div>
        <table class="table table-sm">
            <tr>
                <td><strong>Status:</strong></td>
                <td><span class="badge bg-${statusClass}">${data.status}</span></td>
            </tr>
            <tr>
                <td><strong>Database:</strong></td>
                <td><span class="badge bg-${data.database === 'connected' ? 'success' : 'danger'}">${data.database}</span></td>
            </tr>
            <tr>
                <td><strong>Timestamp:</strong></td>
                <td>${new Date(data.timestamp).toLocaleString()}</td>
            </tr>
        </table>
    `;
}

/**
 * Show statistics modal
 */
function showStats() {
    const modal = new bootstrap.Modal(document.getElementById('statsModal'));
    modal.show();
    
    // Load statistics
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            const content = document.getElementById('stats-content');
            content.innerHTML = formatStatsData(data);
        })
        .catch(error => {
            const content = document.getElementById('stats-content');
            content.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Failed to load statistics: ${error.message}
                </div>
            `;
        });
}

/**
 * Format statistics data for display
 */
function formatStatsData(data) {
    return `
        <div class="row">
            <div class="col-6 text-center">
                <h3 class="text-primary">${data.devices || 0}</h3>
                <p class="text-muted">Devices</p>
            </div>
            <div class="col-6 text-center">
                <h3 class="text-success">${data.documents || 0}</h3>
                <p class="text-muted">Documents</p>
            </div>
            <div class="col-6 text-center">
                <h3 class="text-info">${data.audit_results || 0}</h3>
                <p class="text-muted">Audit Results</p>
            </div>
            <div class="col-6 text-center">
                <h3 class="text-warning">${data.chat_messages || 0}</h3>
                <p class="text-muted">Chat Messages</p>
            </div>
        </div>
        <hr>
        <small class="text-muted">Last updated: ${new Date().toLocaleString()}</small>
    `;
}

/**
 * Show about modal
 */
function showAbout() {
    const modal = new bootstrap.Modal(document.getElementById('aboutModal'));
    modal.show();
}

/**
 * Handle AJAX form submissions
 */
function handleAjaxForm(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const url = form.action || window.location.pathname;
    const method = form.method || 'POST';
    
    // Show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...';
    submitButton.disabled = true;
    
    fetch(url, {
        method: method,
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', data.message || 'Operation completed successfully');
            if (data.redirect) {
                window.location.href = data.redirect;
            }
        } else {
            showAlert('danger', data.error || 'Operation failed');
        }
    })
    .catch(error => {
        console.error('Form submission error:', error);
        showAlert('danger', 'An error occurred while processing your request');
    })
    .finally(() => {
        // Reset button
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    });
}

/**
 * Show alert message
 */
function showAlert(type, message, duration = 5000) {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of main content
    const main = document.querySelector('main');
    main.insertBefore(alertContainer, main.firstChild);
    
    // Auto-dismiss after duration
    if (duration > 0) {
        setTimeout(() => {
            if (alertContainer.parentNode) {
                alertContainer.remove();
            }
        }, duration);
    }
}

/**
 * Show loading overlay
 */
function showLoading(message = 'Loading...') {
    const overlay = document.createElement('div');
    overlay.className = 'spinner-overlay';
    overlay.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary mb-3" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p>${message}</p>
        </div>
    `;
    document.body.appendChild(overlay);
    return overlay;
}

/**
 * Hide loading overlay
 */
function hideLoading(overlay) {
    if (overlay && overlay.parentNode) {
        overlay.remove();
    }
}

/**
 * Format date/time for display
 */
function formatDateTime(dateString) {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleString();
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Debounce function for search inputs
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('success', 'Copied to clipboard', 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        showAlert('danger', 'Failed to copy to clipboard', 2000);
    });
}

/**
 * Validate IP address
 */
function isValidIP(ip) {
    const regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return regex.test(ip);
}

/**
 * Validate hostname
 */
function isValidHostname(hostname) {
    const regex = /^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$/;
    return regex.test(hostname);
}

/**
 * Export functions for global use
 */
window.NetworkApp = {
    checkHealth,
    showStats,
    showAbout,
    showAlert,
    showLoading,
    hideLoading,
    formatDateTime,
    formatFileSize,
    copyToClipboard,
    isValidIP,
    isValidHostname,
    debounce
}; 