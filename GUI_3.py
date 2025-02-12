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

# Global variables for serial connection
ser = None
stop_threads = False


class AppInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("1280x720")
        self.configure(bg="white")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.frames = {}

        for F in (MainPage, AnotherPage):  # Add more pages as needed
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.show_frame("MainPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def on_closing(self):
        disconnect_arduino()
        self.destroy()


class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.canvas = tk.Canvas(self, bg="#FFFFFF", height=720, width=1280, bd=0, highlightthickness=0, relief="ridge")
        self.canvas.place(x=0, y=0)

        self.status_label = tk.Label(self.canvas, text="Not Connected", fg="red", font=("Arial", 14))
        self.status_label.place(x=40, y=60)

        self.connect_button = ttk.Button(self.canvas, text="Connect", command=self.connect_to_arduino)
        self.connect_button.place(x=50, y=100, width=100, height=20)

        self.disconnect_button = ttk.Button(self.canvas, text="Disconnect", command=disconnect_arduino,
                                            state="disabled")
        self.disconnect_button.place(x=50, y=130, width=100, height=20)

        # Load and display the animation
        video_directory = Path(__file__).resolve().parent / "video"
        video_name = "Leg Sequence (4).mp4"
        video_path = find_video_file(video_directory, video_name)

        if video_path:
            print(f"Video found: {video_path}")
            self.leg_animation = LegAnimation(self, self.canvas, video_path)
        else:
            messagebox.showerror("Error", f"Video file '{video_name}' not found in '{video_directory}'.")

    def connect_to_arduino(self):
        global ser, stop_threads

        arduino_port = find_arduino_port()
        if arduino_port:
            if ser is None:
                try:
                    ser = serial.Serial(arduino_port, 115200, timeout=2)
                    self.status_label.config(text=f"Connected to {arduino_port}", fg="green")
                    self.connect_button.config(state="disabled")
                    self.disconnect_button.config(state="normal")

                    stop_threads = False
                    reading_thread = threading.Thread(target=read_serial_port, args=(ser, self.leg_animation))
                    reading_thread.start()
                except Exception as e:
                    if ser:
                        ser.close()
                        ser = None
        else:
            messagebox.showwarning("Not Found", "Arduino not found. Please check the connection.")


class AnotherPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = tk.Label(self, text="This is another page!", font=("Arial", 20))
        label.pack(pady=20)


def find_video_file(directory, video_name):
    search_dir = Path(directory)
    for file in search_dir.rglob(video_name):
        if file.is_file():
            return str(file)
    return None


def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Arduino" in port.description or "CH340" in port.description or "USB Serial" in port.description:
            return port.device
    return None


def read_serial_port(arduino, leg_animation):
    global stop_threads
    try:
        while not stop_threads:
            if arduino and arduino.is_open:
                data = arduino.readline().decode().strip()
                if data:
                    values = data.split(",")
                    if len(values) >= 2:
                        try:
                            rad = abs(float(values[0]))
                            position = (rad * 180) / math.pi
                            torque = abs(float(values[1]))
                            print(f"Position: {position}, Torque: {torque}")
                            if leg_animation:
                                leg_animation.update_frame(position)
                        except ValueError:
                            print("Error: Invalid data format.")
            else:
                break
    except Exception as e:
        print("Error reading the serial port:", e)
        stop_threads = True


def disconnect_arduino():
    global ser, stop_threads
    if ser and ser.is_open:
        stop_threads = True
        ser.close()
        ser = None


class LegAnimation:
    def __init__(self, root, canvas, video_path):
        self.root = root
        self.canvas = canvas
        self.video_path = video_path
        self.frames = self.load_video_frames(video_path)
        self.label = tk.Label(self.canvas)
        self.label.place(x=770, y=150)
        self.text_id = self.canvas.create_text(1200, 315, text="0°", font=("Arial", 16), fill="black")
        self.update_frame(0)

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

    def input_to_frame(self, position, total_frames):
        return int(((position) / 150) * (total_frames - 1))

    def update_frame(self, position):
        frame_index = self.input_to_frame(position, len(self.frames))
        frame = self.frames[frame_index]
        frame_image = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.label.config(image=frame_image)
        self.label.image = frame_image
        self.canvas.itemconfig(self.text_id, text=f"{position:.1f}°")


if __name__ == "__main__":
    app = AppInterface()
    app.mainloop()
