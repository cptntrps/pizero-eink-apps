#!/usr/bin/env python3
"""
Migration Script: JSON to SQLite
Migrates medicine_data.json to SQLite database with full validation
"""

import json
import os
import sys
import shutil
from datetime import datetime
from db.medicine_db import MedicineDatabase

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def backup_json_files():
    """Create backup of JSON files before migration"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'/home/user/pizerowgpio/backups/migration_{timestamp}'
    os.makedirs(backup_dir, exist_ok=True)

    files_to_backup = [
        'medicine_data.json',
        'config.json'
    ]

    for filename in files_to_backup:
        src = f'/home/user/pizerowgpio/{filename}'
        if os.path.exists(src):
            dst = f'{backup_dir}/{filename}'
            shutil.copy2(src, dst)
            print(f"✓ Backed up: {filename} → {dst}")

    return backup_dir


def load_json_data():
    """Load existing medicine_data.json"""
    json_path = '/home/user/pizerowgpio/medicine_data.json'

    if not os.path.exists(json_path):
        print(f"❌ Error: {json_path} not found")
        sys.exit(1)

    with open(json_path, 'r') as f:
        data = json.load(f)

    print(f"✓ Loaded JSON data: {len(data.get('medicines', []))} medicines")
    return data


def migrate_medicines(db: MedicineDatabase, json_data: dict):
    """Migrate medicines from JSON to SQLite"""
    medicines = json_data.get('medicines', [])

    print(f"\n📦 Migrating {len(medicines)} medicines...")

    for med in medicines:
        try:
            db.add_medicine(med)
            print(f"  ✓ {med['name']} ({med['dosage']})")
        except Exception as e:
            print(f"  ❌ Failed to migrate {med.get('name', 'unknown')}: {e}")
            raise

    print(f"✓ Migrated {len(medicines)} medicines")


def migrate_tracking(db: MedicineDatabase, json_data: dict):
    """Migrate tracking history from JSON to SQLite"""
    tracking = json_data.get('tracking', {})

    print(f"\n📊 Migrating tracking data for {len(tracking)} days...")

    total_entries = 0

    for date_str, entries in tracking.items():
        for key, entry in entries.items():
            # Parse key: "med_id_timewindow"
            parts = key.rsplit('_', 1)
            if len(parts) != 2:
                print(f"  ⚠️  Skipping invalid tracking key: {key}")
                continue

            medicine_id = parts[0]
            time_window = parts[1]

            # Only insert if marked as taken
            if entry.get('taken', False):
                try:
                    timestamp = datetime.fromisoformat(entry['timestamp'])

                    db.mark_medicine_taken(
                        medicine_id=medicine_id,
                        time_window=time_window,
                        taken_date=datetime.strptime(date_str, '%Y-%m-%d').date(),
                        timestamp=timestamp
                    )

                    total_entries += 1

                except Exception as e:
                    print(f"  ⚠️  Failed to migrate tracking {medicine_id} on {date_str}: {e}")

    print(f"✓ Migrated {total_entries} tracking entries across {len(tracking)} days")


def verify_migration(db: MedicineDatabase, json_data: dict):
    """Verify migration succeeded"""
    print("\n🔍 Verifying migration...")

    # Check medicine count
    json_medicines = len(json_data.get('medicines', []))
    db_medicines = len(db.get_all_medicines(include_inactive=True))

    if json_medicines == db_medicines:
        print(f"✓ Medicine count matches: {db_medicines}")
    else:
        print(f"❌ Medicine count mismatch: JSON={json_medicines}, DB={db_medicines}")
        return False

    # Check tracking count
    json_tracking = sum(len(entries) for entries in json_data.get('tracking', {}).values())
    db_tracking = len(db.get_tracking_history())

    print(f"  Tracking entries: JSON={json_tracking}, DB={db_tracking}")

    # Sample verification: check a few medicines exist
    for med in json_data.get('medicines', [])[:3]:
        db_med = db.get_medicine_by_id(med['id'])
        if db_med:
            print(f"  ✓ Verified: {med['name']}")
        else:
            print(f"  ❌ Missing: {med['name']}")
            return False

    print("✓ Migration verified successfully")
    return True


def main():
    """Main migration process"""
    print("=" * 70)
    print("  Pi Zero 2W Medicine Tracker - JSON to SQLite Migration")
    print("=" * 70)

    # Step 1: Backup
    print("\n1️⃣  Creating backups...")
    backup_dir = backup_json_files()
    print(f"✓ Backups created in: {backup_dir}")

    # Step 2: Load JSON
    print("\n2️⃣  Loading JSON data...")
    json_data = load_json_data()

    # Step 3: Initialize database
    print("\n3️⃣  Initializing SQLite database...")
    db_path = '/home/user/pizerowgpio/medicine.db'

    # Remove existing database if present
    if os.path.exists(db_path):
        response = input(f"\n⚠️  Database already exists: {db_path}\n   Overwrite? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Migration cancelled")
            sys.exit(0)
        os.remove(db_path)
        print("  Removed existing database")

    db = MedicineDatabase(db_path=db_path)
    print(f"✓ Database initialized: {db_path}")

    # Step 4: Migrate medicines
    print("\n4️⃣  Migrating medicines...")
    try:
        migrate_medicines(db, json_data)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)

    # Step 5: Migrate tracking
    print("\n5️⃣  Migrating tracking history...")
    try:
        migrate_tracking(db, json_data)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)

    # Step 6: Verify
    print("\n6️⃣  Verifying migration...")
    if not verify_migration(db, json_data):
        print("\n❌ Verification failed")
        sys.exit(1)

    # Step 7: Optimize
    print("\n7️⃣  Optimizing database...")
    db.vacuum()
    print("✓ Database optimized")

    # Final summary
    print("\n" + "=" * 70)
    print("✅ MIGRATION COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print(f"\n📁 SQLite Database: {db_path}")
    print(f"💾 JSON Backup: {backup_dir}")
    print(f"\n📊 Statistics:")
    print(f"   • Medicines: {len(db.get_all_medicines(include_inactive=True))}")
    print(f"   • Tracking Entries: {len(db.get_tracking_history())}")
    print(f"   • Low Stock: {len(db.get_low_stock_medicines())} medicines")

    taken, total = db.get_today_stats()
    print(f"   • Today's Progress: {taken}/{total} medicines taken")

    print("\n📝 Next Steps:")
    print("   1. Test database with: python3 -c 'from db.medicine_db import MedicineDatabase; db=MedicineDatabase(); print(db.get_all_medicines())'")
    print("   2. Update apps to use new database (medicine_app.py, web_config.py)")
    print("   3. Keep JSON backup for 30 days before deleting")
    print("\n✨ Migration complete!")


if __name__ == '__main__':
    main()
