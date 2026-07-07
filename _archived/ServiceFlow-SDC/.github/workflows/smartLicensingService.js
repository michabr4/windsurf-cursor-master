"use strict";
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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.smartLicensingService = void 0;
const axios_1 = __importDefault(require("axios"));
const logger_1 = __importDefault(require("../../utils/logger"));
class SmartLicensingService {
    config;
    client;
    accessToken = null;
    tokenExpiry = 0;
    constructor() {
        this.config = {
            clientId: process.env.SMART_LICENSING_CLIENT_ID || '',
            clientSecret: process.env.SMART_LICENSING_CLIENT_SECRET || '',
            tokenUrl: process.env.SMART_LICENSING_TOKEN_URL ||
                'https://cloudsso.cisco.com/as/token.oauth2',
            apiUrl: process.env.SMART_LICENSING_API_URL ||
                'https://swapi.cisco.com/services/api/smart-accounts-and-licensing/v1',
        };
        this.client = axios_1.default.create({
            baseURL: this.config.apiUrl,
            timeout: 30000,
            headers: { 'Content-Type': 'application/json' },
        });
        this.client.interceptors.request.use(async (cfg) => {
            const token = await this.getAccessToken();
            if (cfg.headers && token)
                cfg.headers.Authorization = `Bearer ${token}`;
            return cfg;
        });
    }
    isConfigured() {
        return !!(this.config.clientId && this.config.clientSecret);
    }
    /**
     * Obtain OAuth2 token from Cisco SSO
     */
    async getAccessToken() {
        if (this.accessToken && Date.now() < this.tokenExpiry)
            return this.accessToken;
        if (!this.isConfigured()) {
            logger_1.default.warn('Smart Licensing: credentials not configured');
            return null;
        }
        try {
            const params = new URLSearchParams({
                grant_type: 'client_credentials',
                client_id: this.config.clientId,
                client_secret: this.config.clientSecret,
            });
            const { data } = await axios_1.default.post(this.config.tokenUrl, params.toString(), { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
            this.accessToken = data.access_token;
            this.tokenExpiry = Date.now() + (data.expires_in - 60) * 1000;
            logger_1.default.info('Smart Licensing: authenticated successfully');
            return this.accessToken;
        }
        catch (error) {
            logger_1.default.error('Smart Licensing: failed to obtain token:', error);
            return null;
        }
    }
    /**
     * Get smart account information and virtual accounts
     */
    async getSmartAccount(accountDomain) {
        if (!this.isConfigured())
            return null;
        try {
            const { data } = await this.client.get(`/accounts/${accountDomain}`);
            return data;
        }
        catch (error) {
            logger_1.default.error('Smart Licensing: failed to fetch smart account:', error);
            return null;
        }
    }
    /**
     * Get all licenses in a virtual account
     */
    async getVirtualAccountLicenses(accountDomain, virtualAccount) {
        if (!this.isConfigured())
            return [];
        try {
            const { data } = await this.client.get(`/accounts/${accountDomain}/virtual-accounts/${virtualAccount}/licenses`);
            return data.licenses || [];
        }
        catch (error) {
            logger_1.default.error(`Smart Licensing: failed to fetch licenses for ${virtualAccount}:`, error);
            return [];
        }
    }
    /**
     * Get license usage summary across all virtual accounts
     */
    async getLicenseUsageSummary(accountDomain) {
        if (!this.isConfigured())
            return [];
        try {
            const { data } = await this.client.get(`/accounts/${accountDomain}/licenses/usage`);
            return data.usages || [];
        }
        catch (error) {
            logger_1.default.error('Smart Licensing: failed to fetch usage summary:', error);
            return [];
        }
    }
    /**
     * Check if a device is compliant for a given license
     */
    async checkDeviceCompliance(accountDomain, deviceId) {
        if (!this.isConfigured())
            return null;
        try {
            const { data } = await this.client.get(`/accounts/${accountDomain}/devices/${deviceId}/compliance`);
            return data;
        }
        catch (error) {
            logger_1.default.error(`Smart Licensing: compliance check failed for device ${deviceId}:`, error);
            return null;
        }
    }
    /**
     * Map Smart Licensing data to ServiceFlow license DB format
     */
    mapLicenseToDb(entitlement, virtualAccount) {
        const status = entitlement.status === 'ACTIVE'
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
    async syncLicenses(accountDomain) {
        if (!this.isConfigured()) {
            logger_1.default.warn('Smart Licensing: not configured, skipping sync');
            return [];
        }
        logger_1.default.info('Smart Licensing: starting license sync...');
        try {
            const account = await this.getSmartAccount(accountDomain);
            if (!account)
                return [];
            const allLicenses = [];
            for (const va of account.virtualAccounts) {
                const licenses = await this.getVirtualAccountLicenses(accountDomain, va.name);
                for (const lic of licenses) {
                    allLicenses.push(this.mapLicenseToDb(lic, va.name));
                }
            }
            logger_1.default.info(`Smart Licensing: synced ${allLicenses.length} license entitlements`);
            return allLicenses;
        }
        catch (error) {
            logger_1.default.error('Smart Licensing: sync failed:', error);
            return [];
        }
    }
    /**
     * Get licenses expiring within N days
     */
    async getExpiringLicenses(accountDomain, daysAhead = 90) {
        const cutoff = new Date(Date.now() + daysAhead * 24 * 60 * 60 * 1000);
        const allUsage = await this.getLicenseUsageSummary(accountDomain);
        // Also pull from virtual accounts
        const account = await this.getSmartAccount(accountDomain);
        if (!account)
            return [];
        const expiring = [];
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
exports.smartLicensingService = new SmartLicensingService();
exports.default = exports.smartLicensingService;
//# sourceMappingURL=smartLicensingService.js.map