import type { Request, Response } from "express";
import { Router } from "express";
import { env } from "../config.js";
import { createMimirClient } from "../integrations/mimirClient.js";
import { requireAuth, requireRoles } from "../middleware/auth.js";
import { MimirCompanyQuerySchema } from "../schemas/mimir.js";
import {
  getLatestMimirFn,
  getLatestMimirInventory,
  getLatestMimirPsirt,
  getLatestMimirQbr
} from "../jobs/mimirSnapshotStore.js";

export const mimirRouter = Router();

const MIMIR_ROLES = ["admin", "sdm", "tam", "csm", "engineer", "manager", "viewer"] as const;

const mimirClient = createMimirClient(env);

export function isMimirConfigured(): boolean {
  return Boolean(env.MIMIR_CLIENT_ID.trim() && env.MIMIR_CLIENT_SECRET.trim());
}

function resolveCompanyId(req: Request): string | null {
  const parsed = MimirCompanyQuerySchema.safeParse(req.query);
  const fromQuery = parsed.success && parsed.data.companyId ? parsed.data.companyId : "";
  const id = fromQuery || env.MIMIR_COMPANY_ID.trim();
  return id || null;
}

function unconfigured(res: Response): void {
  res.json({
    configured: false,
    message: "Mimir not configured: set MIMIR_CLIENT_ID and MIMIR_CLIENT_SECRET",
    data: null
  });
}

function missingCompany(res: Response): void {
  res.status(400).json({
    message: "companyId required (query param or MIMIR_COMPANY_ID env)"
  });
}

mimirRouter.get("/status", requireAuth, requireRoles([...MIMIR_ROLES]), async (_req, res) => {
  if (!isMimirConfigured()) {
    res.json({ configured: false, ok: false, message: "Mimir credentials not set" });
    return;
  }
  const companyId = env.MIMIR_COMPANY_ID.trim();
  if (!companyId) {
    res.json({
      configured: true,
      ok: true,
      message: "Credentials set; set MIMIR_COMPANY_ID or pass ?companyId= for live probe"
    });
    return;
  }
  const summary = await mimirClient.getPsirtSummary(companyId);
  res.json({
    configured: true,
    ok: summary !== null,
    companyId,
    message: summary !== null ? "Mimir API reachable" : "Mimir API returned no data (check companyId or network)"
  });
});

mimirRouter.get("/devices", requireAuth, requireRoles([...MIMIR_ROLES]), async (req, res) => {
  if (!isMimirConfigured()) {
    unconfigured(res);
    return;
  }
  const companyId = resolveCompanyId(req);
  if (!companyId) {
    missingCompany(res);
    return;
  }
  const devices = await mimirClient.getNpDevices(companyId);
  res.json({ configured: true, companyId, data: devices });
});

mimirRouter.get("/psirt-summary", requireAuth, requireRoles([...MIMIR_ROLES]), async (req, res) => {
  if (!isMimirConfigured()) {
    unconfigured(res);
    return;
  }
  const companyId = resolveCompanyId(req);
  if (!companyId) {
    missingCompany(res);
    return;
  }
  const data = await mimirClient.getPsirtSummary(companyId);
  res.json({ configured: true, companyId, data });
});

mimirRouter.get("/psirt-details", requireAuth, requireRoles([...MIMIR_ROLES]), async (req, res) => {
  if (!isMimirConfigured()) {
    unconfigured(res);
    return;
  }
  const companyId = resolveCompanyId(req);
  if (!companyId) {
    missingCompany(res);
    return;
  }
  const data = await mimirClient.getPsirtDetails(companyId);
  res.json({ configured: true, companyId, data });
});

mimirRouter.get("/fn-summary", requireAuth, requireRoles([...MIMIR_ROLES]), async (req, res) => {
  if (!isMimirConfigured()) {
    unconfigured(res);
    return;
  }
  const companyId = resolveCompanyId(req);
  if (!companyId) {
    missingCompany(res);
    return;
  }
  const data = await mimirClient.getFnSummary(companyId);
  res.json({ configured: true, companyId, data });
});

