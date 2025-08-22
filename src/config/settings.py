import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    def __init__(self, prefix: str):
        self.host = os.getenv(f"{prefix}_DB_HOST", "localhost")
        self.port = int(os.getenv(f"{prefix}_DB_PORT", "3306"))
        self.username = os.getenv(f"{prefix}_DB_USERNAME", "root")
        self.password = os.getenv(f"{prefix}_DB_PASSWORD", "")
        self.database = os.getenv(f"{prefix}_DB_DATABASE")

class Settings:
    # Configuración base de datos raw (datos sin procesar)
    raw_db = DatabaseConfig("RAW")
    
    # Configuración base de datos transformada (datos procesados)
    pronos_db = DatabaseConfig("PRONOS")
    
    # Configuración de API externa - API-Sports
    api_football_key = os.getenv("API_FOOTBALL_KEY", "")
    api_football_host = os.getenv("API_FOOTBALL_HOST", "v3.football.api-sports.io")
    api_football_base_url = os.getenv("API_FOOTBALL_BASE_URL", "https://v3.football.api-sports.io/")
    api_request_timeout = int(os.getenv("API_REQUEST_TIMEOUT", "30"))
    
    # Configuración de logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE", "logs/pronossport.log")
    
    # Configuración de procesamiento
    batch_size = int(os.getenv("BATCH_SIZE", "100"))
    retry_attempts = int(os.getenv("RETRY_ATTEMPTS", "3"))

settings = Settings()