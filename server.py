import sys
import os
import secrets
import random
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Importaciones locales
from core.auth import get_api_key, validate_physical_access
from core.models import MarkdownData, LuckyData
from core.parser import ESC_POS_Parser
from core.printer import PrinterFactory

load_dotenv()

app = FastAPI(title="POS Printer Server", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.get("/", response_class=HTMLResponse)
def index():
    template_path = os.path.join(BASE_DIR, "templates", "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/lucky", response_class=HTMLResponse)
def lucky():
    template_path = os.path.join(BASE_DIR, "templates", "lucky.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/print-md")
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

@app.post("/lucky-print")
def lucky_print(data: LuckyData, api_key: str = Depends(get_api_key)):
    try:
        if data.target == "physical":
            validate_physical_access(data.physical_key)
        p = PrinterFactory.get_printer(data.target)
        # Una frase simple para asegurar estabilidad
        frase = "Confia en el proceso."
        p.set(align="center", bold=True, width=2, height=2)
        p.text(f"\n{frase}\n\n\n\n\n")
        p.close()
        return {"status": "ok", "frase": frase}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
