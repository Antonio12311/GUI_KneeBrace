import cv2
import tkinter as tk
import threading
from tkinter import ttk, messagebox, PhotoImage, Button, Label, Entry
from pathlib import Path
from PIL import Image, ImageTk
import serial.tools.list_ports
import serial
import os
import math
import time
from math import pi, cos, sin

_DIR = os.path.dirname(__file__)
OUTPUT_PATH = Path(__file__).resolve().parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"

# Global variables for serial connection and widgets (flags)
stop_threads = False
cambio_conexion = 0
rad = 0
dist = 0.22
gravity = 9.81



def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)



class Meter(tk.Frame):
    def __init__(self, master=None, **kw):
        tk.Frame.__init__(self, master, **kw)

        self.var = tk.IntVar(self, 0)

        self.canvas = tk.Canvas(self, width=300, height=242,
                                borderwidth=0, relief='sunken',
                                bg='white')  # bg means background
        self.scale = tk.Scale(self, orient='horizontal', from_=0, to=180, variable=self.var)

        # Create the needle (line)
        self.meter = self.canvas.create_line(1000000, 15000000, 1000000, 15000000,
                                             fill='black',
                                             width=3,
                                             arrow='last')

        self.updateMeterLine(0)  # Initialize the needle position

        # Create the arc
        self.canvas.create_arc(30, 30, 200, 200, extent=140, start=230,
                               style='arc', outline='red')

        self.canvas.pack(fill='both')  # Adds the canvas to the window
        self.scale.pack()  # Adds the scale widget to the window

        self.var.trace_add('write', self.updateMeter)

    def updateMeterLine(self, a):
        # Convert the normalized value `a` to an angle in radians
        start_angle = 245  # Start angle of the arc
        extent = 115  # Extent of the arc
        angle_deg = start_angle + a * extent  # Calculate the angle in degrees
        angle_rad = angle_deg * (pi / 180)  # Convert to radians

        # Calculate the endpoint of the needle
        x = 100 + 85 * cos(angle_rad)  # 100 is the center of the canvas
        y = 100 - 85 * sin(angle_rad)

        # Update the needle's position
        self.canvas.coords(self.meter, 100, 100, x, y)

    def updateMeter(self, name1, name2, op):
        """Convert variable to angle on trace"""
        mini = self.scale.cget('from')
        maxi = self.scale.cget('to')
        pos = (self.var.get() - mini) / (maxi - mini)  # Normalized position (0 to 1)
        self.updateMeterLine(pos)  # Update the needle position



