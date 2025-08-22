import os
from loguru import logger
from src.config.settings import settings

def setup_logger():
    # Crear directorio de logs si no existe
    log_dir = os.path.dirname(settings.log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar loguru
    logger.remove()  # Remover configuración por defecto
    
    # Formato del log
    format_string = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
    
    # Log a archivo
    logger.add(
        settings.log_file,
        format=format_string,
        level=settings.log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    # Log a consola
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    return logger

# Inicializar logger al importar el módulo
setup_logger()