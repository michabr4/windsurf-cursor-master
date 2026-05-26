import type { NextFunction, Request, Response } from "express";
import jwt from "jsonwebtoken";
import { env } from "../config.js";

export type AppRole =
  | "admin"
  | "sdm"
  | "tam"
  | "csm"
  | "engineer"
  | "manager"
  | "viewer";

export type AuthContext = {
  userId: string;
  role: AppRole;
};

export type AuthedRequest = Request & { auth?: AuthContext };

export function requireAuth(req: AuthedRequest, res: Response, next: NextFunction): void {
  const authHeader = req.header("authorization");
  const token = authHeader?.startsWith("Bearer ") ? authHeader.slice(7) : undefined;

  if (!token) {
    res.status(401).json({ message: "Unauthorized" });
    return;
  }

  try {
    const decoded = jwt.verify(token, env.JWT_SECRET) as AuthContext;
    req.auth = decoded;
    next();
  } catch {
    res.status(401).json({ message: "Unauthorized" });
  }
}

export function requireRoles(allowed: AppRole[]) {
  return (req: AuthedRequest, res: Response, next: NextFunction): void => {
    const role = req.auth?.role;
    if (!role || !allowed.includes(role)) {
      res.status(403).json({ message: "Forbidden" });
      return;
    }
    next();
  };
}
