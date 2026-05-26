import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { NextFunction, Request, RequestHandler, Response } from 'express';
import { config } from './config';
import { store } from './store';
import { Role } from './types';

export interface AuthTokenPayload {
  userId: string;
  role: Role;
  email: string;
}

export function issueAccessToken(payload: AuthTokenPayload): string {
  return jwt.sign(payload, config.JWT_SECRET, {
    expiresIn: config.JWT_EXPIRE as jwt.SignOptions['expiresIn'],
  });
}

export function issueRefreshToken(payload: AuthTokenPayload): string {
  return jwt.sign(payload, config.JWT_REFRESH_SECRET, {
    expiresIn: config.JWT_REFRESH_EXPIRE as jwt.SignOptions['expiresIn'],
  });
}

export function verifyPassword(plain: string, hash: string): boolean {
  return bcrypt.compareSync(plain, hash);
}

export const authenticate: RequestHandler = (req: Request, res: Response, next: NextFunction): void => {
  const r = req as Request & { auth?: AuthTokenPayload };
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) {
    res.status(401).json({ error: 'Missing Bearer token' });
    return;
  }

  const token = authHeader.slice('Bearer '.length);
  try {
    const decoded = jwt.verify(token, config.JWT_SECRET) as AuthTokenPayload;
    r.auth = decoded;
    next();
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
};

export function authorize(roles: Role[]) {
  return (req: Request, res: Response, next: NextFunction): void => {
    const r = req as Request & { auth?: AuthTokenPayload };
    if (!r.auth) {
      res.status(401).json({ error: 'Unauthorized' });
      return;
    }
    if (!roles.includes(r.auth.role)) {
      res.status(403).json({ error: 'Forbidden' });
      return;
    }
    next();
  };
}

export async function tryLogin(email: string, password: string): Promise<AuthTokenPayload | null> {
  const user = await store.findUserByEmail(email);
  if (!user) return null;
  if (!verifyPassword(password, user.passwordHash)) return null;
  return { userId: user.userId, role: user.role, email: user.email };
}

