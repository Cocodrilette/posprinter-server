import os
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PRINT_SERVER_API_KEY", "mi_super_secreto_123")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

PHYSICAL_KEY = os.getenv("PHYSICAL_PRINTER_KEY", "admin_fisico_456")
PHYSICAL_PRINTER_NAME = os.getenv("PHYSICAL_PRINTER_NAME", "POS-58")

def get_api_key(api_key: str = Security(api_key_header)):
    """Valida la API Key de forma estricta."""
    if api_key == API_KEY:
        return api_key
    raise HTTPException(status_code=403, detail="API Key no válida")

def validate_physical_access(key: str):
    """Valida la clave física de forma estricta."""
    if key == PHYSICAL_KEY:
        return True
    raise HTTPException(status_code=403, detail="Clave de impresora física inválida")
