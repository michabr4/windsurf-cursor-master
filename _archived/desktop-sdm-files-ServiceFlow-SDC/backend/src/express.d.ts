import type { Role } from './types';

declare global {
  namespace Express {
    interface Request {
      requestId?: string;
      auth?: {
        userId: string;
        role: Role;
        email: string;
      };
    }
  }
}

export {};

