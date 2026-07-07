import { Router } from "express";
import { z } from "zod";
import { pool } from "../db.js";
import { audit } from "../middleware/audit.js";
import { requireAuth, requireRoles, type AuthedRequest } from "../middleware/auth.js";

export const incidentsRouter = Router();

const CreateIncident = z.object({
  propertyId: z.string().uuid(),
  deviceId: z.string().uuid().optional(),
  title: z.string().min(5),
  description: z.string().min(5),
  priority: z.enum(["P1", "P2", "P3", "P4"])
});

const PatchIncident = z.object({
  status: z.enum([
    "open",
    "acknowledged",
    "investigating",
    "in-progress",
    "pending",
    "resolved",
    "closed",
    "cancelled"
  ])
});

const UpdatePayload = z.object({
  content: z.string().min(1)
});

const TacLinkPayload = z.object({
  tacCaseNumber: z.string().min(3),
  tacSeverity: z.enum(["1", "2", "3", "4"])
});

incidentsRouter.get("/", requireAuth, async (_req, res) => {
  const result = await pool.query(
    `SELECT incident_id, incident_number, property_id, device_id, title, priority, status, tac_case_number
     FROM mgm.incidents ORDER BY created_at DESC`
  );
  res.json(result.rows);
});

incidentsRouter.post(
  "/",
  requireAuth,
  requireRoles(["admin", "sdm", "tam", "csm", "engineer", "manager"]),
  audit("incident.create"),
  async (req: AuthedRequest, res) => {
    const parsed = CreateIncident.safeParse(req.body);
    if (!parsed.success || !req.auth) {
      res.status(400).json({ message: "Invalid request" });
      return;
    }
    const result = await pool.query(
      `INSERT INTO mgm.incidents
       (property_id, device_id, title, description, priority, status, reported_by, assigned_to)
       VALUES ($1, $2, $3, $4, $5, 'open', $6, $6)
       RETURNING incident_id, incident_number, title, priority, status`,
      [
        parsed.data.propertyId,
        parsed.data.deviceId ?? null,
        parsed.data.title,
        parsed.data.description,
        parsed.data.priority,
        req.auth.userId
      ]
    );
    res.status(201).json(result.rows[0]);
  }
);

incidentsRouter.patch(
  "/:incidentId",
  requireAuth,
  requireRoles(["admin", "sdm", "tam", "engineer", "manager"]),
  audit("incident.status.update"),
  async (req, res) => {
    const parsed = PatchIncident.safeParse(req.body);
    if (!parsed.success) {
      res.status(400).json({ message: "Invalid request" });
      return;
    }
    const result = await pool.query(
      "UPDATE mgm.incidents SET status = $1 WHERE incident_id = $2 RETURNING incident_id, status",
      [parsed.data.status, req.params.incidentId]
    );
    if (result.rowCount === 0) {
      res.status(404).json({ message: "Not found" });
      return;
    }
    res.json(result.rows[0]);
  }
);

incidentsRouter.post(
  "/:incidentId/updates",
  requireAuth,
  audit("incident.update.create"),
  async (req: AuthedRequest, res) => {
    const parsed = UpdatePayload.safeParse(req.body);
    if (!parsed.success || !req.auth) {
      res.status(400).json({ message: "Invalid request" });
      return;
    }
    const result = await pool.query(
      `INSERT INTO mgm.incident_updates (incident_id, user_id, content)
       VALUES ($1, $2, $3)
       RETURNING update_id, incident_id, user_id, content, created_at`,
      [req.params.incidentId, req.auth.userId, parsed.data.content]
    );
    res.status(201).json(result.rows[0]);
  }
);

incidentsRouter.post(
  "/:incidentId/tac-link",
  requireAuth,
  requireRoles(["admin", "sdm", "tam", "engineer"]),
  audit("incident.tac.link"),
  async (req, res) => {
    const parsed = TacLinkPayload.safeParse(req.body);
    if (!parsed.success) {
      res.status(400).json({ message: "Invalid request" });
      return;
    }
    const result = await pool.query(
      `UPDATE mgm.incidents
       SET tac_case_number = $1, tac_severity = $2
       WHERE incident_id = $3
       RETURNING incident_id, tac_case_number, tac_severity`,
      [parsed.data.tacCaseNumber, parsed.data.tacSeverity, req.params.incidentId]
    );
    if (result.rowCount === 0) {
      res.status(404).json({ message: "Not found" });
      return;
    }
    res.json(result.rows[0]);
  }
);
