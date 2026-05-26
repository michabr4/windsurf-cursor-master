import { describe, expect, it } from "vitest";
import { EnvSchema, INSECURE_JWT_SECRET_DEFAULT } from "../config.js";

const baseEnv = {
  NODE_ENV: "production",
  JWT_SECRET: "a".repeat(32),
  JWT_REFRESH_SECRET: "b".repeat(32),
  DB_PASSWORD: "strong_local_password"
};

describe("EnvSchema production secrets", () => {
  it("rejects default JWT secrets outside development", () => {
    const result = EnvSchema.safeParse({
      ...baseEnv,
      NODE_ENV: "test",
      JWT_SECRET: INSECURE_JWT_SECRET_DEFAULT,
      JWT_REFRESH_SECRET: "b".repeat(32)
    });
    expect(result.success).toBe(false);
  });

  it("allows default JWT secrets in development", () => {
    const result = EnvSchema.safeParse({
      NODE_ENV: "development",
      JWT_SECRET: INSECURE_JWT_SECRET_DEFAULT,
      JWT_REFRESH_SECRET: INSECURE_JWT_SECRET_DEFAULT
    });
    expect(result.success).toBe(true);
  });

  it("rejects default DB password in production", () => {
    const result = EnvSchema.safeParse({
      ...baseEnv,
      DB_PASSWORD: "change_me"
    });
    expect(result.success).toBe(false);
  });
});
