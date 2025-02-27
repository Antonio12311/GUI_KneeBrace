import tkinter as tk
import threading
from tkinter import ttk, messagebox, PhotoImage, Button
from pathlib import Path
import serial.tools.list_ports
import serial
import os
import math
import time

_DIR = os.path.dirname(__file__)
OUTPUT_PATH = Path(__file__).resolve().parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class AppInterface2:
    def __init__(self, root):
        self.updateMeterLine = None
        self.MeterWidget = None
        self.messagebox = None
        self.stop_button_widget = None
        self.start_button_widget = None
        self.send_data = None
        self.level = None
        self.value = None
        self.text = None
        self.combobox = None
        self.entry_bg_1 = None
        self.entry_1 = None
        self.connect_button_image = None
        self.ser = None
        self.type_input = None
        self.stop_threads = False
        self.active_animation = True
        self.blink_state = True
        self.root = root
        self.frames_path = Path(__file__).resolve().parent / "light_video"
        self.root.geometry("1000x720")
        self.root.resizable(False, False)
        self.used_color = '#D4DBF5'
        self.root.configure(bg=self.used_color)
        self.canvas = self.create_canvas()
        self.serial_widgets()
        self.create_combo_widget()

    def create_canvas(self):
        canvas = tk.Canvas(
            self.root,
            bg=self.used_color,
            height=720,
            width=1000,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        canvas.place(x=0, y=0)
        return canvas

    def serial_widgets(self):

        self.status_label = tk.Label(self.canvas, text="Sin conexión", fg="red", font=("Georgia", 14),
                                     bg=self.used_color)
        self.status_label.place(x=85.0, y=530.0)

        self.connect_button_image = PhotoImage(file=relative_to_assets("CONNECT_BTN1.png"))
        self.connect_button_image = PhotoImage(file=relative_to_assets("CONNECT_BTN1.png"))
        self.connect_button = Button(
            self.canvas,
            image=self.connect_button_image,
            command=self.connect_to_arduino,
            relief="flat",
            bg=self.used_color
        )
        self.connect_button.place(x=70, y=570)

        self.disconnect_button_image = PhotoImage(file=relative_to_assets("DISCONNECT_BTN1.png"))
        self.disconnect_button = Button(
            self.canvas,
            image=self.disconnect_button_image,
            command=self.disconnect_arduino,
            state="disabled",
            relief="flat",
            bg=self.used_color
        )
        self.disconnect_button.place(x=70, y=630)

    def find_arduino_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "Arduino" in port.description or "CH340" in port.description or "USB Serial" in port.description:
                return port.device
        return None

    def read_serial_port(self):
        try:
            while not self.stop_threads:
                if self.ser and self.ser.is_open:
                    data = self.ser.readline().decode().strip()
                    if data:
                        values = data.split(",")
                        if len(values) >= 2:
                            try:
                                rad = abs(float(values[0]))
                                position = (rad * 180) / math.pi
                                torque = abs(float(values[1]))
                            except ValueError:
                                print("Error: Invalid data format. Skipping this line.")
                        else:
                            print("Error: Insufficient data. Skipping this line.")
                    else:
                        print("Warning: No data received.")
                else:
                    break
        except Exception as e:
            print("Error reading the serial port:", e)
            self.stop_threads = True

    def send_serial_port(self):
        try:
            while not self.stop_threads is True:
                time.sleep(0.05)
        except Exception as e:
            print("Error sending data", e)
            self.stop_threads = True

    def connect_to_arduino(self):
        arduino_port = self.find_arduino_port()
        if arduino_port:
            if self.ser is None:
                try:
                    self.arduino_lock = threading.Lock()
                    self.ser = serial.Serial(arduino_port, 115200, timeout=1)
                    self.status_label.config(text=f"Connected to {arduino_port}", fg="green", font=("Georgia", 14))
                    self.connect_button.config(state="normal")
                    self.disconnect_button.config(state="normal")
                    self.combobox.config(state="normal")
                    self.stop_threads = False

                except Exception as e:
                    messagebox.showerror("Error", f"Failed to connect: {e}")
                    if self.ser:
                        self.ser.close()
                        self.ser = None
                if self.ser is not None:
                    # Starting the reading thread
                    reading_thread = threading.Thread(target=self.read_serial_port, args=self.ser)
                    reading_thread.start()

                    # Starting the sending thread
                    sending_thread = threading.Thread(target=self.send_data, args=self.ser)
                    sending_thread.start()

        else:
            messagebox.showwarning("Not Found", "Arduino not found. Please check the connection.")

    def disconnect_arduino(self):
        self.turn_off_motor()
        if self.ser and self.ser.is_open:
            self.stop_threads = True
            self.ser.close()
            self.ser = None
            self.status_label.config(text="Sin conexión", fg="red", font=("Georgia", 14))
            self.connect_button.config(state="normal")
            self.disconnect_button.config(state="disabled")
            self.combobox.config(state="disabled")
            self.stop_threads = False

    def toggle_boton(self):
        if self.boton_toggle["text"] == "Iniciar":
            self.animation_on_write_serial()
            self.boton_toggle.config(text="Detener", image=self.imagen_detener, command=self.toggle_boton)
        else:
            self.animation_off_write_serial()
            self.boton_toggle.config(text="Iniciar", image=self.imagen_iniciar, command=self.toggle_boton)

    def create_combo_widget(self):
        levels = ["Nivel 1", "Nivel 2", "Nivel 3", "Nivel 4", "Nivel 5"]
        self.combobox = ttk.Combobox(self.canvas, values=levels, font=("Georgia", 14), width=20)
        self.combobox.set("Elija el nivel de fuerza")
        self.combobox.config(state="disabled")  # Make the combobox readonly
        self.combobox.place(x=300, y=555)

        self.imagen_iniciar = PhotoImage(file=relative_to_assets("START_BTN.png"))
        self.imagen_detener = PhotoImage(file=relative_to_assets("STOP_BTN.png"))

        self.boton_toggle = tk.Button(
            self.canvas,
            text="Iniciar",
            font=("Georgia", 16),
            command=self.toggle_boton,
            state="normal",
            relief="flat",
            borderwidth=0,
            bg=self.used_color,
            image=self.imagen_iniciar)
        self.boton_toggle.place(x=745, y=560)
        self.boton_toggle.config(state="normal")

        self.imagen_SI = PhotoImage(file=relative_to_assets("ACHIEVED_BTM.png"))
        self.imagen_NO = PhotoImage(file=relative_to_assets("FAILED_BTN.png"))

        self.yes_button_widget = tk.Button(self.canvas, image=self.imagen_SI, state="disabled",
                                           command=lambda: self.achieved_test("#06D7A0"), relief="flat",
                                           bg=self.used_color)

        self.yes_button_widget.place(x=770, y=200)

        self.no_button_widget = tk.Button(self.canvas, image=self.imagen_NO, state="disabled",
                                          command=lambda: self.failed_test("#F04770"), relief="flat",
                                          bg=self.used_color)
        self.no_button_widget.place(x=770, y=300)

        self.combobox.bind("<<ComboboxSelected>>")

    def animation_on_write_serial(self):
        self.combobox.config(state="disabled")
        time.sleep(0.10)
        self.turn_on_motor()
        time.sleep(0.10)
        self.send_value()

    def animation_off_write_serial(self):
        self.combobox.config(state="readonly")
        time.sleep(0.05)
        self.turn_off_motor()
        time.sleep(0.05)

    def achieved_test(self, color):
        self.combobox.config(state="readonly")
        self.turn_off_motor()

    def failed_test(self, color):
        self.combobox.config(state="readonly")
        self.turn_off_motor()

    def send_value(self):
        cadena = str(self.combobox.get())
        # Extract the number using split()
        nivel = cadena.split()[1]  # Splits the string and takes the second part (index 1)
        self.arduino_lock.acquire()
        time.sleep(0.05)
        self.ser.write((nivel + "\n").encode('ascii'))  # Send only the number
        time.sleep(0.05)
        self.arduino_lock.release()

    def turn_on_motor(self):
        if self.ser is not None:
            cadena = "998\n"
            self.arduino_lock.acquire()
            time.sleep(0.05)
            self.ser.write(cadena.encode('ascii'))
            time.sleep(0.05)
            self.arduino_lock.release()

    def turn_off_motor(self):
        if self.ser is not None:
            cadena = "999\n"
            self.arduino_lock.acquire()
            time.sleep(0.05)
            self.ser.write(cadena.encode('ascii'))
            time.sleep(0.05)
            self.arduino_lock.release()

    def on_closing(self):
        self.turn_off_motor()
        time.sleep(0.05)
        self.disconnect_arduino()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AppInterface2(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
