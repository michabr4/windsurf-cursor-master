"""Configuration management for Status Report Agent."""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Salesforce Configuration
    sf_instance_url: str = Field(default="", env="SF_INSTANCE_URL")
    sf_client_id: str = Field(default="", env="SF_CLIENT_ID")
    sf_client_secret: str = Field(default="", env="SF_CLIENT_SECRET")
    sf_username: str = Field(default="", env="SF_USERNAME")
    sf_password: str = Field(default="", env="SF_PASSWORD")
    sf_security_token: str = Field(default="", env="SF_SECURITY_TOKEN")
    
    # ServiceNow Configuration
    sn_instance_url: str = Field(default="", env="SN_INSTANCE_URL")
    sn_username: str = Field(default="", env="SN_USERNAME")
    sn_password: str = Field(default="", env="SN_PASSWORD")
    sn_client_id: Optional[str] = Field(default=None, env="SN_CLIENT_ID")
    sn_client_secret: Optional[str] = Field(default=None, env="SN_CLIENT_SECRET")
    
    # Azure OpenAI Configuration
    azure_openai_endpoint: str = Field(default="", env="AZURE_OPENAI_ENDPOINT")
    azure_openai_key: str = Field(default="", env="AZURE_OPENAI_KEY")
    azure_openai_deployment: str = Field(default="gpt-4o", env="AZURE_OPENAI_DEPLOYMENT")
    azure_openai_api_version: str = Field(default="2024-02-15-preview", env="AZURE_OPENAI_API_VERSION")
    
    # Alternative: OpenAI direct
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", env="OPENAI_MODEL")
    
    # LLM Provider selection
    llm_provider: str = Field(default="azure", env="LLM_PROVIDER")  # "azure" or "openai"
    
    # Agent Configuration
    lookback_days: int = Field(default=7, env="LOOKBACK_DAYS")
    report_template: str = Field(default="default", env="REPORT_TEMPLATE")
    output_dir: str = Field(default="./output", env="OUTPUT_DIR")
    output_format: str = Field(default="markdown", env="OUTPUT_FORMAT")
    
    # Role Configuration (which role's perspective for the report)
    role: str = Field(default="SDM", env="AGENT_ROLE")  # SDM, PM, or PgM
    
    # Account/Customer filter (optional)
    account_filter: Optional[str] = Field(default=None, env="ACCOUNT_FILTER")
    
    # Email delivery
    smtp_server: Optional[str] = Field(default=None, env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    report_recipients: str = Field(default="", env="REPORT_RECIPIENTS")
    
    # Webex delivery (optional)
    webex_access_token: Optional[str] = Field(default=None, env="WEBEX_ACCESS_TOKEN")
    webex_room_id: Optional[str] = Field(default=None, env="WEBEX_ROOM_ID")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
    
    @property
    def recipients_list(self) -> List[str]:
        """Parse comma-separated recipients into list."""
        if not self.report_recipients:
            return []
        return [r.strip() for r in self.report_recipients.split(",") if r.strip()]
    
    def validate_salesforce(self) -> bool:
        """Check if Salesforce credentials are configured."""
        return bool(self.sf_instance_url and self.sf_username)
    
    def validate_servicenow(self) -> bool:
        """Check if ServiceNow credentials are configured."""
        return bool(self.sn_instance_url and self.sn_username)
    
    def validate_llm(self) -> bool:
        """Check if LLM credentials are configured."""
        if self.llm_provider == "azure":
            return bool(self.azure_openai_endpoint and self.azure_openai_key)
        return bool(self.openai_api_key)


def get_settings() -> Settings:
    """Factory function to get settings instance."""
    return Settings()
