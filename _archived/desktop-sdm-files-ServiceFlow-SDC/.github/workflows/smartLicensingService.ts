/**
 * Cisco Smart Licensing Integration Service
 *
 * Handles:
 * - Fetching license entitlements from Cisco Smart Software Manager (SSM)
 * - Syncing license utilization data to ServiceFlow
 * - Checking compliance status
 * - Querying virtual accounts and license pools
 *
 * Cisco Smart Account & Licensing API:
 *   https://developer.cisco.com/docs/smart-account-and-licensing/
 */

import axios, { AxiosInstance } from 'axios';
import logger from '../../utils/logger';

interface SmartLicensingConfig {
  clientId: string;
  clientSecret: string;
  tokenUrl: string;
  apiUrl: string;
}

interface SmartLicenseEntitlement {
  license: string;
  description?: string;
  billingType?: string;
  licenseType?: string;
  quantity: number;
  status: string;
  endDate?: string;
  startDate?: string;
  subscriptionId?: string;
}

interface SmartVirtualAccount {
  name: string;
  accountType: string;
  defaultVirtualAccount: boolean;
  licenses?: SmartLicenseEntitlement[];
}

interface SmartAccountInfo {
  accountName: string;
  accountType: string;
  virtualAccounts: SmartVirtualAccount[];
}

interface SmartLicenseUsage {
  productFamily: string;
  license: string;
  purchased: number;
  inUse: number;
  available: number;
  compliance: 'In Compliance' | 'Out Of Compliance' | 'Insufficient';
  virtualAccount: string;
  expiryDate?: string;
}

class SmartLicensingService {
  private config: SmartLicensingConfig;
  private client: AxiosInstance;
  private accessToken: string | null = null;
  private tokenExpiry: number = 0;

  constructor() {
    this.config = {
      clientId: process.env.SMART_LICENSING_CLIENT_ID || '',
      clientSecret: process.env.SMART_LICENSING_CLIENT_SECRET || '',
      tokenUrl:
        process.env.SMART_LICENSING_TOKEN_URL ||
        'https://cloudsso.cisco.com/as/token.oauth2',
      apiUrl:
        process.env.SMART_LICENSING_API_URL ||
        'https://swapi.cisco.com/services/api/smart-accounts-and-licensing/v1',
    };

    this.client = axios.create({
      baseURL: this.config.apiUrl,
      timeout: 30000,
      headers: { 'Content-Type': 'application/json' },
    });

    this.client.interceptors.request.use(async (cfg) => {
      const token = await this.getAccessToken();
      if (cfg.headers && token) cfg.headers.Authorization = `Bearer ${token}`;
      return cfg;
    });
  }

  isConfigured(): boolean {
    return !!(this.config.clientId && this.config.clientSecret);
  }

