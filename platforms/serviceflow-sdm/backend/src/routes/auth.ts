import { Router } from "express";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { z } from "zod";
import { pool } from "../db.js";
import { env } from "../config.js";
import { requireAuth, type AuthContext } from "../middleware/auth.js";
import { attachSsoRoutes } from "./sso.js";

export const authRouter = Router();
attachSsoRoutes(authRouter);

const LoginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
});

authRouter.post("/login", async (req, res) => {
  const parsed = LoginSchema.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({
      message: "Invalid request: use a valid email and a password of at least 8 characters."
    });
    return;
  }

  try {
    const email = parsed.data.email.trim().toLowerCase();
    const password = parsed.data.password;
    const result = await pool.query(
      "SELECT user_id, role, password_hash FROM mgm.users WHERE lower(trim(email)) = $1 LIMIT 1",
      [email]
    );

    const user = result.rows[0];
    if (!user) {
      res.status(401).json({ message: "Invalid username or password" });
      return;
    }

    const valid = await bcrypt.compare(password, user.password_hash);
    if (!valid) {
      res.status(401).json({ message: "Invalid username or password" });
      return;
    }

    const payload: AuthContext = { userId: user.user_id, role: user.role };
    const accessToken = jwt.sign(payload, env.JWT_SECRET, {
      expiresIn: env.JWT_EXPIRE as jwt.SignOptions["expiresIn"]
    });
    const refreshToken = jwt.sign(payload, env.JWT_REFRESH_SECRET, {
      expiresIn: env.JWT_REFRESH_EXPIRE as jwt.SignOptions["expiresIn"]
    });
    res.json({ accessToken, refreshToken });
  } catch {
    res.status(500).json({ message: "Internal server error" });
  }
});

authRouter.post("/refresh", (req, res) => {
  const token = typeof req.body?.refreshToken === "string" ? req.body.refreshToken : "";
  if (!token) {
    res.status(400).json({ message: "Invalid request" });
    return;
  }

  try {
    const decoded = jwt.verify(token, env.JWT_REFRESH_SECRET) as AuthContext;
    const accessToken = jwt.sign(decoded, env.JWT_SECRET, {
      expiresIn: env.JWT_EXPIRE as jwt.SignOptions["expiresIn"]
    });
    res.json({ accessToken });
  } catch {
    res.status(401).json({ message: "Unauthorized" });
  }
});

authRouter.post("/logout", requireAuth, (_req, res) => {
  res.status(204).send();
});
