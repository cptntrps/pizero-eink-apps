/* Pi Zero 2W Dashboard - Medicine Tracker */

/* ============================================
   MEDICINE DATA & STATE
   ============================================ */
let medicineData = {medicines: [], tracking: {}, time_windows: {}};
let currentSkipMedicineId = null;

/* ============================================
   MEDICINE UI FUNCTIONS
   ============================================ */

/**
 * Load medicine data from server and display
 */
function loadMedicineDataAndDisplay() {
    loadMedicineData()
        .then(data => {
            medicineData = data;
            displayMedicineList();
            updateRefreshIndicator(true);
        })
        .catch(err => {
            console.error('Failed to load medicine data:', err);
            updateRefreshIndicator(false);
        });
}

/**
 * Update refresh indicator
 * @param {boolean} online - Online status
 */
function updateRefreshIndicator(online) {
    const indicator = document.querySelector('#last-refresh-time .refresh-indicator');
    if (indicator) {
        indicator.className = `refresh-indicator ${online ? 'online' : 'offline'}`;
    }
}

/**
 * Display medicine list in the UI
 */
function displayMedicineList() {
    const listEl = document.getElementById('medicine-list');
    if (!medicineData.medicines || medicineData.medicines.length === 0) {
        listEl.innerHTML = '<p style="color: #6b7280;">No medicines added yet. Click "Add New Medicine" to get started.</p>';
        return;
    }

    let html = '';
    medicineData.medicines.forEach(med => {
        const daysText = med.days.map(d => d.charAt(0).toUpperCase() + d.slice(1)).join(', ');
        const windowText = med.time_window.charAt(0).toUpperCase() + med.time_window.slice(1);
        const foodText = med.with_food ? 'Yes' : 'No';

        const pillsRemaining = med.pills_remaining || 0;
        const lowThreshold = med.low_stock_threshold || 10;
        const isLowStock = pillsRemaining <= lowThreshold;
        const stockColor = isLowStock ? '#ef4444' : '#374151';
        const stockWarning = isLowStock ? ' ⚠️ REORDER SOON!' : '';
        const borderColor = isLowStock ? '#ef4444' : '#e5e7eb';

        html += `
            <div style="border: 2px solid ${borderColor}; border-radius: 6px; padding: 16px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 4px;">${med.name}</h3>
                        <p style="color: #6b7280; font-size: 13px; margin-bottom: 8px;">${med.dosage}</p>
                        <p style="font-size: 12px; color: #374151;">
                            <strong>Time:</strong> ${windowText} (${med.window_start}-${med.window_end})<br>
                            <strong>Days:</strong> ${daysText}<br>
                            <strong>With food:</strong> ${foodText}<br>
                            <strong style="color: ${stockColor};">Pills remaining:</strong> <span style="color: ${stockColor}; font-weight: 600;">${pillsRemaining}${stockWarning}</span><br>
                            <strong>Pills per dose:</strong> ${med.pills_per_dose || 1}
                            ${med.notes ? '<br><strong>Notes:</strong> ' + med.notes : ''}
                        </p>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button onclick="editMedicine('${med.id}')" class="save-btn" style="padding: 6px 12px; font-size: 12px;">Edit</button>
                        <button onclick="deleteMedicine('${med.id}')" class="save-btn" style="padding: 6px 12px; font-size: 12px; background: #ef4444;">Delete</button>
                    </div>
                </div>
            </div>
        `;
    });
    listEl.innerHTML = html;
}

/**
 * Show the add medicine form
 */
function showAddMedicineForm() {
    document.getElementById('medicine-form-card').style.display = 'block';
    document.getElementById('medicine-form-title').textContent = 'Add Medicine';
    document.getElementById('medicine-form').reset();
    document.getElementById('medicine-id').value = '';
    // Check all day checkboxes by default
    document.querySelectorAll('input[name="day"]').forEach(cb => cb.checked = true);
}

/**
 * Cancel medicine form and hide it
 */
function cancelMedicineForm() {
    document.getElementById('medicine-form-card').style.display = 'none';
    document.getElementById('medicine-form').reset();
}

/**
 * Edit existing medicine
 * @param {string} medId - Medicine ID
 */
