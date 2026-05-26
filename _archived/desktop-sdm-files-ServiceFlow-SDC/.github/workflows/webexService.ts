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

import axios, { AxiosInstance } from 'axios';
import crypto from 'crypto';
import logger from '../../utils/logger';

interface WebExConfig {
  botToken: string;
  clientId: string;
  clientSecret: string;
  webhookSecret: string;
  redirectUri: string;
}

interface WebExSpace {
  id: string;
  title: string;
  type: string;
  created: string;
}

interface WebExMessage {
  id: string;
  roomId: string;
  text?: string;
  html?: string;
  created: string;
}

interface WebExMeeting {
  id: string;
  meetingNumber: string;
  title: string;
  password: string;
  webLink: string;
  sipAddress: string;
  start: string;
  end: string;
}

class WebExService {
  private config: WebExConfig;
  private client: AxiosInstance;

  constructor() {
    this.config = {
      botToken: process.env.WEBEX_BOT_TOKEN || '',
      clientId: process.env.WEBEX_CLIENT_ID || '',
      clientSecret: process.env.WEBEX_CLIENT_SECRET || '',
      webhookSecret: process.env.WEBEX_WEBHOOK_SECRET || '',
      redirectUri: process.env.WEBEX_REDIRECT_URI || '',
    };

    this.client = axios.create({
      baseURL: 'https://webexapis.com/v1',
      headers: {
        Authorization: `Bearer ${this.config.botToken}`,
        'Content-Type': 'application/json',
      },
      timeout: 15000,
    });
  }

  private isConfigured(): boolean {
    return !!this.config.botToken;
  }

  /**
   * Verify webhook signature from WebEx
   */
  verifyWebhookSignature(rawBody: string, signature: string): boolean {
    if (!this.config.webhookSecret) return true; // skip in dev
    const hmac = crypto
      .createHmac('sha1', this.config.webhookSecret)
      .update(rawBody)
      .digest('hex');
    return hmac === signature;
  }

  /**
   * Create a new WebEx space
   */
  async createSpace(title: string): Promise<WebExSpace> {
    if (!this.isConfigured()) {
      throw new Error('WebEx bot token not configured');
    }

    try {
      const { data } = await this.client.post<WebExSpace>('/rooms', { title });
      logger.info(`WebEx space created: ${title} (${data.id})`);
      return data;
    } catch (error) {
      logger.error('Failed to create WebEx space:', error);
      throw error;
    }
  }

  /**
   * Create a war-room space for a P1/P2 incident
   */
  async createWarRoom(
    incidentNumber: string,
    propertyName: string,
    priority: string
  ): Promise<WebExSpace> {
    const title = `[WAR ROOM] ${incidentNumber} — ${priority} — ${propertyName}`;
    return this.createSpace(title);
  }

  /**
   * Create a space for a TAC case
   */
  async createTacSpace(caseNumber: string, severity: string): Promise<WebExSpace> {
    const title = `[TAC] ${caseNumber} — SEV-${severity}`;
    return this.createSpace(title);
  }

  /**
   * Send a text message to a space
   */
  async sendMessage(roomId: string, text: string): Promise<WebExMessage> {
    if (!this.isConfigured()) {
      logger.warn('WebEx: bot token not configured, skipping message');
      return { id: '', roomId, text, created: new Date().toISOString() };
    }

    try {
      const { data } = await this.client.post<WebExMessage>('/messages', {
        roomId,
        markdown: text,
      });
      return data;
    } catch (error) {
      logger.error('Failed to send WebEx message:', error);
      throw error;
    }
  }

  /**
   * Send a formatted incident notification to a space
   */
  async sendIncidentNotification(
    roomId: string,
    incidentNumber: string,
    title: string,
    priority: string,
    status: string,
    property: string,
    assignedTo: string,
    dashboardUrl: string
  ): Promise<void> {
    const priorityEmoji: Record<string, string> = {
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
  async sendTacCaseNotification(
    roomId: string,
    caseNumber: string,
    title: string,
    severity: string,
    status: string,
    tacEngineer: string,
    dashboardUrl: string
  ): Promise<void> {
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
  async sendSlaBreachAlert(
    roomId: string,
    incidentNumber: string,
    property: string,
    priority: string,
    dashboardUrl: string
  ): Promise<void> {
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
  async addMember(roomId: string, personEmail: string): Promise<void> {
    if (!this.isConfigured()) return;

    try {
      await this.client.post('/memberships', { roomId, personEmail });
      logger.info(`Added ${personEmail} to WebEx space ${roomId}`);
    } catch (error) {
      logger.warn(`Failed to add ${personEmail} to WebEx space:`, error);
    }
  }

  /**
   * Create a WebEx meeting for a war room
   */
  async createMeeting(
    title: string,
    startTime: string,
    durationMinutes = 60,
    password?: string
  ): Promise<WebExMeeting | null> {
    if (!this.isConfigured()) {
      logger.warn('WebEx: not configured, skipping meeting creation');
      return null;
    }

    const start = new Date(startTime).toISOString();
    const end = new Date(
      new Date(startTime).getTime() + durationMinutes * 60 * 1000
    ).toISOString();

    try {
      const { data } = await this.client.post<WebExMeeting>('/meetings', {
        title,
        start,
        end,
        password: password || Math.random().toString(36).substring(2, 8).toUpperCase(),
        enabledAutoRecordMeeting: false,
        allowAnyUserToBeCoHost: true,
      });
      logger.info(`WebEx meeting created: ${title} (${data.id})`);
      return data;
    } catch (error) {
      logger.error('Failed to create WebEx meeting:', error);
      return null;
    }
  }

  /**
   * Register a webhook with WebEx
   */
  async registerWebhook(
    name: string,
    targetUrl: string,
    resource: string,
    event: string
  ): Promise<void> {
    if (!this.isConfigured()) return;

    try {
      await this.client.post('/webhooks', {
        name,
        targetUrl,
        resource,
        event,
        secret: this.config.webhookSecret,
      });
      logger.info(`WebEx webhook registered: ${name}`);
    } catch (error) {
      logger.warn('Failed to register WebEx webhook:', error);
    }
  }

  /**
   * Get message details (used when handling webhook events)
   */
  async getMessage(messageId: string): Promise<WebExMessage | null> {
    if (!this.isConfigured()) return null;

    try {
      const { data } = await this.client.get<WebExMessage>(`/messages/${messageId}`);
      return data;
    } catch {
      return null;
    }
  }
}

export const webexService = new WebExService();
export default webexService;
