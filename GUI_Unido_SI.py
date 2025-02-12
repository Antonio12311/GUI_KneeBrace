import cv2
import tkinter as tk
import threading
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk
import serial.tools.list_ports
import serial
import os
import math


_DIR = os.path.dirname(__file__)
OUTPUT_PATH = Path(__file__).resolve().parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"

# Global variables for serial connection and widgets (flags)
ser = None
status_label = None
connect_button = None
disconnect_button = None
stop_threads = False


rad = 0
dist = 0.22
gravity = 9.81


def find_video_file(directory, video_name):

    search_dir = Path(directory)

    # Search for the video file recursively
    for file in search_dir.rglob(video_name):
        if file.is_file():  # Ensure it's a file (not a directory)
            return str(file)  # Return the full path as a string

    return None


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
    global status_label, connect_button, disconnect_button

    status_label = tk.Label(canvas, text="Sin conexión", fg="red", font=("Calibri", 14))
    status_label.place(
        x=45.0,
        y=60.0
    )
    connect_button = ttk.Button(canvas, text="Conectar", command=connect_to_arduino)
    connect_button.place(
        x=50.0,
        y=100.0,
        width=100.0,  # Adjusted width to fit text
        height=20.0
    )
    disconnect_button = ttk.Button(canvas, text="Desconectar", command=disconnect_arduino, state="disabled")
    disconnect_button.place(
        x=50.0,
        y=130.0,
        width=100.0,  # Adjusted width to fit text
        height=20.0
    )
    # return status_label, connect_button, disconnect_button


def relative_to_assets(path: str) -> Path:
    return str(ASSETS_PATH / path)


def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Arduino" in port.description or "CH340" in port.description or "USB Serial" in port.description:
            return port.device
    return None


def connect_to_arduino():
    global ser, status_label, connect_button, disconnect_button, stop_threads, leg_animation

    arduino_port = find_arduino_port()
    if arduino_port:
        if ser is None:  # Only connect if not already connected
            try:
                ser = serial.Serial(arduino_port, 115200, timeout=2)
                status_label.config(text=f"Conectado a {arduino_port}", fg="green")
                connect_button.config(state="disabled")
                disconnect_button.config(state="normal")

                # Start the reading thread
                stop_threads = False
                reading_thread = threading.Thread(target=read_serial_port, args=(ser, leg_animation))
                reading_thread.start()

            except Exception as e:
                # messagebox.showerror("Error", f"Failed to connect: {e}")
                if ser:
                    ser.close()
                    ser = None
    else:
        messagebox.showwarning("Sin respuesta", "Arduino no detectado. Revisar la conexión del dispositivo.")


def read_serial_port(arduino,leg_animation):
    global stop_threads, data, position, torque, window, connect, ser, rad

    try:
        while not stop_threads:
            if arduino and arduino.is_open:  # Check if the serial connection is open
                data = arduino.readline().decode().strip()
                if data:
                    values = data.split(",")
                    # Check if there are at least two values
                    if len(values) >= 2:
                        try:
                            # Process the values
                            rad = abs(float(values[0]))  # Assuming the first value is `p_out_s`
                            position = (rad * 180) / math.pi  # Convert radians to degrees
                            torque = abs(float(values[1]))  # Assuming the second value is `t_out_s`
                            print(f"Position: {position}, Torque: {torque}")

                            # Update the animation with the position value
                            if leg_animation:
                                leg_animation.update_frame(position)

                        except ValueError:
                            print("Error: Invalid data format. Skipping this line.")
                    else:
                        print("Error: Insufficient data. Skipping this line.")
                else:
                    print("Warning: No data received.")
            else:
                print("Warning: Serial connection is closed.")
                break  # Exit the loop if the serial connection is closed
    except Exception as e:
        print("Error reading the serial port:", e)
        stop_threads = True


