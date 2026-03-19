import socket
import threading
import uvicorn
import io
import base64
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from PIL import Image

app = FastAPI(title="ESC/POS Emulator Pro")

# Estado global
virtual_paper = []
hex_logs = []

current_state = {
    "align": "left",
    "bold": False,
    "underline": 0,
    "invert": False,
    "font": "a",
    "size": 1,
}


def raster_to_base64(width_bytes, height_dots, data):
    """Convierte datos raster GS v 0 a una imagen base64"""
    try:
        width = width_bytes * 8
        img = Image.new("1", (width, height_dots), 1)
        pixels = img.load()

        for y in range(height_dots):
            for x_byte in range(width_bytes):
                byte = data[y * width_bytes + x_byte]
                for bit in range(8):
                    if (byte >> (7 - bit)) & 1:
                        pixels[x_byte * 8 + bit, y] = 0  # Negro

        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        print(f"Error procesando imagen: {e}")
        return None


def parse_escpos(data: bytes):
    global virtual_paper, hex_logs
    hex_logs.append(
        "\n".join(
            [
                f"{i:04x} | {' '.join(f'{b:02x}' for b in data[i : i + 16]):<47} | {''.join(chr(b) if 32 <= b <= 126 else '.' for b in data[i : i + 16])}"
                for i in range(0, len(data), 16)
            ]
        )
    )

    i = 0
    pending_text = b""

    def flush_text():
        nonlocal pending_text
        if pending_text:
            try:
                # Forzamos ASCII para que los acentos y símbolos se rompan/reemplacen
                # como en la impresora real
                text = pending_text.decode("ascii", errors="replace")
                virtual_paper.append(
                    {
                        "type": "text",
                        "text": text,
                        "align": current_state["align"],
                        "bold": current_state["bold"],
                        "underline": current_state["underline"],
                        "invert": current_state["invert"],
                        "font": current_state["font"],
                        "size": current_state["size"],
                    }
                )
            except Exception as _:
                pass
            pending_text = b""

    while i < len(data):
        # ESC @ (Initialize)
        if data[i : i + 2] == b"\x1b\x40":
            flush_text()
            current_state.update(
                {
                    "align": "left",
                    "bold": False,
                    "underline": 0,
                    "invert": False,
                    "size": 1,
                }
            )
            i += 2
        # ESC a (Alignment)
        elif data[i : i + 2] == b"\x1b\x61":
            flush_text()
            n = data[i + 2]
            current_state["align"] = ["left", "center", "right"][n] if n < 3 else "left"
            i += 3
        # ESC E (Bold)
        elif data[i : i + 2] == b"\x1b\x45":
            flush_text()
            current_state["bold"] = bool(data[i + 2])
            i += 3
        # ESC - (Underline)
        elif data[i : i + 2] == b"\x1b\x2d":
            flush_text()
            current_state["underline"] = data[i + 2]
            i += 3
        # ESC M (Font selection)
        elif data[i : i + 2] == b"\x1b\x4d":
            flush_text()
            current_state["font"] = "b" if data[i + 2] in [1, 49] else "a"
            i += 3
        # ESC t (Code table - saltar)
        elif data[i : i + 2] == b"\x1b\x74":
            i += 3
        # GS ! (Size)
        elif data[i : i + 2] == b"\x1d\x21":
            flush_text()
            n = data[i + 2]
            current_state["size"] = (n & 0x07) + 1  # Simplificado
            i += 3
        # GS B (Invert)
        elif data[i : i + 2] == b"\x1d\x42":
            flush_text()
            current_state["invert"] = bool(data[i + 2])
            i += 3
        # Comandos de configuración de Barcode (Saltar con seguridad)
        elif data[i : i + 2] in [
            b"\x1d\x68",
            b"\x1d\x77",
            b"\x1d\x48",
            b"\x1d\x66",
            b"\x1d\x61",
        ]:
            i += 3
        # GS k (Barcode Nativo)
        elif data[i : i + 2] == b"\x1d\x6b":
            flush_text()
            m = data[i + 2]
            i += 3
            try:
                if m >= 65:  # Sistema B (n bytes de datos)
                    n = data[i]
                    i += 1
                    barcode_data = data[i : i + n].decode("ascii", errors="replace")
                    i += n
                else:  # Sistema A (termina en NULL)
                    start = i
                    while i < len(data) and data[i] != 0:
                        i += 1
                    barcode_data = data[start:i].decode("ascii", errors="replace")
                    i += 1

                # Limpiar prefijos de control y mostrar
                display_data = (
                    barcode_data.replace("{A", "").replace("{B", "").replace("{C", "")
                )
                virtual_paper.append(
                    {"type": "barcode", "text": display_data, "align": "center"}
                )
            except Exception as e:
                print(f"Error barcode: {e}")
                i += 1
        # GS v 0 (Raster Image / QR / Barcode)
        elif data[i : i + 4] == b"\x1d\x76\x30\x00":
            flush_text()
            xL, xH = data[i + 4], data[i + 5]
            yL, yH = data[i + 6], data[i + 7]
            width_bytes = xH * 256 + xL
            height_dots = yH * 256 + yL
            total_bytes = width_bytes * height_dots
            i += 8
            img_data = data[i : i + total_bytes]
            b64 = raster_to_base64(width_bytes, height_dots, img_data)
            if b64:
                virtual_paper.append(
                    {"type": "image", "data": b64, "align": current_state["align"]}
                )
            i += total_bytes
        else:
            char = data[i : i + 1]
            if char == b"\n":
                flush_text()
                virtual_paper.append({"type": "newline"})
            else:
                pending_text += char
            i += 1
    flush_text()


def tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9100))
    server.listen(5)
    print("Printer Emulator listening on 9100...")
    while True:
        client, addr = server.accept()
        data = b""
        while True:
            try:
                client.settimeout(0.5)
                chunk = client.recv(4096)
                if not chunk:
                    break
                data += chunk
            except Exception as _:
                break
        if data:
            parse_escpos(data)
        client.close()


@app.get("/", response_class=HTMLResponse)
async def view_paper():
    lines_html = ""
    for item in virtual_paper:
        if item["type"] == "newline":
            lines_html += '<div style="height: 1em;"></div>'
        elif item["type"] == "image":
            lines_html += f'<div style="text-align: {item["align"]}"><img src="data:image/png;base64,{item["data"]}" style="max-width: 100%;"></div>'
        elif item["type"] == "barcode":
            lines_html += f'<div style="text-align: center; background: #e3f2fd; border: 1px dashed #2196f3; padding: 10px; margin: 5px 0; font-weight: bold; color: #1565c0;">[BARCODE: {item["text"]}]</div>'
        else:
            style = f"text-align: {item['align']}; "
            style += "font-weight: bold; " if item["bold"] else ""
            style += "text-decoration: underline; " if item["underline"] else ""
            if item["invert"]:
                style += "background: black; color: white; display: inline-block; width: 100%; "
            style += f"font-size: {12 + item['size'] * 2}px; "
            style += "font-style: italic; " if item["font"] == "b" else ""

            content = item["text"].replace(" ", "&nbsp;")
            lines_html += f'<div style="{style} min-height: 1.2em;">{content}</div>'

    hex_html = "".join(
        [
            f'<div style="margin-bottom:15px"><strong>Msg #{len(hex_logs) - i}</strong><pre style="font-size:11px">{log}</pre></div>'
            for i, log in enumerate(reversed(hex_logs))
        ]
    )

    return f"""
    <html>
        <head><title>ESC/POS Emulator Pro</title><meta http-equiv="refresh" content="3">
        <style>
            body {{ background:#333; color:#eee; display:flex; padding:20px; font-family:monospace; gap:20px; }}
            .paper {{ background:white; color:black; width:350px; padding:20px; box-shadow:0 0 20px #000; min-height:80vh; }}
            .logs {{ flex:1; background:#1e1e1e; padding:20px; border-radius:8px; height:90vh; overflow-y:auto; color:#0f0; }}
            button {{ background:#c0392b; color:white; border:none; padding:10px; cursor:pointer; margin-bottom:10px; }}
        </style>
        </head>
        <body>
            <div>
                <form action="/clear" method="post"><button type="submit">Limpiar Todo</button></form>
                <div class="paper">{lines_html}</div>
            </div>
            <div class="logs"><h2>HEX DEBUG</h2>{hex_html}</div>
        </body>
    </html>
    """


@app.post("/clear")
async def clear_paper():
    global virtual_paper, hex_logs
    virtual_paper, hex_logs = [], []
    return HTMLResponse("<script>window.location.href='/';</script>")


if __name__ == "__main__":
    threading.Thread(target=tcp_server, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8080)
