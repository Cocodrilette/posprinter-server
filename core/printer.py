from escpos.printer import Network, Win32Raw
from core.auth import PHYSICAL_PRINTER_NAME

class PrinterFactory:
    @staticmethod
    def get_printer(target: str = "emulator"):
        """Fabrica la conexión con la impresora según el destino"""
        try:
            if target == "physical":
                # Conexión via driver de Windows (USB/Bluetooth)
                return Win32Raw(PHYSICAL_PRINTER_NAME)
            
            # Conexión via Red (TCP/IP) al emulador local o IP real
            return Network("127.0.0.1", port=9100)
        except Exception as e:
            raise Exception(f"Error de conexión con la impresora ({target}): {str(e)}")
