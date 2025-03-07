import tkinter as tk
import threading
from tkinter import ttk, messagebox, PhotoImage, Button, Entry, filedialog
from pathlib import Path
from PIL import Image, ImageTk
import serial.tools.list_ports
import serial
import os
import math
import time
import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter  # Importar la función para convertir números a letras de columna
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabelList  # Importar DataLabelList

_DIR = os.path.dirname(__file__)
OUTPUT_PATH = Path(__file__).resolve().parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"


def validate_number_input(new_value):
    if new_value == "":
        return True
    try:
        float(new_value)
        return True
    except ValueError:
        return False


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


class Controller:
    def __init__(self, root):
        self.root = root
        self.patient_data = {}  # Shared data structure
        self.current_frame = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Bind the closing event

    def switch_frame(self, new_frame_class):
        """Switch to a new frame."""
        if hasattr(self.current_frame, 'disconnect_arduino'):
            self.current_frame.disconnect_arduino()  # Disconnect the Arduino if the method exists
        if self.current_frame:
            self.current_frame.pack_forget()  # Hide the current frame
        self.current_frame = new_frame_class(self.root, self, self.patient_data)
        self.current_frame.pack(fill="both", expand=True)

    def on_closing(self):
        """Handle the application closing event."""
        if hasattr(self.current_frame, 'turn_off_motor'):
            self.current_frame.turn_off_motor()  # Turn off the motor if the method exists
        if hasattr(self.current_frame, 'disconnect_arduino'):
            self.current_frame.disconnect_arduino()  # Disconnect the Arduino if the method exists
        time.sleep(0.05)  # Small delay
        self.root.destroy()  # Close the application


# --------------------------- Clase Base para compartir datos --------------------------- #
class AppBase(tk.Frame):
    def __init__(self, root, controller, patient_data):
        super().__init__(root)
        self.root = root
        self.controller = controller
        self.patient_data = patient_data  # Shared patient data
        self.used_color = 'white'
        self.text_color = "#3c3d40"
        self.connected_color = "#00487C"
        self.disconnected_color = "#9E2B25"
        self.root.configure(bg=self.used_color)
        self.validate_func = self.register(validate_number_input)  # Validación numérica


