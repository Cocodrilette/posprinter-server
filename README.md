# POS Printer API

Servidor de impresión térmica para papel de 58mm. Proporciona una interfaz Markdown simplificada y una experiencia interactiva para clientes.

## 🛠️ Instalación y Uso
1. Instala dependencias: `pip install -r requirements.txt`
2. Inicia el servidor: `python server.py`
3. Inicia el emulador: `python emulator.py`

## ⚙️ Configuración (.env)
| Variable | Default | Uso |
|---|---|---|
| `HOST` | `0.0.0.0` | Interfaz de escucha (`127.0.0.1` para solo local) |
| `CORS_ORIGINS` | `*` | Orígenes permitidos, separados por coma |
| `PRINT_SERVER_API_KEY` | `mi_super_secreto_123` | Header `X-API-Key` |
| `PHYSICAL_PRINTER_KEY` | `admin_fisico_456` | Campo `physical_key` para imprimir en física |
| `WEB_PORT` | `8000` | API y interfaz web |
| `EMU_TCP_PORT` | `9100` | Emulador ESC/POS (TCP) |
| `EMU_WEB_PORT` | `9021` | Vista web de `emulator.py` standalone |
| `PHYSICAL_PRINTER_NAME` | `POS-58` | Impresora física (Windows) o cola CUPS (macOS/Linux, ver `lpstat -p`) |
| `USB_VENDOR_ID` / `USB_PRODUCT_ID` | – | macOS/Linux: imprime por USB directo en vez de CUPS (`brew install libusb`; IDs con `ioreg -p IOUSB -l`) |

`start_server.bat`, `manage_firewall.ps1` y el proxy de Vite también leen los puertos de `.env`. Ver `.env.example`.

## 🌐 Acceso desde la Red Local
Para acceder desde otros dispositivos (móvil, tablet, etc.):
1. Obtén tu IP local con `ipconfig`.
2. Habilita los puertos en el Firewall de Windows usando el script incluido:
   - Abre PowerShell como Administrador.
   - Ejecuta: `.\manage_firewall.ps1 enable`
3. Accede desde tu móvil a: `http://TU_IP:8000/lucky`

## 🔐 Seguridad
...
Todas las peticiones deben incluir el header:
`X-API-Key: tu_clave_configurada`

Si el destino es la impresora física (`target: "physical"`), se debe enviar adicionalmente el campo `physical_key` en el cuerpo del JSON.

## 📖 Referencia de API

### POST `/print-md`
Envía texto con formato Markdown personalizado.
**Sintaxis Soportada:**
- `# Título` : Tamaño doble, centrado, negrita.
- `## Subtítulo` : Negrita, centrado.
- `### Título pequeño` : Negrita, subrayado.
- `**texto**` : Negrita interna.
- `!!texto!!` : Texto invertido (negativo).
- `---` : Línea separadora simple.
- `===` : Línea separadora doble.
- `| texto` : Centrado.
- `> texto` : Derecha.
- `[ ]` y `[x]` : Checkboxes.
- `!QR(contenido)` : Genera un código QR centrado.
- `!BC(contenido)` : Genera un código de barras CODE128 centrado.
- `!HEART()`: Genera un corazón centrado de tamaño similar a un QR.
- `!MOON()`: Genera una luna centrada de tamaño similar a un QR.
- `!STAR()`: Genera una estrella centrada de tamaño similar a un QR.

### POST `/lucky-print`
Genera un ticket sorpresa con una estrella mágica y una frase profunda.

## 🌐 Interfaces Web
- `http://localhost:8000/` : Editor Markdown y Administrador.
- `http://localhost:8000/lucky` : Experiencia mágica para clientes.
- `http://localhost:8000/docs` : Documentación interactiva (Swagger).
