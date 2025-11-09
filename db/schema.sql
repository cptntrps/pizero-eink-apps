-- Pi Zero 2W Medicine Tracker Database Schema
-- SQLite 3.x compatible
-- Version: 1.1.0
-- Date: 2025-11-08

-- Note: PRAGMAs are executed separately in Python code, not in this script

-- ============================================================================
-- MEDICINES TABLE
-- ============================================================================
-- Stores medicine/vitamin records with all configuration
CREATE TABLE medicines (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    dosage TEXT NOT NULL,
    time_window TEXT NOT NULL CHECK(time_window IN ('morning', 'afternoon', 'evening', 'night')),
    window_start TEXT NOT NULL,
    window_end TEXT NOT NULL,
    with_food BOOLEAN NOT NULL DEFAULT 0,
    notes TEXT,
    pills_remaining INTEGER NOT NULL DEFAULT 0 CHECK(pills_remaining >= 0),
    pills_per_dose INTEGER NOT NULL DEFAULT 1 CHECK(pills_per_dose > 0),
    low_stock_threshold INTEGER NOT NULL DEFAULT 10 CHECK(low_stock_threshold > 0),
    active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for active medicine queries
CREATE INDEX idx_medicines_active ON medicines(active) WHERE active = 1;

-- Index for time window queries
CREATE INDEX idx_medicines_time_window ON medicines(time_window);

-- ============================================================================
-- MEDICINE_DAYS TABLE
-- ============================================================================
-- Many-to-many relationship between medicines and days of week
CREATE TABLE medicine_days (
    medicine_id TEXT NOT NULL,
    day TEXT NOT NULL CHECK(day IN ('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')),
    PRIMARY KEY (medicine_id, day),
    FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
);

-- Index for day-based queries
CREATE INDEX idx_medicine_days_day ON medicine_days(day);

-- ============================================================================
-- TRACKING TABLE
-- ============================================================================
-- Records of when medicines were taken (or skipped)
CREATE TABLE tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_id TEXT NOT NULL,
    date DATE NOT NULL,
    time_window TEXT NOT NULL,
    taken BOOLEAN NOT NULL DEFAULT 0,
    timestamp TIMESTAMP NOT NULL,
    pills_taken INTEGER NOT NULL DEFAULT 1,
    notes TEXT,
    skipped INTEGER DEFAULT 0,
    skip_reason TEXT DEFAULT NULL,
    skip_timestamp TEXT DEFAULT NULL,
    FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE,
    UNIQUE(medicine_id, date, time_window)
);

-- Indexes for common queries
CREATE INDEX idx_tracking_date ON tracking(date DESC);
CREATE INDEX idx_tracking_medicine ON tracking(medicine_id);
CREATE INDEX idx_tracking_date_medicine ON tracking(date, medicine_id);
CREATE INDEX idx_tracking_taken ON tracking(taken) WHERE taken = 1;
CREATE INDEX idx_tracking_skipped ON tracking(skipped);
CREATE INDEX idx_tracking_skip_timestamp ON tracking(skip_timestamp);

-- ============================================================================
-- TIME_WINDOWS TABLE
-- ============================================================================
-- Predefined time window definitions
CREATE TABLE time_windows (
    name TEXT PRIMARY KEY,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL
);

-- Insert default time windows
INSERT INTO time_windows (name, start_time, end_time) VALUES
    ('morning', '06:00', '12:00'),
    ('afternoon', '12:00', '18:00'),
    ('evening', '18:00', '22:00'),
    ('night', '22:00', '23:59');

-- ============================================================================
-- METADATA TABLE
-- ============================================================================
-- System metadata and last update tracking
CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial metadata
INSERT INTO metadata (key, value) VALUES
    ('schema_version', '1.1.0'),
    ('last_updated', datetime('now'));

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger to update medicines.updated_at on any update
CREATE TRIGGER medicines_updated_at
AFTER UPDATE ON medicines
FOR EACH ROW
BEGIN
    UPDATE medicines SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Triggers to update metadata.last_updated when medicines change
