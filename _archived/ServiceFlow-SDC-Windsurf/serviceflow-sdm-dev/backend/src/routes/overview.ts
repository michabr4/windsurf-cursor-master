import { Router } from "express";
import { pool } from "../db.js";
import { requireAuth } from "../middleware/auth.js";

export const overviewRouter = Router();

/** Aggregated read model for Helix Overview + mockup live strip (one round-trip). */
overviewRouter.get("/summary", requireAuth, async (_req, res) => {
  try {
    const [
      incOpen,
      incP12,
      incTac,
      incOpened7d,
      incResolved7d,
      devCounts,
      tacOpen,
      tacTotal,
      licAgg,
      activity
    ] = await Promise.all([
      pool.query<{ c: string }>(
        `SELECT COUNT(*)::text AS c FROM mgm.incidents
         WHERE LOWER(status) NOT IN ('resolved','closed','cancelled')`
      ),
      pool.query<{ c: string }>(
        `SELECT COUNT(*)::text AS c FROM mgm.incidents
         WHERE LOWER(status) NOT IN ('resolved','closed','cancelled')
           AND priority IN ('P1','P2')`
      ),
      pool.query<{ c: string }>(
        `SELECT COUNT(*)::text AS c FROM mgm.incidents
         WHERE tac_case_number IS NOT NULL AND BTRIM(tac_case_number) <> ''`
      ),
      pool.query<{ c: string }>(
        `SELECT COUNT(*)::text AS c FROM mgm.incidents
         WHERE created_at >= NOW() - INTERVAL '7 days'`
      ),
      pool.query<{ c: string }>(
        `SELECT COUNT(*)::text AS c FROM mgm.incidents
         WHERE updated_at >= NOW() - INTERVAL '7 days'
           AND LOWER(status) IN ('resolved','closed')`
      ),
      pool.query<{ total: string; active: string; maintenance: string; failed: string }>(
        `SELECT
           COUNT(*)::text AS total,
           COUNT(*) FILTER (WHERE LOWER(status) = 'active')::text AS active,
           COUNT(*) FILTER (WHERE LOWER(status) = 'maintenance')::text AS maintenance,
           COUNT(*) FILTER (WHERE LOWER(status) IN ('failed','decommissioned'))::text AS failed
         FROM mgm.devices`
      ),
      pool.query<{ c: string }>(
        `SELECT COUNT(*)::text AS c FROM cisco.tac_cases
         WHERE LOWER(status) NOT IN ('resolved','closed')`
      ),
      pool.query<{ c: string }>(`SELECT COUNT(*)::text AS c FROM cisco.tac_cases`),
      pool.query<{ pct: string | null; rows: string }>(
        `SELECT
           CASE WHEN COUNT(*) = 0 THEN NULL
                ELSE ROUND(
                  100.0 * COUNT(*) FILTER (
                    WHERE LOWER(TRIM(COALESCE(compliance_status,''))) IN ('compliant','healthy','ok','pass','passed')
                  ) / COUNT(*)
                )::numeric
           END AS pct,
           COUNT(*)::text AS rows
         FROM cisco.licenses`
      ),
      pool.query<{
        created_at: Date;
        full_name: string;
        incident_number: string | null;
        content: string;
      }>(
        `SELECT iu.created_at, u.full_name, i.incident_number, iu.content
         FROM mgm.incident_updates iu
         JOIN mgm.incidents i ON i.incident_id = iu.incident_id
         JOIN mgm.users u ON u.user_id = iu.user_id
         ORDER BY iu.created_at DESC
         LIMIT 12`
      )
    ]);

    const n = (row: { c: string } | undefined) => Number(row?.c ?? 0);
    const dr = devCounts.rows[0];

    const licRows = Number(licAgg.rows[0]?.rows ?? 0);
    const licPct =
      licAgg.rows[0]?.pct === null || licAgg.rows[0]?.pct === undefined
        ? null
        : Number(licAgg.rows[0].pct);

    const activities = activity.rows.map((r) => {
      const body = r.content.length > 160 ? `${r.content.slice(0, 157)}…` : r.content;
      return {
        createdAt: r.created_at.toISOString(),
        actor: r.full_name,
        incidentNumber: r.incident_number ?? "—",
        body
      };
    });

    res.json({
      incidents: {
        open: n(incOpen.rows[0]),
        p1P2Open: n(incP12.rows[0]),
        withTacNumber: n(incTac.rows[0]),
        openedLast7d: n(incOpened7d.rows[0]),
        resolvedLast7d: n(incResolved7d.rows[0])
      },
      devices: {
        total: Number(dr?.total ?? 0),
        active: Number(dr?.active ?? 0),
        maintenance: Number(dr?.maintenance ?? 0),
        failed: Number(dr?.failed ?? 0)
      },
      tacCases: {
        open: n(tacOpen.rows[0]),
        total: n(tacTotal.rows[0])
      },
      licenses: {
        compliancePercent: licRows === 0 ? null : licPct,
        rowCount: licRows
      },
      recentActivity: activities
    });
  } catch {
    res.status(500).json({ message: "Failed to load overview summary" });
  }
});
