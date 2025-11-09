/* Pi Zero 2W Dashboard - Main JavaScript */

/* ============================================
   INITIALIZATION
   ============================================ */

// Auto-refresh timer
let autoRefreshTimer = null;
let currentSection = 'dashboard';

// Load config on page load
window.addEventListener('DOMContentLoaded', () => {
    loadConfig();
    initMedicineForm();
    loadHardwareConfig();
    loadSystemConfig();
    loadMenuConfig();
    initAutoRefresh();
    addLastRefreshDisplay();
    enhanceFormSubmissions();
});

/* ============================================
   NAVIGATION FUNCTIONS
   ============================================ */

/**
 * Show specific content section and update active state
 * @param {string} section - Section ID to show
 */
function showSection(section) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));

    // Remove active state from all menu items
    document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));

    // Show selected section
    document.getElementById(section).classList.add('active');

    // Set active state on clicked menu item
    event.target.classList.add('active');

    // Update current section
    currentSection = section;

    // Load medicine data when medicine section is shown and start auto-refresh
    if (section === 'medicine') {
        loadMedicineDataAndDisplay();
        startAutoRefresh();
    } else {
        stopAutoRefresh();
    }
}

/**
 * Toggle submenu visibility
 * @param {string} id - Submenu ID prefix
 */
function toggleSubmenu(id) {
    const submenu = document.getElementById(id + '-submenu');
    submenu.style.display = submenu.style.display === 'none' ? 'block' : 'none';
}

/* ============================================
   UI UTILITY FUNCTIONS
   ============================================ */

/**
 * Show status message
 * @param {string} formId - Form ID prefix
 * @param {boolean} success - Success state
 * @param {string} message - Message to display
 */
function showStatus(formId, success, message) {
    const status = document.getElementById(formId + '-status');
    if (status) {
        status.className = 'status-message ' + (success ? 'success' : 'error');
        status.textContent = message;
        status.style.display = 'block';
        setTimeout(() => status.style.display = 'none', 3000);
    }
    // Also show toast notification
    showToast(message, success ? 'success' : 'error');
}

/* ============================================
   AUTO-REFRESH & REAL-TIME FEATURES
   ============================================ */

/**
 * Initialize auto-refresh functionality
 */
function initAutoRefresh() {
    // Auto-refresh medicine data every 60 seconds if on medicine page
}

/**
 * Start auto-refresh timer
 */
function startAutoRefresh() {
    stopAutoRefresh(); // Clear any existing timer

    autoRefreshTimer = setInterval(() => {
        if (currentSection === 'medicine') {
            loadMedicineDataAndDisplay();
        }
    }, 60000); // 60 seconds
}

/**
 * Stop auto-refresh timer
 */
function stopAutoRefresh() {
    if (autoRefreshTimer) {
        clearInterval(autoRefreshTimer);
        autoRefreshTimer = null;
    }
}

/**
 * Add last refresh time display to medicine section
 */
function addLastRefreshDisplay() {
    const medicineSection = document.getElementById('medicine');
    if (medicineSection) {
        const refreshDiv = document.createElement('div');
        refreshDiv.className = 'last-refresh';
        refreshDiv.id = 'last-refresh-time';
        refreshDiv.innerHTML = '<span class="refresh-indicator online"></span>Ready';

        const firstCard = medicineSection.querySelector('.card');
        if (firstCard) {
            firstCard.appendChild(refreshDiv);
        }
    }
}

/**
 * Enhance form submissions with loading states
 */
function enhanceFormSubmissions() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                setLoadingState(submitBtn, true);
                // Loading state will be removed by API response handlers
                setTimeout(() => setLoadingState(submitBtn, false), 5000); // Safety timeout
            }
        });
    });
}

/* ============================================
   FORM SUBMISSION HANDLERS
   ============================================ */

// Weather Form
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('weather-form').addEventListener('submit', e => {
        e.preventDefault();
        saveConfig('weather', {
            location: document.getElementById('weather-location').value,
            units: document.getElementById('weather-units').value,
            update_interval: parseInt(document.getElementById('weather-interval').value),
            display_format: document.getElementById('weather-format').value
        })
        .then(data => showStatus('weather', data.success, data.message))
        .catch(err => showStatus('weather', false, 'Error: ' + err));
    });
});

