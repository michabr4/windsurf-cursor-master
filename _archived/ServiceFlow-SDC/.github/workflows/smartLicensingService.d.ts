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
declare class SmartLicensingService {
    private config;
    private client;
    private accessToken;
    private tokenExpiry;
    constructor();
    isConfigured(): boolean;
    /**
     * Obtain OAuth2 token from Cisco SSO
     */
    getAccessToken(): Promise<string | null>;
    /**
     * Get smart account information and virtual accounts
     */
    getSmartAccount(accountDomain: string): Promise<SmartAccountInfo | null>;
    /**
     * Get all licenses in a virtual account
     */
    getVirtualAccountLicenses(accountDomain: string, virtualAccount: string): Promise<SmartLicenseEntitlement[]>;
    /**
     * Get license usage summary across all virtual accounts
     */
    getLicenseUsageSummary(accountDomain: string): Promise<SmartLicenseUsage[]>;
    /**
     * Check if a device is compliant for a given license
     */
    checkDeviceCompliance(accountDomain: string, deviceId: string): Promise<{
        compliant: boolean;
        licenses: string[];
    } | null>;
    /**
     * Map Smart Licensing data to ServiceFlow license DB format
     */
    mapLicenseToDb(entitlement: SmartLicenseEntitlement, virtualAccount: string): Record<string, unknown>;
    /**
     * Sync all licenses from Smart Licensing to ServiceFlow DB format
     */
    syncLicenses(accountDomain: string): Promise<Record<string, unknown>[]>;
    /**
     * Get licenses expiring within N days
     */
    getExpiringLicenses(accountDomain: string, daysAhead?: number): Promise<SmartLicenseEntitlement[]>;
}
export declare const smartLicensingService: SmartLicensingService;
export default smartLicensingService;
//# sourceMappingURL=smartLicensingService.d.ts.map