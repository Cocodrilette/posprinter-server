import sys
import os
import secrets
import random
import math
import uvicorn
import threading
import socket
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment as Jinja2Env, FileSystemLoader

# Importaciones locales
from core.auth import get_api_key, validate_physical_access
from core.models import MarkdownData, LuckyData
from core.parser import ESC_POS_Parser
from core.printer import PrinterFactory
from core.emulator import EmulatorEngine

load_dotenv()

# Instancia del motor del emulador
emu = EmulatorEngine()

# Configuración de plantillas e hilos
if getattr(sys, "frozen", False):
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_templates_dir = os.path.join(BASE_DIR, "templates")
_jinja_env = Jinja2Env(loader=FileSystemLoader(_templates_dir), cache_size=0)

app = FastAPI(title="POS Printer Server Pro")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


# --- EMULADOR TCP ---
def start_tcp_emu():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(("0.0.0.0", 9100))
        server.listen(5)
        while True:
            client, _ = server.accept()
            data = b""
            try:
                while True:
                    chunk = client.recv(4096)
                    if not chunk: break
                    data += chunk
            except Exception as e:
                print(f"TCP Emu Recv Error: {e}")
            
            if data:
                emu.parse(data)
            client.close()
    except Exception as e:
        print(f"TCP Emu Server Error: {e}")


# --- RUTAS ---

# Servir archivos estáticos del frontend (si existen)
FRONTEND_PATH = os.path.join(BASE_DIR, "frontend", "dist")
if os.path.exists(FRONTEND_PATH):
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(FRONTEND_PATH, "assets")),
        name="assets",
    )


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    # Si existe el build de React, servir su index.html
    react_index = os.path.join(FRONTEND_PATH, "index.html")
    if os.path.exists(react_index):
        with open(react_index, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    with open(os.path.join(_templates_dir, "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/lucky", response_class=HTMLResponse)
def lucky(request: Request):
    # Si existe el build de React, servir su index.html (React maneja la ruta)
    react_index = os.path.join(FRONTEND_PATH, "index.html")
    if os.path.exists(react_index):
        with open(react_index, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    with open(os.path.join(_templates_dir, "lucky.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/emu-view", response_class=HTMLResponse)
def emu_view(request: Request):
    """Componente reutilizable del emulador (Legacy HTML)"""
    t = _jinja_env.get_template("emulator.html")
    return HTMLResponse(content=t.render(paper=emu.virtual_paper, logs=emu.hex_logs))

@app.get("/api/emu-view")
def emu_view_json():
    """API para obtener el estado del emulador en JSON"""
    return {
        "paper": emu.virtual_paper,
        "logs": emu.hex_logs
    }

@app.post("/api/preview")
def preview_md(data: MarkdownData):
    """Genera una previsualización instantánea sin usar TCP"""
    try:
        from escpos.printer import Dummy
        d = Dummy()
        ESC_POS_Parser.parse_to_printer(d, data.markdown)
        d.text("\n\n")
        
        temp_emu = EmulatorEngine()
        temp_emu.parse(d.output)
        
        return {
            "paper": temp_emu.virtual_paper,
            "logs": temp_emu.hex_logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/emu-clear")
def emu_clear():
    emu.clear()
    return {"status": "ok"}


@app.post("/api/print-md")
def print_md(data: MarkdownData, api_key: str = Depends(get_api_key)):
    try:
        if data.target == "physical":
            validate_physical_access(data.physical_key)
        p = PrinterFactory.get_printer(data.target)
        ESC_POS_Parser.parse_to_printer(p, data.markdown)
        p.text("\n\n\n\n")
        p.close()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/lucky-print")
def lucky_print(data: LuckyData, api_key: str = Depends(get_api_key)):
    try:
        if data.target == "physical":
            validate_physical_access(data.physical_key)
        p = PrinterFactory.get_printer(data.target)
        # Importamos dinámicamente para evitar circulares
        from server_utils import get_star_image, FRASES_PROFUNDAS

        frase = random.choice(FRASES_PROFUNDAS)
        p.set(align="center")
        p.image(get_star_image())
        p.set(align="center", bold=True, width=2, height=2)
        p.text(f"\n{ESC_POS_Parser.clean_text(frase)}\n\n")
        p.text("\n\n\n\n\n")
        p.close()
        return {"status": "ok", "frase": frase}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    threading.Thread(target=start_tcp_emu, daemon=True).start()
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
