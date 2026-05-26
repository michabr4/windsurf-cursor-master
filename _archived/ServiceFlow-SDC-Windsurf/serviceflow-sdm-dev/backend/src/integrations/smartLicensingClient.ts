export class SmartLicensingClient {
  constructor(
    private readonly tokenUrl: string,
    private readonly apiUrl: string,
    private readonly clientId: string,
    private readonly clientSecret: string
  ) {}

  private async accessToken(): Promise<string> {
    if (!this.clientId || !this.clientSecret) return "";
    const body = new URLSearchParams({
      grant_type: "client_credentials",
      client_id: this.clientId,
      client_secret: this.clientSecret
    });
    const response = await fetch(this.tokenUrl, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body
    });
    if (!response.ok) return "";
    const json = await response.json();
    return json?.access_token ?? "";
  }

  async getEntitlements(): Promise<unknown[]> {
    const token = await this.accessToken();
    if (!token) return [];
    const response = await fetch(`${this.apiUrl}/v1/licenses`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!response.ok) return [];
    const json = await response.json();
    return Array.isArray(json?.licenses) ? json.licenses : [];
  }
}
