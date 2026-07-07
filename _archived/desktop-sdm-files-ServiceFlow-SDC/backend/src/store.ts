import bcrypt from 'bcryptjs';
import { Pool } from 'pg';
import { v4 as uuidv4 } from 'uuid';
import { config } from './config';
import { AuditEvent, Device, Incident, IncidentUpdate, Property, TacCase, User } from './types';

type AuditInput = Omit<AuditEvent, 'eventId' | 'createdAt'>;
type CreatePropertyInput = Omit<Property, 'propertyId' | 'createdAt'>;
type CreateDeviceInput = Omit<Device, 'deviceId' | 'createdAt'>;
type CreateIncidentInput = Omit<
  Incident,
  'incidentId' | 'incidentNumber' | 'status' | 'createdAt' | 'updatedAt' | 'reportedBy'
>;
type PatchIncidentInput = Pick<Incident, 'status' | 'assignedTo' | 'priority'>;
type LinkTacInput = { tacCaseNumber: string; tacSeverity?: string };

export interface DataStore {
  init(): Promise<void>;
  findUserByEmail(email: string): Promise<User | null>;
  appendAudit(event: AuditInput): Promise<AuditEvent>;
  listProperties(): Promise<Property[]>;
  createProperty(input: CreatePropertyInput): Promise<Property>;
  listDevices(): Promise<Device[]>;
  createDevice(input: CreateDeviceInput): Promise<Device>;
  listIncidents(): Promise<Incident[]>;
  createIncident(reportedBy: string, input: CreateIncidentInput): Promise<Incident>;
  patchIncident(incidentId: string, input: Partial<PatchIncidentInput>): Promise<Incident | null>;
  addIncidentUpdate(incidentId: string, userId: string, content: string): Promise<IncidentUpdate | null>;
  linkTac(incidentId: string, input: LinkTacInput): Promise<{ incident: Incident; tacCase: TacCase } | null>;
  listTacCases(): Promise<TacCase[]>;
}

const now = (): string => new Date().toISOString();

class InMemoryStore implements DataStore {
  users: User[] = [];
  properties: Property[] = [];
  devices: Device[] = [];
  incidents: Incident[] = [];
  incidentUpdates: IncidentUpdate[] = [];
  tacCases: TacCase[] = [];
  auditEvents: AuditEvent[] = [];
  private incidentSequence = 0;

  async init(): Promise<void> {
    if (this.users.length > 0) return;
    const hash = bcrypt.hashSync(config.BOOTSTRAP_ADMIN_PASSWORD, 12);
    this.users.push({
      userId: uuidv4(),
      email: config.BOOTSTRAP_ADMIN_EMAIL,
      role: 'admin',
      passwordHash: hash,
      isActive: true,
    });
  }

  async findUserByEmail(email: string): Promise<User | null> {
    const user = this.users.find((u) => u.email.toLowerCase() === email.toLowerCase() && u.isActive);
    return user ?? null;
  }

  async appendAudit(event: AuditInput): Promise<AuditEvent> {
    const fullEvent: AuditEvent = { eventId: uuidv4(), createdAt: now(), ...event };
    this.auditEvents.push(fullEvent);
    return fullEvent;
  }

  async listProperties(): Promise<Property[]> {
    return this.properties;
  }

  async createProperty(input: CreatePropertyInput): Promise<Property> {
    const property: Property = { propertyId: uuidv4(), createdAt: now(), ...input };
    this.properties.push(property);
    return property;
  }

  async listDevices(): Promise<Device[]> {
    return this.devices;
  }

  async createDevice(input: CreateDeviceInput): Promise<Device> {
    const device: Device = { deviceId: uuidv4(), createdAt: now(), ...input };
    this.devices.push(device);
    return device;
  }

  async listIncidents(): Promise<Incident[]> {
    return this.incidents;
  }

  async createIncident(reportedBy: string, input: CreateIncidentInput): Promise<Incident> {
    this.incidentSequence += 1;
    const incident: Incident = {
      incidentId: uuidv4(),
      incidentNumber: `INC-${String(this.incidentSequence).padStart(6, '0')}`,
      status: 'open',
      reportedBy,
      createdAt: now(),
      updatedAt: now(),
      ...input,
    };
    this.incidents.push(incident);
    return incident;
  }

  async patchIncident(incidentId: string, input: Partial<PatchIncidentInput>): Promise<Incident | null> {
    const incident = this.incidents.find((i) => i.incidentId === incidentId);
    if (!incident) return null;
    Object.assign(incident, input, { updatedAt: now() });
    return incident;
  }

