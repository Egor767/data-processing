import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")


class DBSettings(BaseModel):
    user: str = os.getenv("DB_USER")
    psw: str = os.getenv("DB_PASSWORD")
    host: str = os.getenv("DB_HOST")
    port: str = os.getenv("DB_PORT")
    name: str = os.getenv("DB_NAME")
    prefix: str = "postgresql+psycopg2"

    @property
    def url(self) -> str:
        return f"{self.prefix}://{self.user}:{self.psw}@{self.host}:{self.port}/{self.name}"


settings = DBSettings()


if __name__=="__main__":
    print(settings.url)
