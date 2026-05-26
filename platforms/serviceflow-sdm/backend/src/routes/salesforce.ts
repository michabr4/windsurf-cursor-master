import { Router } from "express";
import { requireAuth, requireRoles } from "../middleware/auth.js";
import { SalesforceClient } from "../integrations/salesforceClient.js";
import { CreateCaseSchema, PatchCaseSchema, SF_ID_PATTERN } from "../schemas/salesforce.js";

export const salesforceRouter = Router();

const SF_ROLES = ["admin", "sdm", "tam", "csm", "engineer", "manager", "viewer"] as const;
const SF_WRITE_ROLES = ["admin", "sdm", "tam", "csm", "manager"] as const;

salesforceRouter.get("/status", requireAuth, async (_req, res) => {
  try {
    const result = await SalesforceClient.testConnection();
    res.json(result);
  } catch {
    res.status(502).json({ ok: false, message: "Salesforce status check failed" });
  }
});

salesforceRouter.get("/cases", requireAuth, requireRoles([...SF_ROLES]), async (req, res) => {
  if (!SalesforceClient.isConfigured()) {
    res.json({ configured: false, message: "Salesforce not configured", records: [] });
    return;
  }
  try {
    const limit = Math.min(Number(req.query.limit) || 100, 500);
    const result = await SalesforceClient.getCases(limit);
    res.json({ configured: true, totalSize: result.totalSize, records: result.records });
  } catch (e) {
    res.status(502).json({ message: e instanceof Error ? e.message : "Salesforce API error" });
  }
});

salesforceRouter.get("/accounts", requireAuth, requireRoles([...SF_ROLES]), async (req, res) => {
  if (!SalesforceClient.isConfigured()) {
    res.json({ configured: false, message: "Salesforce not configured", records: [] });
    return;
  }
  try {
    const limit = Math.min(Number(req.query.limit) || 100, 500);
    const result = await SalesforceClient.getAccounts(limit);
    res.json({ configured: true, totalSize: result.totalSize, records: result.records });
  } catch (e) {
    res.status(502).json({ message: e instanceof Error ? e.message : "Salesforce API error" });
  }
});

salesforceRouter.get("/contacts", requireAuth, requireRoles([...SF_ROLES]), async (req, res) => {
  if (!SalesforceClient.isConfigured()) {
    res.json({ configured: false, message: "Salesforce not configured", records: [] });
    return;
  }
  try {
    const limit = Math.min(Number(req.query.limit) || 100, 500);
    const accountId = typeof req.query.accountId === "string" ? req.query.accountId : undefined;
    const result = await SalesforceClient.getContacts(accountId, limit);
    res.json({ configured: true, totalSize: result.totalSize, records: result.records });
  } catch (e) {
    res.status(502).json({ message: e instanceof Error ? e.message : "Salesforce API error" });
  }
});

salesforceRouter.get("/opportunities", requireAuth, requireRoles([...SF_ROLES]), async (req, res) => {
  if (!SalesforceClient.isConfigured()) {
    res.json({ configured: false, message: "Salesforce not configured", records: [] });
    return;
  }
  try {
    const limit = Math.min(Number(req.query.limit) || 100, 500);
    const result = await SalesforceClient.getOpportunities(limit);
    res.json({ configured: true, totalSize: result.totalSize, records: result.records });
  } catch (e) {
    res.status(502).json({ message: e instanceof Error ? e.message : "Salesforce API error" });
  }
});

salesforceRouter.get("/entitlements", requireAuth, requireRoles([...SF_ROLES]), async (req, res) => {
  if (!SalesforceClient.isConfigured()) {
    res.json({ configured: false, message: "Salesforce not configured", records: [] });
    return;
  }
  try {
    const limit = Math.min(Number(req.query.limit) || 100, 500);
    const result = await SalesforceClient.getEntitlements(limit);
    res.json({ configured: true, totalSize: result.totalSize, records: result.records });
  } catch (e) {
    res.status(502).json({ message: e instanceof Error ? e.message : "Salesforce API error" });
  }
});

salesforceRouter.get("/service-contracts", requireAuth, requireRoles([...SF_ROLES]), async (req, res) => {
  if (!SalesforceClient.isConfigured()) {
    res.json({ configured: false, message: "Salesforce not configured", records: [] });
    return;
  }
  try {
    const limit = Math.min(Number(req.query.limit) || 100, 500);
    const result = await SalesforceClient.getServiceContracts(limit);
    res.json({ configured: true, totalSize: result.totalSize, records: result.records });
  } catch (e) {
    res.status(502).json({ message: e instanceof Error ? e.message : "Salesforce API error" });
  }
});

salesforceRouter.get("/tasks", requireAuth, requireRoles([...SF_ROLES]), async (req, res) => {
  if (!SalesforceClient.isConfigured()) {
    res.json({ configured: false, message: "Salesforce not configured", records: [] });
    return;
  }
  try {
    const limit = Math.min(Number(req.query.limit) || 100, 500);
    const result = await SalesforceClient.getTasks(limit);
    res.json({ configured: true, totalSize: result.totalSize, records: result.records });
  } catch (e) {
    res.status(502).json({ message: e instanceof Error ? e.message : "Salesforce API error" });
  }
});

