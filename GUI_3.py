import cv2
import tkinter as tk
import threading
from tkinter import ttk, messagebox, PhotoImage, Button, Label
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


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


def find_video_file(directory, video_name):

    search_dir = Path(directory)

    # Search for the video file recursively
    for file in search_dir.rglob(video_name):
        if file.is_file():  # Ensure it's a file (not a directory)
            return str(file)  # Return the full path as a string

    return None

class AppInterface:
    def __init__(self, root):
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
        self.root.geometry("1000x720")
        self.root.configure(bg="white")
        self.canvas = self.create_canvas()
        self.serial_widgets()
        self.video_setup()
        self.name_entry_widget()
        self.age_entry_widget()
        self.create_combo_widget()
        self.apply_combox_changes()

    def create_canvas(self):
        canvas = tk.Canvas(
            self.root,
            bg="#FFFFFF",
            height=720,
            width=1000,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        canvas.place(x=0, y=0)
        return canvas

    def serial_widgets(self):
        self.status_label = tk.Label(self.canvas, text="Not Connected", fg="red", font=("Arial", 14))
        self.status_label.place(x=45.0, y=60.0)
        self.connect_button_image = PhotoImage(file=relative_to_assets("BOTON_IMG_CONECTAR.png"))
        self.connect_button = Button(self.canvas, image=self.connect_button_image, text="Connect", command=self.connect_to_arduino)
        self.connect_button.place(x=50.0, y=100.0, width=120.0, height=40.0)
        self.disconnect_button_image = PhotoImage(file=relative_to_assets("BOTON_IMG_DESCONECTAR.png"))
        self.disconnect_button = Button(self.canvas, image=self.disconnect_button_image, text="Disconnect", command=self.disconnect_arduino, state="disabled")
        self.disconnect_button.place(x=50.0, y=150.0, width=120.0, height=40.0)
        self.switch_button = ttk.Button(self.canvas, text="Go to Interface 1", command=self.switch_to_interface1)
        self.switch_button.place(x=50.0, y=200.0, width=120.0, height=20.0)

        self.turn_on_motor_widget = Button(self.canvas, text="Turn On", command=self.turn_on_motor)
        self.turn_on_motor_widget.place(x=50, y=250, width=100.0, height=20.0)
        self.turn_off_motor_widget = Button(self.canvas, text="Turn Off", command=self.turn_off_motor)
        self.turn_off_motor_widget.place(x=50, y=300, width=100.0, height=20.0)



    def video_setup(self):
        video_directory = Path(__file__).resolve().parent / "video"
        video_name = "Leg Sequence (4).mp4"
        video_path = self.find_video_file(video_directory, video_name)

        if video_path:
            print(f"Video found: {video_path}")
            self.leg_animation = LegAnimation(self.canvas, video_path)
        else:
            messagebox.showerror("Error", f"Video file '{video_name}' not found in '{video_directory}'.")

    def find_video_file(self, directory, video_name):
        search_dir = Path(directory)
        for file in search_dir.rglob(video_name):
            if file.is_file():
                return str(file)
        return None

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
                                print(f"Position: {position}, Torque: {torque}")
                                if self.leg_animation:
                                    self.leg_animation.update_frame(position)
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
                time.sleep(0.50)
        except Exception as e:
            print("Error sending data",e)
            self.stop_threads = True

    def connect_to_arduino(self):
        arduino_port = self.find_arduino_port()
        if arduino_port:
            if self.ser is None:
                try:
                    self.arduino_lock = threading.Lock()
                    self.ser = serial.Serial(arduino_port, 115200, timeout=2)
                    self.status_label.config(text=f"Connected to {arduino_port}", fg="green")
                    self.connect_button.config(state="disabled")
                    self.disconnect_button.config(state="normal")
                    self.stop_threads = False
                    reading_thread = threading.Thread(target=self.read_serial_port, daemon=True)
                    reading_thread.start()


                    sending_thread = threading.Thread(target=self.send_data, args=(self.ser,))
                    sending_thread.start()
                    
                    sending_thread.join()

                    reading_thread.join()

                except Exception as e:
                    messagebox.showerror("Error", f"Failed to connect: {e}")
                    if self.ser:
                        self.ser.close()
                        self.ser = None
        else:
            messagebox.showwarning("Not Found", "Arduino not found. Please check the connection.")

    def disconnect_arduino(self):
        if self.ser and self.ser.is_open:
            self.stop_threads = True
            self.ser.close()
            self.ser = None
            self.status_label.config(text="Disconnected", fg="red")
            self.connect_button.config(state="normal")
            self.disconnect_button.config(state="disabled")
            self.stop_threads = False

    def name_entry_widget(self):
        self.ruta_img = relative_to_assets("Entry_Label_Img.png")
        self.image_widget = PhotoImage(file=self.ruta_img)

        entry_bg_1 = self.canvas.create_image(
            690.0,
            60.0,
            image=self.image_widget
        )
        self.entry_1 = Label(
            bd=0,
            bg="#acdccc",
            fg="#000716",
            highlightthickness=0,
            state="normal",
            font="Calibri 13"
        )
        self.entry_1.place(
            x=415.0,
            y=40.0,
            width=300.0,
            height=35.0
        )
        self.canvas.create_text(
            252.0,
            47,
            anchor="nw",
            text="Nombre de pac.",
            fill="#000000",
            font="Calibri 13"
        )

    def age_entry_widget(self):
        self.ruta_img1 = relative_to_assets("EntryEdad_Label_Img.png")
        self.image_widget1 = PhotoImage(file=self.ruta_img1)

        entry_bg_2 = self.canvas.create_image(
            465.0,
            130.0,
            image=self.image_widget1
        )
        self.entry_2 = Label(
            bd=0,
            bg="#acdccc",
            fg="#000716",
            highlightthickness=0,
            state="normal",
            font="Calibri 13"
        )
        self.entry_2.place(
            x=415.0,
            y=110.0,
            width=80.0,
            height=35.0
        )
        self.canvas.create_text(
            345.0,
            120,
            anchor="nw",
            text="Edad",
            fill="#000000",
            font="Calibri 13"
        )

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
                    self.squares[4 - i].config(bg="green")
                    self.achieved_levels[i] = True
                return True
            else:
                messagebox.showwarning("Aviso",
                                       "Por favor, seleccione el nivel faltante para hacer los test de forma correcta.")
                self.combobox.set("Seleccionar el nivel")
                return False
        return True

    def create_combo_widget(self):
        levels = ["Nivel 1", "Nivel 2", "Nivel 3", "Nivel 4", "Nivel 5"]
        self.combobox = ttk.Combobox(self.canvas, values=levels, font=("Calibri", 16), width=20)
        self.combobox.set("Elija el nivel de fuerza")
        self.combobox.config(state="readonly")  # Make the combobox readonly
        self.combobox.place(x=50, y=350)

        self.cmd_entry = self.canvas.register(self.validate_input)
        self.user_input = tk.Entry(self.canvas, font=("Calibri", 16), width=10, validate="key",
                              validatecommand=(self.cmd_entry, "%P"), bg="white")
        self.user_input.place(x=100, y=420)
        self.user_input.config(state="disabled")

        self.apply_button_widget = tk.Button(self.canvas, text="Aplicar cambios", font=("Nunito", 14),
                                             command=self.apply_combox_changes, relief="raised", borderwidth=5, bg="white")
        self.apply_button_widget.place(x=50, y=530)

        self.message_label = tk.Label(self.canvas, text="", font=("Calibri", 16), bg="#8FFDCD")
        self.message_label.place(x=50, y=600)

        self.strengthT_label = tk.Label(self.canvas, text="F =", font=("Calibri", 18), bg="#8FFDCD")
        self.strengthT_label.place(x=50, y=420)
        self.strengthKG_label = tk.Label(self.canvas, text="Kg", font=("Calibri", 18), bg="#8FFDCD")
        self.strengthKG_label.place(x=250, y=420)

        for i in range(5):
            self.square_widget = tk.Label(self.canvas, text=str(5 - i), font=("Arial", 14), width=11, height=3, relief="solid",
                              bg="white")
            self.square_widget.place(x=450, y=610 - (i * 70))
            self.squares.append(self.square_widget)

        self.titleC_label = tk.Label(self.canvas, text="Niveles", font=("Calibri", 14), bg="#8FFDCD")
        self.titleC_label.place(x=473, y=300)

        self.start_button_widget = tk.Button(self.canvas, text="Iniciar", font=("Calibri", 20), command=self.start_animation,
                                  state="disabled", borderwidth=10, width=6, height=1)
        self.start_button_widget.place(x=850, y=450)

        self.stop_button_widget = tk.Button(self.canvas, text="Detener", font=("Calibri", 20), command=self.stop_animation,
                                  state="disabled", borderwidth=10, width=6, height=1)
        self.stop_button_widget.place(x=850, y=550)

        self.yes_button_widget = tk.Button(self.canvas, text="Si llegó", font=("Calibri", 20), bg="green", state="disabled",
                             command=lambda: self.highlight("green"), relief="raised", borderwidth=10, width=6,
                             height=1)
        self.yes_button_widget.place(x=650, y=450)

        self.no_button_widget = tk.Button(self.canvas, text="No llegó", font=("Calibri", 20), bg="red", state="disabled",
                             command=lambda: self.highlight("red"), relief="raised", borderwidth=10, width=6, height=1)
        self.no_button_widget.place(x=650, y=550)

        self.combobox.bind("<<ComboboxSelected>>", self.update_state)

        self.achieved_levels = [False] * 5

    def apply_combox_changes(self):
        self.level = self.combobox.get()
        self.value = self.user_input.get()

        if self.level.startswith("Nivel "):
            level_num = int(self.level.split(" ")[1])

            if level_num == 4 and self.value.isdigit() and int(self.value) > 10:
                self.message_label.config(text="Límite de valor es 10 en Nivel 4", fg="red")
                return
            elif level_num == 5 and self.value.isdigit() and int(self.value) > 20:
                self.message_label.config(text="Límite de valor es 20 en Nivel 5", fg="red")
                return
            elif level_num in (4, 5) and ((not self.value.strip() or not self.value.isdigit()) or int(self.value) == 0):
                self.message_label.config(text="ERROR. Ingrese un valor de fuerza", fg="red")
                return
            if not self.check_last_lvl(level_num):
                return

            self.message_label.config(text="Cambios aplicados correctamente", fg="green")
            self.start_button_widget.config(state="normal")
            self.stop_button_widget.config(state="normal")
            self.user_input.config(state="disabled")
            self.combobox.config(state="disabled")

        self.message_label.after(5000, lambda: self.message_label.config(text=""))

    def start_animation(self):
        self.level1 = self.combobox.get()
        if self.level1.startswith("Nivel "):
            level1_num = int(self.level1.split(" ")[1])
            if 1 <= level1_num <= 5:
                self.blinking(self.squares[5 - level1_num])
                self.combobox.config(state="disabled")
                self.yes_button_widget.config(state="normal")
                self.no_button_widget.config(state="normal")
                self.user_input.config(state="disabled")
                self.start_button_widget.config(state="disabled")

    def blinking(self, square):
        if self.active_animation:
            color = "blue" if self.blink_state else "white"
            square.config(bg=color)
            self.blink_state = not self.blink_state
            square.after(500, lambda: self.blinking(square))

    def stop_animation(self):
        self.level2 = self.combobox.get()
        self.active_animation = False
        self.yes_button_widget.config(state="disabled")
        self.no_button_widget.config(state="disabled")
        self.combobox.config(state="normal")
        self.start_button_widget.config(state="disabled")
        self.stop_button_widget.config(state="disabled")
        if self.level2.startswith("Nivel "):
            nivel_num = int(self.level2.split(" ")[1])
            if nivel_num > 3:
                self.user_input.config(state="normal")

    def highlight(self, color):
        self.level3 = self.combobox.get()

        if self.level3.startswith("Nivel "):
            level_num = int(self.level3.split(" ")[1])
            if 1 <= level_num <= 3:
                self.stop_animation()
                self.squares[5 - level_num].config(bg=color)
                self.achieved_levels[level_num - 1] = True
                self.user_input.config(state="disabled")
            else:
                self.stop_animation()
                self.squares[5 - level_num].config(bg=color)
                self.achieved_levels[level_num - 1] = True
                self.user_input.config(state="normal")

    def send_value(self, event):
        cadena = str(self.combobox.get())
        self.arduino_lock.acquire()
        time.sleep(0.02)
        self.ser.write(cadena.encode('ascii'))
        time.sleep(0.02)
        self.arduino_lock.release()
        print(self.combobox.get())

    def turn_on_motor(self):
        if self.ser is not None:
            cadena = str(998)
            self.arduino_lock.acquire()
            time.sleep(0.02)
            self.ser.write(cadena.encode('ascii'))
            time.sleep(0.02)
            self.arduino_lock.release()

    def turn_off_motor(self):
        if self.ser is not None:
            cadena = str(999)
            self.arduino_lock.acquire()
            time.sleep(0.02)
            self.ser.write(cadena.encode('ascii'))
            time.sleep(0.02)
            self.arduino_lock.release()

    def switch_to_interface1(self):
        self.canvas.place_forget()  # Hide the current interface
        AppInterphase1(self.root, self)  # Show the second interface

    def show(self):
        self.canvas.place(x=0, y=0)  # Show the current interface

    def on_closing(self):
        self.disconnect_arduino()
        self.root.destroy()


class AppInterphase1:
    def __init__(self, root, app_interface):
        self.root = root
        self.app_interface = app_interface
        self.canvas = self.create_canvas()
        self.init_widgets()

    def create_canvas(self):
        canvas = tk.Canvas(
            self.root,
            bg="#FFFFFF",
            height=720,
            width=1000,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        canvas.place(x=0, y=0)
        return canvas

    def init_widgets(self):
        self.back_button = ttk.Button(self.canvas, text="Back to Main Interface", command=self.switch_to_main_interface)
        self.back_button.place(x=50.0, y=100.0, width=150.0, height=20.0)

    def switch_to_main_interface(self):
        self.canvas.place_forget()  # Hide the current interface
        self.app_interface.show()  # Show the main interface


class LegAnimation:
    def __init__(self, canvas, video_path):
        self.canvas = canvas
        self.video_path = video_path
        self.frames = self.load_video_frames(video_path)
        self.label = tk.Label(self.canvas)
        self.label.place(x=680, y=150)
        self.text_id = self.canvas.create_text(645, 250, text="0°", font=("Arial", 16), fill="black")
        self.update_frame(0)

        self.canvas.create_rectangle(600, 230, 670, 270, outline='black', fill='', width=1)

        self.canvas.create_text(
            830, 130,  # Coordinates (x, y)
            text="Ángulo",  # Text content
            font=("Calibri", 16),  # Font and size
            fill="black"  # Text color
        )

    def load_video_frames(self, video_path):
        cap = cv2.VideoCapture(video_path)
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame)
        cap.release()
        return frames

    def update_frame(self, position):
        frame_index = int(((position) / 150) * (len(self.frames) - 1))
        frame = self.frames[frame_index]
        frame_image = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.label.config(image=frame_image)
        self.label.image = frame_image
        self.canvas.itemconfig(self.text_id, text=f"{position:.1f}°")


if __name__ == "__main__":
    root = tk.Tk()
    app = AppInterface(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()