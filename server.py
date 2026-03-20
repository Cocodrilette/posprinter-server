import sys
import os
import secrets
import random
import math
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
from PIL import Image, ImageDraw

load_dotenv()

app = FastAPI(title="POS Printer Server", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


FRASES_PROFUNDAS = [
    "Lo que buscas tambien te esta buscando a ti.",
    "El silencio es el lenguaje donde nacen las verdades.",
    "Tu destino no es un lugar, sino una nueva forma de ver.",
    "Incluso en la noche mas oscura, las estrellas no dejan de brillar.",
    "Eres el arquitecto de tus propios laberintos.",
    "La respuesta que necesitas ya vive en tu interior.",
    "No busques el camino, se tu mismo el camino.",
    "El universo no conspira contra ti, baila contigo.",
    "Confia en el proceso, incluso cuando no entiendas el mapa.",
    "Tu pasado es una leccion, no una sentencia.",
]


def get_heart_image():
    size = 150
    img = Image.new("1", (size, size), 1)
    draw = ImageDraw.Draw(img)
    # Dibujar corazón usando dos círculos y un triángulo
    draw.ellipse([20, 20, 85, 85], fill=0)
    draw.ellipse([65, 20, 130, 85], fill=0)
    draw.polygon([(22, 65), (128, 65), (75, 140)], fill=0)
    return img


def get_moon_image():
    size = 150
    img = Image.new("1", (size, size), 1)
    draw = ImageDraw.Draw(img)
    # Luna creciente: círculo negro restado por círculo blanco desplazado
    draw.ellipse([20, 20, 130, 130], fill=0)
    draw.ellipse([50, 10, 160, 120], fill=1)
    return img


def get_star_image():
    size = 150
    img = Image.new("1", (size, size), 1)
    draw = ImageDraw.Draw(img)
    cx, cy = 75, 75
    pts = []
    for i in range(10):
        r = 60 if i % 2 == 0 else 25
        a = i * math.pi / 5 - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=0)
    return img


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
        frase = random.choice(FRASES_PROFUNDAS)

        # Selección aleatoria de icono para la suerte
        icon_func = random.choice([get_heart_image, get_star_image, get_moon_image])

        p.set(align="center")
        p.image(icon_func())

        p.set(align="center", bold=True, width=2, height=2)
        p.text(f"\n{ESC_POS_Parser.clean_text(frase)}\n\n")

        p.close()

        return {"status": "ok", "frase": frase}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
