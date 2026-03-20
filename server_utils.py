import math
from PIL import Image, ImageDraw

FRASES_PROFUNDAS = [
    "Lo que buscas tambien te esta buscando a ti.",
    "Tu destino no es un lugar, sino una nueva forma de ver.",
    "Confia en el proceso.",
    "Incluso en la noche mas oscura, las estrellas brillan.",
    "No busques el camino, se tu mismo el camino."
]

def get_star_image():
    size = 150
    img = Image.new('1', (size, size), 1)
    draw = ImageDraw.Draw(img)
    cx, cy = size//2, size//2
    pts = []
    for i in range(10):
        r = 60 if i % 2 == 0 else 25
        a = i * math.pi / 5 - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=0)
    return img

def get_heart_image():
    size = 150
    img = Image.new('1', (size, size), 1)
    draw = ImageDraw.Draw(img)
    # Dibujar un corazón simple con dos círculos y un triángulo
    # O mejor, usando una fórmula paramétrica
    cx, cy = size//2, size//2
    pts = []
    for t in range(0, 628): # 0 a 2*pi
        t /= 100
        # Formula: x = 16*sin^3(t), y = 13*cos(t) - 5*cos(2t) - 2*cos(3t) - cos(4t)
        x = 16 * (math.sin(t) ** 3)
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        # Escalar y centrar (y está invertida en coordenadas de imagen)
        pts.append((cx + x * 4, cy - y * 4))
    draw.polygon(pts, fill=0)
    return img

def get_moon_image():
    size = 150
    img = Image.new('1', (size, size), 1)
    draw = ImageDraw.Draw(img)
    # Dibujar luna creciente (dos círculos superpuestos)
    draw.ellipse([25, 25, 125, 125], fill=0)
    draw.ellipse([45, 20, 145, 120], fill=1)
    return img
