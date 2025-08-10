import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    API1_URL: str = os.getenv("API1_URL", "https://api1.example.com/exchange")
    API1_API_KEY: str = os.getenv("API1_API_KEY", "")

    API2_URL: str = os.getenv("API2_URL", "https://api2.example.com/convert")
    API2_API_KEY: str = os.getenv("API2_API_KEY", "")

    API3_URL: str = os.getenv("API3_URL", "https://api3.example.com/rates")
    API3_API_KEY: str = os.getenv("API3_API_KEY", "")

    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "10"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
