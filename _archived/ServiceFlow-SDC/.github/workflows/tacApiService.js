"use strict";
/**
 * Cisco TAC API Integration Service
 *
 * Handles:
 * - Opening TAC cases via Cisco Support API
 * - Fetching case status and updates from Cisco
 * - Syncing case state back to ServiceFlow DB
 * - Automatic TAC case creation from P1/P2 incidents
 *
 * Cisco Support API v2:
 *   https://developer.cisco.com/docs/support-apis/
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.tacApiService = void 0;
const axios_1 = __importDefault(require("axios"));
const logger_1 = __importDefault(require("../../utils/logger"));
class TacApiService {
    config;
    client;
    accessToken = null;
    tokenExpiry = 0;
    constructor() {
        this.config = {
            apiKey: process.env.TAC_API_KEY || '',
            apiSecret: process.env.TAC_API_SECRET || '',
            baseUrl: process.env.TAC_BASE_URL || 'https://apix.cisco.com/case/v3',
            contractNumber: process.env.TAC_CONTRACT_NUMBER || '',
            tokenUrl: 'https://cloudsso.cisco.com/as/token.oauth2',
        };
        this.client = axios_1.default.create({
            baseURL: this.config.baseUrl,
            timeout: 30000,
            headers: { 'Content-Type': 'application/json' },
        });
        // Attach token to every request
        this.client.interceptors.request.use(async (cfg) => {
            const token = await this.getAccessToken();
            if (cfg.headers)
                cfg.headers.Authorization = `Bearer ${token}`;
            return cfg;
        });
    }
    isConfigured() {
        return !!(this.config.apiKey && this.config.apiSecret);
    }
    /**
     * Obtain OAuth2 client-credentials token from Cisco SSO
     */
    async getAccessToken() {
        if (this.accessToken && Date.now() < this.tokenExpiry) {
            return this.accessToken;
        }
        if (!this.isConfigured()) {
            logger_1.default.warn('TAC API: credentials not configured, using placeholder token');
            return 'unconfigured';
        }
        try {
            const params = new URLSearchParams({
                grant_type: 'client_credentials',
                client_id: this.config.apiKey,
                client_secret: this.config.apiSecret,
            });
            const { data } = await axios_1.default.post(this.config.tokenUrl, params.toString(), { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
            this.accessToken = data.access_token;
            this.tokenExpiry = Date.now() + (data.expires_in - 60) * 1000;
            return this.accessToken;
        }
        catch (error) {
            logger_1.default.error('TAC API: Failed to obtain access token:', error);
            throw new Error('Unable to authenticate with Cisco TAC API');
        }
    }
    /**
     * Open a new TAC case
     */
    async openCase(request) {
        if (!this.isConfigured()) {
            // Return a mock response in development
            logger_1.default.warn('TAC API not configured — returning mock case');
            const mockNum = `TAC${Date.now()}`;
            return {
                case_id: mockNum,
                case_number: mockNum,
                title: request.title,
                description: request.description,
                severity: request.severity,
                status: 'open',
                created_date: new Date().toISOString(),
                last_modified_date: new Date().toISOString(),
            };
        }
        try {
            const payload = {
                title: request.title,
                description: request.description,
                severity: request.severity,
                contract_id: request.contract_id || this.config.contractNumber,
                product: request.product_name
                    ? { name: request.product_name, family: request.product_family || '' }
                    : undefined,
                serial_number: request.serial_number,
                software_version: request.software_version,
                problem_type: request.problem_type,
                contact: request.contact_name
                    ? {
                        name: request.contact_name,
                        email: request.contact_email,
                        phone: request.contact_phone,
                    }
                    : undefined,
            };
            const { data } = await this.client.post('/cases', payload);
            logger_1.default.info(`TAC case opened: ${data.case_number}`);
            return data;
        }
        catch (error) {
            logger_1.default.error('Failed to open TAC case:', error);
            throw error;
        }
    }
    /**
     * Fetch a specific case by case number
     */
    async getCase(caseNumber) {
        if (!this.isConfigured())
            return null;
        try {
            const { data } = await this.client.get(`/cases/${caseNumber}`);
            return data;
        }
        catch (error) {
            logger_1.default.error(`Failed to fetch TAC case ${caseNumber}:`, error);
            return null;
        }
    }
    /**
     * Fetch all open cases for our contract
     */
    async getOpenCases() {
        if (!this.isConfigured())
            return [];
        try {
            const { data } = await this.client.get('/cases', {
                params: {
                    contract_id: this.config.contractNumber,
                    status: 'open',
                    max_results: 100,
                },
            });
            return data.cases || [];
        }
        catch (error) {
            logger_1.default.error('Failed to fetch open TAC cases:', error);
            return [];
        }
    }
    /**
     * Get case notes/updates
     */
    async getCaseNotes(caseNumber) {
        if (!this.isConfigured())
            return [];
        try {
            const { data } = await this.client.get(`/cases/${caseNumber}/notes`);
            return data.notes || [];
        }
        catch (error) {
            logger_1.default.error(`Failed to fetch notes for TAC case ${caseNumber}:`, error);
            return [];
        }
    }
    /**
     * Add a note to an existing case
     */
    async addCaseNote(caseNumber, content, noteType = 'customer') {
        if (!this.isConfigured()) {
            logger_1.default.warn('TAC API not configured — skipping addCaseNote');
            return;
        }
        try {
            await this.client.post(`/cases/${caseNumber}/notes`, {
                content,
                note_type: noteType,
            });
            logger_1.default.info(`Note added to TAC case ${caseNumber}`);
        }
        catch (error) {
            logger_1.default.error(`Failed to add note to TAC case ${caseNumber}:`, error);
            throw error;
        }
    }
    /**
     * Update case severity
     */
    async updateSeverity(caseNumber, severity) {
        if (!this.isConfigured())
            return;
        try {
            await this.client.patch(`/cases/${caseNumber}`, { severity });
            logger_1.default.info(`TAC case ${caseNumber} severity updated to ${severity}`);
        }
        catch (error) {
            logger_1.default.error(`Failed to update severity for TAC case ${caseNumber}:`, error);
            throw error;
        }
    }
    /**
     * Close a TAC case
     */
    async closeCase(caseNumber, resolution) {
        if (!this.isConfigured())
            return;
        try {
            await this.client.patch(`/cases/${caseNumber}`, {
                status: 'closed',
                resolution,
            });
            logger_1.default.info(`TAC case ${caseNumber} closed`);
        }
        catch (error) {
            logger_1.default.error(`Failed to close TAC case ${caseNumber}:`, error);
            throw error;
        }
    }
    /**
     * Sync case data from Cisco API to our DB format
     */
    mapApiCaseToDb(apiCase) {
        return {
            case_number: apiCase.case_number,
            severity: apiCase.severity,
            title: apiCase.title,
            description: apiCase.description,
            status: apiCase.status,
            sub_status: apiCase.sub_status,
            tac_engineer_name: apiCase.owner?.name || null,
            tac_engineer_email: apiCase.owner?.email || null,
            tac_engineer_phone: apiCase.owner?.phone || null,
            tac_engineer_cco_id: apiCase.owner?.user_id || null,
            product_family: apiCase.product?.family || null,
            product_series: apiCase.product?.series || null,
            resolution: apiCase.resolution || null,
            resolution_code: apiCase.resolution_code || null,
            opened_at: apiCase.created_date,
            last_update_at: apiCase.last_modified_date,
            resolved_at: apiCase.resolved_date || null,
        };
    }
}
exports.tacApiService = new TacApiService();
exports.default = exports.tacApiService;
//# sourceMappingURL=tacApiService.js.map