  async addIncidentUpdate(
    incidentId: string,
    userId: string,
    content: string,
  ): Promise<IncidentUpdate | null> {
    const incident = this.incidents.find((i) => i.incidentId === incidentId);
    if (!incident) return null;
    const update: IncidentUpdate = { updateId: uuidv4(), incidentId, userId, content, createdAt: now() };
    this.incidentUpdates.push(update);
    incident.updatedAt = now();
    return update;
  }

  async linkTac(
    incidentId: string,
    input: LinkTacInput,
  ): Promise<{ incident: Incident; tacCase: TacCase } | null> {
    const incident = this.incidents.find((i) => i.incidentId === incidentId);
    if (!incident) return null;

    incident.tacCaseNumber = input.tacCaseNumber;
    incident.tacSeverity = input.tacSeverity;
    incident.updatedAt = now();

    const existingTac = this.tacCases.find((t) => t.caseNumber === input.tacCaseNumber);
    let tacCase: TacCase;
    if (existingTac) {
      tacCase = existingTac;
      tacCase.incidentId = incident.incidentId;
    } else {
      tacCase = {
        tacCaseId: uuidv4(),
        caseNumber: input.tacCaseNumber,
        incidentId: incident.incidentId,
        severity: (input.tacSeverity ?? '3') as TacCase['severity'],
        title: `Linked from ${incident.incidentNumber}`,
        status: 'open',
        createdAt: now(),
      };
      this.tacCases.push(tacCase);
    }

    return { incident, tacCase };
  }

  async listTacCases(): Promise<TacCase[]> {
    return this.tacCases;
  }
}

class PostgresStore implements DataStore {
  private readonly pool: Pool;

  constructor(databaseUrl: string) {
    this.pool = new Pool({ connectionString: databaseUrl });
  }

  async init(): Promise<void> {
    const migrationCheck = await this.pool.query(
      `SELECT to_regclass('public.schema_migrations') AS migration_table`,
    );
    if (!migrationCheck.rows[0]?.migration_table) {
      throw new Error(
        'Postgres schema not initialized. Run: npm run db:migrate',
      );
    }

    const existing = await this.pool.query(`SELECT user_id FROM users WHERE email = $1`, [
      config.BOOTSTRAP_ADMIN_EMAIL,
    ]);
    if (existing.rowCount === 0) {
      await this.pool.query(
        `INSERT INTO users (user_id, email, role, password_hash, is_active)
         VALUES ($1, $2, 'admin', $3, TRUE)`,
        [uuidv4(), config.BOOTSTRAP_ADMIN_EMAIL, bcrypt.hashSync(config.BOOTSTRAP_ADMIN_PASSWORD, 12)],
      );
    }
  }

  async findUserByEmail(email: string): Promise<User | null> {
    const result = await this.pool.query(
      `SELECT user_id, email, role, password_hash, is_active
       FROM users WHERE LOWER(email)=LOWER($1) LIMIT 1`,
      [email],
    );
    if (result.rowCount === 0) return null;
    const row = result.rows[0];
    return {
      userId: row.user_id,
      email: row.email,
      role: row.role,
      passwordHash: row.password_hash,
      isActive: row.is_active,
    };
  }

  async appendAudit(event: AuditInput): Promise<AuditEvent> {
    const entry: AuditEvent = { eventId: uuidv4(), createdAt: now(), ...event };
    await this.pool.query(
      `INSERT INTO audit_events
      (event_id, action_type, action, entity_type, entity_id, user_id, request_id, success, detail, created_at)
      VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)`,
      [
        entry.eventId,
        entry.actionType,
        entry.action,
        entry.entityType ?? null,
        entry.entityId ?? null,
        entry.userId ?? null,
        entry.requestId,
        entry.success,
        entry.detail ?? null,
        entry.createdAt,
      ],
    );
    return entry;
  }

  async listProperties(): Promise<Property[]> {
    const result = await this.pool.query(`SELECT * FROM properties ORDER BY created_at DESC`);
    return result.rows.map((r) => ({
      propertyId: r.property_id,
      propertyCode: r.property_code,
      propertyName: r.property_name,
      city: r.city ?? undefined,
      state: r.state ?? undefined,
      createdAt: r.created_at.toISOString(),
    }));
  }

  async createProperty(input: CreatePropertyInput): Promise<Property> {
    const propertyId = uuidv4();
    const createdAt = now();
    await this.pool.query(
      `INSERT INTO properties (property_id, property_code, property_name, city, state, created_at)
      VALUES ($1,$2,$3,$4,$5,$6)`,
      [propertyId, input.propertyCode, input.propertyName, input.city ?? null, input.state ?? null, createdAt],
    );
    return { propertyId, createdAt, ...input };
  }

