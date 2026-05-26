import { Request, Router } from 'express';
import jwt from 'jsonwebtoken';
import { authenticate, authorize, issueAccessToken, issueRefreshToken, tryLogin } from './auth';
import { config } from './config';
import { queueManager } from './queues';
import { store } from './store';
import {
  deviceSchema,
  incidentCreateSchema,
  incidentPatchSchema,
  incidentTacLinkSchema,
  incidentUpdateSchema,
  loginSchema,
  propertySchema,
  refreshSchema,
} from './validation';

const mutatingRoles = ['admin', 'sdm', 'tam', 'engineer', 'manager'] as const;
type RequestCtx = Request & {
  requestId?: string;
  auth?: {
    userId: string;
    role: string;
    email: string;
  };
};

function parseOrThrow<T>(schema: { parse: (data: unknown) => T }, data: unknown): T {
  return schema.parse(data);
}

function audit(req: Request, actionType: 'create' | 'read' | 'update' | 'delete' | 'login' | 'logout' | 'access', action: string, entityType?: string, entityId?: string, success = true, detail?: string): void {
  const r = req as RequestCtx;
  void store.appendAudit({
    actionType,
    action,
    entityType,
    entityId,
    userId: r.auth?.userId,
    requestId: r.requestId ?? 'unknown',
    success,
    detail,
  });
}

export function buildRouter(): Router {
  const router = Router();

  router.get('/health', (req: Request, res) => {
    const r = req as RequestCtx;
    res.json({
      status: 'ok',
      service: 'serviceflow-sdm-backend',
      time: new Date().toISOString(),
      requestId: r.requestId,
      storageMode: config.STORAGE_MODE,
      queueEnabled: queueManager.isEnabled(),
    });
  });

  router.get('/runtime/status', authenticate, async (_req: Request, res) => {
    const [properties, devices, incidents, tacCases] = await Promise.all([
      store.listProperties(),
      store.listDevices(),
      store.listIncidents(),
      store.listTacCases(),
    ]);
    res.json({
      storageMode: config.STORAGE_MODE,
      queueEnabled: queueManager.isEnabled(),
      counts: {
        properties: properties.length,
        devices: devices.length,
        incidents: incidents.length,
        tacCases: tacCases.length,
      },
    });
  });

  router.post('/auth/login', async (req: Request, res) => {
    const input = parseOrThrow(loginSchema, req.body);
    const payload = await tryLogin(input.email, input.password);
    if (!payload) {
      audit(req, 'login', 'auth.login', 'user', undefined, false, 'Invalid credentials');
      res.status(401).json({ error: 'Invalid username or password' });
      return;
    }

    audit(req, 'login', 'auth.login', 'user', payload.userId, true);
    res.json({
      accessToken: issueAccessToken(payload),
      refreshToken: issueRefreshToken(payload),
      user: payload,
    });
  });

  router.post('/auth/refresh', (req: Request, res) => {
    const input = parseOrThrow(refreshSchema, req.body);
    try {
      const decoded = jwt.verify(input.refreshToken, config.JWT_REFRESH_SECRET) as {
        userId: string;
        role: 'admin' | 'sdm' | 'tam' | 'csm' | 'engineer' | 'manager' | 'viewer';
        email: string;
      };
      res.json({ accessToken: issueAccessToken(decoded) });
    } catch {
      res.status(401).json({ error: 'Invalid refresh token' });
    }
  });

  router.post('/auth/logout', authenticate, (req: Request, res) => {
    const r = req as RequestCtx;
    audit(req, 'logout', 'auth.logout', 'user', r.auth?.userId, true);
    res.status(204).send();
  });

  router.get('/properties', authenticate, async (req: Request, res) => {
    audit(req, 'read', 'properties.list', 'property');
    res.json({ data: await store.listProperties() });
  });

  router.post('/properties', authenticate, authorize([...mutatingRoles]), async (req: Request, res) => {
    const input = parseOrThrow(propertySchema, req.body);
    const property = await store.createProperty(input);
    audit(req, 'create', 'properties.create', 'property', property.propertyId);
    res.status(201).json({ data: property });
  });

  router.get('/devices', authenticate, async (req: Request, res) => {
    audit(req, 'read', 'devices.list', 'device');
    res.json({ data: await store.listDevices() });
  });

  router.post('/devices', authenticate, authorize([...mutatingRoles]), async (req: Request, res) => {
    const input = parseOrThrow(deviceSchema, req.body);
    const exists = (await store.listProperties()).some((p) => p.propertyId === input.propertyId);
    if (!exists) {
      res.status(400).json({ error: 'propertyId does not exist' });
      return;
    }
    const device = await store.createDevice(input);
    audit(req, 'create', 'devices.create', 'device', device.deviceId);
    res.status(201).json({ data: device });
  });

  router.get('/incidents', authenticate, async (req: Request, res) => {
    audit(req, 'read', 'incidents.list', 'incident');
    res.json({ data: await store.listIncidents() });
  });

  router.post('/incidents', authenticate, authorize([...mutatingRoles]), async (req: Request, res) => {
    const r = req as RequestCtx;
    const input = parseOrThrow(incidentCreateSchema, req.body);
    const incident = await store.createIncident(r.auth!.userId, input);
    audit(req, 'create', 'incidents.create', 'incident', incident.incidentId);
    await queueManager.enqueueIncidentCreated({
      incidentId: incident.incidentId,
      incidentNumber: incident.incidentNumber,
      priority: incident.priority,
    });
    res.status(201).json({ data: incident });
  });

  router.patch('/incidents/:incidentId', authenticate, authorize([...mutatingRoles]), async (req: Request, res) => {
    const input = parseOrThrow(incidentPatchSchema, req.body);
    const incident = await store.patchIncident(req.params.incidentId, input);
    if (!incident) {
      res.status(404).json({ error: 'Incident not found' });
      return;
    }
    audit(req, 'update', 'incidents.patch', 'incident', incident.incidentId);
    res.json({ data: incident });
  });

  router.post('/incidents/:incidentId/updates', authenticate, authorize([...mutatingRoles]), async (req: Request, res) => {
    const r = req as RequestCtx;
    const input = parseOrThrow(incidentUpdateSchema, req.body);
    const update = await store.addIncidentUpdate(req.params.incidentId, r.auth!.userId, input.content);
    if (!update) {
      res.status(404).json({ error: 'Incident not found' });
      return;
    }
    audit(req, 'update', 'incidents.add_update', 'incident', update.incidentId);
    res.status(201).json({ data: update });
  });

  router.post('/incidents/:incidentId/tac-link', authenticate, authorize([...mutatingRoles]), async (req: Request, res) => {
    const input = parseOrThrow(incidentTacLinkSchema, req.body);
    const linkResult = await store.linkTac(req.params.incidentId, input);
    if (!linkResult) {
      res.status(404).json({ error: 'Incident not found' });
      return;
    }
    audit(req, 'update', 'incidents.tac_link', 'incident', linkResult.incident.incidentId);
    await queueManager.enqueueTacLink({
      incidentId: linkResult.incident.incidentId,
      tacCaseNumber: linkResult.tacCase.caseNumber,
    });
    res.json({ data: linkResult });
  });

  router.get('/tac-cases', authenticate, async (req: Request, res) => {
    audit(req, 'read', 'tac_cases.list', 'tac_case');
    res.json({ data: await store.listTacCases() });
  });

  return router;
}

