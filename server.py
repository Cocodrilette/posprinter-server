from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from escpos.printer import Win32Raw, Network
import uvicorn

app = FastAPI(title="Print Server FC-588")

# NOTE 32 carateres por linea max


# Definimos la estructura del JSON que esperamos recibir
class Recibo(BaseModel):
    cliente: str
    items: list
    total: float


class PrintData(BaseModel):
    data: str


@app.post("/print")
def print_data(data: PrintData):
    try:
        impresora = Network("127.0.0.1", port=9100)

        impresora.set(
            align="left",
            font="a",
            bold=False,
            underline=0,
            width=1,
            height=1,
            invert=False,
        )

        impresora.text(data.data + "\n\n")
        impresora.close()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al conectar a la impresora: {str(e)}"
        )


@app.post("/imprimir")
def imprimir_recibo(datos: Recibo):
    try:
        impresora = Network("127.0.0.1", port=9100)

        # Formateo del recibo
        impresora.set(align="center", font="a")
        impresora.text("=== MI APLICACION ===\n\n")

        impresora.set(align="left")
        impresora.text(f"Cliente: {datos.cliente}\n")
        impresora.text("--------------------------------\n")

        for item in datos.items:
            impresora.text(f"{item['nombre']} ..... ${item['precio']}\n")

        impresora.text("--------------------------------\n")
        impresora.set(align="right")
        impresora.text(f"TOTAL: ${datos.total}\n\n\n\n")

        # Imprimir
        impresora.close()

        return {"status": "ok", "mensaje": "Impresión enviada correctamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al imprimir: {str(e)}")


@app.get("/test-estilos")
def imprimir_estilos():
    try:
        impresora = Network("127.0.0.1", port=9100)
        # impresora = Win32Raw("POS-X Thermal Printer")

        # Reset
        impresora.set(align="center", font="a", bold=True, width=2, height=2)
        impresora.text("DEMO EMULADOR PRO\n")
        impresora.set(width=1, height=1, bold=False)
        impresora.text("v2.0 - Full Support\n")
        impresora.text("--------------------------------\n\n")

        # --- SECCIÓN 1: FORMATO DE TEXTO ---
        impresora.set(align="left", bold=True, underline=1)
        impresora.text("1. ESTILOS DE TEXTO\n")
        impresora.set(bold=False, underline=0)

        impresora.text("Texto Normal\n")
        impresora.set(bold=True)
        impresora.text("Texto en Negrita\n")
        impresora.set(bold=False, underline=1)
        impresora.text("Texto Subrayado Simple\n")
        impresora.set(underline=2)
        impresora.text("Texto Subrayado Doble\n")
        impresora.set(underline=0, invert=True)
        impresora.text(" TEXTO INVERTIDO (NEGATIVO) \n")
        impresora.set(invert=False, font="b")
        impresora.text("Fuente B (Condensada/Pequeña)\n")

        # --- SECCIÓN 2: ALINEACIÓN ---
        impresora.set(font="a", align="left")
        impresora.text("\n2. ALINEACIONES\n")
        impresora.text("Izquierda\n")
        impresora.set(align="center")
        impresora.text("Centro\n")
        impresora.set(align="right")
        impresora.text("Derecha\n")

        # --- SECCIÓN 3: TAMAÑOS ---
        impresora.set(align="left")
        impresora.text("\n3. TAMAÑOS DE FUENTE\n")
        impresora.set(width=2, height=1)
        impresora.text("Doble Ancho\n")
        impresora.set(width=1, height=2)
        impresora.text("Doble Alto\n")
        impresora.set(width=2, height=2)
        impresora.text("2x2 (GRANDE)\n")
        impresora.set(width=3, height=3)
        impresora.text("3x3 (EXTRA)\n")

        # --- SECCIÓN 4: GRÁFICOS (QR) ---
        impresora.set(align="center")
        impresora.text("\n4. CODIGO QR (RASTER)\n")
        # native=False es clave para que el emulador reciba la imagen
        impresora.qr("https://github.com/recodes", size=8, native=False)
        impresora.text("\nEscanea para probar\n")

        # --- SECCIÓN 5: CÓDIGO DE BARRAS (OPTIMIZADO 58mm) ---
        impresora.text("\n5. CODIGO DE BARRAS (SHORT ID)\n")

        # Generamos un ID aleatorio de 12 caracteres (Equilibrio perfecto)
        # Ejemplo: "A1B2C3D4E5F6"
        import secrets

        short_id = secrets.token_hex(6).upper()  # 6 bytes = 12 caracteres hex

        # width=2 es MUCHO más legible que width=1
        # CODE128 requiere el prefijo {B para caracteres alfanuméricos
        impresora.barcode(
            "{B" + short_id, "CODE128", width=2, height=80, pos="BELOW", font="a"
        )

        impresora.text("\n--- FIN DE LA PRUEBA ---\n\n\n\n")
        impresora.close()

        return {"status": "ok", "mensaje": "Demo completa enviada al emulador"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al imprimir test completo: {str(e)}"
        )


if __name__ == "__main__":
    # Escuchamos en 0.0.0.0 para aceptar peticiones desde WSL o la red local
    uvicorn.run(app, host="0.0.0.0", port=8000)
