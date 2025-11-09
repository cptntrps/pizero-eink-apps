/* Pi Zero 2W Dashboard - API Client */

/* ============================================
   API UTILITIES & ERROR HANDLING
   ============================================ */

/**
 * Global API state
 */
const API = {
    retryAttempts: 3,
    retryDelay: 1000,
    timeout: 30000,
    lastUpdated: null,
    isOnline: true
};

/**
 * Show loading state on button or element
 * @param {HTMLElement} element - Element to show loading state
 * @param {boolean} loading - Loading state
 */
function setLoadingState(element, loading) {
    if (!element) return;

    if (loading) {
        element.setAttribute('data-original-text', element.textContent);
        element.textContent = element.textContent.includes('Save') ? 'Saving...' : 'Loading...';
        element.disabled = true;
        element.classList.add('loading');
    } else {
        const originalText = element.getAttribute('data-original-text');
        if (originalText) {
            element.textContent = originalText;
        }
        element.disabled = false;
        element.classList.remove('loading');
    }
}

/**
 * Make API request with retry logic and error handling
 * @param {string} url - API endpoint
 * @param {Object} options - Fetch options
 * @param {number} retries - Number of retries remaining
 * @returns {Promise<Object>} Response data
 */
async function apiRequest(url, options = {}, retries = API.retryAttempts) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), API.timeout);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });

        clearTimeout(timeout);

        // Check if response is ok
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({
                success: false,
                message: `HTTP ${response.status}: ${response.statusText}`
            }));
            throw new Error(errorData.message || `HTTP ${response.status}`);
        }

        const data = await response.json();
        API.isOnline = true;
        return data;

    } catch (error) {
        clearTimeout(timeout);

        // Network error or timeout
        if (error.name === 'AbortError') {
            console.error('Request timeout:', url);
            if (retries > 0) {
                await new Promise(resolve => setTimeout(resolve, API.retryDelay));
                return apiRequest(url, options, retries - 1);
            }
            throw new Error('Request timeout. Please check your connection.');
        }

        // Retry on network errors
        if (retries > 0 && (error.message.includes('fetch') || error.message.includes('network'))) {
            console.warn(`Retrying request to ${url}. Attempts remaining: ${retries}`);
            await new Promise(resolve => setTimeout(resolve, API.retryDelay));
            return apiRequest(url, options, retries - 1);
        }

        API.isOnline = false;
        throw error;
    }
}

/**
 * Validate form data before submission
 * @param {Object} data - Form data to validate
 * @param {Object} rules - Validation rules
 * @returns {Object} {valid: boolean, errors: string[]}
 */
function validateFormData(data, rules) {
    const errors = [];

    for (const [field, rule] of Object.entries(rules)) {
        const value = data[field];

        if (rule.required && (!value || value === '')) {
            errors.push(`${rule.label || field} is required`);
        }

        if (rule.min !== undefined && value < rule.min) {
            errors.push(`${rule.label || field} must be at least ${rule.min}`);
        }

        if (rule.max !== undefined && value > rule.max) {
            errors.push(`${rule.label || field} must be at most ${rule.max}`);
        }

        if (rule.pattern && !rule.pattern.test(value)) {
            errors.push(`${rule.label || field} format is invalid`);
        }
    }

    return {
        valid: errors.length === 0,
        errors: errors
    };
}

/* ============================================
   CONFIGURATION API
   ============================================ */

/**
 * Load configuration from server
 * @returns {Promise<Object>} Configuration object
 */
async function loadConfig() {
    try {
        const config = await apiRequest('/api/config');

        // Populate Weather fields
        document.getElementById('weather-location').value = config.weather?.location || '';
        document.getElementById('weather-units').value = config.weather?.units || 'metric';
        document.getElementById('weather-interval').value = config.weather?.update_interval || 300;
        document.getElementById('weather-format').value = config.weather?.display_format || 'detailed';

        // Populate MBTA fields
        document.getElementById('mbta-home-id').value = config.mbta?.home_station_id || '';
        document.getElementById('mbta-home-name').value = config.mbta?.home_station_name || '';
        document.getElementById('mbta-work-id').value = config.mbta?.work_station_id || '';
        document.getElementById('mbta-work-name').value = config.mbta?.work_station_name || '';
        document.getElementById('mbta-interval').value = config.mbta?.update_interval || 30;
        document.getElementById('mbta-morning-start').value = config.mbta?.morning_start || '06:00';
        document.getElementById('mbta-morning-end').value = config.mbta?.morning_end || '12:00';
        document.getElementById('mbta-evening-start').value = config.mbta?.evening_start || '15:00';
        document.getElementById('mbta-evening-end').value = config.mbta?.evening_end || '21:00';

        // Populate Disney fields
        document.getElementById('disney-park').value = config.disney?.park_id || 6;
        document.getElementById('disney-interval').value = config.disney?.update_interval || 10;
        document.getElementById('disney-refresh').value = config.disney?.data_refresh_rides || 20;
        document.getElementById('disney-sort').value = config.disney?.sort_by || 'wait_time';

        // Populate Flights fields
        document.getElementById('flights-lat').value = config.flights?.lat || '';
        document.getElementById('flights-lon').value = config.flights?.lon || '';
        document.getElementById('flights-alt').value = config.flights?.altitude || '';

        // Populate Pomodoro fields
        document.getElementById('pomodoro-work').value = config.pomodoro?.work_duration || 1500;
        document.getElementById('pomodoro-short').value = config.pomodoro?.short_break || 300;
        document.getElementById('pomodoro-long').value = config.pomodoro?.long_break || 900;
        document.getElementById('pomodoro-sessions').value = config.pomodoro?.sessions_until_long_break || 4;

        // Populate Forbidden fields
        document.getElementById('forbidden-message').value = config.forbidden?.message || '';

        API.lastUpdated = new Date().toISOString();
        updateLastRefreshTime();
    } catch (err) {
        console.error('Failed to load config:', err);
        showToast('Failed to load configuration', 'error');
    }
}

