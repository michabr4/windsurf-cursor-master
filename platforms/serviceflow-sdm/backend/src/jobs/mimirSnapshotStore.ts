import { pool } from "../db.js";
import type {
  MimirDevice,
  MimirFnSummary,
  MimirPsirtSummary,
  MimirQbrComposite
} from "../integrations/mimirClient.js";

export async function persistMimirSnapshots(
  companyId: string,
  devices: MimirDevice[],
  psirt: MimirPsirtSummary | null,
  fn: MimirFnSummary | null,
  qbr: MimirQbrComposite | null
): Promise<number> {
  const db = await pool.connect();
  let processed = 0;

  try {
    await db.query("BEGIN");

    for (const device of devices) {
      await db.query(
        `INSERT INTO cisco.mimir_inventory_snapshot
           (company_id, device_name, ip_address, product_id, sw_version, device_role, raw_json)
         VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)`,
        [
          companyId,
          device.deviceName ?? null,
          device.ipAddress ?? null,
          device.productId ?? null,
          device.swVersion ?? null,
          device.role ?? null,
          JSON.stringify(device)
        ]
      );
      processed += 1;
    }

    if (psirt) {
      await db.query(
        `INSERT INTO cisco.mimir_psirt_snapshot
           (company_id, total_count, critical, high, medium, low, raw_json)
         VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)`,
        [
          companyId,
          psirt.totalCount,
          psirt.critical,
          psirt.high,
          psirt.medium,
          psirt.low,
          JSON.stringify(psirt)
        ]
      );
      processed += 1;
    }

    if (fn) {
      await db.query(
        `INSERT INTO cisco.mimir_fn_snapshot
           (company_id, total_count, affected_devices, raw_json)
         VALUES ($1, $2, $3, $4::jsonb)`,
        [companyId, fn.totalCount, fn.affectedDevices, JSON.stringify(fn)]
      );
      processed += 1;
    }

    if (qbr) {
      await db.query(
        `INSERT INTO cisco.mimir_qbr_snapshot
           (company_id, risk_composite, psirt_score, fn_score, hw_lifecycle_score, sw_lifecycle_score, raw_json)
         VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)`,
        [
          companyId,
          qbr.riskComposite,
          qbr.psirtScore,
          qbr.fnScore,
          qbr.hwLifecycleScore,
          qbr.swLifecycleScore,
          JSON.stringify(qbr)
        ]
      );
      processed += 1;
    }

    await db.query("COMMIT");
    return processed;
  } catch (err) {
    await db.query("ROLLBACK");
    console.warn(
      JSON.stringify({
        level: "warn",
        message: "mimir_snapshot_persist_failed",
        companyId,
        error: err instanceof Error ? err.message : String(err)
      })
    );
    return 0;
  } finally {
    db.release();
  }
}

export async function getLatestMimirInventory(companyId: string): Promise<{
  syncedAt: string | null;
  devices: Record<string, unknown>[];
}> {
  const latest = await pool.query<{ synced_at: Date }>(
    `SELECT synced_at FROM cisco.mimir_inventory_snapshot
     WHERE company_id = $1 ORDER BY synced_at DESC LIMIT 1`,
    [companyId]
  );
  if (latest.rowCount === 0) {
    return { syncedAt: null, devices: [] };
  }

  const syncedAt = latest.rows[0].synced_at;
  const rows = await pool.query(
    `SELECT device_name AS "deviceName", ip_address AS "ipAddress", product_id AS "productId",
            sw_version AS "swVersion", device_role AS "role", raw_json AS "rawJson"
     FROM cisco.mimir_inventory_snapshot
     WHERE company_id = $1 AND synced_at = $2
     ORDER BY device_name`,
    [companyId, syncedAt]
  );

  return {
    syncedAt: syncedAt.toISOString(),
    devices: rows.rows
  };
}

export async function getLatestMimirPsirt(companyId: string): Promise<Record<string, unknown> | null> {
  const result = await pool.query(
    `SELECT synced_at AS "syncedAt", total_count AS "totalCount", critical, high, medium, low, raw_json AS "rawJson"
     FROM cisco.mimir_psirt_snapshot
     WHERE company_id = $1 ORDER BY synced_at DESC LIMIT 1`,
    [companyId]
  );
  return result.rows[0] ?? null;
}

export async function getLatestMimirFn(companyId: string): Promise<Record<string, unknown> | null> {
  const result = await pool.query(
    `SELECT synced_at AS "syncedAt", total_count AS "totalCount",
            affected_devices AS "affectedDevices", raw_json AS "rawJson"
     FROM cisco.mimir_fn_snapshot
     WHERE company_id = $1 ORDER BY synced_at DESC LIMIT 1`,
    [companyId]
  );
  return result.rows[0] ?? null;
}

export async function getLatestMimirQbr(companyId: string): Promise<Record<string, unknown> | null> {
  const result = await pool.query(
    `SELECT synced_at AS "syncedAt", risk_composite AS "riskComposite", psirt_score AS "psirtScore",
            fn_score AS "fnScore", hw_lifecycle_score AS "hwLifecycleScore",
            sw_lifecycle_score AS "swLifecycleScore", raw_json AS "rawJson"
     FROM cisco.mimir_qbr_snapshot
     WHERE company_id = $1 ORDER BY synced_at DESC LIMIT 1`,
    [companyId]
  );
  return result.rows[0] ?? null;
}
