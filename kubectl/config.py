"""
Configuration
"""
from pydantic import BaseConfig, BaseSettings, Field


class Env(BaseSettings):  # pylint: disable=too-few-public-methods
    """
    Environment variables
    """

    class Config(BaseConfig):  # pylint: disable=too-few-public-methods
        """Config wrapped"""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    FAUNA_SECRET: str = Field(..., env="FAUNA_SECRET")
    API_KEY: str = Field(..., env="API_KEY")
    GITHUB_TOKEN: str = Field(..., env="GITHUB_TOKEN")
    AUTH0_DOMAIN: str = Field(..., env="AUTH0_DOMAIN")
    REDIS_PASSWORD: str = Field(..., env="REDIS_PASSWORD")
    REDIS_HOST: str = Field(..., env="REDIS_HOST")
    REDIS_PORT: int = Field(..., env="REDIS_PORT")
    REDIS_USER: str = Field(..., env="REDIS_USER")
    AWS_ACCESS_KEY_ID: str = Field(..., env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET: str = Field(..., env="AWS_S3_BUCKET")
    AWS_S3_ENDPOINT: str = Field(..., env="AWS_S3_ENDPOINT")
    CF_API_KEY: str = Field(..., env="CF_API_KEY")
    CF_EMAIL: str = Field(..., env="CF_EMAIL")
    CF_ZONE_ID: str = Field(..., env="CF_ZONE_ID")
    CF_ACCOUNT_ID: str = Field(..., env="CF_ACCOUNT_ID")
    IP_ADDR: str = Field(..., env="IP_ADDR")

    def __init__(self, **data):  # pylint: disable=useless-super-delegation
        super().__init__(**data)


env = Env()


# API Endpoints

DOCKER_URL = "https://doctl.smartpro.solutions"

GITHUB_URL = "https://api.github.com"

CLOUDFLARE_URL = "https://api.cloudflare.com/client/v4"

# API Headers

GITHUB_HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {env.GITHUB_TOKEN}",
    "Content-Type": "application/json",
}

CLOUDFLARE_HEADERS = {
    "X-Auth-Email": env.CF_EMAIL,
    "X-Auth-Key": env.CF_API_KEY,
    "Content-Type": "application/json",
}