def create_canvas(root):
    canvas = tk.Canvas(
        root,
        bg="#FFFFFF",
        height=720,
        width=1280,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.place(x=0, y=0)
    return canvas

def connect_widgets(canvas):
    global status_label, disconnect_button, connect_button

    status_label = tk.Label(canvas, text="Sin conexión", fg="red", font=("Calibri", 14), anchor="center", width=20)
    status_label.place(x=45.0, y=60.0, anchor="center")

    connect_button_image = PhotoImage(file=relative_to_assets("BOTON_IMG_CONECTAR.png"))
    connect_button = Button(
        window,
        image=connect_button_image,
        command=connect_to_arduino,
        borderwidth=4,
        highlightthickness=2,
        relief="raised"
    )
    connect_button.place(x=50.0, y=100.0, width=120.0, height=40.0)

    disconnect_button_image = PhotoImage(file=relative_to_assets("BOTON_IMG_DESCONECTAR.png"))
    disconnect_button = Button(
        window,
        image=disconnect_button_image,
        command=disconnect_arduino,
        state="disabled",
        bg="#8FFDCD",
        borderwidth=4,
        highlightthickness=2,
        relief="raised"
    )
    disconnect_button.place(x=50.0, y=150.0, width=120.0, height=40.0)

    return disconnect_button, disconnect_button_image, connect_button, connect_button_image

def name_entry_widget(canvas):
    ruta_img = relative_to_assets("NeonEntry.png")
    image_widget = PhotoImage(file=ruta_img)

    entry_bg_1 = canvas.create_image(
        480.0,
        50.0,
        image=image_widget
    )
    entry_1 = Entry(
        bd=0,
        bg="#D4DBF5",
        fg="#000000",
        highlightthickness=0,
        state="normal",
        font="Calibri 13"
    )
    entry_1.place(
        x=200.0,
        y=32.0,
        width=340.0,
        height=35.0
    )
    canvas.create_text(
        40,
        40,
        anchor="nw",
        text="Nombre de pac.",
        fill="#000000",
        font="Calibri 13"
    )
    return entry_1, image_widget

def age_entry_widget(canvas):
    ruta_img = relative_to_assets("EntryEdad_Label_Img.png")
    image_widget = PhotoImage(file=ruta_img)

    entry_bg_2 = canvas.create_image(
        465.0,
        130.0,
        image=image_widget
    )
    entry_2 = Label(
        bd=0,
        bg="#acdccc",
        fg="#000716",
        highlightthickness=0,
        state="normal",
        font="Calibri 13"
    )
    entry_2.place(
        x=415.0,
        y=110.0,
        width=80.0,
        height=35.0
    )
    canvas.create_text(
        345,
        120,
        anchor="nw",
        text="Edad",
        fill="#FFFFFF",
        font="Calibri 13"
    )
    return entry_2, image_widget

def grados_widget(canvas):
    ruta_img = relative_to_assets("ThetaBox.png")
    image_widget3 = PhotoImage(file=ruta_img)

    box_bg_1 = canvas.create_image(
        648.0,
        329.0,
        image=image_widget3
    )
    return image_widget3

def connect_to_arduino():
    global cambio_conexion
    cambio_conexion = 1
    if cambio_conexion == 1:
        status_label.config(text="Dispositivo Conectado", fg="#549f4d", font=("Calibri", 14))
        connect_button.config(state="disabled")
        disconnect_button.config(state="normal")
        combobox.config(state="normal")
        boton_aplicar.config(state="normal")

def disconnect_arduino():
    cambio_conexion = 0
    if cambio_conexion == 0 and boton_toggle["text"] == "Iniciar":
        status_label.config(text="Sin conexión", fg="red")
        connect_button.config(state="normal")
        disconnect_button.config(state="disabled")
        combobox.config(state="disabled")
        boton_aplicar.config(state="disabled")
    elif cambio_conexion == 0 and boton_toggle["text"] == "Detener":
        messagebox.showwarning("ERROR", "No se puede desconectar mientras el dispositivo está en funcionamiento")

def on_closing():
    window.destroy()



def toggle_boton():
    if boton_toggle["text"] == "Iniciar":
        iniciar_animacion()
        boton_toggle.config(text="Detener",image=imagen_detener, command=toggle_boton)
    else:
        detener_animacion()
        boton_toggle.config(text="Iniciar", image=imagen_iniciar, command=toggle_boton)
        cuadros[4].config(bg="#FFFFFF")
        cuadros[3].config(bg="#FFFFFF")
        cuadros[2].config(bg="#FFFFFF")
        cuadros[1].config(bg="#FFFFFF")
        cuadros[0].config(bg="#FFFFFF")

def validar_entrada(text):
    return text.isdigit() or text == ""

def aplicar_cambios():
    nivel = combobox.get()
    valor = entrada.get()

    if nivel.startswith("Nivel "):
        nivel_num = int(nivel.split(" ")[1])

        if nivel_num == 4 and valor.isdigit() and int(valor) > 10:
            mensaje_label1.config(text="El límite del valor", fg="#F43838", bg="#D4DBF5")
            mensaje_label2.config(text="es 10 en nivel 4", fg="#F43838", bg="#D4DBF5")
            return
        elif nivel_num == 5 and valor.isdigit() and int(valor) > 20:
            mensaje_label1.config(text="El límite del valor", fg="#F43838", bg="#D4DBF5")
            mensaje_label2.config(text="es 20 en Nivel 5", fg="#F43838", bg="#D4DBF5")
            return
        elif nivel_num in (4, 5) and ((not valor.strip() or not valor.isdigit()) or int(valor) == 0):
            mensaje_label1.config(text="ERROR. Ingrese un valor", fg="#F43838", bg="#D4DBF5")
            mensaje_label2.config(text="de fuerza", fg="#F43838", bg="#D4DBF5")
            return
        if not verificar_niveles_anteriores(nivel_num):
            return

        mensaje_label1.config(text="Cambios aplicados", fg="#549f4d")
        mensaje_label2.config(text="correctamente", fg="#549f4d")
        #boton_iniciar.config(state="normal")
        #boton_detener.config(state="normal")
        entrada.config(state="disabled")
        combobox.config(state="disabled")
        boton_toggle.config(state="normal")

    mensaje_label1.after(5000, lambda: mensaje_label1.config(text=""))
    mensaje_label2.after(5000, lambda: mensaje_label2.config(text=""))

def save_boton():
    messagebox.showinfo("Test Finalizado", "El registro y test ha concluido. Su archivo ha sido guardado.")
    boton_save.config(state="disabled")
    entrada.config(state="disabled")
    cuadros[4].config(bg="#FFFFFF")
    cuadros[3].config(bg="#FFFFFF")
    cuadros[2].config(bg="#FFFFFF")
    cuadros[1].config(bg="#FFFFFF")
    cuadros[0].config(bg="#FFFFFF")
    niveles_superados[:] = [False] * len(niveles_superados)

    disconnect_arduino()

def actualizar_estado(event=None):
    # Habilita la entrada solo si Nivel 4 o Nivel 5 están seleccionados
    if combobox.get() in ["Nivel 4", "Nivel 5"]:
        entrada.config(state="normal")
    else:
        entrada.config(state="disabled")
        entrada.delete(0, tk.END)

def verificar_niveles_anteriores(nivel_actual):
    # Pregunta solo si es la primera vez seleccionando un nivel mayor a 1
    if nivel_actual > 1 and not niveles_superados[nivel_actual - 1]:
        respuesta = messagebox.askquestion("Confirmación", f"¿Pasó exitosamente los niveles 1 a {nivel_actual - 1}?")
        if respuesta == "yes":
            for i in range(nivel_actual - 1):
                cuadros[4 - i].config(bg="#06D7A0")
                niveles_superados[i] = True
            return True
        else:
            messagebox.showwarning("Aviso", "Por favor, seleccione el nivel faltante para hacer los test de forma correcta.")
            combobox.set("Seleccionar el nivel")
            return False
    return True

def iniciar_animacion():
    nivel = combobox.get()

    if nivel.startswith("Nivel "):
        nivel_num = int(nivel.split(" ")[1])
        if 1 <= nivel_num <= 5:
            global animacion_activa, blink_state
            animacion_activa = True
            blink_state = True
            parpadear(cuadros[5 - nivel_num])

            combobox.config(state="disabled")
            boton_si.config(state="normal")
            boton_no.config(state="normal")
            entrada.config(state="disabled")
            boton_save.config(state="disabled")
            boton_toggle.config(text="Detener", command=detener_animacion)

def parpadear(cuadro):
    global animacion_activa, blink_state
    if animacion_activa:
        color = "#A56ABD" if blink_state else "white"
        cuadro.config(bg=color)
        blink_state = not blink_state
        cuadro.after(500, lambda: parpadear(cuadro))




def detener_animacion():
    global animacion_activa
    nivel = combobox.get()
    animacion_activa = False
    boton_si.config(state="disabled")
    boton_no.config(state="disabled")
    combobox.config(state="normal")
    #boton_iniciar.config(state="disabled")
    #boton_detener.config(state="disabled")
    boton_toggle.config(text="Iniciar",image=imagen_iniciar, command=iniciar_animacion, state="disabled")
    boton_save.config(state="normal")
    if nivel.startswith("Nivel "):
        nivel_num = int(nivel.split(" ")[1])
        if nivel_num > 3:
            entrada.config(state="normal")



def marcar_llegada(color):
    nivel = combobox.get()

    if nivel.startswith("Nivel "):
        nivel_num = int(nivel.split(" ")[1])
        if 1 <= nivel_num <= 3:
            detener_animacion()
            cuadros[5 - nivel_num].config(bg=color)
            niveles_superados[nivel_num - 1] = True
            entrada.config(state="disabled")
        else:
            detener_animacion()
            cuadros[5 - nivel_num].config(bg=color)
            niveles_superados[nivel_num - 1] = True
            entrada.config(state="normal")


def interface():
    global window, entry_image1, entry_image2, entry_image3, entry_image4, \
        status_label, connect_button, disconnect_button, leg_animation, combobox, entrada, mensaje_label1, mensaje_label2, cuadros, boton_si, boton_no, boton_toggle, niveles_superados, boton_arduino_sim, boton_aplicar, entry_1, image_widget, image_widget3, boton_save, imagen_iniciar, imagen_detener, imagen_aplicar, imagen_guardar

    window = tk.Tk()
    window.geometry("1000x720")
    window.title("Knee Brace GUI")
    window.configure(background='#D4DBF5')
    canvas = create_canvas(window)
    canvas.configure(background='#D4DBF5')




    niveles = ["Nivel 1", "Nivel 2", "Nivel 3", "Nivel 4", "Nivel 5"]
    combobox = ttk.Combobox(window, values=niveles, font=("Calibri", 14), width=20)
    combobox.set("Elija el nivel de fuerza")
    combobox.place(x=300, y=555)
    combobox.config(state="disabled")

    vcmd = window.register(validar_entrada)
    entrada = tk.Entry(window, font=("Calibri", 16), width=10, validate="key", validatecommand=(vcmd, "%P"), bg="#D4DBF5")
    entrada.place(x=350, y=600)
    entrada.config(state="disabled")

    imagen_aplicar = PhotoImage(file=relative_to_assets("APPLY_BTN.png"))

    boton_aplicar = tk.Button(window, image=imagen_aplicar, command=aplicar_cambios, relief="flat", bg="#D4DBF5", highlightbackground="#D4DBF5")
    boton_aplicar.place(x=300, y=640)
    boton_aplicar.config(state="disabled")

    mensaje_label1 = tk.Label(window, text="", font=("Calibri", 12), bg="#D4DBF5")
    mensaje_label1.place(x=490, y=650)
    mensaje_label2 = tk.Label(window, text="", font=("Calibri", 12), bg="#D4DBF5")
    mensaje_label2.place(x=490, y=670)

    fuerzaT_label = tk.Label(window, text="F =", font=("Calibri", 18), bg="#D4DBF5", fg="#000000")
    fuerzaT_label.place(x=300, y=600)
    fuerzaKg_label = tk.Label(window, text="Kg", font=("Calibri", 18), bg="#D4DBF5", fg="#000000")
    fuerzaKg_label.place(x=500, y=600)

    nivelesF_label = tk.Label(window, text="Niveles de fuerza", font=("Calibri", 18), bg="#D4DBF5", fg="#000000")
    nivelesF_label.place(x=300, y=520)

    cuadros = []
    for i in range(5):
        cuadro = tk.Label(window, text=str(5 - i), font=("Arial", 14), width=11, height=3, relief="solid", bg="white")
        cuadro.place(x=750, y=410 - (i * 70))
        cuadros.append(cuadro)

    titleC_label = tk.Label(window, text="Niveles", font=("Calibri", 18), bg="#D4DBF5", fg="#000000")
    titleC_label.place(x=761, y=90)

    grados_label = tk.Label(window, text="Grados", font=("Calibri", 14), bg="#D4DBF5", fg="#000000")
    grados_label.place(x=610, y=280)

    imagen_iniciar = PhotoImage(file=relative_to_assets("START_BTN.png"))
    imagen_detener = PhotoImage(file=relative_to_assets("STOP_BTN.png"))

    boton_toggle = tk.Button(
        window,
        text="Iniciar",
        font=("Calibri", 16),
        command=toggle_boton,
        state="normal",
        image=imagen_iniciar,
        relief="flat",
        borderwidth=0,
        highlightbackground="#D4DBF5",
        bg="#D4DBF5")
    boton_toggle.place(x=745, y=500)
    boton_toggle.config(state="disabled")

    imagen_guardar = PhotoImage(file=relative_to_assets("SAVE_BTN.png"))
    boton_save = tk.Button(
        window,
        image=imagen_guardar,
        state="normal",
        relief="flat",
        borderwidth=0,
        bg="#D4DBF5",
        highlightbackground="#D4DBF5",
        command=save_boton)
    boton_save.place(x=707, y=640)
    boton_save.config(state="disabled")

    imagen_SI = PhotoImage(file=relative_to_assets("ACHIEVED_BTM.png"))
    imagen_NO = PhotoImage(file=relative_to_assets("FAILED_BTN.png"))

    boton_si = tk.Button(window, image=imagen_SI, state="disabled", command=lambda: marcar_llegada("#06D7A0"), relief="flat", bg="#D4DBF5", highlightbackground="#D4DBF5")
    boton_si.place(x=670, y=570)

    boton_no = tk.Button(window, image=imagen_NO, state="disabled", command=lambda: marcar_llegada("#F04770"), relief="flat", bg="#D4DBF5", highlightbackground="#D4DBF5")
    boton_no.place(x=820, y=570)

    status_label = tk.Label(canvas, text="Sin conexión", fg="red", font=("Calibri", 14), bg="#D4DBF5")
    status_label.place(x=50, y=530)

    connect_button_image = PhotoImage(file=relative_to_assets("CONNECT_BTN1.png"))
    connect_button = Button(
        window,
        image=connect_button_image,
        command=connect_to_arduino,
        relief="flat",
        bg="#D4DBF5",
        highlightcolor="black",
        highlightbackground="#D4DBF5"
    )
    connect_button.place(x=100, y=570)

    disconnect_button_image = PhotoImage(file=relative_to_assets("DISCONNECT_BTN1.png"))
    disconnect_button = Button(
        window,
        image=disconnect_button_image,
        command=disconnect_arduino,
        state="disabled",
        relief="flat",
        bg="#D4DBF5",
        highlightbackground="#D4DBF5"
    )
    disconnect_button.place(x=100, y=630)

    combobox.bind("<<ComboboxSelected>>", actualizar_estado)

    niveles_superados = [False] * 5

    entry_1, image_widget = name_entry_widget(canvas)
    image_widget3 = grados_widget(canvas)

    window.resizable(False, False)
    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.mainloop()

animacion_activa = False
blink_state = True

# Run the interface
interface()