import "dotenv/config";
import { z } from "zod";

const EnvSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  PORT: z.coerce.number().default(3000),
  DB_HOST: z.string().default("localhost"),
  DB_PORT: z.coerce.number().default(5432),
  DB_NAME: z.string().default("serviceflow_sdm"),
  DB_USER: z.string().default("serviceflow_admin"),
  DB_PASSWORD: z.string().default("change_me"),
  REDIS_HOST: z.string().default("localhost"),
  REDIS_PORT: z.coerce.number().default(6379),
  JWT_SECRET: z.string().min(32).default("replace_with_32_plus_chars_replace"),
  JWT_REFRESH_SECRET: z.string().min(32).default("replace_with_32_plus_chars_replace"),
  JWT_EXPIRE: z.string().default("24h"),
  JWT_REFRESH_EXPIRE: z.string().default("7d"),
  CORS_ORIGIN: z.string().default("http://localhost:3001"),
  TAC_BASE_URL: z.string().default("https://tools.cisco.com/tac/api/v2"),
  TAC_API_KEY: z.string().default(""),
  TAC_API_SECRET: z.string().default(""),
  DNA_CENTER_HOST: z.string().default(""),
  DNA_CENTER_USERNAME: z.string().default(""),
  DNA_CENTER_PASSWORD: z.string().default(""),
  DNA_CENTER_PORT: z.coerce.number().default(443),
  SMART_LICENSING_TOKEN_URL: z.string().default("https://cloudsso.cisco.com/as/token.oauth2"),
  SMART_LICENSING_API_URL: z.string().default("https://swapi.cisco.com/services/api/smart-accounts-and-licensing"),
  SMART_LICENSING_CLIENT_ID: z.string().default(""),
  SMART_LICENSING_CLIENT_SECRET: z.string().default("")
});

export const env = EnvSchema.parse(process.env);
