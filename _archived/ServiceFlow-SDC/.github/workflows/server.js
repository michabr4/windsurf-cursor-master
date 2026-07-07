"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.io = exports.app = void 0;
require("dotenv/config");
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const helmet_1 = __importDefault(require("helmet"));
const compression_1 = __importDefault(require("compression"));
const express_rate_limit_1 = __importDefault(require("express-rate-limit"));
const http_1 = require("http");
const socket_io_1 = require("socket.io");
const node_cron_1 = __importDefault(require("node-cron"));
const config_1 = __importDefault(require("./config"));
const database_1 = require("./config/database");
const redis_1 = require("./config/redis");
const logger_1 = __importDefault(require("./utils/logger"));
const requestLogger_1 = require("./middleware/requestLogger");
const errorHandler_1 = require("./middleware/errorHandler");
const routes_1 = __importDefault(require("./routes"));
// Services used in cron jobs
const incidentService_1 = require("./services/incidentService");
const licenseService_1 = require("./services/licenseService");
// Integration services used in cron jobs
const dnaCenterService_1 = __importDefault(require("./integrations/dna-center/dnaCenterService"));
const smartLicensingService_1 = __importDefault(require("./integrations/smart-licensing/smartLicensingService"));
const tacApiService_1 = __importDefault(require("./integrations/tac/tacApiService"));
const database_2 = require("./config/database");
const app = (0, express_1.default)();
exports.app = app;
const httpServer = (0, http_1.createServer)(app);
// ============================================================================
// Socket.IO
// ============================================================================
const io = new socket_io_1.Server(httpServer, {
    path: config_1.default.socketio.path,
    cors: {
        origin: config_1.default.socketio.cors.split(',').map((o) => o.trim()),
        methods: ['GET', 'POST'],
        credentials: true,
    },
});
exports.io = io;
io.on('connection', (socket) => {
    logger_1.default.info(`Socket connected: ${socket.id}`);
    socket.on('join:property', (propertyId) => {
        socket.join(`property:${propertyId}`);
        logger_1.default.info(`Socket ${socket.id} joined room property:${propertyId}`);
    });
    socket.on('leave:property', (propertyId) => {
        socket.leave(`property:${propertyId}`);
    });
    socket.on('disconnect', () => {
        logger_1.default.info(`Socket disconnected: ${socket.id}`);
    });
});
// Expose io globally so services can emit events
app.set('io', io);
// ============================================================================
// Middleware
// ============================================================================
app.use((0, helmet_1.default)());
app.use((0, cors_1.default)({
    origin: config_1.default.server.corsOrigin.split(',').map((o) => o.trim()),
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: true,
}));
app.use((0, compression_1.default)());
app.use(express_1.default.json({ limit: '10mb' }));
app.use(express_1.default.urlencoded({ extended: true, limit: '10mb' }));
// Request logging
app.use(requestLogger_1.requestLogger);
// Rate limiting
const limiter = (0, express_rate_limit_1.default)({
    windowMs: config_1.default.rateLimit.windowMs,
    max: config_1.default.rateLimit.maxRequests,
    standardHeaders: true,
    legacyHeaders: false,
    message: { success: false, message: 'Too many requests, please try again later.' },
});
app.use(`/api/${config_1.default.server.apiVersion}`, limiter);
// ============================================================================
// Routes
// ============================================================================
app.use(`/api/${config_1.default.server.apiVersion}`, routes_1.default);
// 404 handler
app.use(errorHandler_1.notFound);
// Global error handler (must be last)
app.use(errorHandler_1.errorHandler);
// ============================================================================
// Scheduled Jobs (cron)
// ============================================================================
function registerCronJobs() {
    // Check SLA breaches every 5 minutes
    node_cron_1.default.schedule('*/5 * * * *', async () => {
        try {
            const breached = await incidentService_1.IncidentService.checkSlaBreaches();
            if (breached > 0) {
                io.emit('sla:breach', { count: breached, timestamp: new Date().toISOString() });
            }
        }
        catch (err) {
            logger_1.default.error('Cron: SLA breach check failed', err);
        }
    });
    // Refresh license expiry statuses daily at 01:00
    node_cron_1.default.schedule('0 1 * * *', async () => {
        try {
            await licenseService_1.LicenseService.refreshExpiryStatuses();
            const expiring = await licenseService_1.LicenseService.getExpiringLicenses(90);
            if (expiring.length > 0) {
                io.emit('licenses:expiring', { count: expiring.length, timestamp: new Date().toISOString() });
            }
        }
        catch (err) {
            logger_1.default.error('Cron: License expiry refresh failed', err);
        }
    });
    // Sync DNA Center device inventory every 4 hours
    node_cron_1.default.schedule('0 */4 * * *', async () => {
        if (!dnaCenterService_1.default.isConfigured())
            return;
        try {
            logger_1.default.info('Cron: DNA Center sync starting...');
            const devices = await dnaCenterService_1.default.syncDevices();
            let synced = 0;
            for (const device of devices) {
                try {
                    await (0, database_2.query)(`INSERT INTO mgm.devices (
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
               updated_at = CURRENT_TIMESTAMP`, [
                        device['hostname'], device['ip_address'], device['mac_address'],
                        device['serial_number'], device['device_type'], device['device_category'],
                        device['model'], device['vendor'], device['software_version'],
                        device['role'], device['status'], device['health_score'],
                        device['cpu_utilization'], device['memory_utilization'],
                        device['last_seen'], true, device['dna_device_id'],
                    ]);
                    synced++;
                }
                catch { /* skip individual failures */ }
            }
            logger_1.default.info(`Cron: DNA Center sync complete — ${synced}/${devices.length} devices`);
            io.emit('integration:dna:synced', { synced, total: devices.length });
        }
        catch (err) {
            logger_1.default.error('Cron: DNA Center sync failed', err);
        }
    });
    // Sync TAC open cases every 30 minutes
    node_cron_1.default.schedule('*/30 * * * *', async () => {
        try {
            const apiCases = await tacApiService_1.default.getOpenCases();
            let synced = 0;
            for (const apiCase of apiCases) {
                const mapped = tacApiService_1.default.mapApiCaseToDb(apiCase);
                try {
                    await (0, database_2.query)(`INSERT INTO cisco.tac_cases (
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
               updated_at = CURRENT_TIMESTAMP`, [
                        mapped['case_number'], mapped['severity'], mapped['title'], mapped['description'],
                        mapped['status'], mapped['sub_status'], mapped['tac_engineer_name'],
                        mapped['tac_engineer_email'], mapped['tac_engineer_phone'], mapped['tac_engineer_cco_id'],
                        mapped['product_family'], mapped['product_series'], mapped['resolution'],
                        mapped['resolution_code'], mapped['opened_at'], mapped['last_update_at'],
                        mapped['resolved_at'],
                    ]);
                    synced++;
                }
                catch { /* skip individual failures */ }
            }
            if (synced > 0) {
                logger_1.default.info(`Cron: TAC sync complete — ${synced}/${apiCases.length} cases`);
                io.emit('integration:tac:synced', { synced, total: apiCases.length });
            }
        }
        catch (err) {
            logger_1.default.error('Cron: TAC sync failed', err);
        }
    });
    // Sync Smart Licensing daily at 02:00
    node_cron_1.default.schedule('0 2 * * *', async () => {
        if (!smartLicensingService_1.default.isConfigured())
            return;
        const accountDomain = process.env.SMART_LICENSING_ACCOUNT_DOMAIN || '';
        if (!accountDomain)
            return;
        try {
            logger_1.default.info('Cron: Smart Licensing sync starting...');
            const licenses = await smartLicensingService_1.default.syncLicenses(accountDomain);
            let synced = 0;
            for (const lic of licenses) {
                try {
                    await (0, database_2.query)(`INSERT INTO cisco.licenses (
               license_type, product_family, product_name, quantity_purchased, quantity_consumed,
               license_model, start_date, expiry_date, status, virtual_account, vendor
             ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
             ON CONFLICT DO NOTHING`, [
                        lic['license_type'], lic['product_family'], lic['product_name'],
                        lic['quantity_purchased'], lic['quantity_consumed'], lic['license_model'],
                        lic['start_date'], lic['expiry_date'], lic['status'],
                        lic['virtual_account'], lic['vendor'],
                    ]);
                    synced++;
                }
                catch { /* skip individual failures */ }
            }
            logger_1.default.info(`Cron: Smart Licensing sync complete — ${synced}/${licenses.length} licenses`);
            io.emit('integration:licensing:synced', { synced, total: licenses.length });
        }
        catch (err) {
            logger_1.default.error('Cron: Smart Licensing sync failed', err);
        }
    });
    logger_1.default.info('Cron jobs registered');
}
// ============================================================================
// Bootstrap
// ============================================================================
async function bootstrap() {
    try {
        await (0, database_1.connectDB)();
        await (0, redis_1.connectRedis)();
        registerCronJobs();
        const port = config_1.default.server.port;
        const host = config_1.default.server.host;
        httpServer.listen(port, host, () => {
            logger_1.default.info(`ServiceFlow SDM API running on http://${host}:${port}/api/${config_1.default.server.apiVersion}`);
            logger_1.default.info(`Environment: ${config_1.default.server.nodeEnv}`);
        });
    }
    catch (err) {
        logger_1.default.error('Failed to start server', err);
        process.exit(1);
    }
}
// Handle uncaught exceptions
process.on('uncaughtException', (err) => {
    logger_1.default.error('Uncaught Exception:', err);
    process.exit(1);
});
process.on('unhandledRejection', (reason) => {
    logger_1.default.error('Unhandled Rejection:', reason);
    process.exit(1);
});
// Graceful shutdown
process.on('SIGTERM', async () => {
    logger_1.default.info('SIGTERM received — shutting down gracefully');
    httpServer.close(() => {
        logger_1.default.info('HTTP server closed');
        process.exit(0);
    });
});
process.on('SIGINT', async () => {
    logger_1.default.info('SIGINT received — shutting down gracefully');
    httpServer.close(() => {
        logger_1.default.info('HTTP server closed');
        process.exit(0);
    });
});
bootstrap();
//# sourceMappingURL=server.js.map