#!/usr/bin/env python3
from flask import Flask, render_template_string, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
CONFIG_FILE = "/home/pizero2w/pizero_apps/config.json"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pi Zero 2W Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f9fafb;
            color: #1f2937;
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        /* Sidebar */
        .sidebar {
            width: 256px;
            background: white;
            box-shadow: 2px 0 8px rgba(0,0,0,0.1);
            padding: 24px 16px;
            border-right: 1px solid #e5e7eb;
            overflow-y: auto;
        }

        .sidebar h1 {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 24px;
            color: #111827;
        }

        .menu-item {
            display: flex;
            align-items: center;
            width: 100%;
            text-align: left;
            padding: 10px 12px;
            margin-bottom: 4px;
            border: none;
            background: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            color: #374151;
            transition: background 0.2s;
        }

        .menu-item:hover {
            background: #dbeafe;
        }

        .menu-item.active {
            background: #bfdbfe;
            font-weight: 500;
            color: #1e40af;
        }

        .menu-item svg {
            margin-right: 8px;
            flex-shrink: 0;
        }

        .submenu {
            margin-left: 24px;
            margin-top: 4px;
        }

        .submenu .menu-item {
            font-size: 13px;
            padding: 8px 12px;
        }

        /* Main content */
        .main-content {
            flex: 1;
            padding: 24px;
            overflow-y: auto;
        }

        .content-section {
            display: none;
        }

        .content-section.active {
            display: block;
        }

        .card {
            background: white;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid #e5e7eb;
        }

        .card h2 {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
            color: #111827;
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 16px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        label {
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 6px;
            color: #374151;
        }

        input, select {
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.2s;
        }

        input:focus, select:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        button.save-btn {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
            margin-top: 16px;
        }

        button.save-btn:hover {
            background: #2563eb;
        }

        .status-message {
            padding: 12px 16px;
            border-radius: 6px;
            margin-top: 16px;
            font-size: 14px;
            display: none;
        }

        .status-message.success {
            background: #d1fae5;
            color: #065f46;
            border: 1px solid #10b981;
        }

        .status-message.error {
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #ef4444;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }

        .info-card {
            background: white;
            padding: 16px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid #e5e7eb;
        }

        .info-card h3 {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
            color: #6b7280;
        }

        .info-card p {
            font-size: 13px;
            color: #374151;
            margin-bottom: 4px;
        }
    </style>
</head>
<body>
    <!-- Sidebar -->
    <aside class="sidebar">
        <h1>Pi Zero 2W</h1>
        <nav>
            <button class="menu-item active" onclick="showSection('dashboard')">
                <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>
                    <rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/>
                </svg>
                Dashboard
            </button>

            <button class="menu-item" onclick="toggleSubmenu('apps')">
                <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"/>
                </svg>
                Applications
            </button>
            <div class="submenu" id="apps-submenu">
                <button class="menu-item" onclick="showSection('weather')">Weather</button>
                <button class="menu-item" onclick="showSection('mbta')">MBTA Transit</button>
                <button class="menu-item" onclick="showSection('disney')">Disney Times</button>
                <button class="menu-item" onclick="showSection('flights')">Flights</button>
                <button class="menu-item" onclick="showSection('pomodoro')">Pomodoro</button>
                <button class="menu-item" onclick="showSection('medicine')">Medicine Tracker</button>
                <button class="menu-item" onclick="showSection('forbidden')">Forbidden</button>
            </div>

            <button class="menu-item" onclick="showSection('settings')">
                <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="3"/><path d="M12 1v6m0 6v6m-9-9h6m6 0h6"/>
                </svg>
                Settings
            </button>
        </nav>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
        <!-- Dashboard Section -->
        <div id="dashboard" class="content-section active">
            <div class="info-grid">
                <div class="info-card">
                    <h3>System Info</h3>
                    <p><strong>Device:</strong> Pi Zero 2W</p>
                    <p><strong>Display:</strong> 2.13" e-ink V4</p>
                </div>
                <div class="info-card">
                    <h3>Network</h3>
                    <p><strong>IP:</strong> 192.168.50.202</p>
                    <p><strong>Port:</strong> 5000</p>
                </div>
            </div>

            <div class="card" style="background: #dbeafe;">
                <h2>Configuration Dashboard</h2>
                <p style="color: #1e40af;">Use the Applications menu to configure each app running on your Pi Zero 2W e-ink display.</p>
            </div>
        </div>

        <!-- Weather Section -->
        <div id="weather" class="content-section">
            <div class="card">
                <h2>Weather & Calendar Configuration</h2>
                <form id="weather-form">
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Location</label>
                            <input type="text" id="weather-location" placeholder="Rio de Janeiro">
                        </div>
                        <div class="form-group">
                            <label>Units</label>
                            <select id="weather-units">
                                <option value="metric">Metric (°C)</option>
                                <option value="imperial">Imperial (°F)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Update Interval (seconds)</label>
                            <input type="number" id="weather-interval" min="60" placeholder="300">
                        </div>
                        <div class="form-group">
                            <label>Display Format</label>
                            <select id="weather-format">
                                <option value="detailed">Detailed</option>
                                <option value="simple">Simple</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit" class="save-btn">Save Weather Settings</button>
                    <div id="weather-status" class="status-message"></div>
                </form>
            </div>
        </div>

        <!-- MBTA Section -->
        <div id="mbta" class="content-section">
            <div class="card">
                <h2>MBTA Transit Configuration</h2>
                <form id="mbta-form">
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Home Station ID</label>
                            <input type="text" id="mbta-home-id" placeholder="place-davis">
                        </div>
                        <div class="form-group">
                            <label>Home Station Name</label>
                            <input type="text" id="mbta-home-name" placeholder="Davis Square">
                        </div>
                        <div class="form-group">
                            <label>Work Station ID</label>
                            <input type="text" id="mbta-work-id" placeholder="place-pktrm">
                        </div>
                        <div class="form-group">
                            <label>Work Station Name</label>
                            <input type="text" id="mbta-work-name" placeholder="Park Street">
                        </div>
                        <div class="form-group">
                            <label>Update Interval (seconds)</label>
                            <input type="number" id="mbta-interval" min="15" placeholder="30">
                        </div>
                        <div class="form-group">
                            <label>Morning Start Time</label>
                            <input type="time" id="mbta-morning-start" value="06:00">
                        </div>
                        <div class="form-group">
                            <label>Morning End Time</label>
                            <input type="time" id="mbta-morning-end" value="12:00">
                        </div>
                        <div class="form-group">
                            <label>Evening Start Time</label>
                            <input type="time" id="mbta-evening-start" value="15:00">
                        </div>
                        <div class="form-group">
                            <label>Evening End Time</label>
                            <input type="time" id="mbta-evening-end" value="21:00">
                        </div>
                    </div>
                    <button type="submit" class="save-btn">Save MBTA Settings</button>
                    <div id="mbta-status" class="status-message"></div>
                </form>
            </div>
        </div>

        <!-- Disney Section -->
        <div id="disney" class="content-section">
            <div class="card">
                <h2>Disney Wait Times Configuration</h2>
                <form id="disney-form">
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Park</label>
                            <select id="disney-park">
                                <option value="6">Magic Kingdom</option>
                                <option value="5">Epcot</option>
                                <option value="7">Hollywood Studios</option>
                                <option value="8">Animal Kingdom</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Update Interval (seconds)</label>
                            <input type="number" id="disney-interval" min="5" placeholder="10">
                        </div>
                        <div class="form-group">
                            <label>Data Refresh (rides)</label>
                            <input type="number" id="disney-refresh" min="10" placeholder="20">
                        </div>
                        <div class="form-group">
                            <label>Sort By</label>
                            <select id="disney-sort">
                                <option value="wait_time">Wait Time</option>
                                <option value="name">Name</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit" class="save-btn">Save Disney Settings</button>
                    <div id="disney-status" class="status-message"></div>
                </form>
            </div>
        </div>

        <!-- Flights Section -->
        <div id="flights" class="content-section">
            <div class="card">
                <h2>Flights Above Configuration</h2>
                <form id="flights-form">
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Latitude</label>
                            <input type="text" id="flights-lat" placeholder="42.3967">
                        </div>
                        <div class="form-group">
                            <label>Longitude</label>
                            <input type="text" id="flights-lon" placeholder="-71.1226">
                        </div>
                        <div class="form-group">
                            <label>Altitude Filter (feet)</label>
                            <input type="number" id="flights-alt" placeholder="10000">
                        </div>
                    </div>
                    <button type="submit" class="save-btn">Save Flights Settings</button>
                    <div id="flights-status" class="status-message"></div>
                </form>
            </div>
        </div>

        <!-- Pomodoro Section -->
        <div id="pomodoro" class="content-section">
            <div class="card">
                <h2>Pomodoro Timer Configuration</h2>
                <form id="pomodoro-form">
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Work Duration (seconds)</label>
                            <input type="number" id="pomodoro-work" min="60" placeholder="1500">
                            <small style="color: #6b7280; margin-top: 4px;">Default: 25 minutes (1500s)</small>
                        </div>
                        <div class="form-group">
                            <label>Short Break (seconds)</label>
                            <input type="number" id="pomodoro-short" min="60" placeholder="300">
                            <small style="color: #6b7280; margin-top: 4px;">Default: 5 minutes (300s)</small>
                        </div>
                        <div class="form-group">
                            <label>Long Break (seconds)</label>
                            <input type="number" id="pomodoro-long" min="60" placeholder="900">
                            <small style="color: #6b7280; margin-top: 4px;">Default: 15 minutes (900s)</small>
                        </div>
                        <div class="form-group">
                            <label>Sessions Until Long Break</label>
                            <input type="number" id="pomodoro-sessions" min="2" max="8" placeholder="4">
                        </div>
                    </div>
                    <button type="submit" class="save-btn">Save Pomodoro Settings</button>
                    <div id="pomodoro-status" class="status-message"></div>
                </form>
            </div>
        </div>

        <!-- Medicine Section -->
        <div id="medicine" class="content-section">
            <div class="card">
                <h2>Medicine & Vitamin Tracker</h2>
                <p style="margin-bottom: 16px; color: #6b7280;">Manage your medicines and vitamins with time window reminders.</p>

                <div id="medicine-list" style="margin-bottom: 20px;">
                    <!-- Medicine list will be populated here -->
                </div>

                <button type="button" class="save-btn" onclick="showAddMedicineForm()">+ Add New Medicine</button>
            </div>

            <!-- Add/Edit Medicine Form (hidden by default) -->
            <div class="card" id="medicine-form-card" style="display: none;">
                <h2 id="medicine-form-title">Add Medicine</h2>
                <form id="medicine-form">
                    <input type="hidden" id="medicine-id" value="">

                    <div class="form-grid">
                        <div class="form-group">
                            <label>Medicine/Vitamin Name</label>
                            <input type="text" id="medicine-name" placeholder="Vitamin D" required>
                        </div>
                        <div class="form-group">
                            <label>Dosage</label>
                            <input type="text" id="medicine-dosage" placeholder="2000 IU" required>
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label>Time Window</label>
                            <select id="medicine-window" required>
                                <option value="morning">Morning (6:00-12:00)</option>
                                <option value="afternoon">Afternoon (12:00-18:00)</option>
                                <option value="evening">Evening (18:00-22:00)</option>
                                <option value="night">Night (22:00-23:59)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Take with Food?</label>
                            <select id="medicine-food">
                                <option value="false">No</option>
                                <option value="true">Yes</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label>Pills Remaining</label>
                            <input type="number" id="medicine-pills-remaining" min="0" placeholder="30" required>
                            <small style="color: #6b7280; margin-top: 4px;">Total pills in current bottle/pack</small>
                        </div>
                        <div class="form-group">
                            <label>Pills Per Dose</label>
                            <input type="number" id="medicine-pills-per-dose" min="1" value="1" placeholder="1" required>
                            <small style="color: #6b7280; margin-top: 4px;">How many pills taken each time</small>
                        </div>
                        <div class="form-group">
                            <label>Low Stock Alert (pills)</label>
                            <input type="number" id="medicine-low-threshold" min="1" value="10" placeholder="10">
                            <small style="color: #6b7280; margin-top: 4px;">Alert when pills remaining ≤ this number</small>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Active Days</label>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                            <label style="display: flex; align-items: center; gap: 4px;">
                                <input type="checkbox" name="day" value="mon" checked> Mon
                            </label>
                            <label style="display: flex; align-items: center; gap: 4px;">
                                <input type="checkbox" name="day" value="tue" checked> Tue
                            </label>
                            <label style="display: flex; align-items: center; gap: 4px;">
                                <input type="checkbox" name="day" value="wed" checked> Wed
                            </label>
                            <label style="display: flex; align-items: center; gap: 4px;">
                                <input type="checkbox" name="day" value="thu" checked> Thu
                            </label>
                            <label style="display: flex; align-items: center; gap: 4px;">
                                <input type="checkbox" name="day" value="fri" checked> Fri
                            </label>
                            <label style="display: flex; align-items: center; gap: 4px;">
                                <input type="checkbox" name="day" value="sat" checked> Sat
                            </label>
                            <label style="display: flex; align-items: center; gap: 4px;">
                                <input type="checkbox" name="day" value="sun" checked> Sun
                            </label>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Notes (optional)</label>
                        <input type="text" id="medicine-notes" placeholder="Take with breakfast">
                    </div>

                    <div style="display: flex; gap: 8px;">
                        <button type="submit" class="save-btn">Save Medicine</button>
                        <button type="button" class="save-btn" onclick="cancelMedicineForm()" style="background: #6b7280;">Cancel</button>
                    </div>
                    <div id="medicine-form-status" class="status-message"></div>
                </form>
            </div>
        </div>

        <!-- Forbidden Section -->
        <div id="forbidden" class="content-section">
            <div class="card">
                <h2>Forbidden Message Configuration</h2>
                <form id="forbidden-form">
                    <div class="form-group">
                        <label>Message Text</label>
                        <input type="text" id="forbidden-message" placeholder="FORBIDDEN">
                    </div>
                    <button type="submit" class="save-btn">Save Forbidden Settings</button>
                    <div id="forbidden-status" class="status-message"></div>
                </form>
            </div>
        </div>

        <!-- Settings Section -->
        <div id="settings" class="content-section">
            <div class="card">
                <h2>System Settings</h2>
                <p>Configuration file: <code>/home/pizero2w/pizero_apps/config.json</code></p>
                <p style="margin-top: 12px; color: #6b7280;">Changes require restarting the menu service to take effect.</p>
            </div>
        </div>
    </main>

    <script>
        // Load config on page load
        window.addEventListener('DOMContentLoaded', loadConfig);

        function loadConfig() {
            fetch('/api/config')
                .then(r => r.json())
                .then(config => {
                    // Weather
                    document.getElementById('weather-location').value = config.weather?.location || '';
                    document.getElementById('weather-units').value = config.weather?.units || 'metric';
                    document.getElementById('weather-interval').value = config.weather?.update_interval || 300;
                    document.getElementById('weather-format').value = config.weather?.display_format || 'detailed';

                    // MBTA
                    document.getElementById('mbta-home-id').value = config.mbta?.home_station_id || '';
                    document.getElementById('mbta-home-name').value = config.mbta?.home_station_name || '';
                    document.getElementById('mbta-work-id').value = config.mbta?.work_station_id || '';
                    document.getElementById('mbta-work-name').value = config.mbta?.work_station_name || '';
                    document.getElementById('mbta-interval').value = config.mbta?.update_interval || 30;
                    document.getElementById('mbta-morning-start').value = config.mbta?.morning_start || '06:00';
                    document.getElementById('mbta-morning-end').value = config.mbta?.morning_end || '12:00';
                    document.getElementById('mbta-evening-start').value = config.mbta?.evening_start || '15:00';
                    document.getElementById('mbta-evening-end').value = config.mbta?.evening_end || '21:00';

                    // Disney
                    document.getElementById('disney-park').value = config.disney?.park_id || 6;
                    document.getElementById('disney-interval').value = config.disney?.update_interval || 10;
                    document.getElementById('disney-refresh').value = config.disney?.data_refresh_rides || 20;
                    document.getElementById('disney-sort').value = config.disney?.sort_by || 'wait_time';

                    // Flights
                    document.getElementById('flights-lat').value = config.flights?.lat || '';
                    document.getElementById('flights-lon').value = config.flights?.lon || '';
                    document.getElementById('flights-alt').value = config.flights?.altitude || '';

                    // Pomodoro
                    document.getElementById('pomodoro-work').value = config.pomodoro?.work_duration || 1500;
                    document.getElementById('pomodoro-short').value = config.pomodoro?.short_break || 300;
                    document.getElementById('pomodoro-long').value = config.pomodoro?.long_break || 900;
                    document.getElementById('pomodoro-sessions').value = config.pomodoro?.sessions_until_long_break || 4;

                    // Forbidden
                    document.getElementById('forbidden-message').value = config.forbidden?.message || '';
                })
                .catch(err => console.error('Failed to load config:', err));
        }

        function showSection(section) {
            document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));
            document.getElementById(section).classList.add('active');
            event.target.classList.add('active');
        }

        function toggleSubmenu(id) {
            const submenu = document.getElementById(id + '-submenu');
            submenu.style.display = submenu.style.display === 'none' ? 'block' : 'none';
        }

        function showStatus(formId, success, message) {
            const status = document.getElementById(formId + '-status');
            status.className = 'status-message ' + (success ? 'success' : 'error');
            status.textContent = message;
            status.style.display = 'block';
            setTimeout(() => status.style.display = 'none', 3000);
        }

        // Form submissions
        document.getElementById('weather-form').addEventListener('submit', e => {
            e.preventDefault();
            fetch('/api/config/weather', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    location: document.getElementById('weather-location').value,
                    units: document.getElementById('weather-units').value,
                    update_interval: parseInt(document.getElementById('weather-interval').value),
                    display_format: document.getElementById('weather-format').value
                })
            })
            .then(r => r.json())
            .then(data => showStatus('weather', data.success, data.message))
            .catch(err => showStatus('weather', false, 'Error: ' + err));
        });

        document.getElementById('mbta-form').addEventListener('submit', e => {
            e.preventDefault();
            fetch('/api/config/mbta', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
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
            })
            .then(r => r.json())
            .then(data => showStatus('mbta', data.success, data.message))
            .catch(err => showStatus('mbta', false, 'Error: ' + err));
        });

        document.getElementById('disney-form').addEventListener('submit', e => {
            e.preventDefault();
            fetch('/api/config/disney', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    park_id: parseInt(document.getElementById('disney-park').value),
                    update_interval: parseInt(document.getElementById('disney-interval').value),
                    data_refresh_rides: parseInt(document.getElementById('disney-refresh').value),
                    sort_by: document.getElementById('disney-sort').value
                })
            })
            .then(r => r.json())
            .then(data => showStatus('disney', data.success, data.message))
            .catch(err => showStatus('disney', false, 'Error: ' + err));
        });

        document.getElementById('flights-form').addEventListener('submit', e => {
            e.preventDefault();
            fetch('/api/config/flights', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    lat: document.getElementById('flights-lat').value,
                    lon: document.getElementById('flights-lon').value,
                    altitude: parseInt(document.getElementById('flights-alt').value)
                })
            })
            .then(r => r.json())
            .then(data => showStatus('flights', data.success, data.message))
            .catch(err => showStatus('flights', false, 'Error: ' + err));
        });

        document.getElementById('pomodoro-form').addEventListener('submit', e => {
            e.preventDefault();
            fetch('/api/config/pomodoro', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    work_duration: parseInt(document.getElementById('pomodoro-work').value),
                    short_break: parseInt(document.getElementById('pomodoro-short').value),
                    long_break: parseInt(document.getElementById('pomodoro-long').value),
                    sessions_until_long_break: parseInt(document.getElementById('pomodoro-sessions').value)
                })
            })
            .then(r => r.json())
            .then(data => showStatus('pomodoro', data.success, data.message))
            .catch(err => showStatus('pomodoro', false, 'Error: ' + err));
        });

        document.getElementById('forbidden-form').addEventListener('submit', e => {
            e.preventDefault();
            fetch('/api/config/forbidden', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    message: document.getElementById('forbidden-message').value
                })
            })
            .then(r => r.json())
            .then(data => showStatus('forbidden', data.success, data.message))
            .catch(err => showStatus('forbidden', false, 'Error: ' + err));
        });

        // Medicine management functions
        let medicineData = {medicines: [], tracking: {}, time_windows: {}};

        function loadMedicineData() {
            fetch('/api/medicine/data')
                .then(r => r.json())
                .then(data => {
                    medicineData = data;
                    displayMedicineList();
                })
                .catch(err => console.error('Failed to load medicine data:', err));
        }

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

        function showAddMedicineForm() {
            document.getElementById('medicine-form-card').style.display = 'block';
            document.getElementById('medicine-form-title').textContent = 'Add Medicine';
            document.getElementById('medicine-form').reset();
            document.getElementById('medicine-id').value = '';
            // Check all day checkboxes by default
            document.querySelectorAll('input[name="day"]').forEach(cb => cb.checked = true);
        }

        function cancelMedicineForm() {
            document.getElementById('medicine-form-card').style.display = 'none';
            document.getElementById('medicine-form').reset();
        }

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

        function deleteMedicine(medId) {
            if (!confirm('Are you sure you want to delete this medicine?')) return;

            fetch('/api/medicine/delete/' + medId, {
                method: 'DELETE'
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    loadMedicineData();
                    showStatus('medicine-form', true, 'Medicine deleted successfully');
                } else {
                    showStatus('medicine-form', false, data.message);
                }
            })
            .catch(err => showStatus('medicine-form', false, 'Error: ' + err));
        }

        document.getElementById('medicine-form').addEventListener('submit', e => {
            e.preventDefault();

            const days = Array.from(document.querySelectorAll('input[name="day"]:checked')).map(cb => cb.value);
            const medId = document.getElementById('medicine-id').value;

            const medicineData = {
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
            medicineData.window_start = windows[medicineData.time_window].start;
            medicineData.window_end = windows[medicineData.time_window].end;

            const url = medId ? '/api/medicine/update' : '/api/medicine/add';

            fetch(url, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(medicineData)
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    cancelMedicineForm();
                    loadMedicineData();
                    showStatus('medicine-form', true, data.message);
                } else {
                    showStatus('medicine-form', false, data.message);
                }
            })
            .catch(err => showStatus('medicine-form', false, 'Error: ' + err));
        });

        // Load medicine data when medicine section is shown
        const originalShowSection = showSection;
        showSection = function(section) {
            originalShowSection(section);
            if (section === 'medicine') {
                loadMedicineData();
            }
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/config', methods=['GET'])
def get_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/config/<section>', methods=['POST'])
def update_config(section):
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        data = request.get_json()
        config[section] = data

        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

        return jsonify({"success": True, "message": f"{section.title()} settings saved successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

# Medicine API endpoints
MEDICINE_DATA_FILE = "/home/pizero2w/pizero_apps/medicine_data.json"

@app.route('/api/medicine/data', methods=['GET'])
def get_medicine_data():
    try:
        with open(MEDICINE_DATA_FILE, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"medicines": [], "tracking": {}, "time_windows": {}}), 200

@app.route('/api/medicine/add', methods=['POST'])
def add_medicine():
    try:
        with open(MEDICINE_DATA_FILE, 'r') as f:
            data = json.load(f)

        new_med = request.get_json()

        if 'medicines' not in data:
            data['medicines'] = []

        data['medicines'].append(new_med)

        # Add timestamp for push refresh
        data['last_updated'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        with open(MEDICINE_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        return jsonify({"success": True, "message": "Medicine added successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/medicine/update', methods=['POST'])
def update_medicine():
    try:
        with open(MEDICINE_DATA_FILE, 'r') as f:
            data = json.load(f)

        updated_med = request.get_json()

        if 'medicines' not in data:
            data['medicines'] = []

        # Find and update the medicine
        found = False
        for i, med in enumerate(data['medicines']):
            if med['id'] == updated_med['id']:
                data['medicines'][i] = updated_med
                found = True
                break

        if not found:
            return jsonify({"success": False, "message": "Medicine not found"}), 404

        # Add timestamp for push refresh
        data['last_updated'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        with open(MEDICINE_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        return jsonify({"success": True, "message": "Medicine updated successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/medicine/delete/<med_id>', methods=['DELETE'])
def delete_medicine(med_id):
    try:
        with open(MEDICINE_DATA_FILE, 'r') as f:
            data = json.load(f)

        if 'medicines' not in data:
            data['medicines'] = []

        # Filter out the medicine to delete
        original_length = len(data['medicines'])
        data['medicines'] = [m for m in data['medicines'] if m['id'] != med_id]

        if len(data['medicines']) == original_length:
            return jsonify({"success": False, "message": "Medicine not found"}), 404

        # Add timestamp for push refresh
        data['last_updated'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        with open(MEDICINE_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        return jsonify({"success": True, "message": "Medicine deleted successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/medicine/mark-taken', methods=['POST'])
def mark_medicine_taken():
    """
    Mark medicine(s) as taken

    Request body:
    {
        "medicine_ids": ["med_001", "med_002"],  // Array of medicine IDs
        "timestamp": "2025-11-07T08:30:00"       // Optional, defaults to now
    }

    OR for single medicine:
    {
        "medicine_id": "med_001",
        "timestamp": "2025-11-07T08:30:00"
    }
    """
    try:
        from datetime import datetime

        with open(MEDICINE_DATA_FILE, 'r') as f:
            data = json.load(f)

        request_data = request.get_json()

        # Support both single and multiple medicines
        medicine_ids = []
        if 'medicine_ids' in request_data:
            medicine_ids = request_data['medicine_ids']
        elif 'medicine_id' in request_data:
            medicine_ids = [request_data['medicine_id']]
        else:
            return jsonify({"success": False, "message": "No medicine_id or medicine_ids provided"}), 400

        # Get timestamp (use provided or current time)
        if 'timestamp' in request_data:
            timestamp = request_data['timestamp']
            # Parse to validate format
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                return jsonify({"success": False, "message": "Invalid timestamp format. Use ISO 8601 (e.g., 2025-11-07T08:30:00)"}), 400
        else:
            dt = datetime.now()
            timestamp = dt.strftime("%Y-%m-%dT%H:%M:%S")

        today = dt.strftime("%Y-%m-%d")

        # Initialize tracking for today if needed
        if 'tracking' not in data:
            data['tracking'] = {}
        if today not in data['tracking']:
            data['tracking'][today] = {}

        # Track which medicines were found and marked
        marked_medicines = []
        not_found = []

        for med_id in medicine_ids:
            # Find the medicine
            medicine = None
            for med in data.get('medicines', []):
                if med['id'] == med_id:
                    medicine = med
                    break

            if not medicine:
                not_found.append(med_id)
                continue

            # Mark as taken
            time_window = medicine.get('time_window', 'morning')
            tracking_key = f"{med_id}_{time_window}"

            data['tracking'][today][tracking_key] = {
                "taken": True,
                "timestamp": timestamp
            }

            # Decrement pill count
            pills_per_dose = medicine.get('pills_per_dose', 1)
            current_count = medicine.get('pills_remaining', 0)
            new_count = max(0, current_count - pills_per_dose)

            # Update pill count in the medicine list
            for i, med in enumerate(data['medicines']):
                if med['id'] == med_id:
                    data['medicines'][i]['pills_remaining'] = new_count
                    break

            marked_medicines.append({
                "id": med_id,
                "name": medicine['name'],
                "pills_remaining": new_count,
                "low_stock": new_count <= medicine.get('low_stock_threshold', 10)
            })

        # Add timestamp for push refresh
        data['last_updated'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        # Save updated data
        with open(MEDICINE_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        # Build response message
        if len(marked_medicines) == 0:
            return jsonify({
                "success": False,
                "message": "No medicines found",
                "not_found": not_found
            }), 404

        response = {
            "success": True,
            "message": f"Marked {len(marked_medicines)} medicine(s) as taken",
            "marked": marked_medicines,
            "timestamp": timestamp
        }

        if not_found:
            response["not_found"] = not_found
            response["message"] += f" ({len(not_found)} not found)"

        return jsonify(response)

    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/medicine/pending', methods=['GET'])
def get_pending_medicines():
    """
    Get medicines that are due now (within time window)

    Optional query params:
    - date: YYYY-MM-DD (defaults to today)
    - time: HH:MM (defaults to current time)
    """
    try:
        from datetime import datetime

        with open(MEDICINE_DATA_FILE, 'r') as f:
            data = json.load(f)

        # Get date and time from query params or use current
        date_str = request.args.get('date')
        time_str = request.args.get('time')

        if date_str and time_str:
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        else:
            dt = datetime.now()

        today = dt.strftime("%Y-%m-%d")
        current_day = dt.strftime("%a").lower()
        current_hour = dt.hour
        current_minute = dt.minute
        current_mins = current_hour * 60 + current_minute

        # Reminder window in minutes
        reminder_window = 30

        pending = []

        for med in data.get('medicines', []):
            if not med.get('active', True):
                continue

            # Check if today is a scheduled day
            if current_day not in med.get('days', []):
                continue

            # Check if in time window
            window_start = med.get('window_start', '00:00')
            window_end = med.get('window_end', '23:59')

            start_h, start_m = map(int, window_start.split(':'))
            end_h, end_m = map(int, window_end.split(':'))

            start_mins = start_h * 60 + start_m - reminder_window
            end_mins = end_h * 60 + end_m + reminder_window

            if not (start_mins <= current_mins <= end_mins):
                continue

            # Check if already taken today
            tracking_key = f"{med['id']}_{med['time_window']}"
            if today in data.get('tracking', {}):
                if tracking_key in data['tracking'][today]:
                    if data['tracking'][today][tracking_key].get('taken', False):
                        continue

            pending.append({
                "id": med['id'],
                "name": med['name'],
                "dosage": med['dosage'],
                "time_window": med['time_window'],
                "with_food": med.get('with_food', False),
                "notes": med.get('notes', ''),
                "pills_remaining": med.get('pills_remaining', 0),
                "low_stock": med.get('pills_remaining', 0) <= med.get('low_stock_threshold', 10)
            })

        return jsonify({
            "success": True,
            "count": len(pending),
            "medicines": pending,
            "checked_at": dt.strftime("%Y-%m-%dT%H:%M:%S")
        })

    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
