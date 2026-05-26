import { NextFunction, Request, Response } from 'express';
import { v4 as uuidv4 } from 'uuid';

export function requestContext(req: Request, _res: Response, next: NextFunction): void {
  const r = req as Request & { requestId?: string };
  r.requestId = req.headers['x-request-id']?.toString() ?? uuidv4();
  next();
}

export function notFound(_req: Request, res: Response): void {
  res.status(404).json({ error: 'Not found' });
}

export function errorHandler(err: unknown, req: Request, res: Response, next: NextFunction): void {
  void next;
  const r = req as Request & { requestId?: string };
  const message = err instanceof Error ? err.message : 'Unexpected server error';
  res.status(500).json({
    error: 'Internal server error',
    requestId: r.requestId,
    detail: process.env.NODE_ENV === 'production' ? undefined : message,
  });
}