  async listDevices(): Promise<Device[]> {
    const result = await this.pool.query(`SELECT * FROM devices ORDER BY created_at DESC`);
    return result.rows.map((r) => ({
      deviceId: r.device_id,
      propertyId: r.property_id,
      hostname: r.hostname,
      serialNumber: r.serial_number ?? undefined,
      model: r.model ?? undefined,
      status: r.status,
      createdAt: r.created_at.toISOString(),
    }));
  }

  async createDevice(input: CreateDeviceInput): Promise<Device> {
    const deviceId = uuidv4();
    const createdAt = now();
    await this.pool.query(
      `INSERT INTO devices (device_id, property_id, hostname, serial_number, model, status, created_at)
      VALUES ($1,$2,$3,$4,$5,$6,$7)`,
      [
        deviceId,
        input.propertyId,
        input.hostname,
        input.serialNumber ?? null,
        input.model ?? null,
        input.status,
        createdAt,
      ],
    );
    return { deviceId, createdAt, ...input };
  }

  async listIncidents(): Promise<Incident[]> {
    const result = await this.pool.query(`SELECT * FROM incidents ORDER BY created_at DESC`);
    return result.rows.map((r) => ({
      incidentId: r.incident_id,
      incidentNumber: r.incident_number,
      propertyId: r.property_id ?? undefined,
      deviceId: r.device_id ?? undefined,
      title: r.title,
      description: r.description ?? undefined,
      priority: r.priority,
      status: r.status,
      reportedBy: r.reported_by,
      assignedTo: r.assigned_to ?? undefined,
      tacCaseNumber: r.tac_case_number ?? undefined,
      tacSeverity: r.tac_severity ?? undefined,
      createdAt: r.created_at.toISOString(),
      updatedAt: r.updated_at.toISOString(),
    }));
  }

  async createIncident(reportedBy: string, input: CreateIncidentInput): Promise<Incident> {
    const incidentId = uuidv4();
    const createdAt = now();
    const next = await this.pool.query(
      `SELECT COALESCE(MAX(CAST(SUBSTRING(incident_number FROM 5) AS INTEGER)), 0) + 1 AS n
       FROM incidents WHERE incident_number ~ '^INC-[0-9]+$'`,
    );
    const incidentNumber = `INC-${String(next.rows[0].n).padStart(6, '0')}`;
    await this.pool.query(
      `INSERT INTO incidents
      (incident_id, incident_number, property_id, device_id, title, description, priority, status, reported_by, assigned_to, created_at, updated_at)
      VALUES ($1,$2,$3,$4,$5,$6,$7,'open',$8,$9,$10,$11)`,
      [
        incidentId,
        incidentNumber,
        input.propertyId ?? null,
        input.deviceId ?? null,
        input.title,
        input.description ?? null,
        input.priority,
        reportedBy,
        input.assignedTo ?? null,
        createdAt,
        createdAt,
      ],
    );
    return {
      incidentId,
      incidentNumber,
      propertyId: input.propertyId,
      deviceId: input.deviceId,
      title: input.title,
      description: input.description,
      priority: input.priority,
      status: 'open',
      reportedBy,
      assignedTo: input.assignedTo,
      createdAt,
      updatedAt: createdAt,
    };
  }

  async patchIncident(incidentId: string, input: Partial<PatchIncidentInput>): Promise<Incident | null> {
    const existing = await this.pool.query(`SELECT * FROM incidents WHERE incident_id=$1`, [incidentId]);
    if (existing.rowCount === 0) return null;
    const row = existing.rows[0];
    const next = {
      status: input.status ?? row.status,
      assignedTo: input.assignedTo ?? row.assigned_to,
      priority: input.priority ?? row.priority,
    };
    const updatedAt = now();
    await this.pool.query(
      `UPDATE incidents SET status=$1, assigned_to=$2, priority=$3, updated_at=$4 WHERE incident_id=$5`,
      [next.status, next.assignedTo ?? null, next.priority, updatedAt, incidentId],
    );
    return {
      incidentId: row.incident_id,
      incidentNumber: row.incident_number,
      propertyId: row.property_id ?? undefined,
      deviceId: row.device_id ?? undefined,
      title: row.title,
      description: row.description ?? undefined,
      priority: next.priority,
      status: next.status,
      reportedBy: row.reported_by,
      assignedTo: next.assignedTo ?? undefined,
      tacCaseNumber: row.tac_case_number ?? undefined,
      tacSeverity: row.tac_severity ?? undefined,
      createdAt: row.created_at.toISOString(),
      updatedAt,
    };
  }

