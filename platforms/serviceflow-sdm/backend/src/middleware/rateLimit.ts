import rateLimit from "express-rate-limit";
import { env } from "../config.js";

const windowMs = env.RATE_LIMIT_WINDOW_MS;
const authMax =
  env.NODE_ENV === "development"
    ? Math.max(env.RATE_LIMIT_AUTH_MAX, 200)
    : env.RATE_LIMIT_AUTH_MAX;
const writeMax =
  env.NODE_ENV === "development"
    ? Math.max(env.RATE_LIMIT_WRITE_MAX, 2000)
    : env.RATE_LIMIT_WRITE_MAX;

/** Brute-force protection for credential exchange (login / refresh). */
export const authCredentialRateLimiter = rateLimit({
  windowMs,
  max: authMax,
  standardHeaders: true,
  legacyHeaders: false,
  skip: (req) => req.method !== "POST" || !["/login", "/refresh"].includes(req.path),
  message: { message: "Too many authentication attempts. Try again later." }
});

/** Limits state-changing API calls (POST/PUT/PATCH/DELETE) under /api/v1. */
export const apiWriteRateLimiter = rateLimit({
  windowMs,
  max: writeMax,
  standardHeaders: true,
  legacyHeaders: false,
  skip: (req) => {
    if (["GET", "HEAD", "OPTIONS"].includes(req.method)) return true;
    if (req.path.startsWith("/health")) return true;
    return false;
  },
  message: { message: "Too many requests. Try again later." }
});
