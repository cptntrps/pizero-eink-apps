# Database Migrations

Safe schema changes and data migrations.

---

## 🚨 Critical Rules

- ✋ **ALWAYS test migrations on production snapshot** before deploying
- ✋ **ALWAYS have rollback (DOWN) migration**
- ✋ **ALWAYS backup before migration in production**
- ✋ **NEVER modify existing migrations** after they've been deployed
- ✋ **MIGRATIONS must be idempotent** (safe to run multiple times)

---

## 📋 Migration Best Practices

### 1. Create Migration

**Good migration naming:**
```
20241109120000_add_email_verified_to_users.ts
20241109120001_create_posts_table.ts
20241109120002_add_index_to_users_email.ts
```

**Include timestamp and descriptive name**

---

### 2. Write Migration (UP and DOWN)

**Example (Knex.js):**
```typescript
// migrations/20241109_add_email_verified.ts
import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.table('users', (table) => {
    table.boolean('email_verified').defaultTo(false);
    table.timestamp('email_verified_at').nullable();
  });

  // Backfill: Mark existing users as verified
  await knex('users')
    .whereNotNull('created_at')
    .update({ email_verified: true });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.table('users', (table) => {
    table.dropColumn('email_verified');
    table.dropColumn('email_verified_at');
  });
}
```

**Example (Sequelize):**
```javascript
module.exports = {
  up: async (queryInterface, Sequelize) => {
    await queryInterface.addColumn('users', 'email_verified', {
      type: Sequelize.BOOLEAN,
      defaultValue: false,
      allowNull: false
    });
  },

  down: async (queryInterface) => {
    await queryInterface.removeColumn('users', 'email_verified');
  }
};
```

---

### 3. Test Migration Locally

```bash
# Run migration
npm run migrate:up

# Verify schema
psql myapp_dev
\d users  # Should show new column

# Test rollback
npm run migrate:down

# Verify reverted
\d users  # Column should be gone

# Re-run migration to test idempotency
npm run migrate:up
npm run migrate:up  # Should not error
```

---

### 4. Test on Production Snapshot

```bash
# 1. Get production data snapshot
pg_dump -h prod-server -U user myapp_prod > prod_snapshot.sql

# 2. Restore to local test database
createdb myapp_test
psql myapp_test < prod_snapshot.sql

# 3. Run migration against test database
DATABASE_URL=postgresql://localhost/myapp_test npm run migrate:up

# 4. Verify data integrity
psql myapp_test
SELECT COUNT(*) FROM users WHERE email_verified IS NULL;  # Should be 0

# 5. Test rollback
DATABASE_URL=postgresql://localhost/myapp_test npm run migrate:down
```

---

## 🔄 Common Migration Patterns

### Adding a Column

```typescript
// ✅ Safe: Nullable or with default
export async function up(knex: Knex) {
  await knex.schema.table('users', (table) => {
    table.string('phone').nullable();
  });
}

// ❌ Unsafe: NOT NULL without default on existing table
export async function up(knex: Knex) {
  await knex.schema.table('users', (table) => {
    table.string('phone').notNullable();  // Will fail!
  });
}
```

---

### Removing a Column

**Safe two-step process:**

**Step 1: Deploy code that doesn't use column**
```typescript
// Stop using the column in code
// Deploy this version
```

**Step 2: Remove column in migration**
```typescript
export async function up(knex: Knex) {
  await knex.schema.table('users', (table) => {
    table.dropColumn('deprecated_field');
  });
}
```

**Why:** Deployed code might still reference column. Remove usage first, then column.

---

### Renaming a Column

**Safe three-step process:**

**Step 1: Add new column**
```typescript
export async function up(knex: Knex) {
  await knex.schema.table('users', (table) => {
    table.string('full_name');
  });

  // Copy data
  await knex.raw('UPDATE users SET full_name = name');
}
```

**Step 2: Update code to use new column** (deploy)

**Step 3: Remove old column**
```typescript
export async function up(knex: Knex) {
  await knex.schema.table('users', (table) => {
    table.dropColumn('name');
  });
}
```

---

### Changing Column Type

**Safe approach:**

```typescript
export async function up(knex: Knex) {
  // 1. Add new column with new type
  await knex.schema.table('users', (table) => {
    table.integer('age_new');
  });

  // 2. Copy and convert data
  await knex.raw(`
    UPDATE users
    SET age_new = CAST(age AS INTEGER)
    WHERE age ~ '^[0-9]+$'
  `);

  // 3. Drop old column
  await knex.schema.table('users', (table) => {
    table.dropColumn('age');
  });

  // 4. Rename new column
  await knex.schema.table('users', (table) => {
    table.renameColumn('age_new', 'age');
  });
}
```

