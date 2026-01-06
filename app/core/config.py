from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"


class ApiPrefix(BaseModel):
    prefix: str = "/internal/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class HashConfig(BaseModel):
    access_secret: str = ""
    refresh_secret: str = ""
    algorithm: str = ""
    access_expire_minutes: int = 30
    refresh_expire_days: int = 30


class CuratorBucketConfig(BaseModel):
    name: str = "curators"

    @property
    def policy(self) -> dict:
        return {
            'Version': '2012-10-17',
            'Statement': [{
                'Sid': 'AddPerm',
                'Effect': 'Allow',
                'Principal': '*',
                'Action': ['s3:GetObject'],
                'Resource': f'arn:aws:s3:::{self.name}/*'
            }]
        }


class S3Config(BaseModel):
    private_host: str = ""
    public_host: str = "http://localhost:9000"
    access_key: str = ""
    secret_key: str = ""
    region: str = ""
    curator_bucket: CuratorBucketConfig = CuratorBucketConfig()


class DatabaseConfig(BaseModel):
    scheme: str = "postgresql+asyncpg"
    name: str = "Alpha_dev"
    user: str = ""
    password: str = ""
    host: str = "pg_db"
    port: int = 5432

    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10
    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def url(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme=self.scheme,
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            path=self.name,
        )

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig = DatabaseConfig()
    hash: HashConfig = HashConfig()
    s3: S3Config = S3Config()


settings = Settings()  # type: ignore