/**
 * Save configuration section
 * @param {string} section - Configuration section name
 * @param {Object} data - Configuration data
 * @returns {Promise<Object>} Response object
 */
async function saveConfig(section, data) {
    return apiRequest(`/api/config/${section}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
}

/* ============================================
   MEDICINE API
   ============================================ */

/**
 * Load medicine data from server
 * @returns {Promise<Object>} Medicine data object
 */
async function loadMedicineData() {
    try {
        const response = await apiRequest('/api/v1/medicines');
        API.lastUpdated = new Date().toISOString();
        updateLastRefreshTime();
        // Transform v1 API response to old format
        return {
            medicines: response.data || [],
            tracking: {},
            time_windows: {}
        };
    } catch (error) {
        console.error('Failed to load medicine data:', error);
        showToast('Failed to load medicine data: ' + error.message, 'error');
        throw error;
    }
}

/**
 * Add new medicine
 * @param {Object} medicineData - Medicine object
 * @returns {Promise<Object>} Response object
 */
async function addMedicine(medicineData) {
    // Validate medicine data
    const validation = validateFormData(medicineData, {
        name: { required: true, label: 'Medicine name' },
        dosage: { required: true, label: 'Dosage' },
        time_window: { required: true, label: 'Time window' },
        pills_remaining: { required: true, min: 0, label: 'Pills remaining' },
        pills_per_dose: { required: true, min: 1, label: 'Pills per dose' }
    });

    if (!validation.valid) {
        const errorMsg = validation.errors.join(', ');
        showToast(errorMsg, 'error');
        throw new Error(errorMsg);
    }

    try {
        const result = await apiRequest('/api/v1/medicines', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(medicineData)
        });
        showToast(result.message || 'Medicine added successfully!', 'success');
        return result;
    } catch (error) {
        console.error('Failed to add medicine:', error);
        showToast('Failed to add medicine: ' + error.message, 'error');
        throw error;
    }
}

/**
 * Update existing medicine
 * @param {Object} medicineData - Medicine object with id
 * @returns {Promise<Object>} Response object
 */
async function updateMedicine(medicineData) {
    // Validate medicine data
    const validation = validateFormData(medicineData, {
        id: { required: true, label: 'Medicine ID' },
        name: { required: true, label: 'Medicine name' },
        dosage: { required: true, label: 'Dosage' },
        time_window: { required: true, label: 'Time window' }
    });

    if (!validation.valid) {
        const errorMsg = validation.errors.join(', ');
        showToast(errorMsg, 'error');
        throw new Error(errorMsg);
    }

    try {
        const result = await apiRequest('/api/v1/medicines', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(medicineData)
        });
        showToast(result.message || 'Medicine updated successfully!', 'success');
        return result;
    } catch (error) {
        console.error('Failed to update medicine:', error);
        showToast('Failed to update medicine: ' + error.message, 'error');
        throw error;
    }
}

/**
 * Delete medicine by ID
 * @param {string} medId - Medicine ID
 * @returns {Promise<Object>} Response object
 */
async function deleteMedicineById(medId) {
    try {
        const result = await apiRequest(`/api/v1/medicines/${medId}`, {
            method: 'DELETE'
        });
        showToast(result.message || 'Medicine deleted successfully!', 'success');
        return result;
    } catch (error) {
        console.error('Failed to delete medicine:', error);
        showToast('Failed to delete medicine: ' + error.message, 'error');
        throw error;
    }
}

/**
 * Mark medicine(s) as taken
 * @param {Array|string} medicineIds - Medicine ID(s)
 * @param {string} timestamp - Optional timestamp
 * @returns {Promise<Object>} Response object
 */
async function markMedicineTaken(medicineIds, timestamp = null) {
    const requestData = {
        medicine_ids: Array.isArray(medicineIds) ? medicineIds : [medicineIds]
    };

    if (timestamp) {
        requestData.timestamp = timestamp;
    }

    try {
        const result = await apiRequest('/api/v1/tracking/mark-taken', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(requestData)
        });
        showToast(result.message || 'Medicine marked as taken!', 'success');
        return result;
    } catch (error) {
        console.error('Failed to mark medicine as taken:', error);
        showToast('Failed to mark medicine as taken: ' + error.message, 'error');
        throw error;
    }
}

/**
 * Get pending medicines
 * @param {string} date - Optional date (YYYY-MM-DD)
 * @param {string} time - Optional time (HH:MM)
 * @returns {Promise<Object>} Pending medicines response
 */
async function getPendingMedicines(date = null, time = null) {
    let url = '/api/v1/tracking/pending';
    const params = new URLSearchParams();

    if (date) params.append('date', date);
    if (time) params.append('time', time);

    if (params.toString()) {
        url += '?' + params.toString();
    }

    try {
        const result = await apiRequest(url);
        return result;
    } catch (error) {
        console.error('Failed to get pending medicines:', error);
        showToast('Failed to get pending medicines: ' + error.message, 'error');
        throw error;
    }
}

/* ============================================
   MEDICINE TRACKING API (v1)
   ============================================ */

/**
 * Mark medicine as taken (v1 API)
 * @param {string} medId - Medicine ID
 * @returns {Promise<Object>} Response object
 */
async function markAsTaken(medId) {
    try {
        const result = await apiRequest('/api/v1/tracking/take', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({medicine_id: medId})
        });
        showToast(result.message || 'Medicine marked as taken!', 'success');
        return result;
    } catch (error) {
        console.error('Failed to mark medicine as taken:', error);
        showToast('Failed to mark medicine as taken: ' + error.message, 'error');
        throw error;
    }
}

/**
 * Skip medicine with reason
 * @param {string} medId - Medicine ID
 * @param {string} reason - Skip reason (forgot, side_effects, out_of_stock, doctor_advised, other)
 * @param {string} notes - Optional notes
 * @returns {Promise<Object>} Response object
 */
async function skipMedicine(medId, reason, notes = '') {
    try {
        const result = await apiRequest('/api/v1/tracking/skip', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                medicine_id: medId,
                reason: reason,
                notes: notes
            })
        });
        showToast(result.message || 'Medicine skipped successfully', 'success');
        return result;
    } catch (error) {
        console.error('Failed to skip medicine:', error);
        showToast('Failed to skip medicine: ' + error.message, 'error');
        throw error;
    }
}

/**
 * Get pending doses for today
 * @returns {Promise<Object>} Response with pending_doses array
 */
async function getPendingDoses() {
    // Tracking endpoints not yet implemented - return empty array
    return { pending_doses: [] };
}

/**
 * Get skip history
 * @param {Object} filters - Optional filters (start_date, end_date, medicine_id)
 * @returns {Promise<Object>} Response with skip_history array
 */
async function getSkipHistory(filters = {}) {
    let url = '/api/v1/tracking/skip-history';
    const params = new URLSearchParams();

    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.medicine_id) params.append('medicine_id', filters.medicine_id);

    if (params.toString()) {
        url += '?' + params.toString();
    }

    try {
        const result = await apiRequest(url);
        return result;
    } catch (error) {
        console.error('Failed to get skip history:', error);
        showToast('Failed to get skip history: ' + error.message, 'error');
        throw error;
    }
}

/**
 * Get detailed adherence statistics
 * @param {Object} filters - Optional filters (start_date, end_date)
 * @returns {Promise<Object>} Response with adherence statistics
 */
async function getAdherenceDetailed(filters = {}) {
    let url = '/api/v1/tracking/adherence-detailed';
    const params = new URLSearchParams();

    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);

    if (params.toString()) {
        url += '?' + params.toString();
    }

    try {
        const result = await apiRequest(url);
        return result;
    } catch (error) {
        console.error('Failed to get adherence statistics:', error);
        showToast('Failed to get adherence statistics: ' + error.message, 'error');
        throw error;
    }
}

/* ============================================
   UI UTILITY FUNCTIONS
   ============================================ */

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type of toast (success, error, info, warning)
 * @param {number} duration - Duration in milliseconds
 */
function showToast(message, type = 'info', duration = 4000) {
    // Remove any existing toasts
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    // Add to document
    document.body.appendChild(toast);

    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);

    // Remove after duration
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Update last refresh time display
 */
function updateLastRefreshTime() {
    const refreshElement = document.getElementById('last-refresh-time');
    if (refreshElement && API.lastUpdated) {
        const date = new Date(API.lastUpdated);
        const timeStr = date.toLocaleTimeString();
        refreshElement.textContent = `Last updated: ${timeStr}`;
    }
}

/**
 * Show/hide loading overlay
 * @param {boolean} show - Show or hide overlay
 */
function showLoadingOverlay(show) {
    let overlay = document.getElementById('loading-overlay');

    if (show && !overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>Loading...</p>
            </div>
        `;
        document.body.appendChild(overlay);
    } else if (!show && overlay) {
        overlay.remove();
    }
}

/**
 * Confirm dialog wrapper
 * @param {string} message - Confirmation message
 * @returns {Promise<boolean>} True if confirmed
 */
async function confirmDialog(message) {
    return new Promise((resolve) => {
        const confirmed = confirm(message);
        resolve(confirmed);
    });
}
