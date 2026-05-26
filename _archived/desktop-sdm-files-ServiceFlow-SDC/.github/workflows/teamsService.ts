/**
 * Microsoft Teams Integration Service
 *
 * Handles:
 * - Sending adaptive card notifications to Teams channels
 * - Creating incident war-room channels
 * - Posting updates to existing channels via webhook
 * - Bot Framework activity payloads (for bot-initiated messages)
 */

import axios from 'axios';
import { Client } from '@microsoft/microsoft-graph-client';
import { ConfidentialClientApplication } from '@azure/msal-node';
import logger from '../../utils/logger';

interface TeamsConfig {
  clientId: string;
  clientSecret: string;
  tenantId: string;
  botId: string;
  botPassword: string;
  webhookBaseUrl: string;
}

interface AdaptiveCardBody {
  type: string;
  [key: string]: unknown;
}

interface IncidentCardData {
  incidentNumber: string;
  title: string;
  priority: string;
  status: string;
  property?: string;
  assignedTo?: string;
  openedAt: string;
  dashboardUrl: string;
}

interface TacCaseCardData {
  caseNumber: string;
  title: string;
  severity: string;
  status: string;
  tacEngineer?: string;
  openedAt: string;
  dashboardUrl: string;
}

class TeamsService {
  private config: TeamsConfig;
  private msalApp: ConfidentialClientApplication | null = null;
  private graphClient: Client | null = null;

  constructor() {
    this.config = {
      clientId: process.env.TEAMS_CLIENT_ID || '',
      clientSecret: process.env.TEAMS_CLIENT_SECRET || '',
      tenantId: process.env.TEAMS_TENANT_ID || '',
      botId: process.env.TEAMS_BOT_ID || '',
      botPassword: process.env.TEAMS_BOT_PASSWORD || '',
      webhookBaseUrl: process.env.TEAMS_WEBHOOK_BASE_URL || '',
    };

    if (this.config.clientId && this.config.clientSecret && this.config.tenantId) {
      this.msalApp = new ConfidentialClientApplication({
        auth: {
          clientId: this.config.clientId,
          clientSecret: this.config.clientSecret,
          authority: `https://login.microsoftonline.com/${this.config.tenantId}`,
        },
      });
    }
  }

  private isConfigured(): boolean {
    return !!(this.config.clientId && this.config.clientSecret && this.config.tenantId);
  }

  private async getAccessToken(): Promise<string> {
    if (!this.msalApp) throw new Error('Teams MSAL not configured');

    const result = await this.msalApp.acquireTokenByClientCredential({
      scopes: ['https://graph.microsoft.com/.default'],
    });

    if (!result?.accessToken) throw new Error('Failed to acquire Teams access token');
    return result.accessToken;
  }

  private getGraphClient(): Client {
    if (!this.graphClient) {
      this.graphClient = Client.initWithMiddleware({
        authProvider: {
          getAccessToken: async () => this.getAccessToken(),
        },
      });
    }
    return this.graphClient;
  }

  /**
   * Send an adaptive card to a channel webhook URL
   */
  async sendWebhookMessage(webhookUrl: string, card: AdaptiveCardBody): Promise<void> {
    try {
      await axios.post(webhookUrl, {
        type: 'message',
        attachments: [
          {
            contentType: 'application/vnd.microsoft.card.adaptive',
            contentUrl: null,
            content: card,
          },
        ],
      });
      logger.info('Teams webhook message sent successfully');
    } catch (error) {
      logger.error('Failed to send Teams webhook message:', error);
      throw error;
    }
  }

  /**
   * Build an adaptive card for an incident notification
   */
  buildIncidentCard(data: IncidentCardData): AdaptiveCardBody {
    const priorityColors: Record<string, string> = {
      P1: 'attention',
      P2: 'warning',
      P3: 'accent',
      P4: 'good',
    };
    const color = priorityColors[data.priority] || 'default';

    return {
      type: 'AdaptiveCard',
      $schema: 'http://adaptivecards.io/schemas/adaptive-card.json',
      version: '1.4',
      body: [
        {
          type: 'Container',
          style: color,
          items: [
            {
              type: 'TextBlock',
              text: `🚨 Incident ${data.incidentNumber} — ${data.priority}`,
              weight: 'bolder',
              size: 'medium',
              color: 'light',
            },
          ],
        },
        {
          type: 'Container',
          items: [
            { type: 'TextBlock', text: data.title, wrap: true, weight: 'bolder' },
            {
              type: 'FactSet',
              facts: [
                { title: 'Priority', value: data.priority },
                { title: 'Status', value: data.status },
                { title: 'Property', value: data.property || 'N/A' },
                { title: 'Assigned To', value: data.assignedTo || 'Unassigned' },
                { title: 'Opened', value: data.openedAt },
              ],
            },
          ],
        },
      ],
      actions: [
        {
          type: 'Action.OpenUrl',
          title: 'View in ServiceFlow',
          url: data.dashboardUrl,
        },
      ],
    };
  }

