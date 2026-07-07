import { createServer } from "node:http";
import { createApp } from "./app.js";
import { env } from "./config.js";
import { pool } from "./db.js";
import { redis } from "./redis.js";

async function bootstrap() {
  await pool.query("SELECT 1");
  await redis.connect().catch(() => undefined);

  const app = createApp();
  const server = createServer(app);

  server.listen(env.PORT, () => {
    console.log(JSON.stringify({ level: "info", message: "backend_started", port: env.PORT }));
  });
}

bootstrap().catch((error) => {
  console.error(JSON.stringify({ level: "error", message: "bootstrap_failed", error: String(error) }));
  process.exit(1);
});