  /**
   * Obtain OAuth2 token from Cisco SSO
   */
  async getAccessToken(): Promise<string | null> {
    if (this.accessToken && Date.now() < this.tokenExpiry) return this.accessToken;
    if (!this.isConfigured()) {
      logger.warn('Smart Licensing: credentials not configured');
      return null;
    }

    try {
      const params = new URLSearchParams({
        grant_type: 'client_credentials',
        client_id: this.config.clientId,
        client_secret: this.config.clientSecret,
      });

      const { data } = await axios.post<{ access_token: string; expires_in: number }>(
        this.config.tokenUrl,
        params.toString(),
        { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
      );

      this.accessToken = data.access_token;
      this.tokenExpiry = Date.now() + (data.expires_in - 60) * 1000;
      logger.info('Smart Licensing: authenticated successfully');
      return this.accessToken;
    } catch (error) {
      logger.error('Smart Licensing: failed to obtain token:', error);
      return null;
    }
  }

  /**
   * Get smart account information and virtual accounts
   */
  async getSmartAccount(accountDomain: string): Promise<SmartAccountInfo | null> {
    if (!this.isConfigured()) return null;

    try {
      const { data } = await this.client.get<SmartAccountInfo>(
        `/accounts/${accountDomain}`
      );
      return data;
    } catch (error) {
      logger.error('Smart Licensing: failed to fetch smart account:', error);
      return null;
    }
  }

  /**
   * Get all licenses in a virtual account
   */
  async getVirtualAccountLicenses(
    accountDomain: string,
    virtualAccount: string
  ): Promise<SmartLicenseEntitlement[]> {
    if (!this.isConfigured()) return [];

    try {
      const { data } = await this.client.get<{ licenses: SmartLicenseEntitlement[] }>(
        `/accounts/${accountDomain}/virtual-accounts/${virtualAccount}/licenses`
      );
      return data.licenses || [];
    } catch (error) {
      logger.error(`Smart Licensing: failed to fetch licenses for ${virtualAccount}:`, error);
      return [];
    }
  }

  /**
   * Get license usage summary across all virtual accounts
   */
  async getLicenseUsageSummary(accountDomain: string): Promise<SmartLicenseUsage[]> {
    if (!this.isConfigured()) return [];

    try {
      const { data } = await this.client.get<{ usages: SmartLicenseUsage[] }>(
        `/accounts/${accountDomain}/licenses/usage`
      );
      return data.usages || [];
    } catch (error) {
      logger.error('Smart Licensing: failed to fetch usage summary:', error);
      return [];
    }
  }

  /**
   * Check if a device is compliant for a given license
   */
  async checkDeviceCompliance(
    accountDomain: string,
    deviceId: string
  ): Promise<{ compliant: boolean; licenses: string[] } | null> {
    if (!this.isConfigured()) return null;

    try {
      const { data } = await this.client.get<{ compliant: boolean; licenses: string[] }>(
        `/accounts/${accountDomain}/devices/${deviceId}/compliance`
      );
      return data;
    } catch (error) {
      logger.error(`Smart Licensing: compliance check failed for device ${deviceId}:`, error);
      return null;
    }
  }

  /**
   * Map Smart Licensing data to ServiceFlow license DB format
   */
  mapLicenseToDb(
    entitlement: SmartLicenseEntitlement,
    virtualAccount: string
  ): Record<string, unknown> {
    const status =
      entitlement.status === 'ACTIVE'
        ? 'active'
        : entitlement.status === 'EXPIRED'
        ? 'expired'
        : entitlement.endDate &&
          new Date(entitlement.endDate).getTime() - Date.now() < 90 * 24 * 60 * 60 * 1000
        ? 'expiring'
        : 'active';

    return {
      license_type: entitlement.licenseType || entitlement.license,
      product_family: entitlement.license.split(':')[0] || 'Unknown',
      product_name: entitlement.description || entitlement.license,
      quantity_purchased: entitlement.quantity,
      quantity_consumed: 0, // filled by device sync
      license_model: entitlement.billingType === 'SUBSCRIPTION' ? 'subscription' : 'perpetual',
      start_date: entitlement.startDate ? new Date(entitlement.startDate).toISOString().split('T')[0] : null,
      expiry_date: entitlement.endDate ? new Date(entitlement.endDate).toISOString().split('T')[0] : null,
      status,
      virtual_account: virtualAccount,
      vendor: 'Cisco',
    };
  }

  /**
   * Sync all licenses from Smart Licensing to ServiceFlow DB format
   */
  async syncLicenses(accountDomain: string): Promise<Record<string, unknown>[]> {
    if (!this.isConfigured()) {
      logger.warn('Smart Licensing: not configured, skipping sync');
      return [];
    }

    logger.info('Smart Licensing: starting license sync...');

    try {
      const account = await this.getSmartAccount(accountDomain);
      if (!account) return [];

      const allLicenses: Record<string, unknown>[] = [];

      for (const va of account.virtualAccounts) {
        const licenses = await this.getVirtualAccountLicenses(accountDomain, va.name);
        for (const lic of licenses) {
          allLicenses.push(this.mapLicenseToDb(lic, va.name));
        }
      }

      logger.info(`Smart Licensing: synced ${allLicenses.length} license entitlements`);
      return allLicenses;
    } catch (error) {
      logger.error('Smart Licensing: sync failed:', error);
      return [];
    }
  }

  /**
   * Get licenses expiring within N days
   */
  async getExpiringLicenses(
    accountDomain: string,
    daysAhead = 90
  ): Promise<SmartLicenseEntitlement[]> {
    const cutoff = new Date(Date.now() + daysAhead * 24 * 60 * 60 * 1000);
    const allUsage = await this.getLicenseUsageSummary(accountDomain);

    // Also pull from virtual accounts
    const account = await this.getSmartAccount(accountDomain);
    if (!account) return [];

    const expiring: SmartLicenseEntitlement[] = [];

    for (const va of account.virtualAccounts) {
      const licenses = await this.getVirtualAccountLicenses(accountDomain, va.name);
      for (const lic of licenses) {
        if (lic.endDate && new Date(lic.endDate) <= cutoff) {
          expiring.push(lic);
        }
      }
    }

    void allUsage; // referenced to avoid TS unused warning
    return expiring;
  }
}

export const smartLicensingService = new SmartLicensingService();
export default smartLicensingService;