function editMedicine(medId) {
    const med = medicineData.medicines.find(m => m.id === medId);
    if (!med) return;

    document.getElementById('medicine-form-card').style.display = 'block';
    document.getElementById('medicine-form-title').textContent = 'Edit Medicine';
    document.getElementById('medicine-id').value = med.id;
    document.getElementById('medicine-name').value = med.name;
    document.getElementById('medicine-dosage').value = med.dosage;
    document.getElementById('medicine-window').value = med.time_window;
    document.getElementById('medicine-food').value = med.with_food.toString();
    document.getElementById('medicine-notes').value = med.notes || '';
    document.getElementById('medicine-pills-remaining').value = med.pills_remaining || 0;
    document.getElementById('medicine-pills-per-dose').value = med.pills_per_dose || 1;
    document.getElementById('medicine-low-threshold').value = med.low_stock_threshold || 10;

    // Set day checkboxes
    document.querySelectorAll('input[name="day"]').forEach(cb => {
        cb.checked = med.days.includes(cb.value);
    });
}

/**
 * Delete medicine with confirmation
 * @param {string} medId - Medicine ID
 */
async function deleteMedicine(medId) {
    const confirmed = await confirmDialog('Are you sure you want to delete this medicine? This action cannot be undone.');
    if (!confirmed) return;

    try {
        const data = await deleteMedicineById(medId);
        if (data.success) {
            await loadMedicineDataAndDisplay();
            showStatus('medicine-form', true, 'Medicine deleted successfully');
        } else {
            showStatus('medicine-form', false, data.message);
        }
    } catch (err) {
        showStatus('medicine-form', false, 'Error: ' + err.message);
    }
}

/* ============================================
   TAB SWITCHING
   ============================================ */

/**
 * Switch between medicine tracker tabs
 * @param {string} tabName - Tab to switch to (medicines, pending, skip-history, adherence)
 */
function switchMedicineTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`tab-${tabName}`).classList.add('active');

    // Update tab content
    document.querySelectorAll('.medicine-tab').forEach(tab => tab.classList.remove('active'));
    document.getElementById(`medicine-tab-${tabName}`).classList.add('active');

    // Load data for the selected tab
    if (tabName === 'pending') {
        loadPendingDoses();
    } else if (tabName === 'skip-history') {
        loadSkipHistory();
    } else if (tabName === 'adherence') {
        loadAdherenceStats();
    }
}

/* ============================================
   PENDING DOSES FUNCTIONS
   ============================================ */

/**
 * Load and display pending doses for today
 */
function loadPendingDoses() {
    getPendingDoses()
        .then(data => {
            displayPendingDoses(data.pending_doses || []);
        })
        .catch(err => {
            console.error('Failed to load pending doses:', err);
            document.getElementById('pending-doses-list').innerHTML =
                '<p style="color: #ef4444;">Error loading pending doses</p>';
        });
}

/**
 * Display pending doses in the UI
 * @param {Array} pendingDoses - Array of pending dose objects
 */
function displayPendingDoses(pendingDoses) {
    const listEl = document.getElementById('pending-doses-list');

    if (!pendingDoses || pendingDoses.length === 0) {
        listEl.innerHTML = '<p style="color: #6b7280;">No pending doses for today. Great job!</p>';
        return;
    }

    let html = '<h3 style="margin-bottom: 12px; font-size: 16px; font-weight: 600;">Today\'s Pending Doses</h3>';

    pendingDoses.forEach(dose => {
        const windowText = dose.time_window.charAt(0).toUpperCase() + dose.time_window.slice(1);

        html += `
            <div style="border: 2px solid #f59e0b; border-radius: 6px; padding: 16px; margin-bottom: 12px; background: #fffbeb;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <h4 style="font-size: 16px; font-weight: 600; margin-bottom: 4px; color: #92400e;">${dose.name}</h4>
                        <p style="color: #78350f; font-size: 13px; margin-bottom: 8px;">${dose.dosage}</p>
                        <p style="font-size: 12px; color: #92400e;">
                            <strong>Time Window:</strong> ${windowText} (${dose.window_start}-${dose.window_end})<br>
                            ${dose.with_food ? '<strong>Take with food</strong><br>' : ''}
                            ${dose.notes ? '<strong>Notes:</strong> ' + dose.notes : ''}
                        </p>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button onclick="markMedicineTaken('${dose.id}')" class="save-btn" style="padding: 8px 16px; font-size: 13px; background: #10b981;">
                            ✓ Take
                        </button>
                        <button onclick="showSkipReasonModal('${dose.id}', '${dose.name.replace(/'/g, "\\'")}', '${dose.time_window}')" class="save-btn" style="padding: 8px 16px; font-size: 13px; background: #f59e0b;">
                            Skip
                        </button>
                    </div>
                </div>
            </div>
        `;
    });

    listEl.innerHTML = html;
}

