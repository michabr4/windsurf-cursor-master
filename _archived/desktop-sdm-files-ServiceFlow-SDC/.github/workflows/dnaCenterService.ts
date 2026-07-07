/**
 * Cisco DNA Center Integration Service
 *
 * Handles:
 * - Device inventory sync from DNA Center
 * - Network health metrics collection
 * - Device detail enrichment (software version, serial, health score)
 * - Token-based authentication with DNA Center API
 *
 * DNA Center API v1/v2:
 *   https://developer.cisco.com/docs/dna-center/
 */

import axios, { AxiosInstance } from 'axios';
import https from 'https';
import logger from '../../utils/logger';

interface DnaCenterConfig {
  host: string;
  username: string;
  password: string;
  port: number;
}

interface DnaDevice {
  id: string;
  hostname: string;
  managementIpAddress: string;
  macAddress?: string;
  serialNumber?: string;
  platformId?: string; // model
  softwareVersion?: string;
  type: string;
  family: string;
  series?: string;
  role: string;
  reachabilityStatus: string;
  reachabilityFailureReason?: string;
  associatedWlcIp?: string;
  collectionStatus: string;
  errorDescription?: string;
  interfaceCount?: string;
  lineCardCount?: string;
  locationName?: string;
  upTime?: string;
  lastUpdated?: string;
  inventoryStatusDetail?: string;
  tag?: string;
  tunnelUdpPort?: string;
  waasDeviceMode?: string;
  /* Health fields */
  overallHealth?: number;
  memoryScore?: number;
  cpuScore?: number;
  noiseScore?: number;
  utilizationScore?: number;
}

interface DnaNetworkHealth {
  healthDistirubution: Array<{
    category: string;
    totalCount: number;
    healthyCount: number;
    unHealthyCount: number;
    healthScore: number;
  }>;
  totalCount: number;
  goodCount: number;
  poorCount: number;
  fairCount: number;
  noHealthCount: number;
  healthScore: number;
  response: Array<{
    time: string;
    healthScore: number;
    goodCount: number;
    poorCount: number;
    fairCount: number;
    unmonCount: number;
  }>;
}

interface DnaTokenResponse {
  Token: string;
}

class DnaCenterService {
  private config: DnaCenterConfig;
  private client: AxiosInstance;
  private token: string | null = null;
  private tokenExpiry: number = 0;

  constructor() {
    this.config = {
      host: process.env.DNA_CENTER_HOST || '',
      username: process.env.DNA_CENTER_USERNAME || '',
      password: process.env.DNA_CENTER_PASSWORD || '',
      port: parseInt(process.env.DNA_CENTER_PORT || '443', 10),
    };

    this.client = axios.create({
      baseURL: `https://${this.config.host}:${this.config.port}/dna/intent/api`,
      timeout: 30000,
      httpsAgent: new https.Agent({ rejectUnauthorized: false }), // DNAC often uses self-signed certs
      headers: { 'Content-Type': 'application/json' },
    });

    this.client.interceptors.request.use(async (cfg) => {
      const token = await this.getToken();
      if (cfg.headers && token) cfg.headers['X-Auth-Token'] = token;
      return cfg;
    });
  }

  isConfigured(): boolean {
    return !!(this.config.host && this.config.username && this.config.password);
  }

  /**
   * Authenticate with DNA Center and get a session token
   */
  async getToken(): Promise<string | null> {
    if (this.token && Date.now() < this.tokenExpiry) return this.token;
    if (!this.isConfigured()) {
      logger.warn('DNA Center: not configured');
      return null;
    }

    try {
      const { data } = await axios.post<DnaTokenResponse>(
        `https://${this.config.host}:${this.config.port}/dna/system/api/v1/auth/token`,
        {},
        {
          auth: { username: this.config.username, password: this.config.password },
          httpsAgent: new https.Agent({ rejectUnauthorized: false }),
          timeout: 15000,
        }
      );
      this.token = data.Token;
      this.tokenExpiry = Date.now() + 55 * 60 * 1000; // tokens last ~1h, refresh at 55m
      logger.info('DNA Center: authenticated successfully');
      return this.token;
    } catch (error) {
      logger.error('DNA Center: authentication failed:', error);
      return null;
    }
  }

  /**
   * Get full device inventory
   */
  async getDevices(limit = 500, offset = 1): Promise<DnaDevice[]> {
    if (!this.isConfigured()) return [];

    try {
      const { data } = await this.client.get<{ response: DnaDevice[] }>('/v1/network-device', {
        params: { limit, offset },
      });
      return data.response || [];
    } catch (error) {
      logger.error('DNA Center: failed to fetch device inventory:', error);
      return [];
    }
  }

