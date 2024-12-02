from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # postgresql_database
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_DATABASE: str
    DB_DRIVER: str
    # jwt
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    RESET_PASSWORD_TOKEN_EXPIRE_MINUTES: int
    # minio_s3
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str
    MINIO_URL: str
    MINIO_REGION: str
    # rabbitmq
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_QUEUE_NAME: str
    RESET_PASSWORD_LINK: str
    # Test_database
    TEST_DB_USERNAME: str
    TEST_DB_PASSWORD: str
    TEST_DB_HOST: str
    TEST_DB_DATABASE: str
    # Redis
    REDIS_HOST: str
    REDIS_PORT: int

    @property
    def db_url(self):
        return f"{self.DB_DRIVER}://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

    @property
    def test_db_url(self):
        return f"{self.DB_DRIVER}://{self.TEST_DB_USERNAME}:{self.TEST_DB_PASSWORD}@{self.TEST_DB_HOST}:{self.DB_PORT}/{self.TEST_DB_DATABASE}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
