export type Role = 'admin' | 'sdm' | 'tam' | 'csm' | 'engineer' | 'manager' | 'viewer';

export interface User {
  userId: string;
  email: string;
  role: Role;
  passwordHash: string;
  isActive: boolean;
}

export interface Property {
  propertyId: string;
  propertyCode: string;
  propertyName: string;
  city?: string;
  state?: string;
  createdAt: string;
}

export interface Device {
  deviceId: string;
  propertyId: string;
  hostname: string;
  serialNumber?: string;
  model?: string;
  status: 'active' | 'inactive' | 'maintenance' | 'decommissioned' | 'failed';
  createdAt: string;
}

export interface IncidentUpdate {
  updateId: string;
  incidentId: string;
  userId: string;
  content: string;
  createdAt: string;
}

export interface Incident {
  incidentId: string;
  incidentNumber: string;
  propertyId?: string;
  deviceId?: string;
  title: string;
  description?: string;
  priority: 'P1' | 'P2' | 'P3' | 'P4';
  status: 'open' | 'acknowledged' | 'investigating' | 'in-progress' | 'pending' | 'resolved' | 'closed';
  reportedBy: string;
  assignedTo?: string;
  tacCaseNumber?: string;
  tacSeverity?: string;
  createdAt: string;
  updatedAt: string;
}

export interface TacCase {
  tacCaseId: string;
  caseNumber: string;
  incidentId?: string;
  severity: '1' | '2' | '3' | '4';
  title: string;
  status: 'open' | 'in-progress' | 'pending-customer' | 'pending-cisco' | 'resolved' | 'closed';
  createdAt: string;
}

export interface AuditEvent {
  eventId: string;
  actionType: 'create' | 'read' | 'update' | 'delete' | 'login' | 'logout' | 'access';
  action: string;
  entityType?: string;
  entityId?: string;
  userId?: string;
  requestId: string;
  success: boolean;
  createdAt: string;
  detail?: string;
}

