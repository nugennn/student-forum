/**
 * CSRF Token Helper
 * Provides utilities for reading CSRF token from cookies and attaching to AJAX requests
 */

/**
 * Get CSRF token from cookies
 * @returns {string} CSRF token value
 */
function getCsrfToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === ('csrftoken=')) {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Setup jQuery AJAX to include CSRF token in headers
 */
function setupCsrfForAjax() {
    const csrfToken = getCsrfToken();
    
    if (csrfToken) {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    // Only add CSRF token for relative URLs
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                }
            }
        });
    }
}

/**
 * Setup Fetch API to include CSRF token in headers
 * Returns a function that can be used as a wrapper for fetch
 */
function setupCsrfForFetch() {
    const csrfToken = getCsrfToken();
    
    return function(url, options = {}) {
        // Only add CSRF token for relative URLs (internal requests)
        if (!(/^http:.*/.test(url) || /^https:.*/.test(url))) {
            if (!options.headers) {
                options.headers = {};
            }
            options.headers['X-CSRFToken'] = csrfToken;
        }
        return fetch(url, options);
    };
}

/**
 * Setup Axios to include CSRF token in headers
 * (if Axios is being used in the project)
 */
function setupCsrfForAxios() {
    if (typeof axios !== 'undefined') {
        const csrfToken = getCsrfToken();
        if (csrfToken) {
            axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
        }
    }
}

/**
 * Prevent CSRF token mismatch caused by browser back-button caching
 * Add cache-control headers to prevent caching of POST responses
 */
function preventCsrfCaching() {
    // Add meta tags to prevent caching
    const meta = document.createElement('meta');
    meta.httpEquiv = 'Cache-Control';
    meta.content = 'no-cache, no-store, must-revalidate';
    document.head.appendChild(meta);
    
    const meta2 = document.createElement('meta');
    meta2.httpEquiv = 'Pragma';
    meta2.content = 'no-cache';
    document.head.appendChild(meta2);
    
    const meta3 = document.createElement('meta');
    meta3.httpEquiv = 'Expires';
    meta3.content = '0';
    document.head.appendChild(meta3);
}

/**
 * Initialize all CSRF protections
 * Call this function on page load
 */
function initializeCsrfProtection() {
    // Setup jQuery AJAX
    setupCsrfForAjax();
    
    // Setup Axios if available
    setupCsrfForAxios();
    
    // Prevent caching issues
    preventCsrfCaching();
    
    console.log('CSRF protection initialized');
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    initializeCsrfProtection();
});
