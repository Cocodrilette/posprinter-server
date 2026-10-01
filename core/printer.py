import subprocess
import sys

from escpos.printer import Network, Dummy
from core.auth import PHYSICAL_PRINTER_NAME
from core.config import EMU_TCP_PORT, USB_VENDOR_ID, USB_PRODUCT_ID, USB_OUT_EP, USB_IN_EP


class CupsRaw(Dummy):
    """Impresora física en macOS/Linux: acumula ESC/POS y lo envía en crudo via CUPS (lpr -o raw)."""

    def __init__(self, printer_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.printer_name = printer_name

    def close(self):
        data = self.output
        if not data:
            return
        self.clear()  # close() también se invoca desde __del__; evita doble envío
        result = subprocess.run(
            ["lpr", "-P", self.printer_name, "-o", "raw"],
            input=data,
            capture_output=True,
        )
        if result.returncode != 0:
            raise Exception(result.stderr.decode(errors="replace").strip() or "lpr falló")


def _win32_raw(name: str):
    from escpos.printer import Win32Raw
    return Win32Raw(name)


class PrinterFactory:
    @staticmethod
    def get_printer(target: str = "emulator"):
        """Fabrica la conexión con la impresora según el destino"""
        try:
            if target == "physical":
                if sys.platform == "win32":
                    # Conexión via driver de Windows (USB/Bluetooth)
                    return _win32_raw(PHYSICAL_PRINTER_NAME)
                if USB_VENDOR_ID and USB_PRODUCT_ID:
                    # macOS/Linux: USB directo (requiere libusb y pyusb)
                    from escpos.printer import Usb
                    return Usb(
                        int(USB_VENDOR_ID, 0), int(USB_PRODUCT_ID, 0),
                        in_ep=int(USB_IN_EP, 0), out_ep=int(USB_OUT_EP, 0),
                    )
                # macOS/Linux: cola CUPS en modo raw
                return CupsRaw(PHYSICAL_PRINTER_NAME)

            # Conexión via Red (TCP/IP) al emulador local o IP real
            return Network("127.0.0.1", port=EMU_TCP_PORT)
        except Exception as e:
            raise Exception(f"Error de conexión con la impresora ({target}): {str(e)}")
