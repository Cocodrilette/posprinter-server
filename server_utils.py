import math
import urllib.request
from io import BytesIO
from PIL import Image, ImageDraw, ImageEnhance

FRASES_PROFUNDAS = [
    "Lo que buscas tambien te esta buscando a ti.",
    "Tu destino no es un lugar, sino una nueva forma de ver.",
    "Confia en el proceso.",
    "Incluso en la noche mas oscura, las estrellas brillan.",
    "No busques el camino, se tu mismo el camino."
]

def get_image_from_url(url, max_width=320):
    """Descarga una imagen de una URL y la procesa con mejoras de contraste y tramado"""
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            img_data = response.read()
        
        img = Image.open(BytesIO(img_data))
        
        # 1. Convertir a RGB si es necesario
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # 2. Redimensionar
        w, h = img.size
        if w > max_width:
            new_h = int(h * (max_width / w))
            img = img.resize((max_width, new_h), Image.Resampling.LANCZOS)
        
        # 3. MEJORAS VISUALES
        # Aumentar contraste (1.5) para que los colores no se vean "lavados"
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.6)
        
        # Aumentar nitidez (2.0) para definir bordes en baja resolución
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
        
        # 4. Convertir a 1-bit usando Floyd-Steinberg dithering explícito
        return img.convert('1')
    except Exception as e:
        print(f"Error cargando imagen desde URL {url}: {e}")
        return None

def split_image(img, chunk_height=100):
    """Divide una imagen en trozos horizontales para evitar saturar el buffer de la impresora"""
    w, h = img.size
    chunks = []
    for i in range(0, h, chunk_height):
        box = (0, i, w, min(i + chunk_height, h))
        chunks.append(img.crop(box))
    return chunks

def get_star_image():
    # Tamaño 180 para igualar al QR
    size = 180
    img = Image.new('1', (size, size), 1)
    draw = ImageDraw.Draw(img)
    cx, cy = size//2, size//2
    pts = []
    for i in range(10):
        r = 80 if i % 2 == 0 else 35
        a = i * math.pi / 5 - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=0)
    return img

def get_heart_image():
    size = 180
    img = Image.new('1', (size, size), 1)
    draw = ImageDraw.Draw(img)
    cx, cy = size//2, size//2
    pts = []
    for t in range(0, 628):
        t /= 100
        x = 16 * (math.sin(t) ** 3)
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        # Escala ajustada para llenar los 180px
        pts.append((cx + x * 5, cy - y * 5))
    draw.polygon(pts, fill=0)
    return img

def get_moon_image():
    size = 180
    img = Image.new('1', (size, size), 1)
    draw = ImageDraw.Draw(img)
    # Luna creciente proporcional al tamaño QR
    draw.ellipse([30, 30, 150, 150], fill=0)
    draw.ellipse([60, 20, 180, 140], fill=1)
    return img
