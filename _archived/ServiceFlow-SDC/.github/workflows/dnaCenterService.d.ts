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
interface DnaDevice {
    id: string;
    hostname: string;
    managementIpAddress: string;
    macAddress?: string;
    serialNumber?: string;
    platformId?: string;
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
declare class DnaCenterService {
    private config;
    private client;
    private token;
    private tokenExpiry;
    constructor();
    isConfigured(): boolean;
    /**
     * Authenticate with DNA Center and get a session token
     */
    getToken(): Promise<string | null>;
    /**
     * Get full device inventory
     */
    getDevices(limit?: number, offset?: number): Promise<DnaDevice[]>;
    /**
     * Get a single device by ID
     */
    getDevice(deviceId: string): Promise<DnaDevice | null>;
    /**
     * Get device by management IP
     */
    getDeviceByIp(ipAddress: string): Promise<DnaDevice | null>;
    /**
     * Get overall network health summary
     */
    getNetworkHealth(): Promise<DnaNetworkHealth | null>;
    /**
     * Get device health details for a specific device
     */
    getDeviceHealth(deviceId: string): Promise<Record<string, unknown> | null>;
    /**
     * Get all interfaces for a device
     */
    getDeviceInterfaces(deviceId: string): Promise<Record<string, unknown>[]>;
    /**
     * Map DNA Center device to ServiceFlow device DB format
     */
    mapDeviceToDb(dnaDevice: DnaDevice): Record<string, unknown>;
    /**
     * Sync all DNA Center devices into ServiceFlow (returns mapped records)
     */
    syncDevices(): Promise<Record<string, unknown>[]>;
}
export declare const dnaCenterService: DnaCenterService;
export default dnaCenterService;
//# sourceMappingURL=dnaCenterService.d.ts.map