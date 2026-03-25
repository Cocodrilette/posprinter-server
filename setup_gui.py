import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import sys
import threading
from dotenv import load_dotenv, set_key

ENV_FILE = ".env"

def save_and_run():
    printer_name = printer_entry.get().strip()
    if not printer_name:
        messagebox.showerror("Error", "Por favor ingresa un nombre de impresora válido")
        return
    
    # Save to .env
    if not os.path.exists(ENV_FILE):
        with open(ENV_FILE, "w") as f:
            f.write(f'PHYSICAL_PRINTER_NAME="{printer_name}"\n')
    else:
        set_key(ENV_FILE, "PHYSICAL_PRINTER_NAME", printer_name)
    
    root.destroy()

def center_window(window, width=400, height=200):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

# Load existing name
load_dotenv()
current_printer = os.getenv("PHYSICAL_PRINTER_NAME", "POS-58")

root = tk.Tk()
root.title("Configuración POS Printer")
center_window(root)

style = ttk.Style()
style.configure("TLabel", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10, "bold"))

main_frame = ttk.Frame(root, padding="20")
main_frame.pack(expand=True, fill="both")

ttk.Label(main_frame, text="Configura tu Impresora Física", font=("Segoe UI", 12, "bold")).pack(pady=(0, 10))
ttk.Label(main_frame, text="Nombre de la impresora (Windows):").pack(anchor="w")

printer_entry = ttk.Entry(main_frame, width=40)
printer_entry.insert(0, current_printer)
printer_entry.pack(pady=5)

ttk.Label(main_frame, text="Ejemplo: POS-58, XP-80, etc.", foreground="gray").pack(anchor="w")

btn_run = ttk.Button(main_frame, text="Guardar y Iniciar Servidor", command=save_and_run)
btn_run.pack(pady=20)

root.mainloop()