salesforceRouter.get("/knowledge", requireAuth, requireRoles([...SF_ROLES]), async (req, res) => {
  if (!SalesforceClient.isConfigured()) {
    res.json({ configured: false, message: "Salesforce not configured", records: [] });
    return;
  }
  try {
    const limit = Math.min(Number(req.query.limit) || 50, 200);
    const result = await SalesforceClient.getKnowledgeArticles(limit);
    res.json({ configured: true, totalSize: result.totalSize, records: result.records });
  } catch (e) {
    res.status(502).json({ message: e instanceof Error ? e.message : "Salesforce API error" });
  }
});

salesforceRouter.get("/console-summary", requireAuth, requireRoles([...SF_ROLES]), async (_req, res) => {
  if (!SalesforceClient.isConfigured()) {
    res.json({ configured: false, message: "Salesforce not configured" });
    return;
  }
  try {
    const [cases, accounts, opps, entitlements, tasks] = await Promise.all([
      SalesforceClient.getCases(50),
      SalesforceClient.getAccounts(50),
      SalesforceClient.getOpportunities(50),
      SalesforceClient.getEntitlements(50),
      SalesforceClient.getTasks(50)
    ]);

    const openCases = cases.records.filter((c) => c.Status !== "Closed");
    const highPriCases = openCases.filter((c) => c.Priority === "High" || c.Priority === "Critical");
    const closedWon = opps.records.filter((o) => o.StageName === "Closed Won");
    const pipeline = opps.records.filter((o) => o.StageName !== "Closed Won" && o.StageName !== "Closed Lost");
    const pipelineValue = pipeline.reduce((sum, o) => sum + (Number(o.Amount) || 0), 0);
    const activeEntitlements = entitlements.records.filter((e) => e.Status === "Active");
    const expiringEntitlements = entitlements.records.filter((e) => {
      if (!e.EndDate) return false;
      const end = new Date(String(e.EndDate));
      const now = new Date();
      const daysLeft = (end.getTime() - now.getTime()) / (1000 * 60 * 60 * 24);
      return daysLeft >= 0 && daysLeft <= 90;
    });

    res.json({
      configured: true,
      pm: {
        totalAccounts: accounts.totalSize,
        activeOpportunities: pipeline.length,
        pipelineValue,
        closedWonCount: closedWon.length,
        openTasks: tasks.totalSize
      },
      delivery: {
        openCases: openCases.length,
        highPriorityCases: highPriCases.length,
        totalCases: cases.totalSize
      },
      success: {
        totalAccounts: accounts.totalSize,
        activeEntitlements: activeEntitlements.length,
        openTasks: tasks.totalSize
      },
      renewals: {
        totalEntitlements: entitlements.totalSize,
        activeEntitlements: activeEntitlements.length,
        expiringIn90Days: expiringEntitlements.length,
        pipelineValue,
        pipelineCount: pipeline.length
      },
      architect: {
        totalAccounts: accounts.totalSize,
        totalCases: cases.totalSize
      }
    });
  } catch (e) {
    res.status(502).json({ message: e instanceof Error ? e.message : "Salesforce API error" });
  }
});

salesforceRouter.post("/cases", requireAuth, requireRoles([...SF_WRITE_ROLES]), async (req, res) => {
  if (!SalesforceClient.isConfigured()) {
    res.status(503).json({ message: "Salesforce not configured" });
    return;
  }
  const parsed = CreateCaseSchema.safeParse(req.body ?? {});
  if (!parsed.success) {
    res.status(400).json({ message: "Invalid request", issues: parsed.error.issues });
    return;
  }
  try {
    const { subject, description, priority, accountId, contactId } = parsed.data;
    const result = await SalesforceClient.createRecord("Case", {
      Subject: subject,
      Description: description ?? "",
      Priority: priority || "Medium",
      AccountId: accountId || null,
      ContactId: contactId || null,
      Origin: "Helix"
    });
    res.status(201).json(result);
  } catch (e) {
    res.status(502).json({ message: e instanceof Error ? e.message : "Salesforce API error" });
  }
});

salesforceRouter.patch("/cases/:caseId", requireAuth, requireRoles([...SF_WRITE_ROLES]), async (req, res) => {
  if (!SalesforceClient.isConfigured()) {
    res.status(503).json({ message: "Salesforce not configured" });
    return;
  }
  const { caseId } = req.params;
  if (!SF_ID_PATTERN.test(caseId)) {
    res.status(400).json({ message: "Invalid caseId format" });
    return;
  }
  const parsed = PatchCaseSchema.safeParse(req.body ?? {});
  if (!parsed.success) {
    res.status(400).json({ message: "Invalid request", issues: parsed.error.issues });
    return;
  }
  try {
    await SalesforceClient.updateRecord("Case", caseId, parsed.data);
    res.json({ id: caseId, updated: true });
  } catch (e) {
    res.status(502).json({ message: e instanceof Error ? e.message : "Salesforce API error" });
  }
});
