import 'dotenv/config';
import express, { Application } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import { createServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';
import cron from 'node-cron';

import config from './config';
import { connectDB } from './config/database';
import { connectRedis } from './config/redis';
import logger from './utils/logger';
import { requestLogger } from './middleware/requestLogger';
import { errorHandler, notFound } from './middleware/errorHandler';
import apiRouter from './routes';

// Services used in cron jobs
import { IncidentService } from './services/incidentService';
import { LicenseService } from './services/licenseService';

// Integration services used in cron jobs
import dnaCenterService from './integrations/dna-center/dnaCenterService';
import smartLicensingService from './integrations/smart-licensing/smartLicensingService';
import tacApiService from './integrations/tac/tacApiService';
import { query } from './config/database';

const app: Application = express();
const httpServer = createServer(app);

// ============================================================================
// Socket.IO
// ============================================================================
const io = new SocketIOServer(httpServer, {
  path: config.socketio.path,
  cors: {
    origin: config.socketio.cors.split(',').map((o) => o.trim()),
    methods: ['GET', 'POST'],
    credentials: true,
  },
});

io.on('connection', (socket) => {
  logger.info(`Socket connected: ${socket.id}`);

  socket.on('join:property', (propertyId: string) => {
    socket.join(`property:${propertyId}`);
    logger.info(`Socket ${socket.id} joined room property:${propertyId}`);
  });

  socket.on('leave:property', (propertyId: string) => {
    socket.leave(`property:${propertyId}`);
  });

  socket.on('disconnect', () => {
    logger.info(`Socket disconnected: ${socket.id}`);
  });
});

// Expose io globally so services can emit events
app.set('io', io);

// ============================================================================
// Middleware
// ============================================================================
app.use(helmet());

app.use(
  cors({
    origin: config.server.corsOrigin.split(',').map((o) => o.trim()),
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: true,
  })
);

app.use(compression());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging
app.use(requestLogger);

// Rate limiting
const limiter = rateLimit({
  windowMs: config.rateLimit.windowMs,
  max: config.rateLimit.maxRequests,
  standardHeaders: true,
  legacyHeaders: false,
  message: { success: false, message: 'Too many requests, please try again later.' },
});
app.use(`/api/${config.server.apiVersion}`, limiter);

// ============================================================================
// Routes
// ============================================================================
app.use(`/api/${config.server.apiVersion}`, apiRouter);

// 404 handler
app.use(notFound);

// Global error handler (must be last)
app.use(errorHandler);

// ============================================================================
// Scheduled Jobs (cron)
// ============================================================================
function registerCronJobs(): void {
  // Check SLA breaches every 5 minutes
  cron.schedule('*/5 * * * *', async () => {
    try {
      const breached = await IncidentService.checkSlaBreaches();
      if (breached > 0) {
        io.emit('sla:breach', { count: breached, timestamp: new Date().toISOString() });
      }
    } catch (err) {
      logger.error('Cron: SLA breach check failed', err);
    }
  });

  // Refresh license expiry statuses daily at 01:00
  cron.schedule('0 1 * * *', async () => {
    try {
      await LicenseService.refreshExpiryStatuses();
      const expiring = await LicenseService.getExpiringLicenses(90);
      if (expiring.length > 0) {
        io.emit('licenses:expiring', { count: expiring.length, timestamp: new Date().toISOString() });
      }
    } catch (err) {
      logger.error('Cron: License expiry refresh failed', err);
    }
  });

  // Sync DNA Center device inventory every 4 hours
  cron.schedule('0 */4 * * *', async () => {
    if (!dnaCenterService.isConfigured()) return;
    try {
      logger.info('Cron: DNA Center sync starting...');
      const devices = await dnaCenterService.syncDevices();
      let synced = 0;
      for (const device of devices) {
        try {
          await query(
            `INSERT INTO mgm.devices (
               hostname, ip_address, mac_address, serial_number,
               device_type, device_category, model, vendor, software_version,
               role, status, health_score, cpu_utilization, memory_utilization,
               last_seen, dna_managed, dna_device_id
             ) VALUES ($1,$2::inet,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17)
             ON CONFLICT (serial_number) DO UPDATE SET
               hostname = EXCLUDED.hostname,
               ip_address = EXCLUDED.ip_address,
               software_version = EXCLUDED.software_version,
               status = EXCLUDED.status,
               health_score = EXCLUDED.health_score,
               cpu_utilization = EXCLUDED.cpu_utilization,
               memory_utilization = EXCLUDED.memory_utilization,
               last_seen = EXCLUDED.last_seen,
               dna_managed = true,
               dna_device_id = EXCLUDED.dna_device_id,
               updated_at = CURRENT_TIMESTAMP`,
            [
              device['hostname'], device['ip_address'], device['mac_address'],
              device['serial_number'], device['device_type'], device['device_category'],
              device['model'], device['vendor'], device['software_version'],
              device['role'], device['status'], device['health_score'],
              device['cpu_utilization'], device['memory_utilization'],
              device['last_seen'], true, device['dna_device_id'],
            ]
          );
          synced++;
        } catch { /* skip individual failures */ }
      }
      logger.info(`Cron: DNA Center sync complete — ${synced}/${devices.length} devices`);
      io.emit('integration:dna:synced', { synced, total: devices.length });
    } catch (err) {
      logger.error('Cron: DNA Center sync failed', err);
    }
  });

  // Sync TAC open cases every 30 minutes
  cron.schedule('*/30 * * * *', async () => {
    try {
      const apiCases = await tacApiService.getOpenCases();
      let synced = 0;
      for (const apiCase of apiCases) {
        const mapped = tacApiService.mapApiCaseToDb(apiCase);
        try {
          await query(
            `INSERT INTO cisco.tac_cases (
               case_number, severity, title, description, status, sub_status,
               tac_engineer_name, tac_engineer_email, tac_engineer_phone, tac_engineer_cco_id,
               product_family, product_series, resolution, resolution_code,
               opened_at, last_update_at, resolved_at, auto_created
             ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,true)
             ON CONFLICT (case_number) DO UPDATE SET
               status = EXCLUDED.status,
               sub_status = EXCLUDED.sub_status,
               tac_engineer_name = EXCLUDED.tac_engineer_name,
               resolution = EXCLUDED.resolution,
               last_update_at = EXCLUDED.last_update_at,
               resolved_at = EXCLUDED.resolved_at,
               updated_at = CURRENT_TIMESTAMP`,
            [
              mapped['case_number'], mapped['severity'], mapped['title'], mapped['description'],
              mapped['status'], mapped['sub_status'], mapped['tac_engineer_name'],
              mapped['tac_engineer_email'], mapped['tac_engineer_phone'], mapped['tac_engineer_cco_id'],
              mapped['product_family'], mapped['product_series'], mapped['resolution'],
              mapped['resolution_code'], mapped['opened_at'], mapped['last_update_at'],
              mapped['resolved_at'],
            ]
          );
          synced++;
        } catch { /* skip individual failures */ }
      }
      if (synced > 0) {
        logger.info(`Cron: TAC sync complete — ${synced}/${apiCases.length} cases`);
        io.emit('integration:tac:synced', { synced, total: apiCases.length });
      }
    } catch (err) {
      logger.error('Cron: TAC sync failed', err);
    }
  });

  // Sync Smart Licensing daily at 02:00
  cron.schedule('0 2 * * *', async () => {
    if (!smartLicensingService.isConfigured()) return;
    const accountDomain = process.env.SMART_LICENSING_ACCOUNT_DOMAIN || '';
    if (!accountDomain) return;
    try {
      logger.info('Cron: Smart Licensing sync starting...');
      const licenses = await smartLicensingService.syncLicenses(accountDomain);
      let synced = 0;
      for (const lic of licenses) {
        try {
          await query(
            `INSERT INTO cisco.licenses (
               license_type, product_family, product_name, quantity_purchased, quantity_consumed,
               license_model, start_date, expiry_date, status, virtual_account, vendor
             ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
             ON CONFLICT DO NOTHING`,
            [
              lic['license_type'], lic['product_family'], lic['product_name'],
              lic['quantity_purchased'], lic['quantity_consumed'], lic['license_model'],
              lic['start_date'], lic['expiry_date'], lic['status'],
              lic['virtual_account'], lic['vendor'],
            ]
          );
          synced++;
        } catch { /* skip individual failures */ }
      }
      logger.info(`Cron: Smart Licensing sync complete — ${synced}/${licenses.length} licenses`);
      io.emit('integration:licensing:synced', { synced, total: licenses.length });
    } catch (err) {
      logger.error('Cron: Smart Licensing sync failed', err);
    }
  });

  logger.info('Cron jobs registered');
}

// ============================================================================
// Bootstrap
// ============================================================================
async function bootstrap(): Promise<void> {
  try {
    await connectDB();
    await connectRedis();

    registerCronJobs();

    const port = config.server.port;
    const host = config.server.host;

    httpServer.listen(port, host, () => {
      logger.info(`ServiceFlow SDM API running on http://${host}:${port}/api/${config.server.apiVersion}`);
      logger.info(`Environment: ${config.server.nodeEnv}`);
    });
  } catch (err) {
    logger.error('Failed to start server', err);
    process.exit(1);
  }
}

// Handle uncaught exceptions
process.on('uncaughtException', (err) => {
  logger.error('Uncaught Exception:', err);
  process.exit(1);
});

process.on('unhandledRejection', (reason) => {
  logger.error('Unhandled Rejection:', reason);
  process.exit(1);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received — shutting down gracefully');
  httpServer.close(() => {
    logger.info('HTTP server closed');
    process.exit(0);
  });
});

process.on('SIGINT', async () => {
  logger.info('SIGINT received — shutting down gracefully');
  httpServer.close(() => {
    logger.info('HTTP server closed');
    process.exit(0);
  });
});

bootstrap();

export { app, io };
