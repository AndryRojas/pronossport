from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import mysql.connector
from mysql.connector import Error
from src.config.settings import settings, DatabaseConfig
from loguru import logger

class DatabaseManager:
    def __init__(self, db_config: DatabaseConfig, db_name: str):
        self.config = db_config
        self.db_name = db_name
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def _create_engine(self) -> Engine:
        connection_string = (
            f"mysql+mysqlconnector://{self.config.username}:{self.config.password}"
            f"@{self.config.host}:{self.config.port}/{self.config.database}"
        )
        return create_engine(
            connection_string,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error en sesión de {self.db_name}: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        try:
            connection = mysql.connector.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password,
                database=self.config.database
            )
            if connection.is_connected():
                logger.info(f"Conexión exitosa a {self.db_name}")
                connection.close()
                return True
        except Error as e:
            logger.error(f"Error conectando a {self.db_name}: {e}")
            return False
        return False

# Instancias de los manejadores de base de datos
raw_db_manager = DatabaseManager(settings.raw_db, "raw_pronossport")
pronos_db_manager = DatabaseManager(settings.pronos_db, "pronossport")