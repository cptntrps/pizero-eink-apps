"""
Automated Backup System
Manages daily backups of critical data files
"""

import os
import shutil
import glob
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class BackupManager:
    """Manages automated backups with rotation"""

    def __init__(self, backup_dir: str = None):
        """Initialize backup manager

        Args:
            backup_dir: Directory to store backups. If None, uses default.
        """
        if backup_dir is None:
            backup_dir = os.environ.get(
                'PIZERO_BACKUP_DIR',
                '/home/pizero2w/backups'
            )

        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)

    def backup_file(self, filepath: str, keep_days: int = 7) -> str:
        """Create timestamped backup of file

        Args:
            filepath: Path to file to backup
            keep_days: Number of days of backups to keep

        Returns:
            Path to backup file

        Raises:
            FileNotFoundError: If source file doesn't exist
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(filepath)
        backup_name = f"{filename}.{timestamp}.backup"
        backup_path = os.path.join(self.backup_dir, backup_name)

        # Copy file
        shutil.copy2(filepath, backup_path)
        logger.info(f"Backed up: {filepath} → {backup_path}")

        # Clean up old backups
        self._cleanup_old_backups(filename, keep_days)

        return backup_path

    def _cleanup_old_backups(self, filename: str, keep_days: int):
        """Remove backups older than keep_days

        Args:
            filename: Base filename to clean up
            keep_days: Number of days to keep
        """
        cutoff_date = datetime.now() - timedelta(days=keep_days)

        # Find all backups for this file
        pattern = os.path.join(self.backup_dir, f"{filename}.*.backup")
        backups = glob.glob(pattern)

        for backup_path in backups:
            # Extract timestamp from filename
            try:
                # Format: filename.YYYYMMDD_HHMMSS.backup
                parts = os.path.basename(backup_path).split('.')
                if len(parts) >= 3:
                    timestamp_str = parts[-2]
                    backup_date = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')

                    if backup_date < cutoff_date:
                        os.remove(backup_path)
                        logger.info(f"Removed old backup: {backup_path}")
            except (ValueError, IndexError) as e:
                logger.warning(f"Could not parse backup filename: {backup_path}: {e}")

    def backup_database(self, db_path: str = None, keep_days: int = 7) -> str:
        """Backup SQLite database file

        Args:
            db_path: Path to database file. If None, uses default.
            keep_days: Number of days of backups to keep

        Returns:
            Path to backup file
        """
        if db_path is None:
            db_path = '/home/pizero2w/pizero_apps/medicine.db'

        return self.backup_file(db_path, keep_days)

    def backup_config(self, config_path: str = None, keep_days: int = 30) -> str:
        """Backup configuration file

        Args:
            config_path: Path to config file. If None, uses default.
            keep_days: Number of days of backups to keep (default: 30 for config)

        Returns:
            Path to backup file
        """
        if config_path is None:
            config_path = '/home/pizero2w/pizero_apps/config.json'

        return self.backup_file(config_path, keep_days)

    def restore_from_backup(self, backup_path: str, target_path: str):
        """Restore file from backup

        Args:
            backup_path: Path to backup file
            target_path: Path to restore to

        Raises:
            FileNotFoundError: If backup file doesn't exist
        """
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        # Create backup of current file before restoring
        if os.path.exists(target_path):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pre_restore_backup = f"{target_path}.pre_restore_{timestamp}"
            shutil.copy2(target_path, pre_restore_backup)
            logger.info(f"Created pre-restore backup: {pre_restore_backup}")

        # Restore from backup
        shutil.copy2(backup_path, target_path)
        logger.info(f"Restored: {backup_path} → {target_path}")

    def list_backups(self, filename: str = None) -> list:
        """List available backups

        Args:
            filename: Filter by filename (optional)

        Returns:
            List of tuples: (backup_path, timestamp)
        """
        if filename:
            pattern = os.path.join(self.backup_dir, f"{filename}.*.backup")
        else:
            pattern = os.path.join(self.backup_dir, "*.backup")

        backups = []

        for backup_path in glob.glob(pattern):
            try:
                # Extract timestamp
                parts = os.path.basename(backup_path).split('.')
                if len(parts) >= 3:
                    timestamp_str = parts[-2]
                    backup_date = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                    backups.append((backup_path, backup_date))
            except (ValueError, IndexError):
                continue

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x[1], reverse=True)

        return backups

    def get_backup_size(self) -> int:
        """Get total size of all backups in bytes

        Returns:
            Total size in bytes
        """
        total_size = 0

        for root, dirs, files in os.walk(self.backup_dir):
            for filename in files:
                if filename.endswith('.backup'):
                    filepath = os.path.join(root, filename)
                    total_size += os.path.getsize(filepath)

        return total_size


def run_daily_backup():
    """Run daily backup (called by cron)"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    manager = BackupManager()

    try:
        # Backup database
        db_path = '/home/pizero2w/pizero_apps/medicine.db'
        if os.path.exists(db_path):
            manager.backup_database(db_path, keep_days=7)
            logger.info("Database backup completed")

        # Backup config (keep longer)
        config_path = '/home/pizero2w/pizero_apps/config.json'
        if os.path.exists(config_path):
            manager.backup_config(config_path, keep_days=30)
            logger.info("Config backup completed")

        # Report backup size
        total_size = manager.get_backup_size()
        size_mb = total_size / (1024 * 1024)
        logger.info(f"Total backup size: {size_mb:.2f} MB")

    except Exception as e:
        logger.error(f"Backup failed: {e}")
        raise


if __name__ == '__main__':
    run_daily_backup()
