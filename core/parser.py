import unicodedata
import re

class ESC_POS_Parser:
    @staticmethod
    def clean_text(text: str) -> str:
        """Normaliza el texto para eliminar acentos y fuerza a ASCII"""
        normalized = unicodedata.normalize('NFD', text)
        cleaned = "".join(c for c in normalized if unicodedata.category(c) != 'Mn')
        return cleaned.encode('ascii', 'ignore').decode('ascii')

    @staticmethod
    def parse_to_printer(impresora, markdown_text: str):
        """Convierte Markdown extendido en comandos ESC/POS"""
        lineas = markdown_text.split("\n")
        
        for linea in lineas:
            linea = linea.strip()
            if not linea:
                impresora.text("\n")
                continue

            # 1. Configuración por defecto de la línea
            current_align = "left"
            current_bold = False
            current_underline = 0
            current_invert = False
            current_width = 1
            current_height = 1

            # --- ELEMENTOS DE BLOQUE (Línea completa) ---

            # Separadores
            if linea == "---":
                impresora.set(align="left", bold=False)
                impresora.text("-" * 32 + "\n")
                continue
            if linea == "===":
                impresora.set(align="left", bold=False)
                impresora.text("=" * 32 + "\n")
                continue

            # Encabezados
            if linea.startswith("# "):
                current_align = "center"
                current_bold = True
                current_width = 2
                current_height = 2
                linea = linea[2:]
            elif linea.startswith("## "):
                current_align = "center"
                current_bold = True
                linea = linea[3:]
            elif linea.startswith("### "):
                current_align = "left"
                current_bold = True
                current_underline = 1
                linea = linea[4:]

            # Comandos de Imagen/Gráficos
            if linea.startswith("!QR(") and linea.endswith(")"):
                content = linea[4:-1]
                impresora.set(align="center")
                impresora.qr(content, size=6, native=False)
                continue
            
            if linea.startswith("!BC(") and linea.endswith(")"):
                content = linea[4:-1]
                impresora.set(align="center")
                # Usamos {B como prefijo para CODE128 alfanumérico
                impresora.barcode("{B" + content, "CODE128", width=2, height=64, pos="BELOW")
                continue

            # Alineaciones de bloque
            if linea.startswith("| "):
                current_align = "center"
                linea = linea[2:]
            elif linea.startswith("> "):
                current_align = "right"
                linea = linea[2:]

            # Listas y Checkboxes
            linea = linea.replace("[ ]", "[ ]").replace("[x]", "[X]")
            if linea.startswith("- ") or linea.startswith("* "):
                impresora.set(align=current_align)
                impresora.text(" * ")
                linea = linea[2:]

            # --- ELEMENTOS INLINE (Dentro de la línea) ---
            linea = ESC_POS_Parser.clean_text(linea)
            
            # Parser de tokens para estilos mixtos
            tokens = re.split(r'(\*\*|!!)', linea)
            bold_state = current_bold
            invert_state = current_invert

            impresora.set(
                align=current_align,
                bold=bold_state,
                underline=current_underline,
                invert=invert_state,
                width=current_width,
                height=current_height
            )

            for token in tokens:
                if not token: continue
                if token == "**":
                    bold_state = not bold_state
                    impresora.set(align=current_align, bold=bold_state, underline=current_underline, invert=invert_state, width=current_width, height=current_height)
                elif token == "!!":
                    invert_state = not invert_state
                    impresora.set(align=current_align, bold=bold_state, underline=current_underline, invert=invert_state, width=current_width, height=current_height)
                else:
                    impresora.text(token)
            
            impresora.text("\n")
