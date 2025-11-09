-- Migration 002: Add skip tracking to medicine database
-- Run after: 001_initial_schema.sql
-- Description: Adds skip functionality to track when doses are intentionally not taken

BEGIN TRANSACTION;

-- Add skip columns to tracking table
ALTER TABLE tracking ADD COLUMN skipped INTEGER DEFAULT 0;
ALTER TABLE tracking ADD COLUMN skip_reason TEXT DEFAULT NULL;
ALTER TABLE tracking ADD COLUMN skip_timestamp TEXT DEFAULT NULL;

-- Update metadata
UPDATE metadata SET value = '1.1.0' WHERE key = 'schema_version';
UPDATE metadata SET value = datetime('now') WHERE key = 'last_updated';

-- Create index for skip queries
CREATE INDEX IF NOT EXISTS idx_tracking_skipped ON tracking(skipped);
CREATE INDEX IF NOT EXISTS idx_tracking_skip_timestamp ON tracking(skip_timestamp);

-- Create view for adherence with skip details
CREATE VIEW IF NOT EXISTS adherence_detailed AS
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

COMMIT;
