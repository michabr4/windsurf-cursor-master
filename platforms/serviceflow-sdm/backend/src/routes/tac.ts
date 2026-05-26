import { Router } from "express";
import { pool } from "../db.js";
import { requireAuth } from "../middleware/auth.js";

export const tacRouter = Router();

tacRouter.get("/", requireAuth, async (_req, res) => {
  const result = await pool.query(
    `SELECT tac_case_id, case_number, severity, status, incident_id, last_update_at
     FROM cisco.tac_cases ORDER BY created_at DESC LIMIT 200`
  );
  res.json(result.rows);
});