// MBTA Form
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('mbta-form').addEventListener('submit', e => {
        e.preventDefault();
        saveConfig('mbta', {
            home_station_id: document.getElementById('mbta-home-id').value,
            home_station_name: document.getElementById('mbta-home-name').value,
            work_station_id: document.getElementById('mbta-work-id').value,
            work_station_name: document.getElementById('mbta-work-name').value,
            update_interval: parseInt(document.getElementById('mbta-interval').value),
            morning_start: document.getElementById('mbta-morning-start').value,
            morning_end: document.getElementById('mbta-morning-end').value,
            evening_start: document.getElementById('mbta-evening-start').value,
            evening_end: document.getElementById('mbta-evening-end').value
        })
        .then(data => showStatus('mbta', data.success, data.message))
        .catch(err => showStatus('mbta', false, 'Error: ' + err));
    });
});

// Disney Form
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('disney-form').addEventListener('submit', e => {
        e.preventDefault();
        saveConfig('disney', {
            park_id: parseInt(document.getElementById('disney-park').value),
            update_interval: parseInt(document.getElementById('disney-interval').value),
            data_refresh_rides: parseInt(document.getElementById('disney-refresh').value),
            sort_by: document.getElementById('disney-sort').value
        })
        .then(data => showStatus('disney', data.success, data.message))
        .catch(err => showStatus('disney', false, 'Error: ' + err));
    });
});

// Flights Form
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('flights-form').addEventListener('submit', e => {
        e.preventDefault();
        saveConfig('flights', {
            lat: document.getElementById('flights-lat').value,
            lon: document.getElementById('flights-lon').value,
            altitude: parseInt(document.getElementById('flights-alt').value)
        })
        .then(data => showStatus('flights', data.success, data.message))
        .catch(err => showStatus('flights', false, 'Error: ' + err));
    });
});

// Pomodoro Form
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('pomodoro-form').addEventListener('submit', e => {
        e.preventDefault();
        saveConfig('pomodoro', {
            work_duration: parseInt(document.getElementById('pomodoro-work').value),
            short_break: parseInt(document.getElementById('pomodoro-short').value),
            long_break: parseInt(document.getElementById('pomodoro-long').value),
            sessions_until_long_break: parseInt(document.getElementById('pomodoro-sessions').value)
        })
        .then(data => showStatus('pomodoro', data.success, data.message))
        .catch(err => showStatus('pomodoro', false, 'Error: ' + err));
    });
});

// Forbidden Form
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('forbidden-form').addEventListener('submit', e => {
        e.preventDefault();
        saveConfig('forbidden', {
            message: document.getElementById('forbidden-message').value
        })
        .then(data => showStatus('forbidden', data.success, data.message))
        .catch(err => showStatus('forbidden', false, 'Error: ' + err));
    });
});

/* ============================================
   HARDWARE CONFIGURATION
   ============================================ */

/**
 * Load hardware configuration
 */
function loadHardwareConfig() {
    fetch('/api/config/hardware')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.config) {
                const cfg = data.config;

                // Profile and input mode
                if (cfg.profile) document.getElementById('hw-profile').value = cfg.profile;
                if (cfg.input_mode) document.getElementById('hw-input-mode').value = cfg.input_mode;

                // Touch settings
                if (cfg.touch) {
                    document.getElementById('hw-touch-enabled').checked = cfg.touch.enabled !== false;
                    if (cfg.touch.driver) document.getElementById('hw-touch-driver').value = cfg.touch.driver;
                    if (cfg.touch.int_pin !== undefined) document.getElementById('hw-touch-int-pin').value = cfg.touch.int_pin;
                    if (cfg.touch.i2c_address) document.getElementById('hw-touch-i2c').value = cfg.touch.i2c_address;
                }

                // Button settings
                if (cfg.button) {
                    if (cfg.button.gpio_pin !== undefined) document.getElementById('hw-button-gpio').value = cfg.button.gpio_pin;
                    if (cfg.button.long_press_threshold !== undefined) document.getElementById('hw-button-long-press').value = cfg.button.long_press_threshold;
                    if (cfg.button.bounce_time !== undefined) document.getElementById('hw-button-bounce').value = cfg.button.bounce_time;
                    document.getElementById('hw-button-pull-up').checked = cfg.button.pull_up !== false;
                }

                // Display settings
                if (cfg.display) {
                    if (cfg.display.model) document.getElementById('hw-display-model').value = cfg.display.model;
                    document.getElementById('hw-display-has-touch').checked = cfg.display.has_touch === true;
                }
            }
        })
        .catch(err => console.error('Error loading hardware config:', err));
}