def disconnect_arduino():
    global ser, status_label, connect_button, disconnect_button, stop_threads

    if ser and ser.is_open:
        # Signal the reading thread to stop
        stop_threads = True

        # Close the serial connection
        ser.close()
        ser = None  # Reset the serial object

        # Update the GUI
        status_label.config(text="Disconnected", fg="red")
        connect_button.config(state="normal")
        disconnect_button.config(state="disabled")

        # Reset the stop_threads flag for future connections
        stop_threads = False


def on_closing():
    disconnect_arduino()
    window.destroy()


class LegAnimation:
    def __init__(self, root, canvas, video_path):
        self.root = root
        self.canvas = canvas
        self.video_path = video_path

        # Load video frames
        self.frames = self.load_video_frames(video_path)

        # Create a label to display the video frame
        self.label = tk.Label(self.canvas)
        self.label.place(x=680, y=150)  # Place the label

        self.text_id = self.canvas.create_text(
            645, 250,  # Coordinates (x, y)
            text="0°",  # Text content
            font=("Calibri", 16),  # Font and size
            fill="black"  # Text color
        )

        # Initialize with the first frame
        self.update_frame(0)  # Start with position 0

    def load_video_frames(self, video_path):
        """Load the video and extract frames."""
        cap = cv2.VideoCapture(video_path)
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Convert BGR (OpenCV) to RGB (PIL/Tkinter)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame)
        cap.release()
        return frames

    def input_to_frame(self, position, total_frames):
        """Map position value (in degrees) to frame index."""
        # Map 0° to 150° to 0 to (total_frames - 1)
        return int(((position) / 150) * (total_frames - 1))

    def update_frame(self, position):
        """Update the displayed frame based on position value."""
        frame_index = self.input_to_frame(position, len(self.frames))
        frame = self.frames[frame_index]
        frame_image = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.label.config(image=frame_image)
        self.label.image = frame_image  # Keep a reference to avoid garbage collection

        # Update the text with the current position value
        self.canvas.itemconfig(self.text_id, text=f"{position:.1f}°")


class TextUpdate:
    def __init__(self, root, canvas):
        self.root = root
        self.canvas = canvas

        self.canvas.create_rectangle(600, 230, 670, 270, outline='black', fill='', width=1)

        self.canvas.create_text(
            830, 130,  # Coordinates (x, y)
            text="Ángulo",  # Text content
            font=("Calibri", 16),  # Font and size
            fill="black"  # Text color
        )

def validar_entrada(text):
    return text.isdigit() or text == ""


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
                cuadros[4 - i].config(bg="green")
                niveles_superados[i] = True
            return True
        else:
            messagebox.showwarning("Aviso", "Por favor, seleccione el nivel faltante para hacer los test de forma correcta.")
            combobox.set("Seleccionar el nivel")
            return False
    return True



def aplicar_cambios():
    nivel = combobox.get()
    valor = entrada.get()

    if nivel.startswith("Nivel "):
        nivel_num = int(nivel.split(" ")[1])

        if nivel_num == 4 and valor.isdigit() and int(valor) > 10:
            mensaje_label.config(text="Límite de valor es 10 en Nivel 4", fg="red")
            return
        elif nivel_num == 5 and valor.isdigit() and int(valor) > 20:
            mensaje_label.config(text="Límite de valor es 20 en Nivel 5", fg="red")
            return
        elif nivel_num in (4, 5) and ((not valor.strip() or not valor.isdigit()) or int(valor) == 0):
            mensaje_label.config(text="ERROR. Ingrese un valor de fuerza", fg="red")
            return
        if not verificar_niveles_anteriores(nivel_num):
            return

        mensaje_label.config(text="Cambios aplicados correctamente", fg="green")
        boton_iniciar.config(state="normal")
        boton_detener.config(state="normal")
        entrada.config(state="disabled")
        combobox.config(state="disabled")

    mensaje_label.after(5000, lambda: mensaje_label.config(text=""))


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
            boton_iniciar.config(state="disabled")


