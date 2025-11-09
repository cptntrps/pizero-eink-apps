"""
Medicine Database Abstraction Layer
Provides ACID-compliant database operations for medicine tracking
"""

import logging
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class MedicineDatabase:
    """Thread-safe SQLite database for medicine tracking"""

    def __init__(self, db_path: str = None):
        """Initialize database connection

        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            db_path = os.environ.get(
                'PIZERO_MEDICINE_DB',
                '/home/pizero2w/pizero_apps/medicine.db'
            )

        self.db_path = db_path
        self._local = threading.local()
        self._init_db()
        logger.info(f"MedicineDatabase initialized: {db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self._local.conn.row_factory = sqlite3.Row
            # Enable foreign keys
            self._local.conn.execute("PRAGMA foreign_keys = ON")
            # Enable WAL mode for better concurrency
            self._local.conn.execute("PRAGMA journal_mode = WAL")
        return self._local.conn

    @contextmanager
    def transaction(self):
        """Context manager for database transactions with automatic rollback"""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction failed, rolling back: {e}")
            raise

    def _init_db(self):
        """Initialize database schema if not exists"""
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

        # Check if database exists
        db_exists = os.path.exists(self.db_path)

        if not db_exists:
            logger.info("Creating new database")
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            # Read and execute schema
            # Note: executescript() automatically commits, so don't use transaction wrapper
            conn = self._get_connection()
            with open(schema_path, 'r') as f:
                schema_sql = f.read()

            try:
                conn.executescript(schema_sql)
                conn.commit()
                logger.info("Database schema created successfully")
            except Exception as e:
                logger.error(f"Failed to create database schema: {e}")
                conn.rollback()
                raise
        else:
            # Verify schema version
            conn = self._get_connection()
            try:
                cursor = conn.execute(
                    "SELECT value FROM metadata WHERE key = 'schema_version'"
                )
                row = cursor.fetchone()
                if row:
                    logger.info(f"Database schema version: {row['value']}")
            except sqlite3.OperationalError:
                # Table doesn't exist yet
                logger.warning("Metadata table not found - database may be incomplete")

    def get_last_updated(self) -> str:
        """Get last updated timestamp from metadata"""
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT value FROM metadata WHERE key = 'last_updated'"
        )
        row = cursor.fetchone()
        return row['value'] if row else datetime.now().isoformat()

    def get_all_medicines(self, include_inactive: bool = False) -> List[Dict]:
        """Get all medicines with their scheduled days

        Args:
            include_inactive: If True, includes inactive medicines

        Returns:
            List of medicine dictionaries
        """
        conn = self._get_connection()

        query = """
        SELECT
            m.*,
            GROUP_CONCAT(md.day) as days
        FROM medicines m
        LEFT JOIN medicine_days md ON m.id = md.medicine_id
        """

        if not include_inactive:
            query += " WHERE m.active = 1"

        query += " GROUP BY m.id ORDER BY m.name"

        cursor = conn.execute(query)
        medicines = []

        for row in cursor.fetchall():
            med = dict(row)
            # Convert days string to list
            med['days'] = row['days'].split(',') if row['days'] else []
            # Convert boolean integers to actual booleans
            med['with_food'] = bool(med['with_food'])
            med['active'] = bool(med['active'])
            medicines.append(med)

        return medicines

    def get_medicine_by_id(self, medicine_id: str) -> Optional[Dict]:
        """Get single medicine by ID

        Args:
            medicine_id: Medicine ID

        Returns:
            Medicine dictionary or None if not found
        """
        medicines = [m for m in self.get_all_medicines(include_inactive=True)
                     if m['id'] == medicine_id]
        return medicines[0] if medicines else None

    def add_medicine(self, medicine_data: Dict) -> bool:
        """Add new medicine with ACID transaction

        Args:
            medicine_data: Dictionary with medicine fields

        Returns:
            True if successful

        Raises:
            ValueError: If validation fails
            sqlite3.IntegrityError: If medicine_id already exists
        """
        required_fields = ['id', 'name', 'dosage', 'time_window', 'window_start',
                           'window_end', 'days', 'pills_remaining', 'pills_per_dose',
                           'low_stock_threshold']

        for field in required_fields:
            if field not in medicine_data:
                raise ValueError(f"Missing required field: {field}")

        try:
            with self.transaction() as conn:
                # Insert medicine
                conn.execute("""
                    INSERT INTO medicines (
                        id, name, dosage, time_window, window_start, window_end,
                        with_food, notes, pills_remaining, pills_per_dose,
                        low_stock_threshold, active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    medicine_data['id'],
                    medicine_data['name'],
                    medicine_data['dosage'],
                    medicine_data['time_window'],
                    medicine_data['window_start'],
                    medicine_data['window_end'],
                    1 if medicine_data.get('with_food', False) else 0,
                    medicine_data.get('notes'),
                    medicine_data['pills_remaining'],
                    medicine_data['pills_per_dose'],
                    medicine_data['low_stock_threshold'],
                    1 if medicine_data.get('active', True) else 0
                ))

                # Insert days
                for day in medicine_data['days']:
                    conn.execute(
                        "INSERT INTO medicine_days (medicine_id, day) VALUES (?, ?)",
                        (medicine_data['id'], day)
                    )

            logger.info(f"Added medicine: {medicine_data['id']}")
            return True

        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to add medicine (integrity error): {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to add medicine: {e}")
            raise

    def update_medicine(self, medicine_id: str, medicine_data: Dict) -> bool:
        """Update existing medicine

        Args:
            medicine_id: Medicine ID to update
            medicine_data: Dictionary with medicine fields

        Returns:
            True if successful

        Raises:
            ValueError: If medicine not found
        """
        try:
            with self.transaction() as conn:
                # Check if medicine exists
                cursor = conn.execute(
                    "SELECT id FROM medicines WHERE id = ?",
                    (medicine_id,)
                )
                if cursor.fetchone() is None:
                    raise ValueError(f"Medicine not found: {medicine_id}")

                # Update medicine
                conn.execute("""
                    UPDATE medicines SET
                        name = ?, dosage = ?, time_window = ?,
                        window_start = ?, window_end = ?, with_food = ?,
                        notes = ?, pills_remaining = ?, pills_per_dose = ?,
                        low_stock_threshold = ?, active = ?
                    WHERE id = ?
                """, (
                    medicine_data['name'],
                    medicine_data['dosage'],
                    medicine_data['time_window'],
                    medicine_data['window_start'],
                    medicine_data['window_end'],
                    1 if medicine_data.get('with_food', False) else 0,
                    medicine_data.get('notes'),
                    medicine_data['pills_remaining'],
                    medicine_data['pills_per_dose'],
                    medicine_data['low_stock_threshold'],
                    1 if medicine_data.get('active', True) else 0,
                    medicine_id
                ))

                # Update days (delete and re-insert)
                conn.execute(
                    "DELETE FROM medicine_days WHERE medicine_id = ?",
                    (medicine_id,)
                )

                for day in medicine_data['days']:
                    conn.execute(
                        "INSERT INTO medicine_days (medicine_id, day) VALUES (?, ?)",
                        (medicine_id, day)
                    )

            logger.info(f"Updated medicine: {medicine_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update medicine: {e}")
            raise

    def delete_medicine(self, medicine_id: str) -> bool:
        """Delete medicine (cascade deletes days and tracking)

        Args:
            medicine_id: Medicine ID to delete

        Returns:
            True if successful
        """
        try:
            with self.transaction() as conn:
                cursor = conn.execute(
                    "DELETE FROM medicines WHERE id = ?",
                    (medicine_id,)
                )

                if cursor.rowcount == 0:
                    raise ValueError(f"Medicine not found: {medicine_id}")

            logger.info(f"Deleted medicine: {medicine_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete medicine: {e}")
            raise

    def get_pending_medicines(
            self,
            check_date: date = None,
            check_time: datetime = None) -> List[Dict]:
        """Get medicines due at specified time with reminder window

        Args:
            check_date: Date to check (defaults to today)
            check_time: Time to check (defaults to now)

        Returns:
            List of pending medicine dictionaries
        """
        if check_date is None:
            check_date = date.today()
        if check_time is None:
            check_time = datetime.now()

        date_str = check_date.strftime('%Y-%m-%d')
        current_day = check_time.strftime('%a').lower()
        current_mins = check_time.hour * 60 + check_time.minute

        # Reminder window (30 minutes before/after)
        reminder_window = 30

        conn = self._get_connection()

        query = """
        SELECT DISTINCT m.*,
            GROUP_CONCAT(md.day) as days
        FROM medicines m
        INNER JOIN medicine_days md ON m.id = md.medicine_id
        LEFT JOIN tracking t ON m.id = t.medicine_id
            AND t.date = ?
            AND t.time_window = m.time_window
        WHERE m.active = 1
          AND md.day = ?
          AND (t.taken IS NULL OR t.taken = 0)
        GROUP BY m.id
        """

        cursor = conn.execute(query, (date_str, current_day))
        pending = []

        for row in cursor.fetchall():
            med = dict(row)

            # Check if in time window (with reminder buffer)
            window_start_parts = med['window_start'].split(':')
            window_end_parts = med['window_end'].split(':')

            start_mins = int(window_start_parts[0]) * 60 + \
                int(window_start_parts[1]) - reminder_window
            end_mins = int(window_end_parts[0]) * 60 + int(window_end_parts[1]) + reminder_window

            if start_mins <= current_mins <= end_mins:
                # Convert types
                med['days'] = row['days'].split(',') if row['days'] else []
                med['with_food'] = bool(med['with_food'])
                med['active'] = bool(med['active'])
                pending.append(med)

        return pending

    def mark_medicine_taken(self, medicine_id: str, time_window: str = None,
                            taken_date: date = None, timestamp: datetime = None) -> Dict:
        """Mark medicine as taken and decrement pill count (ACID transaction)

        Args:
            medicine_id: Medicine ID
            time_window: Time window (defaults to medicine's time_window)
            taken_date: Date taken (defaults to today)
            timestamp: Timestamp (defaults to now)

        Returns:
            Dictionary with success status, pills_remaining, low_stock

        Raises:
            ValueError: If medicine not found
        """
        if taken_date is None:
            taken_date = date.today()
        if timestamp is None:
            timestamp = datetime.now()

        date_str = taken_date.strftime('%Y-%m-%d')
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')

        try:
            with self.transaction() as conn:
                # Get medicine details with row lock
                cursor = conn.execute(
                    "SELECT * FROM medicines WHERE id = ?",
                    (medicine_id,)
                )
                med = cursor.fetchone()

                if med is None:
                    raise ValueError(f"Medicine not found: {medicine_id}")

                # Use medicine's time_window if not specified
                if time_window is None:
                    time_window = med['time_window']

                pills_per_dose = med['pills_per_dose']
                pills_remaining = med['pills_remaining']

                # Insert or update tracking
                conn.execute("""
                    INSERT INTO tracking (medicine_id, date, time_window, taken, timestamp, pills_taken)
                    VALUES (?, ?, ?, 1, ?, ?)
                    ON CONFLICT(medicine_id, date, time_window)
                    DO UPDATE SET taken=1, timestamp=excluded.timestamp, pills_taken=excluded.pills_taken
                """, (medicine_id, date_str, time_window, timestamp_str, pills_per_dose))

                # Decrement pill count
                new_count = max(0, pills_remaining - pills_per_dose)
                conn.execute(
                    "UPDATE medicines SET pills_remaining = ? WHERE id = ?",
                    (new_count, medicine_id)
                )

                low_stock = new_count <= med['low_stock_threshold']

                logger.info(f"Marked medicine taken: {medicine_id} at {timestamp_str}")

                return {
                    'success': True,
                    'medicine_id': medicine_id,
                    'pills_remaining': new_count,
                    'low_stock': low_stock
                }

        except Exception as e:
            logger.error(f"Failed to mark medicine taken: {e}")
            raise

    def skip_medicine(self, medicine_id: str, time_window: str = None,
                     skip_date: date = None, skip_timestamp: datetime = None,
                     skip_reason: str = None) -> Dict:
        """Mark medicine as skipped (not taken)

        Args:
            medicine_id: Medicine ID
            time_window: Time window (defaults to medicine's time_window)
            skip_date: Date skipped (defaults to today)
            skip_timestamp: Timestamp (defaults to now)
            skip_reason: Optional reason (Forgot, Side effects, Out of stock, Doctor advised, Other)

        Returns:
            Dict with medicine info and skip confirmation

        Raises:
            ValueError: If medicine not found
        """
        if skip_date is None:
            skip_date = date.today()
        if skip_timestamp is None:
            skip_timestamp = datetime.now()

        date_str = skip_date.strftime('%Y-%m-%d')
        timestamp_str = skip_timestamp.strftime('%Y-%m-%d %H:%M:%S')

        try:
            with self.transaction() as conn:
                # Get medicine details with row lock
                cursor = conn.execute(
                    "SELECT * FROM medicines WHERE id = ?",
                    (medicine_id,)
                )
                med = cursor.fetchone()

                if med is None:
                    raise ValueError(f"Medicine not found: {medicine_id}")

                # Use medicine's time_window if not specified
                if time_window is None:
                    time_window = med['time_window']

                # Insert or update tracking with skip status
                # Note: We don't decrement pill count for skipped doses
                # The timestamp field is required (NOT NULL), so we set it to skip_timestamp for consistency
                conn.execute("""
                    INSERT INTO tracking (medicine_id, date, time_window, taken, timestamp, skipped, skip_timestamp, skip_reason)
                    VALUES (?, ?, ?, 0, ?, 1, ?, ?)
                    ON CONFLICT(medicine_id, date, time_window)
                    DO UPDATE SET skipped=1, skip_timestamp=excluded.skip_timestamp, skip_reason=excluded.skip_reason
                """, (medicine_id, date_str, time_window, timestamp_str, timestamp_str, skip_reason))

                logger.info(f"Marked medicine skipped: {medicine_id} at {timestamp_str} (reason: {skip_reason})")

                return {
                    'success': True,
                    'medicine_id': medicine_id,
                    'skip_date': date_str,
                    'skip_timestamp': timestamp_str,
                    'skip_reason': skip_reason,
                    'time_window': time_window
                }

        except Exception as e:
            logger.error(f"Failed to mark medicine skipped: {e}")
            raise

    def get_skip_history(self, medicine_id: str = None,
                        start_date: date = None, end_date: date = None) -> List[Dict]:
        """Get skip history

        Args:
            medicine_id: Filter by medicine (optional)
            start_date: Start date (optional)
            end_date: End date (optional)

        Returns:
            List of skipped doses with reasons
        """
        conn = self._get_connection()

        query = """
        SELECT t.*, m.name, m.dosage
        FROM tracking t
        INNER JOIN medicines m ON t.medicine_id = m.id
        WHERE t.skipped = 1
        """

        params = []

        if medicine_id:
            query += " AND t.medicine_id = ?"
            params.append(medicine_id)

        if start_date:
            query += " AND t.date >= ?"
            params.append(start_date.strftime('%Y-%m-%d'))

        if end_date:
            query += " AND t.date <= ?"
            params.append(end_date.strftime('%Y-%m-%d'))

        query += " ORDER BY t.date DESC, t.skip_timestamp DESC"

        cursor = conn.execute(query, params)

        return [dict(row) for row in cursor.fetchall()]

    def get_adherence_detailed(self, start_date: date = None,
                              end_date: date = None) -> Dict:
        """Get detailed adherence stats including skips

        Args:
            start_date: Start date (optional)
            end_date: End date (optional)

        Returns:
            Dict with: taken, skipped, missed, total, adherence_rate, skip_rate
        """
        conn = self._get_connection()

        # Default to last 30 days if not specified
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        date_str_start = start_date.strftime('%Y-%m-%d')
        date_str_end = end_date.strftime('%Y-%m-%d')

        query = """
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN taken = 1 THEN 1 ELSE 0 END) as taken,
            SUM(CASE WHEN skipped = 1 THEN 1 ELSE 0 END) as skipped,
            SUM(CASE WHEN taken = 0 AND skipped = 0 THEN 1 ELSE 0 END) as missed
        FROM tracking
        WHERE date >= ? AND date <= ?
        """

        cursor = conn.execute(query, (date_str_start, date_str_end))
        row = cursor.fetchone()

        total = row['total'] or 0
        taken = row['taken'] or 0
        skipped = row['skipped'] or 0
        missed = row['missed'] or 0

        adherence_rate = (taken / total * 100) if total > 0 else 0.0
        skip_rate = (skipped / total * 100) if total > 0 else 0.0

        return {
            'taken': taken,
            'skipped': skipped,
            'missed': missed,
            'total': total,
            'adherence_rate': round(adherence_rate, 1),
            'skip_rate': round(skip_rate, 1)
        }

    def get_today_stats(self, check_date: date = None) -> Tuple[int, int, int]:
        """Get today's adherence statistics

        Args:
            check_date: Date to check (defaults to today)

        Returns:
            Tuple of (medicines_taken, medicines_skipped, total_medicines)
        """
        if check_date is None:
            check_date = date.today()

        date_str = check_date.strftime('%Y-%m-%d')
        current_day = check_date.strftime('%a').lower()

        conn = self._get_connection()

        query = """
        SELECT
            COUNT(DISTINCT m.id) as total,
            COUNT(DISTINCT CASE WHEN t.taken = 1 THEN t.medicine_id END) as taken,
            COUNT(DISTINCT CASE WHEN t.skipped = 1 THEN t.medicine_id END) as skipped
        FROM medicines m
        INNER JOIN medicine_days md ON m.id = md.medicine_id
        LEFT JOIN tracking t ON m.id = t.medicine_id AND t.date = ?
        WHERE m.active = 1 AND md.day = ?
        """

        cursor = conn.execute(query, (date_str, current_day))
        row = cursor.fetchone()

        return (row['taken'] or 0, row['skipped'] or 0, row['total'] or 0)

    def get_tracking_history(self, medicine_id: str = None,
                             start_date: date = None, end_date: date = None) -> List[Dict]:
        """Get tracking history

        Args:
            medicine_id: Filter by medicine ID (optional)
            start_date: Start date (optional)
            end_date: End date (optional)

        Returns:
            List of tracking records
        """
        conn = self._get_connection()

        query = """
        SELECT t.*, m.name, m.dosage
        FROM tracking t
        INNER JOIN medicines m ON t.medicine_id = m.id
        WHERE 1=1
        """

        params = []

        if medicine_id:
            query += " AND t.medicine_id = ?"
            params.append(medicine_id)

        if start_date:
            query += " AND t.date >= ?"
            params.append(start_date.strftime('%Y-%m-%d'))

        if end_date:
            query += " AND t.date <= ?"
            params.append(end_date.strftime('%Y-%m-%d'))

        query += " ORDER BY t.date DESC, t.timestamp DESC"

        cursor = conn.execute(query, params)

        return [dict(row) for row in cursor.fetchall()]

    def get_low_stock_medicines(self) -> List[Dict]:
        """Get medicines at or below low stock threshold

        Returns:
            List of low stock medicines
        """
        conn = self._get_connection()

        cursor = conn.execute("""
            SELECT
                id, name, dosage, pills_remaining, low_stock_threshold,
                pills_per_dose,
                ROUND(CAST(pills_remaining AS REAL) / CAST(pills_per_dose AS REAL), 1) as days_remaining
            FROM medicines
            WHERE active = 1
              AND pills_remaining <= low_stock_threshold
            ORDER BY pills_remaining ASC
        """)

        return [dict(row) for row in cursor.fetchall()]

    def vacuum(self):
        """Optimize database (reclaim space, rebuild indexes)"""
        conn = self._get_connection()
        conn.execute("VACUUM")
        conn.execute("ANALYZE")
        logger.info("Database optimized (VACUUM + ANALYZE)")

    def close(self):
        """Close database connection"""
        if hasattr(self._local, 'conn') and self._local.conn is not None:
            self._local.conn.close()
            self._local.conn = None
            logger.info("Database connection closed")
