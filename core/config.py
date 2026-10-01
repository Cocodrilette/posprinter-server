import os
from dotenv import load_dotenv

load_dotenv()

# Servidor
HOST = os.getenv("HOST", "0.0.0.0")                      # interfaz de escucha
WEB_PORT = int(os.getenv("WEB_PORT", "8000"))            # API + interfaz web
EMU_TCP_PORT = int(os.getenv("EMU_TCP_PORT", "9100"))    # emulador ESC/POS (TCP)
EMU_WEB_PORT = int(os.getenv("EMU_WEB_PORT", "9021"))    # emulator.py standalone (vista web)
# Impresora USB directa (macOS/Linux, sin CUPS). Formato hex: 0x0483
USB_VENDOR_ID = os.getenv("USB_VENDOR_ID", "")
USB_PRODUCT_ID = os.getenv("USB_PRODUCT_ID", "")
USB_OUT_EP = os.getenv("USB_OUT_EP", "0x02")
USB_IN_EP = os.getenv("USB_IN_EP", "0x81")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
