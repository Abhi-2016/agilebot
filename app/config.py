from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str
    supabase_url: str
    supabase_key: str
    redis_url: str = "redis://localhost:6379"
    azure_bot_app_id: str
    azure_bot_app_password: str
    azure_bot_tenant_id: str
    jira_base_url: str
    jira_email: str
    jira_api_token: str
    jira_project_key: str

    class Config:
        env_file = ".env"


settings = Settings()