  async addIncidentUpdate(
    incidentId: string,
    userId: string,
    content: string,
  ): Promise<IncidentUpdate | null> {
    const existing = await this.pool.query(`SELECT incident_id FROM incidents WHERE incident_id=$1`, [incidentId]);
    if (existing.rowCount === 0) return null;
    const updateId = uuidv4();
    const createdAt = now();
    await this.pool.query(
      `INSERT INTO incident_updates (update_id, incident_id, user_id, content, created_at)
       VALUES ($1,$2,$3,$4,$5)`,
      [updateId, incidentId, userId, content, createdAt],
    );
    await this.pool.query(`UPDATE incidents SET updated_at=$1 WHERE incident_id=$2`, [createdAt, incidentId]);
    return { updateId, incidentId, userId, content, createdAt };
  }

  async linkTac(
    incidentId: string,
    input: LinkTacInput,
  ): Promise<{ incident: Incident; tacCase: TacCase } | null> {
    const inc = await this.pool.query(`SELECT * FROM incidents WHERE incident_id=$1`, [incidentId]);
    if (inc.rowCount === 0) return null;
    await this.pool.query(
      `UPDATE incidents SET tac_case_number=$1, tac_severity=$2, updated_at=NOW() WHERE incident_id=$3`,
      [input.tacCaseNumber, input.tacSeverity ?? null, incidentId],
    );

    const tc = await this.pool.query(`SELECT * FROM tac_cases WHERE case_number=$1`, [input.tacCaseNumber]);
    let tacCase: TacCase;
    if (tc.rows.length > 0) {
      const row = tc.rows[0];
      await this.pool.query(`UPDATE tac_cases SET incident_id=$1 WHERE tac_case_id=$2`, [
        incidentId,
        row.tac_case_id,
      ]);
      tacCase = {
        tacCaseId: row.tac_case_id,
        caseNumber: row.case_number,
        incidentId,
        severity: row.severity,
        title: row.title,
        status: row.status,
        createdAt: row.created_at.toISOString(),
      };
    } else {
      const tacCaseId = uuidv4();
      const createdAt = now();
      const incRow = inc.rows[0];
      await this.pool.query(
        `INSERT INTO tac_cases (tac_case_id, case_number, incident_id, severity, title, status, created_at)
         VALUES ($1,$2,$3,$4,$5,'open',$6)`,
        [tacCaseId, input.tacCaseNumber, incidentId, input.tacSeverity ?? '3', `Linked from ${incRow.incident_number}`, createdAt],
      );
      tacCase = {
        tacCaseId,
        caseNumber: input.tacCaseNumber,
        incidentId,
        severity: (input.tacSeverity ?? '3') as TacCase['severity'],
        title: `Linked from ${incRow.incident_number}`,
        status: 'open',
        createdAt,
      };
    }

    const incUpdated = await this.pool.query(`SELECT * FROM incidents WHERE incident_id=$1`, [incidentId]);
    const r = incUpdated.rows[0];
    const incident: Incident = {
      incidentId: r.incident_id,
      incidentNumber: r.incident_number,
      propertyId: r.property_id ?? undefined,
      deviceId: r.device_id ?? undefined,
      title: r.title,
      description: r.description ?? undefined,
      priority: r.priority,
      status: r.status,
      reportedBy: r.reported_by,
      assignedTo: r.assigned_to ?? undefined,
      tacCaseNumber: r.tac_case_number ?? undefined,
      tacSeverity: r.tac_severity ?? undefined,
      createdAt: r.created_at.toISOString(),
      updatedAt: r.updated_at.toISOString(),
    };

    return { incident, tacCase };
  }

  async listTacCases(): Promise<TacCase[]> {
    const result = await this.pool.query(`SELECT * FROM tac_cases ORDER BY created_at DESC`);
    return result.rows.map((r) => ({
      tacCaseId: r.tac_case_id,
      caseNumber: r.case_number,
      incidentId: r.incident_id ?? undefined,
      severity: r.severity,
      title: r.title,
      status: r.status,
      createdAt: r.created_at.toISOString(),
    }));
  }
}

function buildStore(): DataStore {
  if (config.STORAGE_MODE === 'postgres') {
    if (!config.DATABASE_URL) {
      throw new Error('STORAGE_MODE=postgres requires DATABASE_URL');
    }
    return new PostgresStore(config.DATABASE_URL);
  }
  return new InMemoryStore();
}

export const store: DataStore = buildStore();