/**
 * Mark a medicine as taken
 * @param {string} medId - Medicine ID
 */
function markMedicineTaken(medId) {
    markAsTaken(medId)
        .then(data => {
            if (data.success) {
                loadPendingDoses(); // Refresh the list
                showStatus('medicine-form', true, 'Medicine marked as taken!');
            } else {
                showStatus('medicine-form', false, data.message || 'Failed to mark as taken');
            }
        })
        .catch(err => showStatus('medicine-form', false, 'Error: ' + err));
}

/* ============================================
   SKIP FUNCTIONALITY
   ============================================ */

/**
 * Show skip reason modal
 * @param {string} medId - Medicine ID
 * @param {string} medName - Medicine name
 * @param {string} timeWindow - Time window
 */
function showSkipReasonModal(medId, medName, timeWindow) {
    currentSkipMedicineId = medId;
    document.getElementById('skip-medicine-name').textContent =
        `Skip ${medName} for ${timeWindow} time window?`;
    document.getElementById('skip-reason-modal').style.display = 'flex';
    // Reset form
    document.querySelector('input[name="skip-reason"][value="forgot"]').checked = true;
    document.getElementById('skip-notes').value = '';
}

/**
 * Close skip reason modal
 */
function closeSkipReasonModal() {
    document.getElementById('skip-reason-modal').style.display = 'none';
    currentSkipMedicineId = null;
}

/**
 * Confirm skip medicine with reason
 */
function confirmSkipMedicine() {
    const reason = document.querySelector('input[name="skip-reason"]:checked').value;
    const notes = document.getElementById('skip-notes').value;

    if (!currentSkipMedicineId) {
        showStatus('skip-modal', false, 'Error: No medicine selected');
        return;
    }

    skipMedicine(currentSkipMedicineId, reason, notes)
        .then(data => {
            if (data.success) {
                closeSkipReasonModal();
                loadPendingDoses(); // Refresh pending doses
                showStatus('medicine-form', true, 'Medicine skipped successfully');
            } else {
                showStatus('skip-modal', false, data.message || 'Failed to skip medicine');
            }
        })
        .catch(err => showStatus('skip-modal', false, 'Error: ' + err));
}

/* ============================================
   SKIP HISTORY FUNCTIONS
   ============================================ */

/**
 * Load and display skip history
 */
function loadSkipHistory() {
    getSkipHistory()
        .then(data => {
            displaySkipHistory(data.skip_history || []);
        })
        .catch(err => {
            console.error('Failed to load skip history:', err);
            document.getElementById('skip-history-list').innerHTML =
                '<p style="color: #ef4444;">Error loading skip history</p>';
        });
}

/**
 * Display skip history in the UI
 * @param {Array} skipHistory - Array of skip event objects
 */