def parpadear(cuadro):
    global animacion_activa, blink_state
    if animacion_activa:
        color = "blue" if blink_state else "white"
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
    boton_iniciar.config(state="disabled")
    boton_detener.config(state="disabled")
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
        status_label, connect_button, disconnect_button, leg_animation, combobox, entrada, mensaje_label, cuadros, boton_si, boton_no, boton_iniciar, boton_detener, niveles_superados

    window = tk.Tk()
    window.geometry("1000x720")
    window.configure(background='#8FFDCD')
    canvas = create_canvas(window)
    canvas.configure(background='#8FFDCD')

    video_directory = Path(__file__).resolve().parent / "video"  # Search in the "video" folder
    video_name = "Leg Sequence (4).mp4"  # Name of the video file

    # Automatically detect the video path
    video_path = find_video_file(video_directory, video_name)

    if video_path:
        print(f"Video found: {video_path}")
    else:
        print(f"Error: Video file '{video_name}' not found in '{video_directory}'.")
        messagebox.showerror("Error", f"Video file '{video_name}' not found in '{video_directory}'.")
        return

    niveles = ["Nivel 1", "Nivel 2", "Nivel 3", "Nivel 4", "Nivel 5"]
    combobox = ttk.Combobox(window, values=niveles, font=("Calibri", 16), width=20)
    combobox.set("Elija el nivel de fuerza")
    combobox.place(x=50, y=350)

    vcmd = window.register(validar_entrada)
    entrada = tk.Entry(window, font=("Calibri", 16), width=10, validate="key", validatecommand=(vcmd, "%P"))
    entrada.place(x=100, y=420)
    entrada.config(state="disabled")

    boton_aplicar = tk.Button(window, text="Aplicar cambios", font=("Nunito", 14), command=aplicar_cambios, relief="raised", borderwidth=5)
    boton_aplicar.place(x=50, y=530)

    mensaje_label = tk.Label(window, text="", font=("Calibri", 16), bg="#8FFDCD")
    mensaje_label.place(x=50, y=600)

    fuerzaT_label = tk.Label(window, text="F =", font=("Calibri", 18), bg="#8FFDCD")
    fuerzaT_label.place(x=50, y=420)

    nivelesF_label = tk.Label(window, text="Niveles de fuerza", font=("Calibri", 18), bg="#8FFDCD")
    nivelesF_label.place(x=50, y=310)

    cuadros = []
    for i in range(5):
        cuadro = tk.Label(window, text=str(5 - i), font=("Arial", 14), width=11, height=3, relief="solid", bg="white")
        cuadro.place(x=450, y=610 - (i * 70))
        cuadros.append(cuadro)

    titleC_label = tk.Label(window, text="Niveles", font=("Calibri", 14), bg="#8FFDCD")
    titleC_label.place(x=473, y=300)

    boton_iniciar = tk.Button(window, text="Iniciar", font=("Calibri", 20), command=iniciar_animacion, state="disabled", borderwidth=10, width=6, height=1)
    boton_iniciar.place(x=850, y=450)

    boton_detener = tk.Button(window, text="Detener", font=("Calibri", 20), command=detener_animacion, state="disabled", borderwidth=10, width=6, height=1)
    boton_detener.place(x=850, y=550)

    boton_si = tk.Button(window, text="Si llegó", font=("Calibri", 20), bg="green", state="disabled",
                         command=lambda: marcar_llegada("green"), relief="raised", borderwidth=10, width=6, height=1)
    boton_si.place(x=650, y=450)

    boton_no = tk.Button(window, text="No llegó", font=("Calibri", 20), bg="red", state="disabled",
                         command=lambda: marcar_llegada("red"), relief="raised", borderwidth=10, width=6, height=1)
    boton_no.place(x=650, y=550)

    combobox.bind("<<ComboboxSelected>>", actualizar_estado)

    niveles_superados = [False] * 5

    leg_animation = LegAnimation(window, canvas, video_path)
    TextUpdate(window, canvas)

    connect_widgets(canvas)

    window.resizable(False, False)
    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.mainloop()


animacion_activa = False
blink_state = True

start_connection = threading.Thread(target=connect_to_arduino)
start_connection.start()

# Run the interface
interface()

start_connection.join()