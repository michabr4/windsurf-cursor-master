import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';
import { Pool } from 'pg';

dotenv.config();

function migrationDir(): string {
  return path.resolve(process.cwd(), 'db', 'migrations');
}

async function ensureMetaTable(pool: Pool): Promise<void> {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS schema_migrations (
      version TEXT PRIMARY KEY,
      applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
  `);
}

async function appliedVersions(pool: Pool): Promise<Set<string>> {
  const result = await pool.query<{ version: string }>('SELECT version FROM schema_migrations');
  return new Set(result.rows.map((r) => r.version));
}

export async function runMigrations(): Promise<void> {
  const databaseUrl = process.env.DATABASE_URL;
  if (!databaseUrl) {
    throw new Error('DATABASE_URL is required for migrations');
  }

  const pool = new Pool({ connectionString: databaseUrl });
  try {
    await ensureMetaTable(pool);
    const applied = await appliedVersions(pool);

    const dir = migrationDir();
    if (!fs.existsSync(dir)) {
      throw new Error(`Migration directory not found: ${dir}`);
    }

    const files = fs
      .readdirSync(dir)
      .filter((f) => f.endsWith('.sql'))
      .sort((a, b) => a.localeCompare(b));

    for (const file of files) {
      if (applied.has(file)) continue;
      const sql = fs.readFileSync(path.join(dir, file), 'utf-8');
      await pool.query('BEGIN');
      try {
        await pool.query(sql);
        await pool.query('INSERT INTO schema_migrations (version) VALUES ($1)', [file]);
        await pool.query('COMMIT');
        console.log(`Applied migration: ${file}`);
      } catch (err) {
        await pool.query('ROLLBACK');
        throw err;
      }
    }
  } finally {
    await pool.end();
  }
}

if (require.main === module) {
  runMigrations()
    .then(() => {
      console.log('Migrations complete');
    })
    .catch((err) => {
      console.error('Migration failed:', err);
      process.exit(1);
    });
}