class AppInterface0(AppBase):
    def __init__(self, root, controller, patient_data):
        super().__init__(root, controller, patient_data)
        self.pack(fill="both", expand=True)
        self.dimension_x0 = "630"
        self.dimension_y0 = "550"

        self.screen_width = self.root.winfo_screenwidth()  # Obtiene el ancho de la pantalla
        self.screen_height = self.root.winfo_screenheight()  # Obtiene el alto de la pantalla
        self.x0 = (self.screen_width // 2) - (int(self.dimension_x0) // 2)  # Calcula la posición X
        self.y0 = (self.screen_height // 2) - (int(self.dimension_y0) // 2)  # Calcula la posición Y
        self.root.geometry(f"{self.dimension_x0}x{self.dimension_y0}+{self.x0}+{self.y0}")

        self.root.resizable(False, False)
        self.root.configure(bg=self.used_color)
        self.canvas = self.create_canvas(self.dimension_y0, self.dimension_x0)
        self.validate_func = self.canvas.register(validate_number_input)
        self.init_widgets()

    def create_canvas(self, dimension_y, dimension_x):
        canvas = tk.Canvas(
            self.root,
            bg=self.used_color,
            height=int(dimension_y),
            width=int(dimension_x),
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        canvas.place(x=0, y=0)
        return canvas

    def init_widgets(self):
        # Title
        self.canvas.create_text(145, 25, anchor="nw", text="Registro de paciente", fill=self.text_color, font=("Inter", 30))

        # Patient name

        self.patient_bg_image = PhotoImage(file=relative_to_assets("PATIENT_ENTR_BG.png"))
        self.canvas.create_image(105, 101, image=self.patient_bg_image, anchor="nw")

        self.entry_00 = Entry(bd=0, bg="white", fg="#000000", highlightthickness=0, font=("Inter", 13))
        self.entry_00.place(x=140.0, y=127.0, width=320.0, height=20.0)

        # Expedient #
        self.exp_bg_image = PhotoImage(file=relative_to_assets("EXP_ENTR_BG.png"))
        self.canvas.create_image(105, 169, image=self.exp_bg_image, anchor="nw")
        self.entry_02 = Entry(bd=0, bg="white", fg="#000000", highlightthickness=0, state="normal", font=("Inter", 13))
        self.entry_02.place(x=140.0, y=195.0, width=320.0, height=20.0)

        # Age
        self.age_bg_image = PhotoImage(file=relative_to_assets("AGE_ENTRY_BG.png"))
        self.canvas.create_image(105, 237, image=self.age_bg_image, anchor="nw")
        self.entry_01 = Entry(bd=0, bg="white", fg="#000000", highlightthickness=0, state="normal",
                              font=("Inter", 13), validate="key", validatecommand=(self.validate_func, "%P"))
        self.entry_01.place(x=140.0, y=263.0, width=100.0, height=20.0)

        # Sex
        self.sex_bg_image = PhotoImage(file=relative_to_assets("SEX_ENTRY_BG.png"))
        self.canvas.create_image(327, 237, image=self.sex_bg_image, anchor="nw")
        genders = ["Masculino", "Femenino"]
        self.combobox1 = ttk.Combobox(self.canvas, values=genders, font=("Inter", 12))
        self.combobox1.config(state="readonly")
        self.combobox1.set("...")
        self.combobox1.place(x=360.0, y=262.0, width=120.0, height=20)

        # Physical activity
        self.act_bg_image = PhotoImage(file=relative_to_assets("ACT_ENTRY_BG.png"))
        self.canvas.create_image(105, 308, image=self.act_bg_image, anchor="nw")
        lifestl = ["Sedentario", "Actividad moderada", "Deportista"]
        self.combobox2 = ttk.Combobox(self.canvas, values=lifestl, font=("Inter", 13))
        self.combobox2.config(state="readonly")
        self.combobox2.set("...")
        self.combobox2.place(x=140.0, y=333.0, width=200.0, height=24)

        # Date
        self.date_bg_image = PhotoImage(file=relative_to_assets("DATE_ENTRY_BG.png"))
        self.canvas.create_image(105, 376, image=self.date_bg_image, anchor="nw")

        # Next page button
        self.register_bg_image = PhotoImage(file=relative_to_assets("SWITCH_BTN_BG.png"))
        self.switch_button = tk.Button(self.canvas, image=self.register_bg_image, text="Go to Interface 1",
                                       command=self.save_and_next, state="normal", relief="flat",
                                       borderwidth=0, bg=self.used_color,)
        self.switch_button.place(x=224.0, y=476.0)

        # Settings page button
        self.settings_bg_image = PhotoImage(file=relative_to_assets("COG_BG.png"))
        self.settings_button = Button(
            self.canvas,
            image=self.settings_bg_image,
            relief="flat",
            bg=self.used_color
        )
        self.settings_button.place(x=544, y=476)

        self.select_bg_image = PhotoImage(file=relative_to_assets("SELECT_BG_IMAGE.png"))
        self.select_folder_button = Button(
            self.canvas,
            image=self.select_bg_image,
            command=self.select_output_folder,
            relief="flat",
            state="normal",
            bg=self.used_color
        )
        self.select_folder_button.place(x=400, y=386)

    def select_output_folder(self):
        """Abre un diálogo para seleccionar la carpeta de salida."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_folder = Path(folder_selected)
            self.patient_data["output_folder"] = self.output_folder  # Guardar la ruta en patient_data
            messagebox.showinfo("Carpeta seleccionada", f"Los archivos se guardarán en: {self.output_folder}")

    def get_all_entries(self):
        return (
            self.entry_00.get(),
            self.entry_01.get(),
            self.entry_02.get(),
            self.combobox1.set("...")  # Sex
        )

    def reset_entries(self):
        # Reset all entries to blank
        self.entry_00.delete(0, tk.END)
        self.entry_01.delete(0, tk.END)
        self.entry_02.delete(0, tk.END)

    def save_and_next(self):
        """Guarda la información y cambia de interfaz."""
        self.patient_data["Nombre"] = self.entry_00.get()
        self.patient_data["Edad"] = self.entry_01.get()
        self.patient_data["Sexo"] = self.combobox1.get()
        self.patient_data["Actividad"] = self.combobox2.get()
        self.patient_data["Expediente"] = self.entry_02.get()

        if not all(self.patient_data.values()):
            messagebox.showwarning("Error", "Asegúrese de llenar todos los espacios")
            return
        self.controller.switch_frame(AppInterface1)

    def error_message(self):
        messagebox.showwarning("Error", "Asegurese de llenar todos los espacios")

    def show(self):
        self.canvas.place(x=0, y=0)  # Show the current interface

    def on_closing(self):
        self.root.destroy()


# --------------------------- Segunda Interfaz --------------------------- #
class AppInterface1(AppBase):
    def __init__(self, root, controller, patient_data):
        super().__init__(root, controller, patient_data)
        self.pack(fill="both", expand=True)
        self.root = root
        self.dimension_x0 = "630"
        self.dimension_y0 = "550"
        self.root.resizable(False, False)
        self.root.configure(bg=self.used_color)

        self.screen_width = self.root.winfo_screenwidth()  # Obtiene el ancho de la pantalla
        self.screen_height = self.root.winfo_screenheight()  # Obtiene el alto de la pantalla
        self.x0 = (self.screen_width // 2) - (int(self.dimension_x0) // 2)  # Calcula la posición X
        self.y0 = (self.screen_height // 2) - (int(self.dimension_y0) // 2)  # Calcula la posición Y
        self.root.geometry(f"{self.dimension_x0}x{self.dimension_y0}+{self.x0}+{self.y0}")

        self.canvas = self.create_canvas(self.dimension_y0, self.dimension_x0)
        self.validate_func = self.canvas.register(validate_number_input)
        self.init_widgets()

    def create_canvas(self, dimension_y, dimension_x):
        canvas = tk.Canvas(
            self.root,
            bg=self.used_color,
            height=int(dimension_y),
            width=int(dimension_x),
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        canvas.place(x=0, y=0)
        return canvas

    def init_widgets(self):
        # switch modes
        self.canvas.create_text(145, 25, anchor="nw", text="Seleccione modalidad", fill=self.text_color, font=("Inter", 30))

        self.canvas.create_text(135, 370, anchor="nw", text="MANUAL", fill=self.text_color, font=("Inter", 14))
        self.manual_bg_image = PhotoImage(file=relative_to_assets("MANUAL_BTN_BG.png"))
        self.manual_button = tk.Button(self.canvas, image=self.manual_bg_image,
                                       command=lambda: self.controller.switch_frame(AppInterface3), state="normal",
                                       relief="flat",
                                       borderwidth=0, bg=self.used_color,)
        self.manual_button.place(x=97.0, y=198.0)

        self.canvas.create_text(405, 370, anchor="nw", text="AUTOMÁTICO", fill=self.text_color, font=("Inter", 14))
        self.automatic_bg_image = PhotoImage(file=relative_to_assets("AUTOMATIC_BTN.png"))
        self.automatic_button = tk.Button(self.canvas, image=self.automatic_bg_image,
                                          command=lambda: self.controller.switch_frame(AppInterface2), state="normal",
                                          relief="flat", borderwidth=0, bg=self.used_color)
        self.automatic_button.place(x=381.0, y=183.0)

        self.go_back_bg_image = PhotoImage(file=relative_to_assets("GO_BACK_BTN1.png"))
        self.go_back_button = tk.Button(self.canvas, image=self.go_back_bg_image,
                                        command=lambda: self.controller.switch_frame(AppInterface0), state="normal",
                                        relief="flat", borderwidth=0, bg=self.used_color)
        self.go_back_button.place(x=520.0, y=474.0)


# --------------------------- Tercera Interfaz --------------------------- #
class AppInterface2(AppBase):
    def __init__(self, root, controller, patient_data):
        super().__init__(root, controller, patient_data)
        self.position = None
        self.messagebox = None
        self.level = None
        self.value = None
        self.text = None
        self.combobox = None
        self.connect_button_image = None
        self.leg_animation = None
        self.ser = None
        self.send_value_running = False
        self.send_value_thread = None
        self.max_torque_reached = False
        self.stop_threads = False
        self.is_connected = False
        self.message_shown = False
        self.active_animation = True
        self.blink_state = True
        self.grados = 0
        self.torque = 0
        self.nivel_actual = None
        self.datos = {
            "Nivel 1": [],
            "Nivel 2": [],
            "Nivel 3": [],
            "Nivel 4": [],
            "Nivel 5": []
        }
        self.time_left = 0
        self.max_angle = 0
        self.running = False
        self.frames_path = Path(__file__).resolve().parent / "light_video"
        self.squares = []
        self.root = root
        self.dimension_x1 = "1000"
        self.dimension_y1 = "720"

        self.screen_width = self.root.winfo_screenwidth()  # Obtiene el ancho de la pantalla
        self.screen_height = self.root.winfo_screenheight()  # Obtiene el alto de la pantalla
        x = (self.screen_width // 2) - (int(self.dimension_x1) // 2)  # Calcula la posición X
        y = (self.screen_height // 2) - (int(self.dimension_y1) // 2)  # Calcula la posición Y
        self.root.geometry(f"{self.dimension_x1}x{self.dimension_y1}+{x}+{y}")

        self.root.resizable(False, False)
        self.root.configure(bg=self.used_color)
        self.canvas = self.create_canvas(self.dimension_x1, self.dimension_y1)
        self.serial_widgets()
        self.create_combo_widget()
        self.apply_combox_changes()
        self.leg_animation = LegAnimation(self.canvas, self.frames_path)
        self.init_widgets()

    def create_canvas(self,dimension_x, dimension_y):
        canvas = tk.Canvas(
            self.root,
            bg=self.used_color,
            height=int(dimension_y),
            width=int(dimension_x),
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        canvas.place(x=0, y=0)
        return canvas

    def serial_widgets(self):

        self.status_label = tk.Label(self.canvas, text="Sin conexión", fg=self.disconnected_color, font=("Inter", 12),
                                     bg=self.used_color)
        self.status_label.place(x=75.0, y=620.0)

        self.connect_button_image = PhotoImage(file=relative_to_assets("CONNECT_BTN0.png"))
        self.disconnect_button_image = PhotoImage(file=relative_to_assets("DISCONNECT_BTN0.png"))


        self.toggle_connection_button = Button(
            self.canvas,
            image=self.connect_button_image,
            command=self.toggle_connection,
            relief="flat",
            bg=self.used_color
        )
        self.toggle_connection_button.place(x=70, y=550)

    def toggle_connection(self):
        if self.is_connected:
            self.disconnect_arduino()
        else:
            self.connect_to_arduino()

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
                                self.position = (rad * 180) / math.pi
                                self.torque = abs(float(values[1]))
                                self.grados = self.position
                                if self.leg_animation:
                                    self.leg_animation.update_frame(self.position, self.torque)
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
                    self.ser = serial.Serial(arduino_port, 115200, timeout=2)
                    self.status_label.config(text=f"Conectado a: {arduino_port}", fg=self.connected_color, font=("Inter", 12))
                    self.toggle_connection_button.config(image=self.disconnect_button_image)
                    self.combobox.config(state="normal")
                    self.apply_button_widget.config(state="normal")
                    self.is_connected = True
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
        else:
            messagebox.showwarning("Not Found", "Arduino not found. Please check the connection.")

    def disconnect_arduino(self):
        self.turn_off_motor()
        if self.ser and self.ser.is_open:
            self.stop_threads = True
            self.ser.close()
            self.ser = None
            self.status_label.config(text="Sin conexión", fg=self.disconnected_color, font=("Inter", 12))
            self.toggle_connection_button.config(image=self.connect_button_image)
            self.combobox.config(state="disabled")
            self.apply_button_widget.config(state="disabled")
            self.is_connected = False
            self.stop_threads = False

    def start_timer(self):
        if not self.running:
            self.time_left = 10  # Set the countdown time in seconds
            self.running = True
            self.message_shown = False  # Reset the flag when the timer starts
            self.update_timer()

    def stop_timer(self):
        if self.running:
            self.time_left = 0  # Set the countdown time in seconds
            self.running = False

    def update_timer(self):
        if not self.running:
            return

        if self.time_left > 0:
            minutes, seconds = divmod(self.time_left, 60)
            self.label_timer.config(text=f"{minutes:02}:{seconds:02}")
            self.time_left -= 1

            if self.position >= self.max_angle and not self.message_shown:
                self.running = False
                self.achieved_test("#06D7A0")
                self.label_timer.config(text="00:00")
                messagebox.showinfo("Timer", "Ha alcanzado la posición deseada!")
                self.message_shown = True  # Set the flag to True after showing the message

            if self.running:
                self.root.after(1000, self.update_timer)

        elif self.time_left == 0 and self.position <= self.max_angle and not self.message_shown:
            self.running = False
            self.failed_test("#F04770")
            self.label_timer.config(text="00:00")
            messagebox.showinfo("Timer", "No ha alcanzado la posición deseada!")
            self.message_shown = True

    def toggle_boton(self):
        if self.boton_toggle["text"] == "Iniciar":
            messagebox.showinfo("Estudio", "Se ha comenzado a aplicar fuerza!")
            self.animation_on_write_serial()
            self.boton_toggle.config(text="Detener", image=self.imagen_detener, command=self.toggle_boton)
        else:
            self.animation_off_write_serial()
            self.stop_timer()
            self.label_timer.config(text="00:00")
            self.boton_toggle.config(text="Iniciar", image=self.imagen_iniciar, command=self.toggle_boton)

            # Stop the send_value loop
            self.send_value_running = False
            if self.send_value_thread is not None:
                self.send_value_thread.join()  # Wait for the thread to finish
                self.send_value_thread = None

            # Reset the squares and achieved levels if necessary
            if self.level.startswith("Nivel "):
                level_num = int(self.level.split(" ")[1])
                self.squares[level_num - 1].config(bg="#FFFFFF")
                self.achieved_levels[level_num - 1] = False

    def send_value(self):
        cadena = str(self.combobox.get())
        nivel = int(cadena.split()[1])
        divided_value = nivel / 4
        cumulative_value = 0

        while self.send_value_running and cumulative_value < nivel:
            cumulative_value += divided_value
            if self.ser and self.ser.is_open:  # Ensure the serial port is open
                self.arduino_lock.acquire()  # Acquire the lock for thread-safe access
                try:
                    self.ser.write((str(cumulative_value) + "\n").encode('ascii'))  # Send the cumulative value
                    print(f"Sent: {cumulative_value}")  # Debug print
                except Exception as e:
                    print(f"Error writing to serial port: {e}")
                finally:
                    self.arduino_lock.release()  # Release the lock
            else:
                print("Serial port is not open.")
                break

            time.sleep(2)  # Wait for 2 seconds before the next iteration

        # When max torque is reached
        if cumulative_value >= nivel:
            self.max_torque_reached = True
            messagebox.showinfo("Alerta", "Se ha alcanzado el torque máximo.")
            self.start_timer()  # Start the countdown timer

    def animation_on_write_serial(self):
        self.combobox.config(state="disabled")
        self.start_animation()
        time.sleep(0.10)
        self.turn_on_motor()
        time.sleep(0.10)

        # Start the send_value function in a separate thread
        self.send_value_running = True
        self.max_torque_reached = False
        self.send_value_thread = threading.Thread(target=self.send_value)
        self.send_value_thread.start()

    def animation_off_write_serial(self):
        self.combobox.config(state="readonly")
        self.stop_animation()
        time.sleep(0.05)
        self.turn_off_motor()
        time.sleep(0.05)

    def turn_on_motor(self):
        if self.ser is not None and self.ser.is_open:
            cadena = "998\n"
            self.arduino_lock.acquire()
            try:
                self.ser.write(cadena.encode('ascii'))
                print("Motor turned on.")
            except Exception as e:
                print(f"Error turning on motor: {e}")
            finally:
                self.arduino_lock.release()

    def turn_off_motor(self):
        if self.ser is not None and self.ser.is_open:
            cadena = "999\n"
            self.arduino_lock.acquire()
            try:
                self.ser.write(cadena.encode('ascii'))
                print("Motor turned off.")
            except Exception as e:
                print(f"Error turning off motor: {e}")
            finally:
                self.arduino_lock.release()

    def origin_motor(self):
        if self.ser is not None:
            cadena = "997\n"
            self.arduino_lock.acquire()
            time.sleep(0.05)
            self.ser.write(cadena.encode('ascii'))
            time.sleep(0.05)
            self.arduino_lock.release()


    def validate_input(self):
        return self.text.isdigit() or self.text == ""

    def update_state(self, event=None):
        if self.combobox.get() in ["Nivel 4", "Nivel 5"]:
            self.user_input.config(state="normal")
        else:
            self.user_input.config(state="disabled")
            self.user_input.delete(0, tk.END)

    def check_last_lvl(self, actual_lvl):
        if actual_lvl > 1 and not self.achieved_levels[actual_lvl - 1]:
            answer = messagebox.askquestion("Confirmación",
                                            f"¿Pasó exitosamente los niveles 1 a {actual_lvl - 1}?")
            if answer == "yes":
                for i in range(actual_lvl - 1):
                    self.squares[i - 5].config(bg="#06D7A0")
                    self.achieved_levels[i] = True
                return True
            else:
                messagebox.showwarning("Aviso",
                                       "Por favor, seleccione el nivel faltante para hacer los test de forma correcta.")
                self.combobox.set("Seleccionar el nivel")
                return False
        return True

    def create_combo_widget(self):
        # Title
        self.canvas.create_text(350, 10, anchor="nw", text="Estudio automático", fill=self.text_color, font=("Inter", 30))
        levels = ["Nivel 1", "Nivel 2", "Nivel 3", "Nivel 4", "Nivel 5"]
        self.combobox = ttk.Combobox(self.canvas, values=levels, font=("Inter", 14), width=20)
        self.combobox.set("Elija el nivel de fuerza")
        self.combobox.config(state="disabled")  # Make the combobox readonly
        self.combobox.place(x=360, y=555)

        self.cmd_entry = self.canvas.register(self.validate_input)
        self.user_input = tk.Entry(self.canvas, font=("Inter", 16), width=10, validate="key",
                                   validatecommand=(self.cmd_entry, "%P"), bg="white")
        self.user_input.place(x=410, y=600)
        self.user_input.config(state="disabled")

        self.apply_image = PhotoImage(file=relative_to_assets("APPLY_BTN0.png"))
        self.apply_button_widget = tk.Button(self.canvas, image=self.apply_image,command=self.apply_combox_changes,
                                             relief="flat", borderwidth=0, bg=self.used_color)
        self.apply_button_widget.place(x=350, y=640)
        self.apply_button_widget.config(state="disabled")

        self.mensaje_label1 = tk.Label(self.canvas, text="", font=("Inter", 12), bg=self.used_color)
        self.mensaje_label1.place(x=570, y=650)
        self.mensaje_label2 = tk.Label(self.canvas, text="", font=("Inter", 12), bg=self.used_color)
        self.mensaje_label2.place(x=570, y=670)

        self.strengthT_label = tk.Label(self.canvas, text="F =", font=("Inter", 18), bg=self.used_color, fg="#000000")
        self.strengthT_label.place(x=360, y=600)
        self.strengthKG_label = tk.Label(self.canvas, text="Kg", font=("Inter", 18), bg=self.used_color, fg="#000000")
        self.strengthKG_label.place(x=540, y=600)

        self.nivelesF_label = self.canvas.create_text(420, 530, text="Niveles de fuerza",font=("Inter", 13),
                                                      fill=self.text_color)

        self.indicator1_bg_image = PhotoImage(file=relative_to_assets("INDICATOR1_BG0.png"))
        self.canvas.create_image(709, 135, image=self.indicator1_bg_image, anchor="nw")

        self.origin_bg_image = PhotoImage(file=relative_to_assets("SET_ORIGIN_BTN_BG.png"))
        self.origin_btn = tk.Button(self.canvas, image=self.origin_bg_image, command=self.origin_motor,
                                    relief="flat", borderwidth=0, bg=self.used_color)
        self.origin_btn.place(x=735.0, y=160.0)

        self.max_angle_text=self.canvas.create_text(810, 270, text="Ángulo máx.:  0.0 °", font=("Inter", 12),
                                                    fill=self.text_color)

        self.save_angle_bg = PhotoImage(file=relative_to_assets("SAVE_ANGLE_BTN0_BG.png"))

        self.max_angle_btn = tk.Button(self.canvas, image=self.save_angle_bg, command=self.save_max_angle,
                                            relief="flat", borderwidth=0, bg=self.used_color)
        self.max_angle_btn.place(x=735.0, y=284.0)
        self.max_angle_btn.config(state="disabled")

        self.label_timer = tk.Label(root, text="00:00", font=("Inter", 12),bg=self.used_color)
        self.label_timer.place(x=740.0, y=385.0)

        self.leg_bg_image = PhotoImage(file=relative_to_assets("LEG_BG.png"))
        self.canvas.create_image(40, 134, image=self.leg_bg_image, anchor="nw")

        self.inidcator_bg_image = PhotoImage(file=relative_to_assets("INDICATOR_BG.png"))
        self.canvas.create_image(40, 445, image=self.inidcator_bg_image, anchor="nw")

        self.inidcator_bg_image1 = PhotoImage(file=relative_to_assets("INDICATOR_BG.png"))
        self.canvas.create_image(300, 445, image=self.inidcator_bg_image1, anchor="nw")

        self.grados_text = self.canvas.create_text(100, 470, text="Grados:", font=("Inter", 13), fill=self.text_color)
        self.torque_text = self.canvas.create_text(360, 470, text="Torque:", font=("Inter", 13), fill=self.text_color)

        self.gauge_bg_image = PhotoImage(file=relative_to_assets("GAUGE_BG0.png"))
        self.canvas.create_image(562, 135, image=self.gauge_bg_image, anchor="nw")

        for i in range(5):
            self.square_widget = tk.Label(self.canvas, text=str(i + 1), font=("Inter", 10), width=12, height=4, bd=0,
                                          highlightbackground="#D3D4D9",
                                          highlightthickness=1, bg="white")
            self.square_widget.place(x=583, y=398 - (i * 60))
            self.squares.append(self.square_widget)

        self.titleC_label = self.canvas.create_text(600, 110, text="Niveles", font=("Inter", 13), fill=self.text_color)

        self.imagen_iniciar = PhotoImage(file=relative_to_assets("START_BTN0.png"))
        self.imagen_detener = PhotoImage(file=relative_to_assets("STOP_BTN0.png"))


        self.save_image = PhotoImage(file=relative_to_assets("SAVE_BTN0.png"))
        self.boton_save = tk.Button(
            self.canvas,
            image=self.save_image,
            state="normal",
            relief="flat",
            borderwidth=0,
            bg=self.used_color,
            command=self.save_boton)
        self.boton_save.place(x=720, y=545)
        self.boton_save.config(state="disabled")

        self.boton_toggle = tk.Button(
            self.canvas,
            text="Iniciar",
            font=("Inter", 16),
            command=self.toggle_boton,
            state="normal",
            relief="flat",
            borderwidth=0,
            bg=self.used_color,
            image=self.imagen_iniciar)
        self.boton_toggle.place(x=734, y=410)
        self.boton_toggle.config(state="disabled")

        self.combobox.bind("<<ComboboxSelected>>", self.update_state)

        self.achieved_levels = [False] * 5

    def save_max_angle(self):
        if self.position is not None:
            self.canvas.itemconfig(self.max_angle_text, text=f"Ángulo máx.:  {self.position:.1f} °")
            self.max_angle = self.position
        else:
            messagebox.showinfo("Error", "No se detecta posición, verifique el sistema")


    def achieved_test(self, color):
        nivel_actual = self.combobox.get()
        if nivel_actual in self.datos:
            self.datos[nivel_actual].append({
                "Grados": self.grados,
                "Torque": self.torque,
                "Llegó": "Sí" if color == "#06D7A0" else "No"  # Dependiendo del color, sabes si llegó o no
            })
        self.highlight(color)
        self.combobox.config(state="readonly")
        self.turn_off_motor()

    def failed_test(self, color):
        nivel_actual = self.combobox.get()
        if nivel_actual in self.datos:
            self.datos[nivel_actual].append({
                "Grados": self.grados,
                "Torque": self.torque,
                "Llegó": "Sí" if color == "#06D7A0" else "No"  # Dependiendo del color, sabes si llegó o no
            })
        self.highlight(color)
        self.combobox.config(state="readonly")
        self.turn_off_motor()

    def apply_combox_changes(self):
        self.level = self.combobox.get()
        self.value = self.user_input.get()

        if self.level.startswith("Nivel "):
            self.level_num = int(self.level.split(" ")[1])

            if self.level_num == 4 and self.value.isdigit() and int(self.value) > 10:
                self.mensaje_label1.config(text="El límite del valor", fg="#00072d", bg="#000000")
                self.mensaje_label2.config(text="es 10 en nivel 4", fg="#00072d", bg="#000000")
                return
            elif self.level_num == 5 and self.value.isdigit() and int(self.value) > 20:
                self.mensaje_label1.config(text="El límite del valor", fg="#00072d", bg="#000000")
                self.mensaje_label2.config(text="es 20 en Nivel 5", fg="#00072d", bg="#000000")
                return
            elif self.level_num in (4, 5) and ((not self.value.strip() or not self.value.isdigit())
                                               or int(self.value) == 0):
                self.mensaje_label1.config(text="ERROR. Ingrese un valor", fg="#00072d", bg="#000000")
                self.mensaje_label2.config(text="de fuerza", fg="#00072d", bg="#000000")
                return
            if not self.check_last_lvl(self.level_num):
                return

            self.mensaje_label1.config(text="Cambios aplicados", fg="#00072D")
            self.mensaje_label2.config(text="correctamente", fg="#00072D")
            self.user_input.config(state="disabled")
            self.boton_toggle.config(state="normal")
            self.combobox.config(state="disabled")
            self.max_angle_btn.config(state="normal")

        self.mensaje_label1.after(5000, lambda: self.mensaje_label1.config(text=""))
        self.mensaje_label2.after(5000, lambda: self.mensaje_label2.config(text=""))

    def save_boton(self):
        try:
            # Crear una lista para almacenar todos los datos
            datos_finales = []

            # Recorrer el diccionario y agregar los datos a la lista
            for nivel, registros in self.datos.items():
                for registro in registros:
                    datos_finales.append({
                        "Nivel": nivel,
                        "Grados": registro["Grados"],
                        "Torque": registro["Torque"],
                        "Llegó": registro["Llegó"]
                    })

            # Obtener la ruta de salida y el número de expediente desde patient_data
            expediente = self.patient_data.get("Expediente", "Sin expediente")
            output_folder = self.patient_data.get("output_folder", Path.cwd())

            if expediente and output_folder:
                # Crear el nombre del archivo con el número de expediente
                output_path = output_folder / f"{expediente}.xlsx"

                # Crear un nuevo libro de Excel
                wb = openpyxl.Workbook()

                # Crear la hoja para el modo automático
                ws_auto = wb.active
                ws_auto.title = "Modo Automático"

                # Escribir la tabla de información personal
                self.write_patient_info(ws_auto)

                # Escribir la tabla de resumen de pruebas de fuerza
                self.write_test_summary(ws_auto, datos_finales)

                # Crear una nueva hoja para el modo manual
                ws_manual = wb.create_sheet("Modo Manual")

                # Escribir la tabla de información personal en la hoja manual
                self.write_patient_info(ws_manual)

                # Guardar el archivo Excel
                wb.save(output_path)

                # Mostrar mensaje de éxito
                messagebox.showinfo("Test Finalizado",
                                    f"El registro y test ha concluido. Su archivo ha sido guardado como {output_path}.")
            else:
                messagebox.showwarning("Error",
                                       "Por favor, ingrese un número de expediente válido y seleccione una carpeta de salida.")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al guardar el archivo: {e}")

        # Deshabilitar el botón de guardar y resetear la interfaz
        self.boton_save.config(state="disabled")
        self.user_input.config(state="disabled")
        self.squares[4].config(bg="#FFFFFF")
        self.squares[3].config(bg="#FFFFFF")
        self.squares[2].config(bg="#FFFFFF")
        self.squares[1].config(bg="#FFFFFF")
        self.squares[0].config(bg="#FFFFFF")
        self.achieved_levels[:] = [False] * len(self.achieved_levels)
        self.datos = {
            "Nivel 1": [],
            "Nivel 2": [],
            "Nivel 3": [],
            "Nivel 4": [],
            "Nivel 5": []
        }

    def write_patient_info(self, ws):
        """Escribe la información del paciente en la hoja de Excel."""
        ws['A1'] = "Información Personal"
        ws['A1'].font = Font(bold=True, size=14, color="FFFFFF")
        ws['A1'].fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
        ws['A1'].alignment = Alignment(horizontal="center", vertical="center")
        ws.merge_cells('A1:E1')  # Combinar celdas para el header (ahora son 5 columnas)

        # Subheaders de la tabla de información personal
        ws['A2'] = "Nombre"
        ws['B2'] = "Edad"
        ws['C2'] = "Sexo"
        ws['D2'] = "Actividad Física"
        ws['E2'] = "Fecha"
        for cell in ws['A2:E2'][0]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="5B9BD5", end_color="5B9BD5", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Datos de la tabla de información personal
        ws['A3'] = self.patient_data.get("Nombre", "No registrado")
        ws['B3'] = self.patient_data.get("Edad", "No registrado")
        ws['C3'] = self.patient_data.get("Sexo", "No registrado")
        ws['D3'] = self.patient_data.get("Actividad", "No registrado")
        ws['E3'] = "Fecha de prueba"  # Puedes agregar un campo para la fecha si es necesario
        for cell in ws['A3:E3'][0]:
            cell.fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")

    def write_test_summary(self, ws, datos_finales):
        """Escribe el resumen de las pruebas de fuerza en la hoja de Excel."""
        # Espacio entre las tablas
        ws['A5'] = ""  # Espacio vacío

        # Escribir la tabla de resumen de pruebas de fuerza
        ws['A6'] = "Resumen de Pruebas de Fuerza"
        ws['A6'].font = Font(bold=True, size=14, color="FFFFFF")
        ws['A6'].fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
        ws['A6'].alignment = Alignment(horizontal="center", vertical="center")
        ws.merge_cells('A6:D6')  # Combinar celdas para el header

        # Subheaders de la tabla de resumen de pruebas de fuerza
        ws['A7'] = "Nivel"
        ws['B7'] = "Grados"
        ws['C7'] = "Torque"
        ws['D7'] = "Llegó"
        for cell in ws['A7:D7'][0]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="5B9BD5", end_color="5B9BD5", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Datos de la tabla de resumen de pruebas de fuerza
        row_index = 8
        for dato in datos_finales:
            ws[f'A{row_index}'] = dato["Nivel"]
            ws[f'B{row_index}'] = dato["Grados"]
            ws[f'C{row_index}'] = dato["Torque"]
            ws[f'D{row_index}'] = dato["Llegó"]
            for cell in ws[f'A{row_index}:D{row_index}'][0]:
                cell.fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
                cell.alignment = Alignment(horizontal="center", vertical="center")
            row_index += 1

    def start_animation(self):
        self.level1 = self.combobox.get()
        if self.level1.startswith("Nivel "):
            self.level1_num = int(self.level1.split(" ")[1])
            if 1 <= self.level1_num <= 5:
                self.active_animation = True
                self.blink_state = True
                self.blinking(self.squares[self.level1_num - 1])
                self.combobox.config(state="disabled")
                self.user_input.config(state="disabled")
                self.boton_save.config(state="disabled")
                self.boton_toggle.config(text="Detener", image=self.imagen_detener)

    def blinking(self, square):
        if self.active_animation:
            color = "#60AFFF" if self.blink_state else "white"
            square.config(bg=color)
            self.blink_state = not self.blink_state
            square.after(500, lambda: self.blinking(square))

    def stop_animation(self):
        self.level = self.combobox.get()
        self.active_animation = False
        self.combobox.config(state="normal")
        self.boton_toggle.config(text="Iniciar", image=self.imagen_iniciar, state="disabled")
        self.boton_save.config(state="normal")

        if self.level.startswith("Nivel "):
            self.nivel_num = int(self.level.split(" ")[1])
            if self.nivel_num > 3:
                self.user_input.config(state="normal")

    def highlight(self, color):
        self.level = self.combobox.get()

        if self.level.startswith("Nivel "):
            self.level_num = int(self.level.split(" ")[1])
            if 1 <= self.level_num <= 3:
                self.stop_animation()
                self.squares[self.level_num - 1].config(bg=color)
                self.achieved_levels[self.level_num - 1] = True
                self.user_input.config(state="disabled")
            else:
                self.stop_animation()
                self.squares[self.level_num - 1].config(bg=color)
                self.achieved_levels[self.level_num - 1] = True
                self.user_input.config(state="normal")

    def init_widgets(self):
        # Mostrar información del paciente
        nombre_paciente = self.patient_data.get("Nombre", "No registrado")
        self.nombre_title = self.canvas.create_text(200, 110, text=f"Animación de pierna de: {nombre_paciente}",
                                                    font=("Inter", 13), fill=self.text_color)

        self.return_image = PhotoImage(file=relative_to_assets("GO_BACK_BTN1.png"))
        self.return_btn = tk.Button(self.canvas, state="normal", relief="flat",
                                    borderwidth=0,
                                    bg=self.used_color,
                                    image=self.return_image,
                                    command=lambda: self.controller.switch_frame(AppInterface1))
        self.return_btn.place(x=810, y=645)

    def on_closing(self):
        self.turn_off_motor()
        time.sleep(0.05)
        self.disconnect_arduino()
        self.root.destroy()


# --------------------------- Cuarta Interfaz --------------------------- #
class AppInterface3(AppBase):
    def __init__(self, root, controller, patient_data):
        super().__init__(root, controller, patient_data)
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
        self.leg_animation = None
        self.ser = None
        self.type_input = None
        self.stop_threads = False
        self.is_connected = False
        self.active_animation = True
        self.blink_state = True
        self.grados = 0
        self.torque = 0
        self.nivel_actual = None
        self.datos = {
            "Nivel 1": [],
            "Nivel 2": [],
            "Nivel 3": [],
            "Nivel 4": [],
            "Nivel 5": []
        }
        self.frames_path = Path(__file__).resolve().parent / "light_video"
        self.squares = []
        self.root = root
        self.dimension_x1 = "1000"
        self.dimension_y1 = "720"

        self.send_value_running = False
        self.send_value_thread = None
        self.max_torque_reached = False

        self.screen_width = self.root.winfo_screenwidth()  # Obtiene el ancho de la pantalla
        self.screen_height = self.root.winfo_screenheight()  # Obtiene el alto de la pantalla
        x = (self.screen_width // 2) - (int(self.dimension_x1) // 2)  # Calcula la posición X
        y = (self.screen_height // 2) - (int(self.dimension_y1) // 2)  # Calcula la posición Y
        self.root.geometry(f"{self.dimension_x1}x{self.dimension_y1}+{x}+{y}")

        self.root.resizable(False, False)
        self.root.configure(bg=self.used_color)
        self.canvas = self.create_canvas(self.dimension_x1, self.dimension_y1)
        self.serial_widgets()
        self.create_combo_widget()
        self.apply_combox_changes()
        self.leg_animation = LegAnimation(self.canvas, self.frames_path)
        self.init_widgets()

    def create_canvas(self,dimension_x, dimension_y):
        canvas = tk.Canvas(
            self.root,
            bg=self.used_color,
            height=int(dimension_y),
            width=int(dimension_x),
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        canvas.place(x=0, y=0)
        return canvas

    def serial_widgets(self):

        self.status_label = tk.Label(self.canvas, text="Sin conexión", fg=self.disconnected_color, font=("Inter", 12),
                                     bg=self.used_color)
        self.status_label.place(x=75.0, y=620.0)

        self.connect_button_image = PhotoImage(file=relative_to_assets("CONNECT_BTN0.png"))
        self.disconnect_button_image = PhotoImage(file=relative_to_assets("DISCONNECT_BTN0.png"))


        self.toggle_connection_button = Button(
            self.canvas,
            image=self.connect_button_image,
            command=self.toggle_connection,
            relief="flat",
            bg=self.used_color
        )
        self.toggle_connection_button.place(x=70, y=550)

    def toggle_connection(self):
        if self.is_connected:
            self.disconnect_arduino()
        else:
            self.connect_to_arduino()

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
                                self.position = (rad * 180) / math.pi
                                self.torque = abs(float(values[1]))
                                self.grados = self.position
                                if self.leg_animation:
                                    self.leg_animation.update_frame(self.position, self.torque)
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
                    self.ser = serial.Serial(arduino_port, 115200, timeout=2)
                    self.status_label.config(text=f"Conectado a: {arduino_port}", fg=self.connected_color, font=("Inter", 12))
                    self.toggle_connection_button.config(image=self.disconnect_button_image)
                    self.combobox.config(state="normal")
                    self.apply_button_widget.config(state="normal")
                    self.is_connected = True
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

        else:
            messagebox.showwarning("Not Found", "Arduino not found. Please check the connection.")

    def disconnect_arduino(self):
        self.turn_off_motor()
        if self.ser and self.ser.is_open:
            self.stop_threads = True
            self.ser.close()
            self.ser = None
            self.status_label.config(text="Sin conexión", fg=self.disconnected_color, font=("Inter", 12))
            self.toggle_connection_button.config(image=self.connect_button_image)
            self.combobox.config(state="disabled")
            self.apply_button_widget.config(state="disabled")
            self.is_connected = False
            self.stop_threads = False

    def toggle_boton(self):
        if self.boton_toggle["text"] == "Iniciar":
            messagebox.showinfo("Estudio", "Se ha comenzado a aplicar fuerza!")
            self.animation_on_write_serial()
            self.boton_toggle.config(text="Detener", image=self.imagen_detener, command=self.toggle_boton)
        else:
            self.animation_off_write_serial()
            self.boton_toggle.config(text="Iniciar", image=self.imagen_iniciar, command=self.toggle_boton)

            # Stop the send_value loop
            self.send_value_running = False
            if self.send_value_thread is not None:
                self.send_value_thread.join()  # Wait for the thread to finish
                self.send_value_thread = None

            # Reset the squares and achieved levels if necessary
            if self.level.startswith("Nivel "):
                level_num = int(self.level.split(" ")[1])
                self.squares[level_num - 1].config(bg="#FFFFFF")
                self.achieved_levels[level_num - 1] = False

    def send_value(self):
        cadena = str(self.combobox.get())
        nivel = int(cadena.split()[1])
        divided_value = nivel / 4
        cumulative_value = 0

        while self.send_value_running and cumulative_value < nivel:
            cumulative_value += divided_value
            if self.ser and self.ser.is_open:  # Ensure the serial port is open
                self.arduino_lock.acquire()  # Acquire the lock for thread-safe access
                try:
                    self.ser.write((str(cumulative_value) + "\n").encode('ascii'))  # Send the cumulative value
                    print(f"Sent: {cumulative_value}")  # Debug print
                except Exception as e:
                    print(f"Error writing to serial port: {e}")
                finally:
                    self.arduino_lock.release()  # Release the lock
            else:
                print("Serial port is not open.")
                break

            time.sleep(2)  # Wait for 2 seconds before the next iteration

        # When max torque is reached
        if cumulative_value >= nivel:
            self.max_torque_reached = True
            messagebox.showinfo("Alerta", "Se ha alcanzado el torque máximo.")

    def animation_on_write_serial(self):
        self.combobox.config(state="disabled")
        self.start_animation()
        time.sleep(0.10)
        self.turn_on_motor()
        time.sleep(0.10)

        # Start the send_value function in a separate thread
        self.send_value_running = True
        self.max_torque_reached = False
        self.send_value_thread = threading.Thread(target=self.send_value)
        self.send_value_thread.start()

    def animation_off_write_serial(self):
        self.combobox.config(state="readonly")
        self.stop_animation()
        time.sleep(0.05)
        self.turn_off_motor()
        time.sleep(0.05)

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

    def origin_motor(self):
        if self.ser is not None:
            cadena = "997\n"
            self.arduino_lock.acquire()
            time.sleep(0.05)
            self.ser.write(cadena.encode('ascii'))
            time.sleep(0.05)
            self.arduino_lock.release()

    def validate_input(self):
        return self.text.isdigit() or self.text == ""

    def update_state(self, event=None):
        if self.combobox.get() in ["Nivel 4", "Nivel 5"]:
            self.user_input.config(state="normal")
        else:
            self.user_input.config(state="disabled")
            self.user_input.delete(0, tk.END)

    def check_last_lvl(self, actual_lvl):
        if actual_lvl > 1 and not self.achieved_levels[actual_lvl - 1]:
            answer = messagebox.askquestion("Confirmación",
                                            f"¿Pasó exitosamente los niveles 1 a {actual_lvl - 1}?")
            if answer == "yes":
                for i in range(actual_lvl - 1):
                    self.squares[i - 5].config(bg="#06D7A0")
                    self.achieved_levels[i] = True
                return True
            else:
                messagebox.showwarning("Aviso",
                                       "Por favor, seleccione el nivel faltante para hacer los test de forma correcta.")
                self.combobox.set("Seleccionar el nivel")
                return False
        return True

    def create_combo_widget(self):
        # Title
        self.canvas.create_text(380, 10, anchor="nw", text="Estudio Manual", fill=self.text_color, font=("Inter", 30))
        levels = ["Nivel 1", "Nivel 2", "Nivel 3", "Nivel 4", "Nivel 5"]
        self.combobox = ttk.Combobox(self.canvas, values=levels, font=("Inter", 14), width=20)
        self.combobox.set("Elija el nivel de fuerza")
        self.combobox.config(state="disabled")  # Make the combobox readonly
        self.combobox.place(x=360, y=555)

        self.cmd_entry = self.canvas.register(self.validate_input)
        self.user_input = tk.Entry(self.canvas, font=("Inter", 16), width=10, validate="key",
                                   validatecommand=(self.cmd_entry, "%P"), bg="white")
        self.user_input.place(x=410, y=600)
        self.user_input.config(state="disabled")

        self.apply_image = PhotoImage(file=relative_to_assets("APPLY_BTN0.png"))
        self.apply_button_widget = tk.Button(self.canvas, image=self.apply_image,
                                             command=self.apply_combox_changes, relief="flat", borderwidth=0,
                                             bg=self.used_color)
        self.apply_button_widget.place(x=350, y=640)
        self.apply_button_widget.config(state="disabled")

        self.mensaje_label1 = tk.Label(self.canvas, text="", font=("Inter", 12), bg=self.used_color)
        self.mensaje_label1.place(x=570, y=650)
        self.mensaje_label2 = tk.Label(self.canvas, text="", font=("Inter", 12), bg=self.used_color)
        self.mensaje_label2.place(x=570, y=670)

        self.strengthT_label = tk.Label(self.canvas, text="F =", font=("Inter", 18), bg=self.used_color, fg="#404045")
        self.strengthT_label.place(x=360, y=600)
        self.strengthKG_label = tk.Label(self.canvas, text="Kg", font=("Inter", 18), bg=self.used_color, fg="#404045")
        self.strengthKG_label.place(x=540, y=600)

        self.nivelesF_label = self.canvas.create_text(420, 530, text="Niveles de fuerza",font=("Inter", 13),
                                                      fill=self.text_color)

        self.indicator1_bg_image = PhotoImage(file=relative_to_assets("INDICATOR1_BG0.png"))
        self.canvas.create_image(709, 135, image=self.indicator1_bg_image, anchor="nw")

        self.achieved_bg_image = PhotoImage(file=relative_to_assets("ACHIEVED_BTN_BG.png"))
        self.achieved_button = Button(self.canvas, image=self.achieved_bg_image,
                                      command=lambda: self.achieved_test("#06D7A0"),
                                      relief="flat", bg=self.used_color, state="disabled")
        self.achieved_button.place(x=730.0, y=240.0)

        self.failed_bg_image = PhotoImage(file=relative_to_assets("FAILED_BTN_BG.png"))
        self.failed_button = Button(self.canvas, image=self.failed_bg_image,
                                    command=lambda: self.failed_test("#F04770"),
                                    relief="flat", bg=self.used_color, state="disabled")
        self.failed_button.place(x=730.0, y=325.0)

        self.origin_bg_image = PhotoImage(file=relative_to_assets("SET_ORIGIN_BTN_BG.png"))
        self.origin_btn = tk.Button(self.canvas, image=self.origin_bg_image, command=self.origin_motor,
                                    relief="flat", borderwidth=0, bg=self.used_color)
        self.origin_btn.place(x=735.0, y=160.0)

        self.leg_bg_image = PhotoImage(file=relative_to_assets("LEG_BG.png"))
        self.canvas.create_image(40, 134, image=self.leg_bg_image, anchor="nw")

        self.inidcator_bg_image = PhotoImage(file=relative_to_assets("INDICATOR_BG.png"))
        self.canvas.create_image(40, 445, image=self.inidcator_bg_image, anchor="nw")

        self.inidcator_bg_image1 = PhotoImage(file=relative_to_assets("INDICATOR_BG.png"))
        self.canvas.create_image(300, 445, image=self.inidcator_bg_image1, anchor="nw")

        self.grados_text = self.canvas.create_text(100, 470, text="Grados:", font=("Inter", 13), fill=self.text_color)
        self.torque_text = self.canvas.create_text(360, 470, text="Torque:", font=("Inter", 13), fill=self.text_color)

        self.gauge_bg_image = PhotoImage(file=relative_to_assets("GAUGE_BG0.png"))
        self.canvas.create_image(562, 135, image=self.gauge_bg_image, anchor="nw")

        for i in range(5):
            self.square_widget = tk.Label(self.canvas, text=str(i + 1), font=("Inter", 10), width=12, height=4, bd=0,
                                          highlightbackground="#D3D4D9",
                                          highlightthickness=1, bg="white")
            self.square_widget.place(x=583, y=398 - (i * 60))
            self.squares.append(self.square_widget)

        self.titleC_label = self.canvas.create_text(600, 110, text="Niveles", font=("Inter", 13), fill=self.text_color)

        self.imagen_iniciar = PhotoImage(file=relative_to_assets("START_BTN0.png"))
        self.imagen_detener = PhotoImage(file=relative_to_assets("STOP_BTN0.png"))


        self.save_image = PhotoImage(file=relative_to_assets("SAVE_BTN0.png"))
        self.boton_save = tk.Button(
            self.canvas,
            image=self.save_image,
            state="normal",
            relief="flat",
            borderwidth=0,
            bg=self.used_color,
            command=self.save_boton)
        self.boton_save.place(x=720, y=545)
        self.boton_save.config(state="disabled")

        self.boton_toggle = tk.Button(
            self.canvas,
            image=self.imagen_iniciar,
            text="Iniciar",
            font=("Inter", 16),
            command=self.toggle_boton,
            state="normal",
            relief="flat",
            borderwidth=0,
            bg=self.used_color,
            )
        self.boton_toggle.place(x=734, y=410)
        self.boton_toggle.config(state="disabled")

        self.combobox.bind("<<ComboboxSelected>>", self.update_state)

        self.achieved_levels = [False] * 5

    def achieved_test(self, color):
        nivel_actual = self.combobox.get()
        if nivel_actual in self.datos:
            self.datos[nivel_actual].append({
                "Grados": self.grados,
                "Torque": self.torque,
                "Llegó": "Sí" if color == "#06D7A0" else "No"  # Dependiendo del color, sabes si llegó o no
            })
        self.highlight(color)
        self.combobox.config(state="readonly")
        self.turn_off_motor()

    def failed_test(self, color):
        nivel_actual = self.combobox.get()
        if nivel_actual in self.datos:
            self.datos[nivel_actual].append({
                "Grados": self.grados,
                "Torque": self.torque,
                "Llegó": "Sí" if color == "#06D7A0" else "No"  # Dependiendo del color, sabes si llegó o no
            })
        self.highlight(color)
        self.combobox.config(state="readonly")
        self.turn_off_motor()

    def apply_combox_changes(self):
        self.level = self.combobox.get()
        self.value = self.user_input.get()

        if self.level.startswith("Nivel "):
            self.level_num = int(self.level.split(" ")[1])

            if self.level_num == 4 and self.value.isdigit() and int(self.value) > 10:
                self.mensaje_label1.config(text="El límite del valor", fg="#00072d", bg="#000000")
                self.mensaje_label2.config(text="es 10 en nivel 4", fg="#00072d", bg="#000000")
                return
            elif self.level_num == 5 and self.value.isdigit() and int(self.value) > 20:
                self.mensaje_label1.config(text="El límite del valor", fg="#00072d", bg="#000000")
                self.mensaje_label2.config(text="es 20 en Nivel 5", fg="#00072d", bg="#000000")
                return
            elif self.level_num in (4, 5) and ((not self.value.strip() or not self.value.isdigit())
                                               or int(self.value) == 0):
                self.mensaje_label1.config(text="ERROR. Ingrese un valor", fg="#00072d", bg="#000000")
                self.mensaje_label2.config(text="de fuerza", fg="#00072d", bg="#000000")
                return
            if not self.check_last_lvl(self.level_num):
                return

            self.mensaje_label1.config(text="Cambios aplicados", fg="#00072D")
            self.mensaje_label2.config(text="correctamente", fg="#00072D")
            self.user_input.config(state="disabled")
            self.combobox.config(state="disabled")
            self.boton_toggle.config(state="normal")

        self.mensaje_label1.after(5000, lambda: self.mensaje_label1.config(text=""))
        self.mensaje_label2.after(5000, lambda: self.mensaje_label2.config(text=""))

    def update_frame(self, position, torque):
        """Actualiza los datos de grados y torque."""
        self.grados = position
        self.torque = torque

        # Guardar los datos en self.datos
        nivel_actual = self.combobox.get()
        if nivel_actual in self.datos:
            self.datos[nivel_actual].append({
                "Grados": self.grados,  # Guardar los grados
                "Torque": self.torque,  # Guardar el torque
                "Llegó": "Sí"  # O "No", dependiendo de la lógica de tu aplicación
            })

    def save_boton(self):
        try:
            # Crear una lista para almacenar todos los datos
            datos_finales = []

            # Recorrer el diccionario y agregar los datos a la lista
            for nivel, registros in self.datos.items():
                for registro in registros:
                    datos_finales.append({
                        "Nivel": nivel,
                        "Grados": registro["Grados"],
                        "Torque": registro["Torque"],
                        "Llegó": registro["Llegó"]
                    })

            # Obtener la ruta de salida y el número de expediente desde patient_data
            expediente = self.patient_data.get("Expediente", "Sin expediente")
            output_folder = self.patient_data.get("output_folder", Path.cwd())

            if expediente and output_folder:
                # Crear el nombre del archivo con el número de expediente
                output_path = output_folder / f"{expediente}.xlsx"

                # Crear un nuevo libro de Excel
                wb = openpyxl.Workbook()

                # Crear la hoja para el modo manual
                ws_manual = wb.active
                ws_manual.title = "Modo Manual"

                # Escribir la tabla de información personal
                self.write_patient_info(ws_manual)

                # Escribir la tabla de resumen de pruebas de fuerza
                self.write_test_summary(ws_manual, datos_finales)

                # ----------------------
                # Crear la gráfica de barras a partir de la tabla de resumen
                # ----------------------

                # Crear la gráfica de barras
                chart = BarChart()
                chart.title = "Grados por Nivel"
                chart.x_axis.title = "Nivel"  # Eje X: Niveles
                chart.y_axis.title = "Grados"  # Eje Y: Grados

                # Referencias para los datos de la gráfica
                # Suponiendo que la tabla de resumen comienza en la fila 7 (A7:D7 es el header)
                data = Reference(ws_manual, min_col=2, min_row=8, max_row=7 + len(datos_finales),
                                 max_col=2)  # Columna B (Grados)
                categories = Reference(ws_manual, min_col=1, min_row=8,
                                       max_row=7 + len(datos_finales))  # Columna A (Nivel)

                # Agregar los datos a la gráfica
                chart.add_data(data, titles_from_data=True)
                chart.set_categories(categories)

                # Configurar las etiquetas de datos (valores arriba de las barras)
                chart.dLbls = None  # Deshabilitar las etiquetas de datos

                # Agregar la gráfica a la hoja
                ws_manual.add_chart(chart, "F7")  # Colocar la gráfica al lado de la tabla

                # Guardar el archivo Excel
                wb.save(output_path)

                # Mostrar mensaje de éxito
                messagebox.showinfo("Test Finalizado",
                                    f"El registro y test ha concluido. Su archivo ha sido guardado como {output_path}.")
            else:
                messagebox.showwarning("Error",
                                       "Por favor, ingrese un número de expediente válido y seleccione una carpeta de salida.")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al guardar el archivo: {e}")

        # Deshabilitar el botón de guardar y resetear la interfaz
        self.boton_save.config(state="disabled")
        self.user_input.config(state="disabled")
        self.squares[4].config(bg="#FFFFFF")
        self.squares[3].config(bg="#FFFFFF")
        self.squares[2].config(bg="#FFFFFF")
        self.squares[1].config(bg="#FFFFFF")
        self.squares[0].config(bg="#FFFFFF")
        self.achieved_levels[:] = [False] * len(self.achieved_levels)
        self.datos = {
            "Nivel 1": [],
            "Nivel 2": [],
            "Nivel 3": [],
            "Nivel 4": [],
            "Nivel 5": []
        }

    def write_patient_info(self, ws):
        """Escribe la información del paciente en la hoja de Excel."""
        ws['A1'] = "Información Personal"
        ws['A1'].font = Font(bold=True, size=14, color="FFFFFF")
        ws['A1'].fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
        ws['A1'].alignment = Alignment(horizontal="center", vertical="center")
        ws.merge_cells('A1:E1')  # Combinar celdas para el header (ahora son 5 columnas)

        # Subheaders de la tabla de información personal
        ws['A2'] = "Nombre"
        ws['B2'] = "Edad"
        ws['C2'] = "Sexo"
        ws['D2'] = "Actividad Física"
        ws['E2'] = "Fecha"
        for cell in ws['A2:E2'][0]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="5B9BD5", end_color="5B9BD5", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Datos de la tabla de información personal
        ws['A3'] = self.patient_data.get("Nombre", "No registrado")
        ws['B3'] = self.patient_data.get("Edad", "No registrado")
        ws['C3'] = self.patient_data.get("Sexo", "No registrado")
        ws['D3'] = self.patient_data.get("Actividad", "No registrado")
        ws['E3'] = "Fecha de prueba"  # Puedes agregar un campo para la fecha si es necesario
        for cell in ws['A3:E3'][0]:
            cell.fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")

    def write_test_summary(self, ws, datos_finales):
        """Escribe el resumen de las pruebas de fuerza en la hoja de Excel."""
        # Espacio entre las tablas
        ws['A5'] = ""  # Espacio vacío

        # Escribir la tabla de resumen de pruebas de fuerza
        ws['A6'] = "Resumen de Pruebas de Fuerza"
        ws['A6'].font = Font(bold=True, size=14, color="FFFFFF")
        ws['A6'].fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
        ws['A6'].alignment = Alignment(horizontal="center", vertical="center")
        ws.merge_cells('A6:D6')  # Combinar celdas para el header

        # Subheaders de la tabla de resumen de pruebas de fuerza
        ws['A7'] = "Nivel"
        ws['B7'] = "Grados"
        ws['C7'] = "Torque"
        ws['D7'] = "Llegó"
        for cell in ws['A7:D7'][0]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="5B9BD5", end_color="5B9BD5", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Datos de la tabla de resumen de pruebas de fuerza
        row_index = 8
        for dato in datos_finales:
            ws[f'A{row_index}'] = dato["Nivel"]
            ws[f'B{row_index}'] = dato["Grados"]  # Asegúrate de que los grados se escriban aquí
            ws[f'C{row_index}'] = dato["Torque"]
            ws[f'D{row_index}'] = dato["Llegó"]
            for cell in ws[f'A{row_index}:D{row_index}'][0]:
                cell.fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
                cell.alignment = Alignment(horizontal="center", vertical="center")
            row_index += 1

    def start_animation(self):
        self.level1 = self.combobox.get()
        if self.level1.startswith("Nivel "):
            self.level1_num = int(self.level1.split(" ")[1])
            if 1 <= self.level1_num <= 5:
                self.active_animation = True
                self.blink_state = True
                self.blinking(self.squares[self.level1_num - 1])
                self.combobox.config(state="disabled")
                self.achieved_button.config(state="normal")
                self.failed_button.config(state="normal")
                self.user_input.config(state="disabled")
                self.boton_save.config(state="disabled")
                self.boton_toggle.config(text="Detener", image=self.imagen_detener)

    def blinking(self, square):
        if self.active_animation:
            color = "#60AFFF" if self.blink_state else "white"
            square.config(bg=color)
            self.blink_state = not self.blink_state
            square.after(500, lambda: self.blinking(square))

    def stop_animation(self):
        self.level = self.combobox.get()
        self.active_animation = False
        self.achieved_button.config(state="disabled")
        self.failed_button.config(state="disabled")
        self.combobox.config(state="normal")
        self.boton_toggle.config(text="Iniciar", image=self.imagen_iniciar, state="disabled")
        self.boton_save.config(state="normal")

        if self.level.startswith("Nivel "):
            self.nivel_num = int(self.level.split(" ")[1])
            if self.nivel_num > 3:
                self.user_input.config(state="normal")

    def highlight(self, color):
        self.level = self.combobox.get()

        if self.level.startswith("Nivel "):
            self.level_num = int(self.level.split(" ")[1])
            if 1 <= self.level_num <= 3:
                self.stop_animation()
                self.squares[self.level_num - 1].config(bg=color)
                self.achieved_levels[self.level_num - 1] = True
                self.user_input.config(state="disabled")
            else:
                self.stop_animation()
                self.squares[self.level_num - 1].config(bg=color)
                self.achieved_levels[self.level_num - 1] = True
                self.user_input.config(state="normal")

    def init_widgets(self):
        # Mostrar información del paciente
        nombre_paciente = self.patient_data.get("Nombre", "No registrado")
        self.nombre_title = self.canvas.create_text(190, 110, text=f"Animación de pierna de: {nombre_paciente}",
                                                    fill=self.text_color, font=("Inter", 13))

        self.return_image = PhotoImage(file=relative_to_assets("GO_BACK_BTN1.png"))
        self.return_btn = tk.Button(self.canvas, state="normal", relief="flat",
                                    borderwidth=0,
                                    bg=self.used_color,
                                    image=self.return_image,
                                    command=lambda: self.controller.switch_frame(AppInterface1))
        self.return_btn.place(x=865, y=645)

    def on_closing(self):
        self.turn_off_motor()
        time.sleep(0.05)
        self.disconnect_arduino()
        self.root.destroy()


# --------------------------- Imagen de pierna --------------------------- #
class LegAnimation:
    def __init__(self, canvas, image_folder_path):
        self.canvas = canvas
        self.image_folder_path = image_folder_path

        # Load PNG frames from the folder
        self.frames = self.load_png_frames(image_folder_path)

        # Create a label to display the image frame
        self.label = tk.Label(self.canvas, bg="white", highlightthickness=0)
        self.label.place(x=46, y=137)  # Place the label

        self.text_id1 = self.canvas.create_text(
            240, 470,  # Coordinates (x, y)
            text="0.0°",  # Text content
            font=("Inter", 13),  # Font and size
            fill="black"  # Text color
        )

        self.text_id2 = self.canvas.create_text(
            490, 470,  # Coordinates (x, y)
            text="0.0",  # Text content
            font=("Inter", 13),  # Font and size
            fill="black"  # Text color
        )

        # Initialize with the first frame
        self.update_frame(0,0)  # Start with position 0

    def load_png_frames(self, image_folder_path):
        frames = []
        # Sort files to ensure correct order
        files = sorted(Path(image_folder_path).iterdir(), key=lambda x: int(x.stem.split("_")[-1]))
        for file in files:
            if file.is_file() and file.suffix.lower() == ".png":
                image = Image.open(file)
                frames.append(image)
        return frames

    def input_to_frame(self, position, total_frames, degrees_per_frame=2.3):
        frame_index = int(position / degrees_per_frame)
        # Ensure the frame index is within bounds
        frame_index = max(0, min(frame_index, total_frames - 1))
        return frame_index

    def update_frame(self, position, torque):
        """Update the displayed frame based on position value."""
        frame_index = self.input_to_frame(position, len(self.frames))
        frame = self.frames[frame_index]
        frame_image = ImageTk.PhotoImage(image=frame)
        self.label.config(image=frame_image)
        self.label.image = frame_image  # Keep a reference to avoid garbage collection

        # Update the text with the current value
        self.canvas.itemconfig(self.text_id1, text=f"{position:.1f}°")
        self.canvas.itemconfig(self.text_id2, text=f"{torque:.1f}  N/m")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("630x550")
    controller = Controller(root)  # Create the controller
    controller.switch_frame(AppInterface0)  # Start with AppInterface0
    root.mainloop()