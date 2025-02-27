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


class AppInterface1:
    def __init__(self, root):
        self.root = root
        self.used_color = '#D4DBF5'
        self.canvas = self.create_canvas()
        self.root.geometry("1000x720")
        self.root.resizable(False, False)
        self.root.configure(bg=self.used_color)
        self.validate_func = self.canvas.register(validate_number_input)
        self.init_widgets()

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

    def init_widgets(self):
        self.switch_button = ttk.Button(self.canvas, text="Go to Interface 1", command=self.switch_to_interface1)
        self.switch_button.place(x=850.0, y=670.0, width=120.0, height=20.0)

        self.entry_00 = Entry(bd=0, bg="white", fg="#000000", highlightthickness=0, state="normal",
                             font=("Georgia", 15))  # Name
        self.entry_00.place(x=420.0, y=200.0, width=370.0, height=31.0)

        self.entry_01 = Entry(bd=0, bg="white", fg="#000000", highlightthickness=0, state="normal",
                              font=("Georgia", 15), validate="key", validatecommand=(self.validate_func, "%P"))  # Age
        self.entry_01.place(x=420.0, y=250.0, width=100.0, height=31.0)

        self.entry_02 = Entry(bd=0, bg="white", fg="#000000", highlightthickness=0, state="normal",
                              font=("Georgia", 15))  # Expedient #
        self.entry_02.place(x=420.0, y=300.0, width=370.0, height=31.0)

        self.settings_button_image = PhotoImage(file=relative_to_assets("Settings_Btn.png"))
        self.settings_button = Button(
            self.canvas,
            image=self.settings_button_image,
            relief="flat",
            bg=self.used_color
        )
        self.settings_button.place(x=900, y=30)

        genders = ["Masculino", "Femenino"]
        self.combobox1 = ttk.Combobox(self.canvas, values=genders, font=("Georgia", 14))
        self.combobox1.config(state="readonly")
        self.combobox1.set("...")  # Sex

        self.combobox1.place(x=670.0, y=250.0, width=120.0, height=31)

        self.canvas.create_text(400, 100, anchor="nw", text="Registro de paciente", fill="#000000", font=("Georgia", 20))
        self.canvas.create_text(250, 200, anchor="nw", text="Nombre de pac. :", fill="#000000", font=("Georgia", 14))
        self.canvas.create_text(250, 250, anchor="nw", text="Edad :", fill="#000000", font=("Georgia", 14))
        self.canvas.create_text(580, 250, anchor="nw", text="Sexo :", fill="#000000", font=("Georgia", 14))
        self.canvas.create_text(250, 300, anchor="nw", text="# de expediente :", fill="#000000", font=("Georgia", 14))

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
        """
        if self.entry_00 == "" or self.entry_01 == "" or self.entry_02 == "" or self.combobox1.get() == "...":
            self.error_message()

        else:"""
        self.canvas.place_forget()  # Hide the current interface
        AppInterface2(self.root, self)  # Show the second interface

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
        self.active_animation = True
        self.blink_state = True
        self.squares = []
        self.root = root
        self.frames_path = Path(__file__).resolve().parent / "light_video"
        self.app_interface = init_interface
        self.root.geometry("1000x720")
        self.root.resizable(False, False)
        self.used_color = '#D4DBF5'
        self.root.configure(bg=self.used_color)
        self.canvas = self.create_canvas()
        self.print_all_entries()
        self.serial_widgets()
        self.name_entry_widget()
        #  self.grados_widget()
        self.create_combo_widget()
        self.apply_combox_changes()
        self.leg_animation = LegAnimation(self.canvas, self.frames_path)
        self.init_widgets()

    def print_all_entries(self):
        self.entries = self.app_interface.get_all_entries()

    def name_entry_widget(self):
        self.ruta_img = relative_to_assets("EntryNameLabel.png")
        self.image_widget = PhotoImage(file=self.ruta_img)
        self.entry_bg_1 = self.canvas.create_image(
            480.0,
            37.0,
            image=self.image_widget
        )
        self.canvas.create_text(
            35,
            25,
            anchor="nw",
            text=f"Nombre de pac. :     {self.entries[0]}",
            fill="#000000",
            font=("Georgia", 14)
        )

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
                    self.status_label.config(text=f"Connected to {arduino_port}", fg="green", font=("Georgia", 14))
                    self.connect_button.config(state="disabled")
                    self.disconnect_button.config(state="normal")
                    self.combobox.config(state="normal")
                    self.apply_button_widget.config(state="normal")
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
            self.apply_button_widget.config(state="disabled")
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
        levels = ["Nivel 1", "Nivel 2", "Nivel 3", "Nivel 4", "Nivel 5"]
        self.combobox = ttk.Combobox(self.canvas, values=levels, font=("Georgia", 14), width=20)
        self.combobox.set("Elija el nivel de fuerza")
        self.combobox.config(state="disabled")  # Make the combobox readonly
        self.combobox.place(x=300, y=555)

        self.cmd_entry = self.canvas.register(self.validate_input)
        self.user_input = tk.Entry(self.canvas, font=("Georgia", 16), width=10, validate="key",
                                   validatecommand=(self.cmd_entry, "%P"), bg="white")
        self.user_input.place(x=350, y=600)
        self.user_input.config(state="disabled")

        self.apply_image = PhotoImage(file=relative_to_assets("APPLY_BTN.png"))
        self.apply_button_widget = tk.Button(self.canvas, image=self.apply_image,
                                             command=self.apply_combox_changes, relief="flat", borderwidth=5,
                                             bg=self.used_color)
        self.apply_button_widget.place(x=300, y=640)
        self.apply_button_widget.config(state="disabled")

        self.mensaje_label1 = tk.Label(self.canvas, text="", font=("Georgia", 12), bg=self.used_color)
        self.mensaje_label1.place(x=490, y=650)
        self.mensaje_label2 = tk.Label(self.canvas, text="", font=("Georgia", 12), bg=self.used_color)
        self.mensaje_label2.place(x=490, y=670)

        self.strengthT_label = tk.Label(self.canvas, text="F =", font=("Georgia", 18), bg=self.used_color, fg="#000000")
        self.strengthT_label.place(x=300, y=600)
        self.strengthKG_label = tk.Label(self.canvas, text="Kg", font=("Georgia", 18), bg=self.used_color, fg="#000000")
        self.strengthKG_label.place(x=480, y=600)

        self.nivelesF_label = tk.Label(self.canvas, text="Niveles de fuerza", font=("Georgia", 16),
                                       bg=self.used_color, fg="#000000")
        self.nivelesF_label.place(x=300, y=520)

        self.position_label = tk.Label(self.canvas, text="Posición de la pierna", font=("Georgia", 16),
                                       bg=self.used_color, fg="#000000")
        self.position_label.place(x=240, y=110)

        for i in range(5):
            self.square_widget = tk.Label(self.canvas, text=str(i + 1), font=("Georgia", 12), width=11, height=3, bd=0,
                                          highlightbackground=self.used_color, highlightcolor=self.used_color,
                                          highlightthickness=3, bg="white")
            self.square_widget.place(x=590, y=385 - (i * 57))
            self.squares.append(self.square_widget)

        self.titleC_label = tk.Label(self.canvas, text="Niveles", font=("Georgia", 16), bg=self.used_color,
                                     fg="#000000")
        self.titleC_label.place(x=610, y=110)

        self.canvas.create_rectangle(70, 455, 320, 490, fill="white", outline="")  # Angle bd
        self.canvas.create_rectangle(330, 455, 573, 490, fill="white", outline="")  # Torque bd

        self.grados_label = tk.Label(self.canvas, text="Grados:", font=("Georgia", 14), bg="white", fg="#000000")
        self.grados_label.place(x=85, y=455)

        self.torque_label = tk.Label(self.canvas, text="Torque:", font=("Georgia", 14), bg="white", fg="#000000")
        self.torque_label.place(x=340, y=455)

        self.imagen_iniciar = PhotoImage(file=relative_to_assets("START_BTN.png"))
        self.imagen_detener = PhotoImage(file=relative_to_assets("STOP_BTN.png"))

        self.save_image = PhotoImage(file=relative_to_assets("SAVE_BTN.png"))
        self.boton_save = tk.Button(
            self.canvas,
            image=self.save_image,
            state="normal",
            relief="flat",
            borderwidth=0,
            bg=self.used_color,
            command=self.save_boton)
        self.boton_save.place(x=705, y=650)
        self.boton_save.config(state="disabled")

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
        self.boton_toggle.config(state="disabled")

        self.combobox.bind("<<ComboboxSelected>>", self.update_state)

        self.achieved_levels = [False] * 5

        self.canvas.create_text(780, 180, text="Ángulo máx.", font=("Georgia", 14), fill="black")
        self.canvas.create_text(780, 300, text="Ángulo min.", font=("Georgia", 14), fill="black")
        self.max_angle_text = self.canvas.create_text(780, 220, text="0.0 °", font=("Georgia", 14), fill="black")
        self.min_angle_text = self.canvas.create_text(780, 330, text="0.0 °", font=("Georgia", 14), fill="black")

        self.save_max_angle = ttk.Button(self.canvas, text="Guardar", command=self.save_max_angle)
        self.save_max_angle.place(x=870.0, y=210.0, width=100.0, height=20.0)
        self.save_min_angle = ttk.Button(self.canvas, text="Guardar", command=self.save_min_angle)
        self.save_min_angle.place(x=870.0, y=320.0, width=100.0, height=20.0)


    def save_min_angle(self):
        self.canvas.itemconfig(self.min_angle_text, text=f"{self.position:.1f} °")
        self.max_angle = self.position

    def save_max_angle(self):
        self.canvas.itemconfig(self.max_angle_text, text=f"{self.position:.1f} °")
        self.min_angle = self.position

    def timer_test(self):
        if

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
            color = "blue" if self.blink_state else "white"
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
        self.return_btn.place(x=860, y=15)

    def switch_to_main_interface(self):
        self.canvas.place_forget()  # Hide the current interface
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
        self.label = tk.Label(self.canvas)
        self.label.place(x=70, y=160)  # Place the label

        self.text_id1 = self.canvas.create_text(
            190, 470,  # Coordinates (x, y)
            text="0°",  # Text content
            font=("Georgia", 14),  # Font and size
            fill="black"  # Text color
        )

        self.text_id2 = self.canvas.create_text(
            470, 470,  # Coordinates (x, y)
            text="0.0",  # Text content
            font=("Georgia", 14),  # Font and size
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
    app = AppInterface1(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()