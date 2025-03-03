import tkinter as tk
import threading
from tkinter import ttk, messagebox, PhotoImage, Button, Entry
from pathlib import Path
from PIL import Image, ImageTk
import serial.tools.list_ports
import serial
import os
import math
import time

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


class AppInterface0:
    def __init__(self, root):
        self.root = root
        self.used_color = 'white'
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
        self.canvas.create_text(145, 25, anchor="nw", text="Registro de paciente", fill="#000000", font=("Inter", 30))

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
        self.canvas.create_image(327, 237, image=self.age_bg_image, anchor="nw")
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
        self.register_bg_image = PhotoImage(file=relative_to_assets("Group 16.png"))
        self.switch_button = tk.Button(self.canvas, image=self.register_bg_image,
                                       command=self.switch_to_interface1, state="normal", relief="flat",
                                       borderwidth=0, bg=self.used_color,)
        self.switch_button.place(x=224.0, y=476.0)

        # Settings page button
        self.settings_bg_image = PhotoImage(file=relative_to_assets("configuracion-cog 1.png"))
        self.settings_button = Button(
            self.canvas,
            image=self.settings_bg_image,
            relief="flat",
            bg=self.used_color
        )
        self.settings_button.place(x=544, y=476)

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

    def error_message(self):
        messagebox.showwarning("Error", "Asegurese de llenar todos los espacios")

    def switch_to_interface1(self):
        self.canvas.place_forget()  # Hide the current interface
        AppInterface1(self.root, self)  # Show the second interface

    def show(self):
        self.canvas.place(x=0, y=0)  # Show the current interface

    def on_closing(self):
        self.root.destroy()


class AppInterface1:
    def __init__(self, root, register_interface):
        self.root = root
        self.used_color = 'white'
        self.dimension_x0 = "630"
        self.dimension_y0 = "550"
        self.register_interface = register_interface

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
        self.canvas.create_text(145, 25, anchor="nw", text="Seleccione modo de estudio", fill="#000000", font=("Inter", 30))

        # Next page button
        self.register_bg_image = PhotoImage(file=relative_to_assets("Group 16.png"))
        self.switch_button = tk.Button(self.canvas, image=self.register_bg_image, text="Go to Interface 1",
                                       command=self.switch_to_interface1, state="normal", relief="flat",
                                       borderwidth=0, bg=self.used_color,)
        self.switch_button.place(x=224.0, y=476.0)

    def error_message(self):
        messagebox.showwarning("Error", "Asegurese de llenar todos los espacios")

    def switch_to_interface1(self):
        """
        if self.entry_00 == "" or self.entry_01 == "" or self.entry_02 == "" or self.combobox1.get() == "...":
            self.error_message()

        else:"""
        self.canvas.place_forget()  # Hide the current interface
        # AppInterface2(self.root, self)  # Show the second interface
        self.register_interface.show()  # Show the main interface


    def show(self):
        self.canvas.place(x=0, y=0)  # Show the current interface

    def on_closing(self):
        self.root.destroy()


