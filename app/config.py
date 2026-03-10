from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mqtt_broker: str = "localhost"
    mqqt_port: int = 1883
    mqqt_topic_prefix: str = "greenhouse"

    api_host: str = "localhost"
    api_port: int = 8000
    debug: bool = True

    DATABASE_URL: str = "sqlite:///./greenhouse.db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    class Congif:
        env_file = ".env"


settings = Settings()
