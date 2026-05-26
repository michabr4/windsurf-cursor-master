import { Router } from "express";
import { env } from "../config.js";
import { WebexClient } from "../integrations/webexClient.js";
import { SalesforceClient } from "../integrations/salesforceClient.js";
import { requireAuth, requireRoles } from "../middleware/auth.js";
import { runDnaSync, runSmartLicensingSync, runTacSync } from "../jobs/syncService.js";
import { SyncSourceParamSchema, WarRoomBodySchema } from "../schemas/integrations.js";

export const integrationsRouter = Router();

const WAR_ROOM_ROLES = ["admin", "sdm", "tam", "manager", "engineer"] as const;

integrationsRouter.post(
  "/webex/war-room",
  requireAuth,
  requireRoles([...WAR_ROOM_ROLES]),
  async (req, res) => {
    const parsed = WarRoomBodySchema.safeParse(req.body ?? {});
    if (!parsed.success) {
      res.status(400).json({ message: "Invalid request", issues: parsed.error.issues });
      return;
    }

    const token = env.WEBEX_BOT_TOKEN.trim();
    if (!token) {
      res.status(503).json({
        message:
          "Webex is not configured: set WEBEX_BOT_TOKEN in the server environment (bot must allow creating spaces)."
      });
      return;
    }
    try {
      const raw = parsed.data.title?.trim() ?? "";
      const title =
        raw ||
        `Helix war room · ${new Date().toISOString().replace(/\.\d{3}Z$/, "Z")}`;
      const client = new WebexClient(token);
      const result = await client.createRoom(title);
      if (!result.ok) {
        const status = result.status >= 400 && result.status < 600 ? result.status : 502;
        res.status(status).json({ message: result.message });
        return;
      }
      const webUrl = `https://teams.webex.com/l/spaces/${result.id}`;
      res.status(201).json({
        roomId: result.id,
        title: result.title,
        webUrl
      });
    } catch {
      res.status(502).json({ message: "Webex API request failed" });
    }
  }
);

integrationsRouter.post(
  "/sync/:source",
  requireAuth,
  requireRoles(["admin", "sdm", "tam", "manager"]),
  async (req, res) => {
    const sourceParsed = SyncSourceParamSchema.safeParse(req.params.source);
    if (!sourceParsed.success) {
      res.status(400).json({ message: "Unsupported source" });
      return;
    }
    const source = sourceParsed.data;
    try {
      if (source === "dna-center") {
        const count = await runDnaSync();
        res.json({ source, processed: count });
        return;
      }
      if (source === "tac") {
        const count = await runTacSync();
        res.json({ source, processed: count });
        return;
      }
      if (source === "smart-licensing") {
        const count = await runSmartLicensingSync();
        res.json({ source, processed: count });
        return;
      }
      if (source === "salesforce") {
        const result = await SalesforceClient.testConnection();
        res.json({ source, processed: 0, status: result.ok ? "connected" : "error", message: result.message });
        return;
      }
    } catch {
      res.status(502).json({ message: `Sync failed for source: ${source}` });
    }
  }
);
