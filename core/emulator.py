import base64
import io
import re
from PIL import Image

class EmulatorEngine:
    def __init__(self):
        self.virtual_paper = []
        self.hex_logs = []
        self.reset_state()

    def reset_state(self):
        self.current_state = {
            "align": "left",
            "bold": False,
            "underline": 0,
            "invert": False,
            "width": 1,
            "height": 1,
            "font": "a",
            "size": 0
        }

    def clear(self):
        self.virtual_paper = []
        self.hex_logs = []
        self.reset_state()

    def raster_to_base64(self, width_bytes, height_dots, data):
        try:
            width = width_bytes * 8
            img = Image.new("1", (width, height_dots), 1)
            pixels = img.load()
            for y in range(height_dots):
                for x_byte in range(width_bytes):
                    idx = y * width_bytes + x_byte
                    if idx >= len(data): break
                    byte = data[idx]
                    for bit in range(8):
                        if (byte >> (7 - bit)) & 1:
                            pixels[x_byte * 8 + bit, y] = 0
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode()
        except: return None

    def parse(self, data: bytes):
        log_entry = "\n".join([
            f"{i:04x} | {' '.join(f'{b:02x}' for b in data[i:i+16]):<47} | "
            f"{''.join(chr(b) if 32<=b<=126 else '.' for b in data[i:i+16])}" 
            for i in range(0, len(data), 16)
        ])
        self.hex_logs.append(log_entry)
        
        i = 0
        pending = b""
        
        def flush():
            nonlocal pending
            if pending:
                try:
                    text = pending.decode("cp437", errors="replace")
                    parts = text.split('\n')
                    for idx, part in enumerate(parts):
                        if part:
                            self.virtual_paper.append({
                                "type": "text", 
                                "text": part, 
                                **self.current_state.copy()
                            })
                        if idx < len(parts) - 1:
                            self.virtual_paper.append({"type": "newline"})
                except Exception as e:
                    print(f"Error flushing text: {e}")
                pending = b""

        while i < len(data):
            # ESC @ (Initialize)
            if data[i:i+2] == b'\x1b\x40':
                flush(); self.reset_state(); i += 2
            
            # ESC a n (Alignment)
            elif data[i:i+2] == b'\x1b\x61':
                flush()
                if i + 2 < len(data):
                    n = data[i+2]
                    self.current_state["align"] = ["left", "center", "right"][n % 3]
                i += 3
                
            # ESC E n (Bold)
            elif data[i:i+2] == b'\x1b\x45':
                flush()
                if i + 2 < len(data):
                    self.current_state["bold"] = bool(data[i+2] & 0x01)
                i += 3
                
            # ESC - n (Underline)
            elif data[i:i+2] == b'\x1b\x2d':
                flush()
                if i + 2 < len(data):
                    self.current_state["underline"] = data[i+2]
                i += 3
                
            # ESC ! n (Print mode)
            elif data[i:i+2] == b'\x1b\x21':
                flush()
                if i + 2 < len(data):
                    n = data[i+2]
                    self.current_state["bold"] = bool(n & 8)
                    self.current_state["height"] = 2 if (n & 16) else 1
                    self.current_state["width"] = 2 if (n & 32) else 1
                    self.current_state["underline"] = 1 if (n & 128) else 0
                i += 3

            # ESC M n (Select font)
            elif data[i:i+2] == b'\x1b\x4d':
                flush()
                if i+2 < len(data):
                    self.current_state["font"] = "b" if data[i+2] in [1, 49] else "a"
                i += 3

            # ESC t n (Select code table)
            elif data[i:i+2] == b'\x1b\x74':
                i += 3 # Ignorar pero saltar n

            # ESC d n (Print and feed n lines)
            elif data[i:i+2] == b'\x1b\x64':
                flush()
                if i+2 < len(data):
                    for _ in range(data[i+2]):
                        self.virtual_paper.append({"type": "newline"})
                i += 3

            # GS ! n (Select character size)
            elif data[i:i+2] == b'\x1d\x21':
                flush()
                if i + 2 < len(data):
                    n = data[i+2]
                    self.current_state["width"] = ((n >> 4) & 0x07) + 1
                    self.current_state["height"] = (n & 0x07) + 1
                i += 3

            # GS B n (Invert)
            elif data[i:i+2] == b'\x1d\x42':
                flush()
                if i + 2 < len(data):
                    self.current_state["invert"] = bool(data[i+2] & 0x01)
                i += 3

            # GS L nL nH (Set left margin)
            elif data[i:i+2] == b'\x1d\x4c':
                i += 4 # Ignorar margin 2 bytes

            # GS W nL nH (Set print area width)
            elif data[i:i+2] == b'\x1d\x57':
                i += 4 # Ignorar width 2 bytes

            # GS k (Print barcode)
            elif data[i:i+2] == b'\x1d\x6b':
                flush()
                if i + 2 >= len(data): 
                    i += 2; continue
                m = data[i+2]; i += 3
                try:
                    if m >= 65:
                        if i < len(data):
                            n = data[i]; i += 1
                            bdata = data[i:i+n].decode('ascii', errors='replace')
                            i += n
                        else: bdata = ""
                    else:
                        start = i
                        while i < len(data) and data[i] != 0: i += 1
                        bdata = data[start:i].decode('ascii', errors='replace')
                        i += 1
                    bdata = re.sub(r'\{[A-Z]', '', bdata)
                    self.virtual_paper.append({"type": "barcode", "text": bdata, "align": "center"})
                except: pass

            # GS v 0 (Print raster bit image)
            elif data[i:i+3] == b'\x1d\x76\x30':
                flush()
                if i + 7 < len(data):
                    # m = data[i+3], ignoramos modo m
                    xL, xH = data[i+4], data[i+5]
                    yL, yH = data[i+6], data[i+7]
                    wb, hd = xH * 256 + xL, yH * 256 + yL
                    i += 8
                    total_bytes = wb * hd
                    img_data = data[i:i+total_bytes]
                    i += total_bytes
                    b64 = self.raster_to_base64(wb, hd, img_data)
                    if b64:
                        self.virtual_paper.append({"type": "image", "data": b64, "align": self.current_state["align"]})
                else: i += 4

            # Saltos genéricos para comandos ESC / GS no manejados de 1 o 2 parámetros
            elif data[i:i+1] == b'\x1b' or data[i:i+1] == b'\x1d':
                # Si llegamos aquí es un comando ESC/GS que no conocemos específicamente.
                # Intentamos saltar basándonos en patrones comunes si no queremos que salgan caracteres raros.
                # Pero por ahora solo lo tratamos como bytes de texto si no coinciden arriba.
                # Para evitar caracteres raros, podemos "consumir" el ESC y el siguiente byte.
                i += 2 
            
            else:
                char = data[i:i+1]
                if char == b'\n':
                    flush(); self.virtual_paper.append({"type": "newline"})
                elif char == b'\r': pass
                else: pending += char
                i += 1
        flush()