class AppInterface2:
    def __init__(self, root, init_interface):
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
        self.frames_path = Path(__file__).resolve().parent / "light_video"
        self.app_interface = init_interface
        self.squares = []
        self.root = root
        self.dimension_x1 = "1000"
        self.dimension_y1 = "720"

        self.screen_width = self.root.winfo_screenwidth()  # Obtiene el ancho de la pantalla
        self.screen_height = self.root.winfo_screenheight()  # Obtiene el alto de la pantalla
        x = (self.screen_width // 2) - (int(self.dimension_x1) // 2)  # Calcula la posición X
        y = (self.screen_height // 2) - (int(self.dimension_y1) // 2)  # Calcula la posición Y
        self.root.geometry(f"{self.dimension_x1}x{self.dimension_y1}+{x}+{y}")

        self.root.geometry(self.dimension_x1+"x"+self.dimension_y1)
        self.root.resizable(False, False)
        self.used_color = 'white'
        self.root.configure(bg=self.used_color)
        self.canvas = self.create_canvas(self.dimension_x1, self.dimension_y1)
        self.print_all_entries()
        self.serial_widgets()
        self.name_entry_widget()
        self.create_combo_widget()
        self.apply_combox_changes()
        self.leg_animation = LegAnimation(self.canvas, self.frames_path)
        self.init_widgets()

    def print_all_entries(self):
        self.entries = self.app_interface.get_all_entries()

    def name_entry_widget(self):
        self.canvas.create_text(
            50,
            100,
            anchor="nw",
            text=f"Posición de la pierna de :     {self.entries[0]}",
            fill="#000000",
            font=("Inter", 13)
        )

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

        self.status_label = tk.Label(self.canvas, text="Sin conexión", fg="red", font=("Inter", 12),
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
                    self.status_label.config(text=f"Connected to {arduino_port}", fg="green", font=("Inter", 12))
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
            self.status_label.config(text="Sin conexión", fg="red", font=("Inter", 12))
            self.toggle_connection_button.config(image=self.connect_button_image)
            self.combobox.config(state="disabled")
            self.apply_button_widget.config(state="disabled")
            self.is_connected = False
            self.stop_threads = False

    def toggle_boton(self):
        if self.boton_toggle["text"] == "Iniciar":
            self.animation_on_write_serial()
            self.boton_toggle.config(text="Detener", image=self.imagen_detener, command=self.toggle_boton)
        else:
            self.animation_off_write_serial()
            self.boton_toggle.config(text="Iniciar", image=self.imagen_iniciar, command=self.toggle_boton)
        if self.level.startswith("Nivel "):
            level_num = int(self.level.split(" ")[1])
            self.squares[level_num].config(bg="#FFFFFF")

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

    def soon_message(self):
        messagebox.showinfo("PROXIMAMENTE", "Menú, pestañas de registro y mejora visual en desarrollo")

    def create_combo_widget(self):
        # Title
        self.canvas.create_text(350, 10, anchor="nw", text="Estudio automático", fill="#000000", font=("Inter", 30))
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
                                             command=self.apply_combox_changes, relief="flat", borderwidth=5,
                                             bg=self.used_color)
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
                                                      fill="black")

        self.indicator1_bg_image = PhotoImage(file=relative_to_assets("INDICATOR1_BG0.png"))
        self.canvas.create_image(709, 135, image=self.indicator1_bg_image, anchor="nw")

        self.canvas.create_text(790, 180, text="Ángulo máx.", font=("Inter", 13), fill="black")
        self.canvas.create_text(790, 300, text="Ángulo min.", font=("Inter", 13), fill="black")
        self.max_angle_text = self.canvas.create_text(780, 220, text="0.0 °", font=("Inter", 13), fill="black")
        self.min_angle_text = self.canvas.create_text(780, 330, text="0.0 °", font=("Inter", 13), fill="black")

        self.save_max_angle = ttk.Button(self.canvas, text="Guardar", command=self.save_max_angle)
        self.save_max_angle.place(x=850.0, y=210.0, width=100.0, height=20.0)
        self.save_min_angle = ttk.Button(self.canvas, text="Guardar", command=self.save_min_angle)
        self.save_min_angle.place(x=850.0, y=320.0, width=100.0, height=20.0)

        self.leg_bg_image = PhotoImage(file=relative_to_assets("LEG_BG.png"))
        self.canvas.create_image(40, 134, image=self.leg_bg_image, anchor="nw")

        self.inidcator_bg_image = PhotoImage(file=relative_to_assets("INDICATOR_BG.png"))
        self.canvas.create_image(40, 445, image=self.inidcator_bg_image, anchor="nw")

        self.inidcator_bg_image1 = PhotoImage(file=relative_to_assets("INDICATOR_BG.png"))
        self.canvas.create_image(300, 445, image=self.inidcator_bg_image1, anchor="nw")

        self.grados_text = self.canvas.create_text(100, 470, text="Grados:", font=("Inter", 13), fill="black")
        self.torque_text = self.canvas.create_text(360, 470, text="Torque:", font=("Inter", 13), fill="black")

        self.gauge_bg_image = PhotoImage(file=relative_to_assets("GAUGE_BG0.png"))
        self.canvas.create_image(562, 135, image=self.gauge_bg_image, anchor="nw")

        for i in range(5):
            self.square_widget = tk.Label(self.canvas, text=str(i + 1), font=("Inter", 10), width=12, height=4, bd=0,
                                          highlightbackground="#D3D4D9",
                                          highlightthickness=1, bg="white")
            self.square_widget.place(x=583, y=398 - (i * 60))
            self.squares.append(self.square_widget)

        self.titleC_label = self.canvas.create_text(600, 110, text="Niveles", font=("Inter", 13), fill="black")

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



    def save_min_angle(self):
        self.canvas.itemconfig(self.min_angle_text, text=f"{self.position:.1f} °")
        self.max_angle = self.position

    def save_max_angle(self):
        self.canvas.itemconfig(self.max_angle_text, text=f"{self.position:.1f} °")
        self.min_angle = self.position


    def achieved_test(self, color):
        self.highlight(color)
        self.combobox.config(state="readonly")
        self.turn_off_motor()

    def failed_test(self, color):
        self.highlight(color)
        self.combobox.config(state="readonly")
        self.turn_off_motor()

    def apply_combox_changes(self):
        self.level = self.combobox.get()
        self.value = self.user_input.get()

        if self.level.startswith("Nivel "):
            self.level_num = int(self.level.split(" ")[1])

            if self.level_num == 4 and self.value.isdigit() and int(self.value) > 10:
                self.mensaje_label1.config(text="El límite del valor", fg="#F43838", bg="#000000")
                self.mensaje_label2.config(text="es 10 en nivel 4", fg="#F43838", bg="#000000")
                return
            elif self.level_num == 5 and self.value.isdigit() and int(self.value) > 20:
                self.mensaje_label1.config(text="El límite del valor", fg="#F43838", bg="#000000")
                self.mensaje_label2.config(text="es 20 en Nivel 5", fg="#F43838", bg="#000000")
                return
            elif self.level_num in (4, 5) and ((not self.value.strip() or not self.value.isdigit())
                                               or int(self.value) == 0):
                self.mensaje_label1.config(text="ERROR. Ingrese un valor", fg="#F43838", bg="#000000")
                self.mensaje_label2.config(text="de fuerza", fg="#F43838", bg="#000000")
                return
            if not self.check_last_lvl(self.level_num):
                return

            self.mensaje_label1.config(text="Cambios aplicados", fg="#5BFF2F")
            self.mensaje_label2.config(text="correctamente", fg="#5BFF2F")
            self.user_input.config(state="disabled")
            self.combobox.config(state="disabled")
            self.boton_toggle.config(state="normal")

        self.mensaje_label1.after(5000, lambda: self.mensaje_label1.config(text=""))
        self.mensaje_label2.after(5000, lambda: self.mensaje_label2.config(text=""))

    def save_boton(self):
        messagebox.showinfo("Test Finalizado", "El registro y test ha concluido. Su archivo ha sido guardado.")
        self.boton_save.config(state="disabled")
        self.user_input.config(state="disabled")
        self.squares[4].config(bg="#FFFFFF")
        self.squares[3].config(bg="#FFFFFF")
        self.squares[2].config(bg="#FFFFFF")
        self.squares[1].config(bg="#FFFFFF")
        self.squares[0].config(bg="#FFFFFF")
        self.achieved_levels[:] = [False] * len(self.achieved_levels)

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

    def send_value(self):
        cadena = str(self.combobox.get())
        # Extract the number using split()
        nivel = cadena.split()[1]  # Splits the string and takes the second part (index 1)
        self.arduino_lock.acquire()
        time.sleep(0.05)
        self.ser.write((nivel + "\n").encode('ascii'))  # Send only the number
        time.sleep(0.05)
        self.arduino_lock.release()

    def animation_on_write_serial(self):
        self.combobox.config(state="disabled")
        self.start_animation()
        time.sleep(0.10)
        self.turn_on_motor()
        time.sleep(0.10)
        self.send_value()

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

    def init_widgets(self):
        self.return_image = PhotoImage(file=relative_to_assets("ReturnImgBtn.png"))
        self.return_btn = tk.Button(
            self.canvas,
            state="normal",
            relief="flat",
            borderwidth=0,
            bg=self.used_color,
            image=self.return_image,
            command=lambda: [self.switch_to_main_interface(), self.app_interface.reset_entries()]
        )
        self.return_btn.place(x=810, y=645)

    def switch_to_main_interface(self):
        self.canvas.place_forget()  # Hide the current interface
        self.disconnect_arduino()
        self.root.geometry(f"{self.app_interface.dimension_x0}x{self.app_interface.dimension_y0}"
                           f"+{self.app_interface.x0}+{self.app_interface.y0}")
        self.app_interface.show()  # Show the main interface

    def on_closing(self):
        self.turn_off_motor()
        time.sleep(0.05)
        self.disconnect_arduino()
        self.root.destroy()


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
    app = AppInterface0(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()