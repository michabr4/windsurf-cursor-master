import rateLimit from "express-rate-limit";
import { env } from "../config.js";

const isProd = env.NODE_ENV === "production";

/** Brute-force protection for credential exchange (login / refresh). */
export const authCredentialRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: isProd ? 15 : 200,
  standardHeaders: true,
  legacyHeaders: false,
  skip: (req) => req.method !== "POST" || !["/login", "/refresh"].includes(req.path),
  message: { message: "Too many authentication attempts. Try again later." }
});

/** Limits state-changing API calls (POST/PUT/PATCH/DELETE) under /api/v1. */
export const apiWriteRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: isProd ? 300 : 2000,
  standardHeaders: true,
  legacyHeaders: false,
  skip: (req) => {
    if (["GET", "HEAD", "OPTIONS"].includes(req.method)) return true;
    if (req.path.startsWith("/health")) return true;
    return false;
  },
  message: { message: "Too many requests. Try again later." }
});
