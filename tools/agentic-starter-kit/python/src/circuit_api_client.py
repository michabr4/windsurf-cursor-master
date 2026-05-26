import base64
import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv


load_dotenv()


class CircuitApiClient:
    def __init__(self) -> None:
        self.client_id = os.getenv("BRIDGE_API_CLIENT_ID")
        self.client_secret = os.getenv("BRIDGE_API_CLIENT_SECRET")
        self.token_url = os.getenv(
            "BRIDGE_API_TOKEN_URL", "https://id.cisco.com/oauth2/default/v1/token"
        )
        self.chat_base_url = os.getenv("CISCO_CHAT_API_BASE_URL", "https://chat-ai.cisco.com")
        self.app_key = os.getenv("BRIDGE_API_APP_KEY")
        self.user_id = os.getenv("CISCO_BRAIN_USER_ID")
        self.chat_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.model = os.getenv("CISCO_CHAT_MODEL", "gpt-4.1")
        self.api_version = os.getenv("CISCO_CHAT_API_VERSION", "2024-12-01-preview")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_api_key = os.getenv("OLLAMA_API_KEY", "")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")

    @staticmethod
    def _env_flag(name: str) -> bool:
        v = os.getenv(name, "").strip().lower()
        return v in ("1", "true", "yes", "on")

    def use_ollama(self) -> bool:
        return self._env_flag("USE_OLLAMA")

    def _require(self, value: str | None, label: str) -> str:
        if not value:
            raise ValueError(f"Missing required environment variable: {label}")
        return value

    def get_bridge_access_token(self) -> str:
        client_id = self._require(self.client_id, "BRIDGE_API_CLIENT_ID")
        client_secret = self._require(self.client_secret, "BRIDGE_API_CLIENT_SECRET")

        # This sample mirrors the original note's Basic-auth client credential flow.
        basic_value = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {basic_value}",
        }

        response = requests.post(
            self.token_url,
            headers=headers,
            data="grant_type=client_credentials",
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("access_token", "")

    def build_chat_completion_url(self) -> str:
        if self.use_ollama():
            base = self.ollama_base_url.rstrip("/")
            if not base.endswith("/v1"):
                base = f"{base}/v1"
            return f"{base}/chat/completions"
        base_url = self.chat_base_url.rstrip("/")
        return f"{base_url}/openai/deployments/{self.model}/chat/completions?api-version={self.api_version}"

    def send_chat_prompt(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> Dict[str, Any]:
        if self.use_ollama():
            headers: Dict[str, str] = {"Content-Type": "application/json"}
            if self.ollama_api_key.strip():
                headers["Authorization"] = f"Bearer {self.ollama_api_key.strip()}"
            payload: Dict[str, Any] = {
                "model": self.ollama_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
            }
        else:
            api_key = self._require(self.chat_api_key, "AZURE_OPENAI_API_KEY")
            app_key = self._require(self.app_key, "BRIDGE_API_APP_KEY")
            user_id = self._require(self.user_id, "CISCO_BRAIN_USER_ID")

            # Keep these values server-side. They identify the app and user context.
            headers = {
                "Content-Type": "application/json",
                "api-key": api_key,
                "x-ms-useragent": f'{{"appkey": "{app_key}", "user": "{user_id}"}}',
            }
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
            }

        response = requests.post(self.build_chat_completion_url(), headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def extract_first_message(response_json: Dict[str, Any]) -> str:
        choices: List[Dict[str, Any]] = response_json.get("choices", [])
        if not choices:
            return ""
        message = choices[0].get("message", {})
        return message.get("content", "")
