import tkinter as tk
from pathlib import Path

OUTPUT_PATH = Path(__file__).resolve().parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# Cargar imágenes
def load_images():
    global img_normal, img_hover, img_click
    img_normal = tk.PhotoImage(file=relative_to_assets("CONNECT_BTN1.png"))   # Imagen por defecto
    img_hover = tk.PhotoImage(file=relative_to_assets("CONNECT_BTN2.png"))   # Imagen cuando el cursor está encima
    img_click = tk.PhotoImage(file=relative_to_assets("CONNECT_BTN3.png"))   # Imagen cuando se hace clic

# Funciones para cambiar la imagen
def on_enter(event):
    button.config(image=img_hover)

def on_leave(event):
    button.config(image=img_normal)

def on_click(event):  # Se cambió el nombre de la función
    button.config(image=img_click)

# Crear ventana
root = tk.Tk()
root.config(bg="white")
root.title("Botón con imágenes")

# Cargar imágenes antes de usarlas
load_images()

# Crear botón con imagen inicial
button = tk.Button(root, image=img_normal, borderwidth=0)
button.pack(pady=20, padx=20)

# Vincular eventos
button.bind("<Enter>", on_enter)  # Cambia imagen al pasar el cursor
button.bind("<Leave>", on_leave)  # Vuelve a la imagen original cuando el cursor se va
button.bind("<Button-1>", on_click)  # Evento de clic (primer botón del ratón)

root.mainloop()



