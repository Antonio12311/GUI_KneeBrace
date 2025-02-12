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

class AppInterface:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1280x720")
        self.root.configure(bg="white")
        self.canvas = self.create_canvas()
        self.leg_animation = None
        self.ser = None
        self.stop_threads = False
        self.init_widgets()
        self.video_setup()

    def create_canvas(self):
        canvas = tk.Canvas(
            self.root,
            bg="#FFFFFF",
            height=720,
            width=1280,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        canvas.place(x=0, y=0)
        return canvas

    def init_widgets(self):
        self.status_label = tk.Label(self.canvas, text="Not Connected", fg="red", font=("Arial", 14))
        self.status_label.place(x=40.0, y=60.0)
        self.connect_button = ttk.Button(self.canvas, text="Connect", command=self.connect_to_arduino)
        self.connect_button.place(x=50.0, y=100.0, width=100.0, height=20.0)
        self.disconnect_button = ttk.Button(self.canvas, text="Disconnect", command=self.disconnect_arduino, state="disabled")
        self.disconnect_button.place(x=50.0, y=130.0, width=100.0, height=20.0)
        self.switch_button = ttk.Button(self.canvas, text="Go to Interface 1", command=self.switch_to_interface1)
        self.switch_button.place(x=50.0, y=160.0, width=120.0, height=20.0)

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

    def connect_to_arduino(self):
        arduino_port = self.find_arduino_port()
        if arduino_port:
            if self.ser is None:
                try:
                    self.ser = serial.Serial(arduino_port, 115200, timeout=2)
                    self.status_label.config(text=f"Connected to {arduino_port}", fg="green")
                    self.connect_button.config(state="disabled")
                    self.disconnect_button.config(state="normal")
                    self.stop_threads = False
                    threading.Thread(target=self.read_serial_port, daemon=True).start()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to connect: {e}")
                    if self.ser:
                        self.ser.close()
                        self.ser = None
        else:
            messagebox.showwarning("Not Found", "Arduino not found. Please check the connection.")

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

    def disconnect_arduino(self):
        if self.ser and self.ser.is_open:
            self.stop_threads = True
            self.ser.close()
            self.ser = None
            self.status_label.config(text="Disconnected", fg="red")
            self.connect_button.config(state="normal")
            self.disconnect_button.config(state="disabled")
            self.stop_threads = False

    def switch_to_interface1(self):
        self.canvas.place_forget()  # Hide the current interface
        AppInterface1(self.root, self)  # Show the second interface

    def show(self):
        self.canvas.place(x=0, y=0)  # Show the current interface

    def on_closing(self):
        self.disconnect_arduino()
        self.root.destroy()


class AppInterface1:
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
            width=1280,
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