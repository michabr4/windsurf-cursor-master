import dotenv from "dotenv";

dotenv.config({ path: new URL("../../.env", import.meta.url) });

export class WebexClient {
  constructor() {
    this.accessToken = process.env.WEBEX_ACCESS_TOKEN;
    this.baseUrl = (process.env.WEBEX_API_BASE_URL || "https://webexapis.com/v1").replace(/\/$/, "");
    this.maxPageSize = Number(process.env.WEBEX_MAX_PAGE_SIZE || 50);
  }

  requireToken() {
    if (!this.accessToken) {
      throw new Error("Missing required environment variable: WEBEX_ACCESS_TOKEN");
    }
    return this.accessToken;
  }

  buildHeaders() {
    return {
      Authorization: `Bearer ${this.requireToken()}`,
      "Content-Type": "application/json"
    };
  }

  async getAllPages(path, params = {}) {
    const items = [];
    let nextUrl = new URL(`${this.baseUrl}${path}`);

    for (const [key, value] of Object.entries({ max: this.maxPageSize, ...params })) {
      nextUrl.searchParams.set(key, String(value));
    }

    while (nextUrl) {
      const response = await fetch(nextUrl, { headers: this.buildHeaders() });
      if (!response.ok) {
        throw new Error(`Webex request failed with status ${response.status}`);
      }

      const json = await response.json();
      items.push(...(json.items || []));

      // Webex pagination uses an HTTP Link header instead of a body field.
      const linkHeader = response.headers.get("link") || "";
      const nextMatch = linkHeader.match(/<([^>]+)>;\s*rel="next"/i);
      nextUrl = nextMatch ? new URL(nextMatch[1]) : null;
    }

    return items;
  }

  listSpaces() {
    // The API path is /rooms, but most users know these as spaces.
    return this.getAllPages("/rooms");
  }

  listMessages(roomId) {
    return this.getAllPages("/messages", { roomId });
  }

  listRecordings() {
    return this.getAllPages("/recordings");
  }

  listTranscripts() {
    return this.getAllPages("/meeting/transcripts");
  }

  async getTranscriptDetails(transcriptId) {
    const response = await fetch(`${this.baseUrl}/meeting/transcripts/${transcriptId}`, {
      headers: this.buildHeaders()
    });

    if (!response.ok) {
      throw new Error(`Transcript request failed with status ${response.status}`);
    }

    return response.json();
  }
}