/**
 * Detect hardware automatically
 */
function detectHardware() {
    showStatus('hardware', true, 'Detecting hardware...');

    fetch('/api/hardware/detect', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showStatus('hardware', true, 'Hardware detected successfully!');
                loadHardwareConfig();
            } else {
                showStatus('hardware', false, data.message || 'Detection failed');
            }
        })
        .catch(err => showStatus('hardware', false, 'Error: ' + err));
}

// Hardware Form
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('hardware-form').addEventListener('submit', e => {
        e.preventDefault();

        const config = {
            profile: document.getElementById('hw-profile').value,
            input_mode: document.getElementById('hw-input-mode').value,
            touch: {
                enabled: document.getElementById('hw-touch-enabled').checked,
                driver: document.getElementById('hw-touch-driver').value,
                int_pin: parseInt(document.getElementById('hw-touch-int-pin').value),
                i2c_address: document.getElementById('hw-touch-i2c').value
            },
            button: {
                gpio_pin: parseInt(document.getElementById('hw-button-gpio').value),
                long_press_threshold: parseInt(document.getElementById('hw-button-long-press').value),
                bounce_time: parseInt(document.getElementById('hw-button-bounce').value),
                pull_up: document.getElementById('hw-button-pull-up').checked
            },
            display: {
                model: document.getElementById('hw-display-model').value,
                has_touch: document.getElementById('hw-display-has-touch').checked
            }
        };

        fetch('/api/config/hardware', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        })
        .then(response => response.json())
        .then(data => showStatus('hardware', data.success, data.message))
        .catch(err => showStatus('hardware', false, 'Error: ' + err));
    });
});

/* ============================================
   SYSTEM SETTINGS
   ============================================ */

/**
 * Load system configuration
 */
function loadSystemConfig() {
    fetch('/api/config/system')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.config) {
                const cfg = data.config;

                // WiFi settings
                if (cfg.wifi_ssid) document.getElementById('sys-wifi-ssid').value = cfg.wifi_ssid;
                // Don't populate password for security

                // Hotspot settings
                if (cfg.hotspot_enabled !== undefined) document.getElementById('sys-hotspot-enabled').checked = cfg.hotspot_enabled;
                if (cfg.hotspot_ssid) document.getElementById('sys-hotspot-ssid').value = cfg.hotspot_ssid;

                // Display settings
                if (cfg.display_brightness !== undefined) {
                    document.getElementById('sys-brightness').value = cfg.display_brightness;
                    document.getElementById('brightness-value').textContent = cfg.display_brightness + '%';
                }
                if (cfg.rotation !== undefined) document.getElementById('sys-rotation').value = cfg.rotation;
                if (cfg.refresh_mode) document.getElementById('sys-refresh-mode').value = cfg.refresh_mode;

                // System options
                if (cfg.timezone) document.getElementById('sys-timezone').value = cfg.timezone;

                // Power management
                if (cfg.auto_sleep !== undefined) document.getElementById('sys-auto-sleep').checked = cfg.auto_sleep;
                if (cfg.sleep_timeout) document.getElementById('sys-sleep-timeout').value = cfg.sleep_timeout;

                // Monitoring
                if (cfg.enable_metrics !== undefined) document.getElementById('sys-enable-metrics').checked = cfg.enable_metrics;
            }
        })
        .catch(err => console.error('Error loading system config:', err));
}

