import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { pool } from "../db.js";
import { ensureDevUserPasswordHashes } from "./ensureDevPasswords.js";

async function runSql(relativePath: string) {
  const filePath = resolve(process.cwd(), "..", "infra", relativePath);
  const sql = await readFile(filePath, "utf8");
  await pool.query(sql);
}

async function main() {
  await runSql("migrations/001_init.sql");
  await runSql("migrations/002_mimir_snapshots.sql");
  await runSql("seeds/001_seed.sql");
  const pwdRows = await ensureDevUserPasswordHashes();
  console.log(
    JSON.stringify({
      level: "info",
      message: "migrations_completed",
      dev_password_hash_rows_updated: pwdRows
    })
  );
  await pool.end();
}

main().catch((error) => {
  console.error(JSON.stringify({ level: "error", message: "migrations_failed", error: String(error) }));
  process.exit(1);
});
