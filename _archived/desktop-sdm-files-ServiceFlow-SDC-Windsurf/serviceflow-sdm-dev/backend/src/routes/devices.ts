import { Router } from "express";
import { z } from "zod";
import { pool } from "../db.js";
import { audit } from "../middleware/audit.js";
import { requireAuth, requireRoles } from "../middleware/auth.js";

export const devicesRouter = Router();

const CreateDevice = z.object({
  propertyId: z.string().uuid(),
  hostname: z.string().min(1),
  ipAddress: z.string().ip(),
  serialNumber: z.string().min(3),
  status: z.enum(["active", "inactive", "maintenance", "decommissioned", "failed"])
});

devicesRouter.get("/", requireAuth, async (_req, res) => {
  const result = await pool.query(
    "SELECT device_id, property_id, hostname, ip_address, serial_number, status FROM mgm.devices ORDER BY hostname"
  );
  res.json(result.rows);
});

devicesRouter.post(
  "/",
  requireAuth,
  requireRoles(["admin", "sdm", "engineer", "manager"]),
  audit("device.create"),
  async (req, res) => {
    const parsed = CreateDevice.safeParse(req.body);
    if (!parsed.success) {
      res.status(400).json({ message: "Invalid request" });
      return;
    }
    const result = await pool.query(
      `INSERT INTO mgm.devices (property_id, hostname, ip_address, serial_number, status)
       VALUES ($1, $2, $3, $4, $5)
       RETURNING device_id, property_id, hostname, ip_address, serial_number, status`,
      [
        parsed.data.propertyId,
        parsed.data.hostname,
        parsed.data.ipAddress,
        parsed.data.serialNumber,
        parsed.data.status
      ]
    );
    res.status(201).json(result.rows[0]);
  }
);