---

### Adding an Index

```typescript
export async function up(knex: Knex) {
  await knex.schema.table('users', (table) => {
    table.index('email', 'idx_users_email');
  });
}

export async function down(knex: Knex) {
  await knex.schema.table('users', (table) => {
    table.dropIndex('email', 'idx_users_email');
  });
}
```

**Note:** Creating indexes can lock table. For large tables, use `CONCURRENTLY`:
```sql
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```

---

## 📊 Data Migrations

### Backfilling Data

```typescript
export async function up(knex: Knex) {
  // Add column
  await knex.schema.table('users', (table) => {
    table.string('display_name');
  });

  // Backfill in batches (avoid locking large tables)
  const batchSize = 1000;
  let offset = 0;

  while (true) {
    const users = await knex('users')
      .whereNull('display_name')
      .limit(batchSize)
      .offset(offset);

    if (users.length === 0) break;

    for (const user of users) {
      await knex('users')
        .where({ id: user.id })
        .update({
          display_name: `${user.first_name} ${user.last_name}`
        });
    }

    offset += batchSize;
  }
}
```

---

### Data Transformation

```typescript
export async function up(knex: Knex) {
  // Transform JSON column to normalized table

  // 1. Create new table
  await knex.schema.createTable('user_preferences', (table) => {
    table.uuid('id').primary();
    table.uuid('user_id').references('users.id');
    table.string('key').notNullable();
    table.string('value');
    table.unique(['user_id', 'key']);
  });

  // 2. Migrate data
  const users = await knex('users').select('id', 'preferences_json');

  for (const user of users) {
    const preferences = JSON.parse(user.preferences_json || '{}');

    for (const [key, value] of Object.entries(preferences)) {
      await knex('user_preferences').insert({
        id: generateUuid(),
        user_id: user.id,
        key,
        value: String(value)
      });
    }
  }

  // 3. (Later) Drop old column
}
```

---

## 🚀 Production Migration Process

### Pre-Migration Checklist

- [ ] Migration tested on production snapshot
- [ ] Migration has DOWN/rollback
- [ ] Backup scheduled (or taken)
- [ ] Team notified of migration window
- [ ] Deployment plan documented
- [ ] Monitoring ready
- [ ] Migration time estimated

---

### Execution Steps

```bash
# 1. BACKUP DATABASE (critical!)
pg_dump myapp_production > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Put application in maintenance mode (if needed)
#    For long migrations or schema changes

# 3. Run migration
npm run migrate:up

# 4. Verify migration success
npm run migrate:status

# 5. Verify data integrity
psql myapp_production
SELECT COUNT(*) FROM users WHERE email_verified IS NOT NULL;
# Check expected results

# 6. Deploy new application code
npm run deploy

# 7. Verify application works
npm run test:smoke

# 8. Monitor for errors
# Check logs, error tracking, metrics

# 9. Exit maintenance mode
```

---

### If Migration Fails

```bash
# 1. STAY CALM

# 2. Rollback migration
npm run migrate:down

# 3. Verify rollback successful
npm run migrate:status

# 4. Restore from backup if database corrupted
psql myapp_production < backup_20241109_120000.sql

# 5. Verify application working
npm run test:smoke

# 6. Investigate issue
#    - What failed?
#    - Why did it fail?
#    - Test fix locally

# 7. Fix and retry in next deployment window
```

---

## ⚠️ Common Pitfalls

### Making Destructive Changes Without Backup

```
❌ NEVER: Drop column without backup
✅ ALWAYS: Backup first, then drop
```

### Not Testing on Production Data

```
❌ Works on dev (100 rows)
❌ Fails on prod (10 million rows) - timeout
✅ Test on production snapshot first
```

### Breaking Changes Without Coordination

```
Migration removes column
Code still uses column
Result: 500 errors

✅ Deploy code changes first, then migration
```

---

## 📋 Migration Checklist

### Before Writing Migration
- [ ] Understand what needs to change
- [ ] Consider backward compatibility
- [ ] Plan rollback strategy

### Writing Migration
- [ ] UP migration created
- [ ] DOWN migration created
- [ ] Migration is idempotent
- [ ] Data preservation considered
- [ ] Performance impact assessed

### Testing Migration
- [ ] Tested locally (up and down)
- [ ] Tested on production snapshot
- [ ] Verified data integrity
- [ ] Rollback tested
- [ ] Performance measured

### Production Deployment
- [ ] Backup taken
- [ ] Team notified
- [ ] Maintenance window scheduled (if needed)
- [ ] Monitoring in place
- [ ] Rollback plan ready

---

**Remember:** Database migrations are irreversible without backups. Always backup, always test, always have a rollback plan.
