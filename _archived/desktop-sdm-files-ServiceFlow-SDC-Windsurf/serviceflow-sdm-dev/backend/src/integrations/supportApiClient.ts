export class SupportApiClient {
  constructor(
    private readonly apiKey: string,
    private readonly apiSecret: string
  ) {}

  async getContractBySerial(_serialNumber: string): Promise<unknown | null> {
    if (!this.apiKey || !this.apiSecret) return null;
    return null;
  }

  async getEoxByPid(_productId: string): Promise<unknown | null> {
    if (!this.apiKey || !this.apiSecret) return null;
    return null;
  }

  async getBugById(_bugId: string): Promise<unknown | null> {
    if (!this.apiKey || !this.apiSecret) return null;
    return null;
  }
}