function displaySkipHistory(skipHistory) {
    const listEl = document.getElementById('skip-history-list');

    if (!skipHistory || skipHistory.length === 0) {
        listEl.innerHTML = '<p style="color: #6b7280;">No skip history yet.</p>';
        return;
    }

    // Create table
    let html = `
        <h3 style="margin-bottom: 12px; font-size: 16px; font-weight: 600;">Skip History</h3>
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                <thead>
                    <tr style="background: #f3f4f6; border-bottom: 2px solid #e5e7eb;">
                        <th style="padding: 12px; text-align: left; font-weight: 600;">Date</th>
                        <th style="padding: 12px; text-align: left; font-weight: 600;">Medicine</th>
                        <th style="padding: 12px; text-align: left; font-weight: 600;">Time Window</th>
                        <th style="padding: 12px; text-align: left; font-weight: 600;">Reason</th>
                        <th style="padding: 12px; text-align: left; font-weight: 600;">Notes</th>
                    </tr>
                </thead>
                <tbody>
    `;

    skipHistory.forEach((skip, index) => {
        const bgColor = index % 2 === 0 ? '#ffffff' : '#f9fafb';
        const reasonText = formatSkipReason(skip.reason);
        const windowText = skip.time_window ?
            (skip.time_window.charAt(0).toUpperCase() + skip.time_window.slice(1)) : 'N/A';

        html += `
            <tr style="background: ${bgColor}; border-bottom: 1px solid #e5e7eb;">
                <td style="padding: 12px;">${skip.date || 'N/A'}</td>
                <td style="padding: 12px; font-weight: 500;">${skip.medicine_name || 'Unknown'}</td>
                <td style="padding: 12px;">${windowText}</td>
                <td style="padding: 12px;">
                    <span style="background: #fef3c7; color: #92400e; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 500;">
                        ${reasonText}
                    </span>
                </td>
                <td style="padding: 12px; color: #6b7280;">${skip.notes || '-'}</td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    listEl.innerHTML = html;
}

/**
 * Format skip reason for display
 * @param {string} reason - Skip reason code
 * @returns {string} Formatted reason text
 */
function formatSkipReason(reason) {
    const reasonMap = {
        'forgot': 'Forgot',
        'side_effects': 'Side Effects',
        'out_of_stock': 'Out of Stock',
        'doctor_advised': 'Doctor Advised',
        'other': 'Other'
    };
    return reasonMap[reason] || reason;
}

/* ============================================
   ADHERENCE STATISTICS FUNCTIONS
   ============================================ */

/**
 * Load and display adherence statistics
 */
function loadAdherenceStats() {
    getAdherenceDetailed()
        .then(data => {
            displayAdherenceStats(data);
        })
        .catch(err => {
            console.error('Failed to load adherence stats:', err);
            document.getElementById('adherence-stats').innerHTML =
                '<p style="color: #ef4444;">Error loading adherence statistics</p>';
        });
}

/**
 * Display adherence statistics in the UI
 * @param {Object} stats - Adherence statistics object
 */
function displayAdherenceStats(stats) {
    const statsEl = document.getElementById('adherence-stats');

    const adherenceRate = stats.adherence_rate || 0;
    const skipRate = stats.skip_rate || 0;
    const taken = stats.taken || 0;
    const skipped = stats.skipped || 0;
    const missed = stats.missed || 0;
    const total = stats.total || 0;

    const adherenceColor = adherenceRate >= 80 ? '#10b981' : adherenceRate >= 60 ? '#f59e0b' : '#ef4444';
    const skipColor = skipRate >= 20 ? '#ef4444' : skipRate >= 10 ? '#f59e0b' : '#6b7280';

    let html = `
        <h3 style="margin-bottom: 16px; font-size: 16px; font-weight: 600;">Adherence Statistics</h3>

        <!-- Overall Stats -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
            <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; padding: 16px;">
                <p style="color: #1e40af; font-size: 12px; font-weight: 600; margin-bottom: 4px;">TOTAL DOSES</p>
                <p style="font-size: 28px; font-weight: 700; color: #1e40af;">${total}</p>
            </div>
            <div style="background: #d1fae5; border: 1px solid #10b981; border-radius: 6px; padding: 16px;">
                <p style="color: #065f46; font-size: 12px; font-weight: 600; margin-bottom: 4px;">TAKEN</p>
                <p style="font-size: 28px; font-weight: 700; color: #065f46;">${taken}</p>
            </div>
            <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 6px; padding: 16px;">
                <p style="color: #92400e; font-size: 12px; font-weight: 600; margin-bottom: 4px;">SKIPPED</p>
                <p style="font-size: 28px; font-weight: 700; color: #92400e;">${skipped}</p>
            </div>
            <div style="background: #fee2e2; border: 1px solid #ef4444; border-radius: 6px; padding: 16px;">
                <p style="color: #991b1b; font-size: 12px; font-weight: 600; margin-bottom: 4px;">MISSED</p>
                <p style="font-size: 28px; font-weight: 700; color: #991b1b;">${missed}</p>
            </div>
        </div>

        <!-- Adherence Rate -->
        <div style="margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="font-size: 14px; font-weight: 600; color: #374151;">Adherence Rate</span>
                <span style="font-size: 14px; font-weight: 700; color: ${adherenceColor};">${adherenceRate.toFixed(1)}%</span>
            </div>
            <div style="background: #e5e7eb; border-radius: 9999px; height: 24px; overflow: hidden;">
                <div style="background: ${adherenceColor}; height: 100%; width: ${adherenceRate}%; transition: width 0.3s;"></div>
            </div>
            <p style="margin-top: 4px; font-size: 12px; color: #6b7280;">Percentage of scheduled doses taken on time</p>
        </div>

        <!-- Skip Rate -->
        <div style="margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="font-size: 14px; font-weight: 600; color: #374151;">Skip Rate</span>
                <span style="font-size: 14px; font-weight: 700; color: ${skipColor};">${skipRate.toFixed(1)}%</span>
            </div>
            <div style="background: #e5e7eb; border-radius: 9999px; height: 24px; overflow: hidden;">
                <div style="background: ${skipColor}; height: 100%; width: ${skipRate}%; transition: width 0.3s;"></div>
            </div>
            <p style="margin-top: 4px; font-size: 12px; color: #6b7280;">Percentage of doses intentionally skipped</p>
        </div>
    `;

    // Add per-medicine breakdown if available
    if (stats.by_medicine && stats.by_medicine.length > 0) {
        html += `
            <h4 style="margin-top: 24px; margin-bottom: 12px; font-size: 14px; font-weight: 600;">By Medicine</h4>
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                    <thead>
                        <tr style="background: #f3f4f6; border-bottom: 2px solid #e5e7eb;">
                            <th style="padding: 12px; text-align: left; font-weight: 600;">Medicine</th>
                            <th style="padding: 12px; text-align: center; font-weight: 600;">Taken</th>
                            <th style="padding: 12px; text-align: center; font-weight: 600;">Skipped</th>
                            <th style="padding: 12px; text-align: center; font-weight: 600;">Missed</th>
                            <th style="padding: 12px; text-align: center; font-weight: 600;">Adherence</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        stats.by_medicine.forEach((med, index) => {
            const bgColor = index % 2 === 0 ? '#ffffff' : '#f9fafb';
            const medAdherence = med.adherence_rate || 0;
            const medColor = medAdherence >= 80 ? '#10b981' : medAdherence >= 60 ? '#f59e0b' : '#ef4444';

            html += `
                <tr style="background: ${bgColor}; border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 12px; font-weight: 500;">${med.medicine_name}</td>
                    <td style="padding: 12px; text-align: center; color: #10b981; font-weight: 600;">${med.taken || 0}</td>
                    <td style="padding: 12px; text-align: center; color: #f59e0b; font-weight: 600;">${med.skipped || 0}</td>
                    <td style="padding: 12px; text-align: center; color: #ef4444; font-weight: 600;">${med.missed || 0}</td>
                    <td style="padding: 12px; text-align: center;">
                        <span style="background: ${medColor}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">
                            ${medAdherence.toFixed(1)}%
                        </span>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;
    }

    statsEl.innerHTML = html;
}

/* ============================================
   MEDICINE FORM INITIALIZATION
   ============================================ */

/**
 * Initialize medicine form submission handler
 */
function initMedicineForm() {
    const form = document.getElementById('medicine-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = form.querySelector('button[type="submit"]');
        setLoadingState(submitBtn, true);

        try {
            const days = Array.from(document.querySelectorAll('input[name="day"]:checked')).map(cb => cb.value);
            const medId = document.getElementById('medicine-id').value;

            // Validate at least one day is selected
            if (days.length === 0) {
                showStatus('medicine-form', false, 'Please select at least one day');
                setLoadingState(submitBtn, false);
                return;
            }

            const medicineFormData = {
                id: medId || 'med_' + Date.now(),
                name: document.getElementById('medicine-name').value,
                dosage: document.getElementById('medicine-dosage').value,
                time_window: document.getElementById('medicine-window').value,
                with_food: document.getElementById('medicine-food').value === 'true',
                days: days,
                notes: document.getElementById('medicine-notes').value,
                pills_remaining: parseInt(document.getElementById('medicine-pills-remaining').value) || 0,
                pills_per_dose: parseInt(document.getElementById('medicine-pills-per-dose').value) || 1,
                low_stock_threshold: parseInt(document.getElementById('medicine-low-threshold').value) || 10,
                active: true
            };

            // Get window times from selection
            const windows = {
                morning: {start: '06:00', end: '12:00'},
                afternoon: {start: '12:00', end: '18:00'},
                evening: {start: '18:00', end: '22:00'},
                night: {start: '22:00', end: '23:59'}
            };
            medicineFormData.window_start = windows[medicineFormData.time_window].start;
            medicineFormData.window_end = windows[medicineFormData.time_window].end;

            const data = medId ? await updateMedicine(medicineFormData) : await addMedicine(medicineFormData);

            if (data.success) {
                cancelMedicineForm();
                await loadMedicineDataAndDisplay();
                showStatus('medicine-form', true, data.message);
            } else {
                showStatus('medicine-form', false, data.message);
            }
        } catch (err) {
            showStatus('medicine-form', false, 'Error: ' + err.message);
        } finally {
            setLoadingState(submitBtn, false);
        }
    });
}
