# POS Printer API Pro 🚀

Servidor de impresión térmica para papel de 58mm. Proporciona una interfaz Markdown simplificada y una experiencia interactiva para clientes.

## 🛠️ Instalación y Uso
1. Instala dependencias: `pip install -r requirements.txt`
2. Inicia el servidor: `python server.py`
3. Inicia el emulador: `python emulator.py`

## 🔐 Seguridad
Todas las peticiones deben incluir el header:
`X-API-Key: tu_clave_configurada`

Si el destino es la impresora física (`target: "physical"`), se debe enviar adicionalmente el campo `physical_key` en el cuerpo del JSON.

## 📖 Referencia de API

### POST `/print-md`
Envía texto con formato Markdown personalizado.
**Sintaxis Soportada:**
- `# Título` : Tamaño doble, centrado, negrita.
- `## Subtítulo` : Negrita, centrado.
- `**texto**` : Negrita interna.
- `---` : Línea separadora.
- `| texto` : Centrado.
- `> texto` : Derecha.

### POST `/lucky-print`
Genera un ticket sorpresa con una estrella mágica y una frase profunda.

## 🌐 Interfaces Web
- `http://localhost:8000/` : Editor Markdown y Administrador.
- `http://localhost:8000/lucky` : Experiencia mágica para clientes.
- `http://localhost:8000/docs` : Documentación interactiva (Swagger).
