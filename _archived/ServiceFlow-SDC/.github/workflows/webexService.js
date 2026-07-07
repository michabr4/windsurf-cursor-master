"use strict";
/**
 * Cisco WebEx Integration Service
 *
 * Handles:
 * - Creating WebEx spaces (rooms) for incidents and war rooms
 * - Sending messages and cards to WebEx spaces
 * - Listing space members
 * - Webhook event processing
 * - Meeting creation via WebEx Meetings API
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.webexService = void 0;
const axios_1 = __importDefault(require("axios"));
const crypto_1 = __importDefault(require("crypto"));
const logger_1 = __importDefault(require("../../utils/logger"));
class WebExService {
    config;
    client;
    constructor() {
        this.config = {
            botToken: process.env.WEBEX_BOT_TOKEN || '',
            clientId: process.env.WEBEX_CLIENT_ID || '',
            clientSecret: process.env.WEBEX_CLIENT_SECRET || '',
            webhookSecret: process.env.WEBEX_WEBHOOK_SECRET || '',
            redirectUri: process.env.WEBEX_REDIRECT_URI || '',
        };
        this.client = axios_1.default.create({
            baseURL: 'https://webexapis.com/v1',
            headers: {
                Authorization: `Bearer ${this.config.botToken}`,
                'Content-Type': 'application/json',
            },
            timeout: 15000,
        });
    }
    isConfigured() {
        return !!this.config.botToken;
    }
    /**
     * Verify webhook signature from WebEx
     */
    verifyWebhookSignature(rawBody, signature) {
        if (!this.config.webhookSecret)
            return true; // skip in dev
        const hmac = crypto_1.default
            .createHmac('sha1', this.config.webhookSecret)
            .update(rawBody)
            .digest('hex');
        return hmac === signature;
    }
    /**
     * Create a new WebEx space
     */
    async createSpace(title) {
        if (!this.isConfigured()) {
            throw new Error('WebEx bot token not configured');
        }
        try {
            const { data } = await this.client.post('/rooms', { title });
            logger_1.default.info(`WebEx space created: ${title} (${data.id})`);
            return data;
        }
        catch (error) {
            logger_1.default.error('Failed to create WebEx space:', error);
            throw error;
        }
    }
    /**
     * Create a war-room space for a P1/P2 incident
     */
    async createWarRoom(incidentNumber, propertyName, priority) {
        const title = `[WAR ROOM] ${incidentNumber} — ${priority} — ${propertyName}`;
        return this.createSpace(title);
    }
    /**
     * Create a space for a TAC case
     */
    async createTacSpace(caseNumber, severity) {
        const title = `[TAC] ${caseNumber} — SEV-${severity}`;
        return this.createSpace(title);
    }
    /**
     * Send a text message to a space
     */
    async sendMessage(roomId, text) {
        if (!this.isConfigured()) {
            logger_1.default.warn('WebEx: bot token not configured, skipping message');
            return { id: '', roomId, text, created: new Date().toISOString() };
        }
        try {
            const { data } = await this.client.post('/messages', {
                roomId,
                markdown: text,
            });
            return data;
        }
        catch (error) {
            logger_1.default.error('Failed to send WebEx message:', error);
            throw error;
        }
    }
    /**
     * Send a formatted incident notification to a space
     */
    async sendIncidentNotification(roomId, incidentNumber, title, priority, status, property, assignedTo, dashboardUrl) {
        const priorityEmoji = {
            P1: '🔴',
            P2: '🟠',
            P3: '🟡',
            P4: '🟢',
        };
        const emoji = priorityEmoji[priority] || '⚪';
        const message = [
            `## ${emoji} Incident ${incidentNumber} — **${priority}**`,
            `**${title}**`,
            '',
            `| Field | Value |`,
            `|---|---|`,
            `| Status | ${status} |`,
            `| Property | ${property} |`,
            `| Assigned To | ${assignedTo || 'Unassigned'} |`,
            '',
            `[View in ServiceFlow](${dashboardUrl})`,
        ].join('\n');
        await this.sendMessage(roomId, message);
    }
    /**
     * Send a TAC case notification to a space
     */
    async sendTacCaseNotification(roomId, caseNumber, title, severity, status, tacEngineer, dashboardUrl) {
        const message = [
            `## 🔧 TAC Case ${caseNumber} — **SEV-${severity}**`,
            `**${title}**`,
            '',
            `| Field | Value |`,
            `|---|---|`,
            `| Status | ${status} |`,
            `| TAC Engineer | ${tacEngineer || 'Pending Assignment'} |`,
            '',
            `[View TAC Case](${dashboardUrl})`,
        ].join('\n');
        await this.sendMessage(roomId, message);
    }
    /**
     * Send an SLA breach alert to a space
     */
    async sendSlaBreachAlert(roomId, incidentNumber, property, priority, dashboardUrl) {
        const message = [
            `## ⏰ **SLA BREACH** — ${incidentNumber}`,
            '',
            `An incident has **breached** its SLA target and requires immediate attention.`,
            '',
            `| Field | Value |`,
            `|---|---|`,
            `| Incident | ${incidentNumber} |`,
            `| Property | ${property} |`,
            `| Priority | ${priority} |`,
            '',
            `[Take Action Now](${dashboardUrl})`,
        ].join('\n');
        await this.sendMessage(roomId, message);
    }
    /**
     * Add a person to a WebEx space by email
     */
    async addMember(roomId, personEmail) {
        if (!this.isConfigured())
            return;
        try {
            await this.client.post('/memberships', { roomId, personEmail });
            logger_1.default.info(`Added ${personEmail} to WebEx space ${roomId}`);
        }
        catch (error) {
            logger_1.default.warn(`Failed to add ${personEmail} to WebEx space:`, error);
        }
    }
    /**
     * Create a WebEx meeting for a war room
     */
    async createMeeting(title, startTime, durationMinutes = 60, password) {
        if (!this.isConfigured()) {
            logger_1.default.warn('WebEx: not configured, skipping meeting creation');
            return null;
        }
        const start = new Date(startTime).toISOString();
        const end = new Date(new Date(startTime).getTime() + durationMinutes * 60 * 1000).toISOString();
        try {
            const { data } = await this.client.post('/meetings', {
                title,
                start,
                end,
                password: password || Math.random().toString(36).substring(2, 8).toUpperCase(),
                enabledAutoRecordMeeting: false,
                allowAnyUserToBeCoHost: true,
            });
            logger_1.default.info(`WebEx meeting created: ${title} (${data.id})`);
            return data;
        }
        catch (error) {
            logger_1.default.error('Failed to create WebEx meeting:', error);
            return null;
        }
    }
    /**
     * Register a webhook with WebEx
     */
    async registerWebhook(name, targetUrl, resource, event) {
        if (!this.isConfigured())
            return;
        try {
            await this.client.post('/webhooks', {
                name,
                targetUrl,
                resource,
                event,
                secret: this.config.webhookSecret,
            });
            logger_1.default.info(`WebEx webhook registered: ${name}`);
        }
        catch (error) {
            logger_1.default.warn('Failed to register WebEx webhook:', error);
        }
    }
    /**
     * Get message details (used when handling webhook events)
     */
    async getMessage(messageId) {
        if (!this.isConfigured())
            return null;
        try {
            const { data } = await this.client.get(`/messages/${messageId}`);
            return data;
        }
        catch {
            return null;
        }
    }
}
exports.webexService = new WebExService();
exports.default = exports.webexService;
//# sourceMappingURL=webexService.js.map