  /**
   * Build an adaptive card for a TAC case notification
   */
  buildTacCaseCard(data: TacCaseCardData): AdaptiveCardBody {
    const severityColors: Record<string, string> = {
      '1': 'attention',
      '2': 'warning',
      '3': 'accent',
      '4': 'good',
    };
    const color = severityColors[data.severity] || 'default';

    return {
      type: 'AdaptiveCard',
      $schema: 'http://adaptivecards.io/schemas/adaptive-card.json',
      version: '1.4',
      body: [
        {
          type: 'Container',
          style: color,
          items: [
            {
              type: 'TextBlock',
              text: `🔧 TAC Case ${data.caseNumber} — SEV-${data.severity}`,
              weight: 'bolder',
              size: 'medium',
              color: 'light',
            },
          ],
        },
        {
          type: 'Container',
          items: [
            { type: 'TextBlock', text: data.title, wrap: true, weight: 'bolder' },
            {
              type: 'FactSet',
              facts: [
                { title: 'Severity', value: `SEV-${data.severity}` },
                { title: 'Status', value: data.status },
                { title: 'TAC Engineer', value: data.tacEngineer || 'Pending' },
                { title: 'Opened', value: data.openedAt },
              ],
            },
          ],
        },
      ],
      actions: [
        {
          type: 'Action.OpenUrl',
          title: 'View TAC Case',
          url: data.dashboardUrl,
        },
      ],
    };
  }

  /**
   * Send incident alert to a Teams channel
   */
  async notifyIncident(webhookUrl: string, data: IncidentCardData): Promise<void> {
    if (!webhookUrl) {
      logger.warn('Teams: No webhook URL provided for incident notification');
      return;
    }
    const card = this.buildIncidentCard(data);
    await this.sendWebhookMessage(webhookUrl, card);
  }

  /**
   * Send TAC case alert to a Teams channel
   */
  async notifyTacCase(webhookUrl: string, data: TacCaseCardData): Promise<void> {
    if (!webhookUrl) {
      logger.warn('Teams: No webhook URL provided for TAC case notification');
      return;
    }
    const card = this.buildTacCaseCard(data);
    await this.sendWebhookMessage(webhookUrl, card);
  }

  /**
   * Create a new Teams channel in a team (requires Graph API)
   */
  async createChannel(
    teamId: string,
    channelName: string,
    description?: string
  ): Promise<{ id: string; displayName: string; webUrl: string }> {
    if (!this.isConfigured()) {
      throw new Error('Teams Graph API not configured — set TEAMS_CLIENT_ID, CLIENT_SECRET, TENANT_ID');
    }

    try {
      const client = this.getGraphClient();
      const channel = await client.api(`/teams/${teamId}/channels`).post({
        displayName: channelName,
        description: description || '',
        membershipType: 'standard',
      });
      logger.info(`Teams channel created: ${channelName} (${channel.id})`);
      return {
        id: channel.id,
        displayName: channel.displayName,
        webUrl: channel.webUrl,
      };
    } catch (error) {
      logger.error('Failed to create Teams channel:', error);
      throw error;
    }
  }

  /**
   * Post a plain text message to a Teams channel via Graph API
   */
  async postChannelMessage(teamId: string, channelId: string, message: string): Promise<void> {
    if (!this.isConfigured()) {
      logger.warn('Teams Graph API not configured — skipping channel message');
      return;
    }

    try {
      const client = this.getGraphClient();
      await client.api(`/teams/${teamId}/channels/${channelId}/messages`).post({
        body: { contentType: 'html', content: message },
      });
      logger.info('Teams channel message posted');
    } catch (error) {
      logger.error('Failed to post Teams channel message:', error);
      throw error;
    }
  }

  /**
   * Send an SLA breach alert
   */
  async notifySlaBreath(
    webhookUrl: string,
    incidentNumber: string,
    property: string,
    priority: string,
    openedAt: string,
    dashboardUrl: string
  ): Promise<void> {
    if (!webhookUrl) return;

    const card: AdaptiveCardBody = {
      type: 'AdaptiveCard',
      $schema: 'http://adaptivecards.io/schemas/adaptive-card.json',
      version: '1.4',
      body: [
        {
          type: 'Container',
          style: 'attention',
          items: [
            {
              type: 'TextBlock',
              text: `⏰ SLA BREACH — ${incidentNumber}`,
              weight: 'bolder',
              size: 'large',
              color: 'light',
            },
          ],
        },
        {
          type: 'Container',
          items: [
            {
              type: 'TextBlock',
              text: 'An incident has breached its SLA target.',
              wrap: true,
            },
            {
              type: 'FactSet',
              facts: [
                { title: 'Incident', value: incidentNumber },
                { title: 'Property', value: property },
                { title: 'Priority', value: priority },
                { title: 'Opened', value: openedAt },
              ],
            },
          ],
        },
      ],
      actions: [
        { type: 'Action.OpenUrl', title: 'Take Action Now', url: dashboardUrl },
      ],
    };

    await this.sendWebhookMessage(webhookUrl, card);
  }
}

export const teamsService = new TeamsService();
export default teamsService;