// System Form
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('system-form').addEventListener('submit', e => {
        e.preventDefault();

        const config = {
            wifi_ssid: document.getElementById('sys-wifi-ssid').value,
            hotspot_enabled: document.getElementById('sys-hotspot-enabled').checked,
            hotspot_ssid: document.getElementById('sys-hotspot-ssid').value,
            display_brightness: parseInt(document.getElementById('sys-brightness').value),
            rotation: parseInt(document.getElementById('sys-rotation').value),
            refresh_mode: document.getElementById('sys-refresh-mode').value,
            timezone: document.getElementById('sys-timezone').value,
            auto_sleep: document.getElementById('sys-auto-sleep').checked,
            sleep_timeout: parseInt(document.getElementById('sys-sleep-timeout').value),
            enable_metrics: document.getElementById('sys-enable-metrics').checked
        };

        // Only include password if provided
        const wifiPassword = document.getElementById('sys-wifi-password').value;
        if (wifiPassword) {
            config.wifi_password = wifiPassword;
        }

        const hotspotPassword = document.getElementById('sys-hotspot-password').value;
        if (hotspotPassword) {
            config.hotspot_password = hotspotPassword;
        }

        fetch('/api/config/system', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        })
        .then(response => response.json())
        .then(data => showStatus('system', data.success, data.message))
        .catch(err => showStatus('system', false, 'Error: ' + err));
    });
});

/* ============================================
   MENU CONFIGURATION
   ============================================ */

/**
 * Load menu configuration
 */
function loadMenuConfig() {
    fetch('/api/config/menu')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.config) {
                const cfg = data.config;

                // Load app list configuration
                if (cfg.apps) {
                    cfg.apps.forEach(app => {
                        const appId = app.id || app.name.toLowerCase().replace(/\s+/g, '-');
                        const enabledEl = document.getElementById(`app-${appId}-enabled`);
                        const nameEl = document.getElementById(`app-${appId}-name`);
                        const orderEl = document.getElementById(`app-${appId}-order`);

                        if (enabledEl) enabledEl.checked = app.enabled !== false;
                        if (nameEl) nameEl.value = app.name || '';
                        if (orderEl) orderEl.value = app.order || 0;
                    });
                }

                // Menu behavior settings
                if (cfg.button_hold_time !== undefined) {
                    document.getElementById('menu-button-hold').value = cfg.button_hold_time;
                }
                if (cfg.scroll_speed !== undefined) {
                    document.getElementById('menu-scroll-speed').value = cfg.scroll_speed;
                }
            }
        })
        .catch(err => console.error('Error loading menu config:', err));
}

/**
 * Move app up or down in order
 */
function moveApp(appId, direction) {
    const orderInput = document.getElementById(`app-${appId}-order`);
    if (!orderInput) return;

    let currentOrder = parseInt(orderInput.value);
    if (direction === 'up' && currentOrder > 1) {
        orderInput.value = currentOrder - 1;
    } else if (direction === 'down' && currentOrder < 10) {
        orderInput.value = currentOrder + 1;
    }
}

// Menu Form
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('menu-form').addEventListener('submit', e => {
        e.preventDefault();

        // Collect app configurations
        const apps = [];
        const appIds = ['medicine', 'disney', 'flights', 'forbidden', 'reboot'];

        appIds.forEach(id => {
            const enabled = document.getElementById(`app-${id}-enabled`);
            const name = document.getElementById(`app-${id}-name`);
            const order = document.getElementById(`app-${id}-order`);

            if (enabled && name && order) {
                apps.push({
                    id: id,
                    name: name.value,
                    enabled: enabled.checked,
                    order: parseInt(order.value)
                });
            }
        });

        const config = {
            apps: apps,
            button_hold_time: parseInt(document.getElementById('menu-button-hold').value),
            scroll_speed: parseInt(document.getElementById('menu-scroll-speed').value)
        };

        fetch('/api/config/menu', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        })
        .then(response => response.json())
        .then(data => showStatus('menu', data.success, data.message))
        .catch(err => showStatus('menu', false, 'Error: ' + err));
    });
});