mimirRouter.get("/fn-details", requireAuth, requireRoles([...MIMIR_ROLES]), async (req, res) => {
  if (!isMimirConfigured()) {
    unconfigured(res);
    return;
  }
  const companyId = resolveCompanyId(req);
  if (!companyId) {
    missingCompany(res);
    return;
  }
  const data = await mimirClient.getFnDetails(companyId);
  res.json({ configured: true, companyId, data });
});

mimirRouter.get("/compliance-bp", requireAuth, requireRoles([...MIMIR_ROLES]), async (req, res) => {
  if (!isMimirConfigured()) {
    unconfigured(res);
    return;
  }
  const companyId = resolveCompanyId(req);
  if (!companyId) {
    missingCompany(res);
    return;
  }
  const data = await mimirClient.getBpSummary(companyId);
  res.json({ configured: true, companyId, data });
});

mimirRouter.get("/qbr", requireAuth, requireRoles([...MIMIR_ROLES]), async (req, res) => {
  if (!isMimirConfigured()) {
    unconfigured(res);
    return;
  }
  const companyId = resolveCompanyId(req);
  if (!companyId) {
    missingCompany(res);
    return;
  }
  const data = await mimirClient.getQbrComposite(companyId);
  res.json({ configured: true, companyId, data });
});

mimirRouter.get("/peer-comparison", requireAuth, requireRoles([...MIMIR_ROLES]), async (req, res) => {
  if (!isMimirConfigured()) {
    unconfigured(res);
    return;
  }
  const companyId = resolveCompanyId(req);
  if (!companyId) {
    missingCompany(res);
    return;
  }
  const data = await mimirClient.getBcibmPeerComparison(companyId);
  res.json({ configured: true, companyId, data });
});

mimirRouter.get("/snapshots/devices", requireAuth, requireRoles([...MIMIR_ROLES]), async (req, res) => {
  const companyId = resolveCompanyId(req);
  if (!companyId) {
    missingCompany(res);
    return;
  }
  try {
    const snapshot = await getLatestMimirInventory(companyId);
    res.json({ companyId, source: "snapshot", ...snapshot });
  } catch {
    res.status(500).json({ message: "Failed to load Mimir device snapshots" });
  }
});

mimirRouter.get("/snapshots/psirt-summary", requireAuth, requireRoles([...MIMIR_ROLES]), async (req, res) => {
  const companyId = resolveCompanyId(req);
  if (!companyId) {
    missingCompany(res);
    return;
  }
  try {
    const data = await getLatestMimirPsirt(companyId);
    res.json({ companyId, source: "snapshot", data });
  } catch {
    res.status(500).json({ message: "Failed to load Mimir PSIRT snapshot" });
  }
});

mimirRouter.get("/snapshots/fn-summary", requireAuth, requireRoles([...MIMIR_ROLES]), async (req, res) => {
  const companyId = resolveCompanyId(req);
  if (!companyId) {
    missingCompany(res);
    return;
  }
  try {
    const data = await getLatestMimirFn(companyId);
    res.json({ companyId, source: "snapshot", data });
  } catch {
    res.status(500).json({ message: "Failed to load Mimir FN snapshot" });
  }
});

mimirRouter.get("/snapshots/qbr", requireAuth, requireRoles([...MIMIR_ROLES]), async (req, res) => {
  const companyId = resolveCompanyId(req);
  if (!companyId) {
    missingCompany(res);
    return;
  }
  try {
    const data = await getLatestMimirQbr(companyId);
    res.json({ companyId, source: "snapshot", data });
  } catch {
    res.status(500).json({ message: "Failed to load Mimir QBR snapshot" });
  }
});

mimirRouter.get("/risk-summary", requireAuth, requireRoles([...MIMIR_ROLES]), async (req, res) => {
  if (!isMimirConfigured()) {
    unconfigured(res);
    return;
  }
  const companyId = resolveCompanyId(req);
  if (!companyId) {
    missingCompany(res);
    return;
  }
  const data = await mimirClient.getRiskMitigationSummary(companyId);
  res.json({ configured: true, companyId, data });
});
