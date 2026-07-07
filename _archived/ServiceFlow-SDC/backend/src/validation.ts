import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

export const refreshSchema = z.object({
  refreshToken: z.string().min(10),
});

export const propertySchema = z.object({
  propertyCode: z.string().min(2).max(20),
  propertyName: z.string().min(2).max(255),
  city: z.string().max(100).optional(),
  state: z.string().max(50).optional(),
});

export const deviceSchema = z.object({
  propertyId: z.string().uuid(),
  hostname: z.string().min(2).max(255),
  serialNumber: z.string().max(100).optional(),
  model: z.string().max(100).optional(),
  status: z.enum(['active', 'inactive', 'maintenance', 'decommissioned', 'failed']).default('active'),
});

export const incidentCreateSchema = z.object({
  propertyId: z.string().uuid().optional(),
  deviceId: z.string().uuid().optional(),
  title: z.string().min(3).max(500),
  description: z.string().max(5000).optional(),
  priority: z.enum(['P1', 'P2', 'P3', 'P4']),
  assignedTo: z.string().uuid().optional(),
});

export const incidentPatchSchema = z.object({
  status: z.enum(['open', 'acknowledged', 'investigating', 'in-progress', 'pending', 'resolved', 'closed']).optional(),
  assignedTo: z.string().uuid().optional(),
  priority: z.enum(['P1', 'P2', 'P3', 'P4']).optional(),
}).refine((obj) => Object.keys(obj).length > 0, {
  message: 'At least one field is required for patch',
});

export const incidentUpdateSchema = z.object({
  content: z.string().min(1).max(5000),
});

export const incidentTacLinkSchema = z.object({
  tacCaseNumber: z.string().min(3).max(100),
  tacSeverity: z.enum(['1', '2', '3', '4']).optional(),
});