  /**
   * Get a single device by ID
   */
  async getDevice(deviceId: string): Promise<DnaDevice | null> {
    if (!this.isConfigured()) return null;

    try {
      const { data } = await this.client.get<{ response: DnaDevice }>(
        `/v1/network-device/${deviceId}`
      );
      return data.response;
    } catch (error) {
      logger.error(`DNA Center: failed to fetch device ${deviceId}:`, error);
      return null;
    }
  }

  /**
   * Get device by management IP
   */
  async getDeviceByIp(ipAddress: string): Promise<DnaDevice | null> {
    if (!this.isConfigured()) return null;

    try {
      const { data } = await this.client.get<{ response: DnaDevice[] }>('/v1/network-device', {
        params: { managementIpAddress: ipAddress },
      });
      return data.response?.[0] || null;
    } catch (error) {
      logger.error(`DNA Center: failed to fetch device by IP ${ipAddress}:`, error);
      return null;
    }
  }

  /**
   * Get overall network health summary
   */
  async getNetworkHealth(): Promise<DnaNetworkHealth | null> {
    if (!this.isConfigured()) return null;

    try {
      const { data } = await this.client.get<DnaNetworkHealth>('/v1/network-health', {
        params: { timestamp: Date.now() },
      });
      return data;
    } catch (error) {
      logger.error('DNA Center: failed to fetch network health:', error);
      return null;
    }
  }

  /**
   * Get device health details for a specific device
   */
  async getDeviceHealth(deviceId: string): Promise<Record<string, unknown> | null> {
    if (!this.isConfigured()) return null;

    try {
      const { data } = await this.client.get<{ response: unknown[] }>(
        '/v1/device-health',
        { params: { deviceRole: 'ALL', timestamp: Date.now() } }
      );
      const devices = data.response || [];
      return (devices as Record<string, unknown>[]).find(
        (d) => d['id'] === deviceId
      ) || null;
    } catch (error) {
      logger.error(`DNA Center: failed to fetch device health for ${deviceId}:`, error);
      return null;
    }
  }

  /**
   * Get all interfaces for a device
   */
  async getDeviceInterfaces(deviceId: string): Promise<Record<string, unknown>[]> {
    if (!this.isConfigured()) return [];

    try {
      const { data } = await this.client.get<{ response: unknown[] }>(
        `/v1/interface/network-device/${deviceId}`
      );
      return (data.response || []) as Record<string, unknown>[];
    } catch (error) {
      logger.error(`DNA Center: failed to fetch interfaces for device ${deviceId}:`, error);
      return [];
    }
  }

  /**
   * Map DNA Center device to ServiceFlow device DB format
   */
  mapDeviceToDb(dnaDevice: DnaDevice): Record<string, unknown> {
    return {
      hostname: dnaDevice.hostname,
      ip_address: dnaDevice.managementIpAddress,
      mac_address: dnaDevice.macAddress || null,
      serial_number: dnaDevice.serialNumber || null,
      device_type: dnaDevice.type,
      device_category: dnaDevice.family,
      model: dnaDevice.platformId || null,
      vendor: 'Cisco',
      software_version: dnaDevice.softwareVersion || null,
      role: dnaDevice.role,
      status: dnaDevice.reachabilityStatus === 'Reachable' ? 'active' : 'failed',
      health_score: dnaDevice.overallHealth ?? null,
      cpu_utilization: dnaDevice.utilizationScore ?? null,
      memory_utilization: dnaDevice.memoryScore ?? null,
      last_seen: dnaDevice.lastUpdated
        ? new Date(dnaDevice.lastUpdated).toISOString()
        : null,
      dna_managed: true,
      dna_device_id: dnaDevice.id,
    };
  }

  /**
   * Sync all DNA Center devices into ServiceFlow (returns mapped records)
   */
  async syncDevices(): Promise<Record<string, unknown>[]> {
    if (!this.isConfigured()) {
      logger.warn('DNA Center: not configured, skipping sync');
      return [];
    }

    logger.info('DNA Center: starting device sync...');
    let offset = 1;
    const limit = 500;
    const allDevices: DnaDevice[] = [];

    while (true) {
      const batch = await this.getDevices(limit, offset);
      if (batch.length === 0) break;
      allDevices.push(...batch);
      if (batch.length < limit) break;
      offset += limit;
    }

    logger.info(`DNA Center: fetched ${allDevices.length} devices`);
    return allDevices.map((d) => this.mapDeviceToDb(d));
  }
}

export const dnaCenterService = new DnaCenterService();
export default dnaCenterService;
