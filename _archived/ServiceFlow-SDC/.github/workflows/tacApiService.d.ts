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
interface TacApiCase {
    case_id: string;
    case_number: string;
    title: string;
    description: string;
    severity: string;
    status: string;
    sub_status?: string;
    owner?: {
        name: string;
        email: string;
        phone?: string;
        user_id?: string;
    };
    product?: {
        name: string;
        family: string;
        series?: string;
    };
    created_date: string;
    last_modified_date: string;
    resolved_date?: string;
    resolution?: string;
    resolution_code?: string;
}
interface TacApiCaseNote {
    note_id: string;
    case_id: string;
    content: string;
    created_by: string;
    created_date: string;
    note_type: string;
}
interface OpenCaseRequest {
    title: string;
    description: string;
    severity: '1' | '2' | '3' | '4';
    contract_id: string;
    product_name?: string;
    product_family?: string;
    serial_number?: string;
    software_version?: string;
    problem_type?: string;
    contact_name?: string;
    contact_email?: string;
    contact_phone?: string;
}
declare class TacApiService {
    private config;
    private client;
    private accessToken;
    private tokenExpiry;
    constructor();
    private isConfigured;
    /**
     * Obtain OAuth2 client-credentials token from Cisco SSO
     */
    getAccessToken(): Promise<string>;
    /**
     * Open a new TAC case
     */
    openCase(request: OpenCaseRequest): Promise<TacApiCase>;
    /**
     * Fetch a specific case by case number
     */
    getCase(caseNumber: string): Promise<TacApiCase | null>;
    /**
     * Fetch all open cases for our contract
     */
    getOpenCases(): Promise<TacApiCase[]>;
    /**
     * Get case notes/updates
     */
    getCaseNotes(caseNumber: string): Promise<TacApiCaseNote[]>;
    /**
     * Add a note to an existing case
     */
    addCaseNote(caseNumber: string, content: string, noteType?: string): Promise<void>;
    /**
     * Update case severity
     */
    updateSeverity(caseNumber: string, severity: '1' | '2' | '3' | '4'): Promise<void>;
    /**
     * Close a TAC case
     */
    closeCase(caseNumber: string, resolution: string): Promise<void>;
    /**
     * Sync case data from Cisco API to our DB format
     */
    mapApiCaseToDb(apiCase: TacApiCase): Record<string, unknown>;
}
export declare const tacApiService: TacApiService;
export default tacApiService;
//# sourceMappingURL=tacApiService.d.ts.map