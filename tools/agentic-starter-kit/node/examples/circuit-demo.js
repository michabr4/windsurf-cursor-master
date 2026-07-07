import { CircuitApiClient } from "../src/circuitApiClient.js";

const client = new CircuitApiClient();

try {
  const bridgeToken = await client.getBridgeAccessToken();
  console.log("Bridge access token acquired:", bridgeToken ? "yes" : "no");
} catch (error) {
  console.log("Bridge token request failed:", error.message);
}

try {
  // Keep chat separate from token retrieval so partial configuration still
  // lets users learn from the first half of the example.
  const responseJson = await client.sendChatPrompt("Translate to French: Hello, how are you?");
  console.log("Chat response:");
  console.log(client.extractFirstMessage(responseJson));
} catch (error) {
  console.log("Chat request failed:", error.message);
  console.log(
    "This is expected if chat is not configured: set USE_OLLAMA=1 (default model qwen2.5-coder:7b via OLLAMA_MODEL), or set the Cisco chat variables in .env."
  );
}
