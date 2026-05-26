import express from "express";
import cors from "cors";
import cookieParser from "cookie-parser";
import { env } from "./config.js";
import { helmetByPath } from "./middleware/helmetByPath.js";
import { healthRouter } from "./routes/health.js";
import { authRouter } from "./routes/auth.js";
import { propertiesRouter } from "./routes/properties.js";
import { devicesRouter } from "./routes/devices.js";
import { incidentsRouter } from "./routes/incidents.js";
import { tacRouter } from "./routes/tac.js";
import { integrationsRouter } from "./routes/integrations.js";
import { sourceAdminRouter } from "./routes/sourceAdmin.js";
import { powerBiRouter } from "./routes/powerBi.js";
import { salesforceRouter } from "./routes/salesforce.js";

export function createApp() {
  const app = express();
  app.use(helmetByPath);
  app.use(
    cors({
      origin: env.CORS_ORIGIN.split(",").map((o) => o.trim()).filter(Boolean),
      credentials: true
    })
  );
  app.use(cookieParser(env.JWT_SECRET));
  app.use(express.json({ limit: "1mb" }));
  app.use("/", express.static("public"));

  app.use("/api/v1/health", healthRouter);
  app.use("/api/v1/auth", authRouter);
  app.use("/api/v1/properties", propertiesRouter);
  app.use("/api/v1/devices", devicesRouter);
  app.use("/api/v1/incidents", incidentsRouter);
  app.use("/api/v1/tac-cases", tacRouter);
  app.use("/api/v1/integrations", integrationsRouter);
  app.use("/api/v1/admin", sourceAdminRouter);
  app.use("/api/v1/analytics/powerbi", powerBiRouter);
  app.use("/api/v1/salesforce", salesforceRouter);

  return app;
}
