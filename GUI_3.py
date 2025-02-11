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
import time

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

    status_label = tk.Label(canvas, text="Not Connected", fg="red", font=("Arial", 14))
    status_label.place(
        x=40.0,
        y=60.0
    )
    connect_button = ttk.Button(canvas, text="Connect", command=connect_to_arduino)
    connect_button.place(
        x=50.0,
        y=100.0,
        width=100.0,  # Adjusted width to fit text
        height=20.0
    )
    disconnect_button = ttk.Button(canvas, text="Disconnect", command=disconnect_arduino, state="disabled")
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
    global ser, status_label, connect_button, disconnect_button, stop_threads

    arduino_port = find_arduino_port()
    if arduino_port:
        if ser is None:  # Only connect if not already connected
            try:
                ser = serial.Serial(arduino_port, 115200, timeout=2)
                status_label.config(text=f"Connected to {arduino_port}", fg="green")
                connect_button.config(state="disabled")
                disconnect_button.config(state="normal")

                # Start the reading thread
                stop_threads = False
                reading_thread = threading.Thread(target=read_serial_port, args=(ser,))
                reading_thread.start()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to connect: {e}")
                if ser:
                    ser.close()
                    ser = None
    else:
        messagebox.showwarning("Not Found", "Arduino not found. Please check the connection.")


def read_serial_port(arduino):
    global stop_threads, data, position, torque, window, connect, ser, rad, position
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
                            position = (rad * 180) / math.pi
                            torque = abs(float(values[1]))  # Assuming the second value is `t_out_s`
                            print(f"Position: {position}, Torque: {torque}")
                        except ValueError:
                            print("Error: Invalid data format. Skipping this line.")
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
        self.label.place(x=770, y=150)  # Place the label

        self.text_id = self.canvas.create_text(
            1200, 315,  # Coordinates (x, y)
            text="0°",  # Text content
            font=("Arial", 16),  # Font and size
            fill="black"  # Text color
        )

        # Initialize with the first frame
        self.update_frame(0)

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

    def input_to_frame(self, input_value, total_frames):
        """Map input value (0-150) to frame index."""
        # Map 0 to 150 to 0 to (total_frames - 1)
        return int(((115 - input_value) / 115) * (total_frames - 1))

    def update_frame(self, input_value):
        """Update the displayed frame based on input value."""
        frame_index = self.input_to_frame(input_value, len(self.frames))
        frame = self.frames[frame_index]
        frame_image = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.label.config(image=frame_image)
        self.label.image = frame_image  # Keep a reference to avoid garbage collection

        # Update the text with the current input value
        self.canvas.itemconfig(self.text_id, text=f"{input_value}°")


class TextUpdate:
    def __init__(self, root, canvas):
        self.root = root
        self.canvas = canvas

        self.canvas.create_rectangle(1160, 290, 1230, 340, outline='black', fill='', width=1)

        self.canvas.create_text(
            1195, 275,  # Coordinates (x, y)
            text="Ángulo",  # Text content
            font=("Arial", 16),  # Font and size
            fill="black"  # Text color
        )


def interface():
    global window, entry_image1, entry_image2, entry_image3, entry_image4, \
        status_label, connect_button, disconnect_button

    window = tk.Tk()
    window.geometry("1280x720")
    window.configure(bg="white")
    canvas = create_canvas(window)
    video_path = r"C:\Users\Anton\PycharmProjects\GUI_KneeBrace\video\Leg sequence (4).mp4"  # Use raw string

    # Initialize the LegAnimation and TextUpdate classes
    LegAnimation(window, canvas, video_path)
    TextUpdate(window, canvas)

    connect_widgets(canvas)

    window.resizable(False, False)
    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.mainloop()


start_connection = threading.Thread(target=connect_to_arduino)
start_connection.start()

# Run the interface
interface()

start_connection.join()