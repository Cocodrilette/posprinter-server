import unicodedata
import re
import textwrap

class ESC_POS_Parser:
    @staticmethod
    def clean_text(text: str) -> str:
        """Normaliza el texto para eliminar acentos y fuerza a ASCII"""
        normalized = unicodedata.normalize("NFD", text)
        cleaned = "".join(c for c in normalized if unicodedata.category(c) != "Mn")
        return cleaned.encode("ascii", "ignore").decode("ascii")

    @staticmethod
    def parse_to_printer(impresora, markdown_text: str):
        """Convierte Markdown extendido en comandos ESC/POS con auto-wrap"""
        lineas = markdown_text.split("\n")
        
        # Ancho base para Font A en 58mm (aprox 32 chars)
        MAX_CHARS = 32

        for linea in lineas:
            linea = linea.strip()
            if not linea:
                impresora.set(align="left", font="a", bold=False, underline=0, invert=False, width=1, height=1)
                impresora.text("\n")
                continue

            # 1. Configuración por defecto de la línea
            current_align = "left"
            current_bold = False
            current_underline = 0
            current_invert = False
            current_width = 1
            current_height = 1
            
            # --- ELEMENTOS DE BLOQUE ---
            if linea == "---":
                impresora.set(align="left", bold=False)
                impresora.text("-" * MAX_CHARS + "\n")
                continue
            if linea == "===":
                impresora.set(align="left", bold=False)
                impresora.text("=" * MAX_CHARS + "\n")
                continue

            # Encabezados (Afectan al ancho de línea disponible)
            if linea.startswith("# "):
                current_align = "center"; current_bold = True
                current_width = 2; current_height = 2
                linea = linea[2:]
            elif linea.startswith("## "):
                current_align = "center"; current_bold = True
                linea = linea[3:]
            elif linea.startswith("### "):
                current_align = "left"; current_bold = True; current_underline = 1
                linea = linea[4:]

            # Comandos de Imagen/Gráficos
            if linea.startswith("!QR(") and linea.endswith(")"):
                impresora.set(align="center")
                impresora.qr(linea[4:-1], size=6, native=False)
                continue
            if linea.startswith("!BC(") and linea.endswith(")"):
                impresora.set(align="center")
                impresora.barcode("{B" + linea[4:-1], "CODE128", width=2, height=64, pos="BELOW")
                continue
            if linea.startswith("!IMG(") and linea.endswith(")"):
                from server_utils import get_image_from_url, split_image
                url = linea[5:-1]
                impresora.set(align="center")
                img = get_image_from_url(url)
                if img:
                    # Reducimos interlineado a 0 para que los trozos no tengan separación (fisica)
                    try:
                        impresora._raw(b'\x1b\x33\x00')
                    except: pass
                    
                    # Dividimos en trozos de 64px para máxima compatibilidad
                    chunks = split_image(img, chunk_height=64)
                    for chunk in chunks:
                        impresora.image(chunk)
                    
                    # Restauramos interlineado por defecto
                    try:
                        impresora._raw(b'\x1b\x32')
                    except: pass
                    
                    # Pequeño avance de papel extra al final
                    impresora.text("\n")
                continue
            if linea == "!HEART()":
                from server_utils import get_heart_image
                impresora.set(align="center"); impresora.image(get_heart_image())
                continue
            if linea == "!STAR()":
                from server_utils import get_star_image
                impresora.set(align="center"); impresora.image(get_star_image())
                continue
            if linea == "!MOON()":
                from server_utils import get_moon_image
                impresora.set(align="center"); impresora.image(get_moon_image())
                continue

            # Alineaciones
            if linea.startswith("| "):
                current_align = "center"; linea = linea[2:]
            elif linea.startswith("> "):
                current_align = "right"; linea = linea[2:]

            # Tablas { Item : Valor }
            if linea.startswith("{") and " : " in linea and linea.endswith("}"):
                content = linea[1:-1]
                parts = content.split(" : ", 1)
                key = ESC_POS_Parser.clean_text(parts[0].strip())
                val = ESC_POS_Parser.clean_text(parts[1].strip())
                
                # Para tablas, el wrap es más complejo, cortamos el key si es necesario
                # Reservamos espacio para el valor (10 chars)
                max_k = MAX_CHARS - len(val) - 1
                key = key[:max_k]
                dots = MAX_CHARS - len(key) - len(val)
                impresora.set(align="left", font="a")
                impresora.text(f"{key}{'.' * dots}{val}\n")
                continue

            # Checkboxes y Listas
            linea = linea.replace("[ ]", "[ ]").replace("[x]", "[X]")
            if linea.startswith("- ") or linea.startswith("* "):
                prefix = " * "
                linea = linea[2:]
            else:
                prefix = ""

            # --- RENDERIZADO FINAL CON WRAP ---
            linea = ESC_POS_Parser.clean_text(linea)
            
            # El ancho efectivo depende de si la fuente es doble ancho
            effective_width = MAX_CHARS // current_width
            
            # Aplicar word wrap (respetando prefijos si hay)
            wrapped_lines = textwrap.wrap(linea, width=effective_width - len(prefix))
            
            impresora.set(
                align=current_align, bold=current_bold, underline=current_underline,
                invert=current_invert, width=current_width, height=current_height
            )

            if not wrapped_lines: # Caso de solo prefijo o linea vacia que llego aqui
                impresora.text(f"{prefix}\n")
                continue

            for idx, w_line in enumerate(wrapped_lines):
                display_line = f"{prefix if idx == 0 else ''}{w_line}"
                
                # Manejar estilos inline (**bold**, !!invert!!)
                # Nota: El wrap puede romper tokens de estilo, pero para tickets sencillos
                # es mejor priorizar el ancho que el estilo inline complejo roto.
                tokens = re.split(r"(\*\*|!!)", display_line)
                bold_s, invert_s = current_bold, current_invert
                
                for token in tokens:
                    if not token: continue
                    if token == "**":
                        bold_s = not bold_s
                        impresora.set(align=current_align, bold=bold_s, underline=current_underline,
                                      invert=invert_s, width=current_width, height=current_height)
                    elif token == "!!":
                        invert_s = not invert_s
                        impresora.set(align=current_align, bold=bold_s, underline=current_underline,
                                      invert=invert_s, width=current_width, height=current_height)
                    else:
                        impresora.text(token)
                impresora.text("\n")
