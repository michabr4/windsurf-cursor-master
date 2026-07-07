export type DnaDevice = {
  id: string;
  hostname: string;
  managementIpAddress?: string;
  serialNumber?: string;
  reachabilityStatus?: string;
};

export class DnaCenterClient {
  constructor(
    private readonly host: string,
    private readonly username: string,
    private readonly password: string,
    private readonly port: number
  ) {}

  private async token(): Promise<string> {
    const response = await fetch(`https://${this.host}:${this.port}/dna/system/api/v1/auth/token`, {
      method: "POST",
      headers: {
        Authorization: `Basic ${Buffer.from(`${this.username}:${this.password}`).toString("base64")}`
      }
    });
    if (!response.ok) return "";
    const json = await response.json();
    return json?.Token ?? "";
  }

  async listDevices(): Promise<DnaDevice[]> {
    const token = await this.token();
    if (!token) return [];
    const response = await fetch(`https://${this.host}:${this.port}/dna/intent/api/v1/network-device`, {
      headers: { "X-Auth-Token": token }
    });
    if (!response.ok) return [];
    const json = await response.json();
    return Array.isArray(json?.response) ? json.response : [];
  }
}
