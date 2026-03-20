import unicodedata

class ESC_POS_Parser:
    @staticmethod
    def clean_text(text: str) -> str:
        """Normaliza el texto para eliminar acentos y fuerza a ASCII"""
        normalized = unicodedata.normalize('NFD', text)
        cleaned = "".join(c for c in normalized if unicodedata.category(c) != 'Mn')
        return cleaned.encode('ascii', 'ignore').decode('ascii')

    @staticmethod
    def parse_to_printer(impresora, markdown_text: str):
        """Convierte Markdown simple en comandos ESC/POS"""
        lineas = markdown_text.split("\n")
        for linea in lineas:
            linea = ESC_POS_Parser.clean_text(linea.strip())
            if not linea:
                impresora.text("\n")
                continue

            impresora.set(align="left", font="a", bold=False, width=1, height=1)

            if linea == "---":
                impresora.text("-" * 32 + "\n")
                continue

            if linea.startswith("# "):
                impresora.set(align="center", bold=True, width=2, height=2)
                impresora.text(linea[2:] + "\n")
                continue
            elif linea.startswith("## "):
                impresora.set(align="center", bold=True)
                impresora.text(linea[3:] + "\n")
                continue

            if linea.startswith("| "):
                impresora.set(align="center")
                linea = linea[2:]
            elif linea.startswith("> "):
                impresora.set(align="right")
                linea = linea[2:]

            if linea.startswith("- ") or linea.startswith("* "):
                impresora.text(" * ")
                linea = linea[2:]

            if "**" in linea:
                partes = linea.split("**")
                for i, parte in enumerate(partes):
                    impresora.set(bold=(i % 2 != 0))
                    impresora.text(parte)
                impresora.text("\n")
            else:
                impresora.text(linea + "\n")