CREATE TRIGGER medicines_metadata_insert
AFTER INSERT ON medicines
BEGIN
    UPDATE metadata SET value = datetime('now'), updated_at = datetime('now') WHERE key = 'last_updated';
END;

CREATE TRIGGER medicines_metadata_update
AFTER UPDATE ON medicines
BEGIN
    UPDATE metadata SET value = datetime('now'), updated_at = datetime('now') WHERE key = 'last_updated';
END;

CREATE TRIGGER medicines_metadata_delete
AFTER DELETE ON medicines
BEGIN
    UPDATE metadata SET value = datetime('now'), updated_at = datetime('now') WHERE key = 'last_updated';
END;

-- Triggers to update metadata.last_updated when tracking changes
CREATE TRIGGER tracking_metadata_insert
AFTER INSERT ON tracking
BEGIN
    UPDATE metadata SET value = datetime('now'), updated_at = datetime('now') WHERE key = 'last_updated';
END;

CREATE TRIGGER tracking_metadata_update
AFTER UPDATE ON tracking
BEGIN
    UPDATE metadata SET value = datetime('now'), updated_at = datetime('now') WHERE key = 'last_updated';
END;

CREATE TRIGGER tracking_metadata_delete
AFTER DELETE ON tracking
BEGIN
    UPDATE metadata SET value = datetime('now'), updated_at = datetime('now') WHERE key = 'last_updated';
END;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Active medicines with their scheduled days
CREATE VIEW v_medicines_with_days AS
SELECT
    m.*,
    GROUP_CONCAT(md.day) as days
FROM medicines m
LEFT JOIN medicine_days md ON m.id = md.medicine_id
WHERE m.active = 1
GROUP BY m.id;

-- View: Today's adherence statistics
CREATE VIEW v_today_stats AS
SELECT
    DATE('now') as date,
    COUNT(DISTINCT m.id) as total_medicines,
    COUNT(DISTINCT CASE WHEN t.taken = 1 THEN t.medicine_id END) as medicines_taken,
    ROUND(
        CAST(COUNT(DISTINCT CASE WHEN t.taken = 1 THEN t.medicine_id END) AS REAL) /
        CAST(COUNT(DISTINCT m.id) AS REAL) * 100,
        1
    ) as adherence_percentage
FROM medicines m
INNER JOIN medicine_days md ON m.id = md.medicine_id
LEFT JOIN tracking t ON m.id = t.medicine_id AND t.date = DATE('now')
WHERE m.active = 1
  AND md.day = LOWER(SUBSTR('SunMonTueWedThuFriSat', 1 + 3 * CAST(STRFTIME('%w', 'now') AS INTEGER), 3));

-- View: Low stock medicines
CREATE VIEW v_low_stock_medicines AS
SELECT
    id,
    name,
    dosage,
    pills_remaining,
    low_stock_threshold,
    ROUND(
        CAST(pills_remaining AS REAL) / CAST(pills_per_dose AS REAL),
        1
    ) as days_remaining
FROM medicines
WHERE active = 1
  AND pills_remaining <= low_stock_threshold
ORDER BY pills_remaining ASC;

-- View: Adherence with skip details
CREATE VIEW adherence_detailed AS
SELECT
    m.id as medicine_id,
    m.name,
    m.dosage,
    t.date,
    t.time_window,
    t.taken,
    t.skipped,
    t.timestamp as taken_timestamp,
    t.skip_timestamp,
    t.skip_reason,
    CASE
        WHEN t.taken = 1 THEN 'taken'
        WHEN t.skipped = 1 THEN 'skipped'
        ELSE 'pending'
    END as status
FROM medicines m
LEFT JOIN tracking t ON m.id = t.medicine_id
ORDER BY t.date DESC, m.name;

-- ============================================================================
-- INTEGRITY CHECKS
-- ============================================================================

-- Function to verify database integrity
-- Run: PRAGMA integrity_check;
-- Run: PRAGMA foreign_key_check;

-- ============================================================================
-- PERFORMANCE TUNING
-- ============================================================================

-- Note: VACUUM and ANALYZE must be run outside of transactions
-- Run these manually after schema creation:
-- VACUUM;
-- ANALYZE;
