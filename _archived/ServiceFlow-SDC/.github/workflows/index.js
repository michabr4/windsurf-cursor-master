"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.config = void 0;
const dotenv_1 = __importDefault(require("dotenv"));
dotenv_1.default.config();
exports.config = {
    server: {
        nodeEnv: process.env.NODE_ENV || 'development',
        port: parseInt(process.env.PORT || '3000', 10),
        host: process.env.HOST || '0.0.0.0',
        apiVersion: process.env.API_VERSION || 'v1',
        corsOrigin: process.env.CORS_ORIGIN || 'http://localhost:3001',
    },
    db: {
        host: process.env.DB_HOST || 'localhost',
        port: parseInt(process.env.DB_PORT || '5432', 10),
        name: process.env.DB_NAME || 'serviceflow_sdm',
        user: process.env.DB_USER || 'serviceflow_admin',
        password: process.env.DB_PASSWORD || '',
        poolMin: parseInt(process.env.DB_POOL_MIN || '2', 10),
        poolMax: parseInt(process.env.DB_POOL_MAX || '10', 10),
    },
    redis: {
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379', 10),
        password: process.env.REDIS_PASSWORD || '',
        db: parseInt(process.env.REDIS_DB || '0', 10),
    },
    security: {
        jwtSecret: process.env.JWT_SECRET || 'dev_secret_change_in_production',
        jwtExpire: process.env.JWT_EXPIRE || '24h',
        jwtRefreshSecret: process.env.JWT_REFRESH_SECRET || 'dev_refresh_secret',
        jwtRefreshExpire: process.env.JWT_REFRESH_EXPIRE || '7d',
        bcryptRounds: parseInt(process.env.BCRYPT_ROUNDS || '12', 10),
    },
    rateLimit: {
        windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '900000', 10),
        maxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100', 10),
    },
    logging: {
        level: process.env.LOG_LEVEL || 'info',
        file: process.env.LOG_FILE || 'logs/app.log',
    },
    socketio: {
        path: process.env.SOCKET_IO_PATH || '/socket.io',
        cors: process.env.SOCKET_IO_CORS || 'http://localhost:3001',
    },
    features: {
        tacAutoCreate: process.env.ENABLE_TAC_AUTO_CREATE === 'true',
        teamsIntegration: process.env.ENABLE_TEAMS_INTEGRATION === 'true',
        webexIntegration: process.env.ENABLE_WEBEX_INTEGRATION === 'true',
        emailNotifications: process.env.ENABLE_EMAIL_NOTIFICATIONS === 'true',
    },
    teams: {
        clientId: process.env.TEAMS_CLIENT_ID || '',
        clientSecret: process.env.TEAMS_CLIENT_SECRET || '',
        tenantId: process.env.TEAMS_TENANT_ID || '',
        botId: process.env.TEAMS_BOT_ID || '',
        botPassword: process.env.TEAMS_BOT_PASSWORD || '',
        webhookBaseUrl: process.env.TEAMS_WEBHOOK_BASE_URL || '',
    },
    webex: {
        botToken: process.env.WEBEX_BOT_TOKEN || '',
        clientId: process.env.WEBEX_CLIENT_ID || '',
        clientSecret: process.env.WEBEX_CLIENT_SECRET || '',
        webhookSecret: process.env.WEBEX_WEBHOOK_SECRET || '',
        redirectUri: process.env.WEBEX_REDIRECT_URI || '',
    },
    tac: {
        apiKey: process.env.TAC_API_KEY || '',
        apiSecret: process.env.TAC_API_SECRET || '',
        baseUrl: process.env.TAC_BASE_URL || 'https://apix.cisco.com/case/v3',
        contractNumber: process.env.TAC_CONTRACT_NUMBER || '',
    },
    dnaCenter: {
        host: process.env.DNA_CENTER_HOST || '',
        username: process.env.DNA_CENTER_USERNAME || '',
        password: process.env.DNA_CENTER_PASSWORD || '',
        port: parseInt(process.env.DNA_CENTER_PORT || '443', 10),
    },
    smartLicensing: {
        clientId: process.env.SMART_LICENSING_CLIENT_ID || '',
        clientSecret: process.env.SMART_LICENSING_CLIENT_SECRET || '',
        tokenUrl: process.env.SMART_LICENSING_TOKEN_URL || 'https://cloudsso.cisco.com/as/token.oauth2',
        apiUrl: process.env.SMART_LICENSING_API_URL ||
            'https://swapi.cisco.com/services/api/smart-accounts-and-licensing/v1',
        accountDomain: process.env.SMART_LICENSING_ACCOUNT_DOMAIN || '',
    },
};
exports.default = exports.config;
//# sourceMappingURL=index.js.map