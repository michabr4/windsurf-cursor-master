const FETCH_TIMEOUT_MS = 15_000;

export interface MimirDevice {
  deviceName: string;
  ipAddress: string;
  productId: string;
  swVersion: string;
  role: string;
}

export interface MimirPsirtSummary {
  totalCount: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface MimirFnSummary {
  totalCount: number;
  affectedDevices: number;
}

export interface MimirQbrComposite {
  riskComposite: number;
  psirtScore: number;
  fnScore: number;
  hwLifecycleScore: number;
  swLifecycleScore: number;
}

export interface MimirBenchmark {
  psirtCountPeerComparison: unknown;
  fnCountPeerComparison: unknown;
}

export interface MimirBpSummary {
  complianceScore: number;
  passCount: number;
  failCount: number;
}

type MimirEnvelope<T> = {
  meta?: { pagination?: unknown; attributes?: unknown; status?: unknown };
  data?: T;
};

type OAuthTokenResponse = {
  access_token?: string;
  expires_in?: number;
};

function companyQuery(companyId: string): string {
  return `companyId=${encodeURIComponent(companyId)}`;
}

export class MimirClient {
  private tokenCache: { token: string; expiresAt: number } | null = null;

  constructor(
    private readonly baseUrl: string,
    private readonly tokenUrl: string,
    private readonly clientId: string,
    private readonly clientSecret: string
  ) {}

  private async getAccessToken(): Promise<string> {
    if (!this.clientId || !this.clientSecret) return "";

    if (this.tokenCache && Date.now() < this.tokenCache.expiresAt) {
      return this.tokenCache.token;
    }

    try {
      const body = new URLSearchParams({
        grant_type: "client_credentials",
        client_id: this.clientId,
        client_secret: this.clientSecret
      });

      const response = await fetch(this.tokenUrl, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
        signal: AbortSignal.timeout(FETCH_TIMEOUT_MS)
      });

      if (!response.ok) {
        console.warn(
          JSON.stringify({
            level: "warn",
            message: "mimir_oauth_failed",
            status: response.status
          })
        );
        return "";
      }

      const json = (await response.json()) as OAuthTokenResponse;
      const token = json.access_token ?? "";
      if (!token) return "";

      const expiresIn = typeof json.expires_in === "number" && json.expires_in > 60 ? json.expires_in : 3600;
      this.tokenCache = {
        token,
        expiresAt: Date.now() + (expiresIn - 60) * 1000
      };
      return token;
    } catch (err) {
      console.warn(
        JSON.stringify({
          level: "warn",
          message: "mimir_oauth_error",
          error: err instanceof Error ? err.message : String(err)
        })
      );
      return "";
    }
  }

  private async fetchEnvelope<T>(path: string, context: string): Promise<T | null> {
    const token = await this.getAccessToken();
    if (!token) return null;

    const url = `${this.baseUrl.replace(/\/$/, "")}${path}`;
    try {
      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
        signal: AbortSignal.timeout(FETCH_TIMEOUT_MS)
      });

      if (!response.ok) {
        console.warn(
          JSON.stringify({
            level: "warn",
            message: "mimir_request_failed",
            context,
            status: response.status
          })
        );
        return null;
      }

      const json = (await response.json()) as MimirEnvelope<T>;
      return (json.data ?? null) as T | null;
    } catch (err) {
      console.warn(
        JSON.stringify({
          level: "warn",
          message: "mimir_request_error",
          context,
          error: err instanceof Error ? err.message : String(err)
        })
      );
      return null;
    }
  }

  private unwrapRecord<T>(data: T | T[] | null): T | null {
    if (data == null) return null;
    if (Array.isArray(data)) {
      if (data.length === 0) return null;
      return data[0] ?? null;
    }
    return data;
  }

  async getNpDevices(companyId: string): Promise<MimirDevice[]> {
    const data = await this.fetchEnvelope<MimirDevice[] | MimirDevice>(
      `/np/devices?${companyQuery(companyId)}`,
      "getNpDevices"
    );
    if (data == null) return [];
    return Array.isArray(data) ? data : [data];
  }

  async getPsirtSummary(companyId: string): Promise<MimirPsirtSummary | null> {
    const data = await this.fetchEnvelope<MimirPsirtSummary | MimirPsirtSummary[]>(
      `/np/psirt-summary?${companyQuery(companyId)}`,
      "getPsirtSummary"
    );
    return this.unwrapRecord(data);
  }

  async getFnSummary(companyId: string): Promise<MimirFnSummary | null> {
    const data = await this.fetchEnvelope<MimirFnSummary | MimirFnSummary[]>(
      `/np/fn-summary?${companyQuery(companyId)}`,
      "getFnSummary"
    );
    return this.unwrapRecord(data);
  }

  async getQbrComposite(companyId: string): Promise<MimirQbrComposite | null> {
    const data = await this.fetchEnvelope<MimirQbrComposite | MimirQbrComposite[]>(
      `/qbr/risk-composite?${companyQuery(companyId)}`,
      "getQbrComposite"
    );
    return this.unwrapRecord(data);
  }

  async getBcibmPeerComparison(companyId: string): Promise<MimirBenchmark | null> {
    const data = await this.fetchEnvelope<MimirBenchmark | MimirBenchmark[]>(
      `/bcibm/psirt-count-peer-comparison?${companyQuery(companyId)}`,
      "getBcibmPeerComparison"
    );
    return this.unwrapRecord(data);
  }

  async getBpSummary(companyId: string): Promise<MimirBpSummary | null> {
    const data = await this.fetchEnvelope<MimirBpSummary | MimirBpSummary[]>(
      `/compliance/bp-summary?${companyQuery(companyId)}`,
      "getBpSummary"
    );
    return this.unwrapRecord(data);
  }

  async getPsirtDetails(companyId: string): Promise<unknown[]> {
    const data = await this.fetchEnvelope<unknown[] | unknown>(
      `/np/psirt-details?${companyQuery(companyId)}`,
      "getPsirtDetails"
    );
    if (data == null) return [];
    return Array.isArray(data) ? data : [data];
  }

  async getFnDetails(companyId: string): Promise<unknown[]> {
    const data = await this.fetchEnvelope<unknown[] | unknown>(
      `/np/fn-details?${companyQuery(companyId)}`,
      "getFnDetails"
    );
    if (data == null) return [];
    return Array.isArray(data) ? data : [data];
  }

  async getRiskMitigationSummary(companyId: string): Promise<unknown | null> {
    const data = await this.fetchEnvelope<unknown | unknown[]>(
      `/bciapi/risk-mitigation-summary?${companyQuery(companyId)}`,
      "getRiskMitigationSummary"
    );
    return this.unwrapRecord(data);
  }
}

export function createMimirClient(env: {
  MIMIR_BASE_URL: string;
  MIMIR_OAUTH_TOKEN_URL: string;
  MIMIR_CLIENT_ID: string;
  MIMIR_CLIENT_SECRET: string;
}): MimirClient {
  return new MimirClient(
    env.MIMIR_BASE_URL,
    env.MIMIR_OAUTH_TOKEN_URL,
    env.MIMIR_CLIENT_ID,
    env.MIMIR_CLIENT_SECRET
  );
}
