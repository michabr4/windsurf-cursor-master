import dotenv from "dotenv";

dotenv.config({ path: new URL("../../.env", import.meta.url) });

export class CircuitApiClient {
  constructor() {
    this.clientId = process.env.BRIDGE_API_CLIENT_ID;
    this.clientSecret = process.env.BRIDGE_API_CLIENT_SECRET;
    this.tokenUrl = process.env.BRIDGE_API_TOKEN_URL || "https://id.cisco.com/oauth2/default/v1/token";
    this.chatBaseUrl = process.env.CISCO_CHAT_API_BASE_URL || "https://chat-ai.cisco.com";
    this.appKey = process.env.BRIDGE_API_APP_KEY;
    this.userId = process.env.CISCO_BRAIN_USER_ID;
    this.chatApiKey = process.env.AZURE_OPENAI_API_KEY;
    this.model = process.env.CISCO_CHAT_MODEL || "gpt-4.1";
    this.apiVersion = process.env.CISCO_CHAT_API_VERSION || "2024-12-01-preview";
    this.ollamaBaseUrl = process.env.OLLAMA_BASE_URL || "http://localhost:11434";
    this.ollamaApiKey = process.env.OLLAMA_API_KEY || "";
    this.ollamaModel = process.env.OLLAMA_MODEL || "qwen2.5-coder:7b";
  }

  static envFlag(name) {
    const v = (process.env[name] || "").trim().toLowerCase();
    return ["1", "true", "yes", "on"].includes(v);
  }

  useOllama() {
    return CircuitApiClient.envFlag("USE_OLLAMA");
  }

  requireValue(value, label) {
    if (!value) {
      throw new Error(`Missing required environment variable: ${label}`);
    }
    return value;
  }

  async getBridgeAccessToken() {
    const clientId = this.requireValue(this.clientId, "BRIDGE_API_CLIENT_ID");
    const clientSecret = this.requireValue(this.clientSecret, "BRIDGE_API_CLIENT_SECRET");
    // This sample mirrors the original note's Basic-auth client credential flow.
    const basicValue = Buffer.from(`${clientId}:${clientSecret}`, "utf8").toString("base64");

    const response = await fetch(this.tokenUrl, {
      method: "POST",
      headers: {
        Accept: "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        Authorization: `Basic ${basicValue}`
      },
      body: "grant_type=client_credentials"
    });

    if (!response.ok) {
      throw new Error(`Bridge token request failed with status ${response.status}`);
    }

    const json = await response.json();
    return json.access_token || "";
  }

  buildChatCompletionUrl() {
    if (this.useOllama()) {
      let base = this.ollamaBaseUrl.replace(/\/$/, "");
      if (!base.endsWith("/v1")) {
        base = `${base}/v1`;
      }
      return `${base}/chat/completions`;
    }
    return `${this.chatBaseUrl.replace(/\/$/, "")}/openai/deployments/${this.model}/chat/completions?api-version=${this.apiVersion}`;
  }

  async sendChatPrompt(prompt, systemPrompt = "You are a helpful assistant.") {
    let headers;
    let body;
    if (this.useOllama()) {
      headers = { "Content-Type": "application/json" };
      if (this.ollamaApiKey.trim()) {
        headers.Authorization = `Bearer ${this.ollamaApiKey.trim()}`;
      }
      body = JSON.stringify({
        model: this.ollamaModel,
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: prompt }
        ]
      });
    } else {
      const apiKey = this.requireValue(this.chatApiKey, "AZURE_OPENAI_API_KEY");
      const appKey = this.requireValue(this.appKey, "BRIDGE_API_APP_KEY");
      const userId = this.requireValue(this.userId, "CISCO_BRAIN_USER_ID");

      // Keep these values on the server side so the browser never sees them.
      headers = {
        "Content-Type": "application/json",
        "api-key": apiKey,
        "x-ms-useragent": JSON.stringify({ appkey: appKey, user: userId })
      };
      body = JSON.stringify({
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: prompt }
        ]
      });
    }

    const response = await fetch(this.buildChatCompletionUrl(), {
      method: "POST",
      headers,
      body
    });

    if (!response.ok) {
      throw new Error(`Cisco chat request failed with status ${response.status}`);
    }

    return response.json();
  }

  extractFirstMessage(responseJson) {
    return responseJson?.choices?.[0]?.message?.content || "";
  }
}
