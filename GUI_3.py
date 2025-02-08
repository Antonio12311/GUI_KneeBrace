import cv2
import tkinter as tk
import threading
from tkinter import Entry, PhotoImage
from pathlib import Path
from PIL import Image, ImageTk
import os

_DIR = os.path.dirname(__file__)
OUTPUT_PATH = Path(__file__).resolve().parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"


class LegAnimation:
    def __init__(self, root, canvas, video_path):
        self.root = root
        self.canvas = canvas
        self.video_path = video_path

        # Load video frames
        self.frames = self.load_video_frames(video_path)

        # Create a label to display the video frame
        self.label = tk.Label(self.canvas)
        self.label.place(x=770, y=200)  # Place the label

        self.text_id = self.canvas.create_text(
            1200, 315,  # Coordinates (x, y)
            text="0°",  # Text content
            font=("Arial", 16),  # Font and size
            fill="black"  # Text color
        )

        # Initialize with the first frame
        self.update_frame(0)

        # Start a thread to listen for keyboard input
        self.input_thread = threading.Thread(target=self.listen_for_input, daemon=True)
        self.input_thread.start()

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

    def listen_for_input(self):
        while True:
            try:
                # Get input from the terminal
                input_value = int(input("Enter a value between 0 and 150: "))
                if 0 <= input_value <= 150:
                    # Schedule the frame update in the main thread
                    self.root.after(0, self.update_frame, input_value)
                else:
                    print("Input must be between 0 and 150.")
            except ValueError:
                print("Invalid input. Please enter a number.")


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


def relative_to_assets(path: str) -> Path:
    return str(ASSETS_PATH / path)


def name_entry_widget(canvas):
    ruta_img = relative_to_assets("Text_bar0.png")
    image_widget = PhotoImage(file=ruta_img)

    entry_bg_1 = canvas.create_image(
        850.0,
        70.0,
        image=image_widget
    )
    entry_1 = Entry(
        bd=0,
        bg="#acdccc",
        fg="#000716",
        highlightthickness=0,
        state="normal",
        font="Calibri 13"
    )
    entry_1.place(
        x=575.0,
        y=50.0,
        width=300.0,
        height=35.0
    )
    canvas.create_text(
        445.0,
        57,
        anchor="nw",
        text="Nombre de pac.",
        fill="#000000",
        font="Calibri 13"
    )
    return entry_1, image_widget  # Keep a reference to the video to avoid garbage collection


def age_entry_widget(canvas):
    ruta_img = relative_to_assets("Text_bar1.png")
    image_widget = PhotoImage(file=ruta_img)

    entry_bg_2 = canvas.create_image(
        625.0,
        130.0,
        image=image_widget
    )
    entry_2 = Entry(
        bd=0,
        bg="#acdccc",
        fg="#000716",
        highlightthickness=0,
        state="normal",
        font="Calibri 13"
    )
    entry_2.place(
        x=575.0,
        y=110.0,
        width=80.0,
        height=35.0
    )
    canvas.create_text(
        510.0,
        120,
        anchor="nw",
        text="Edad",
        fill="#000000",
        font="Calibri 13"
    )
    return entry_2, image_widget  # Keep a reference to the video to avoid garbage collection


def sex_entry_widget(canvas):
    ruta_img = relative_to_assets("Text_bar1.png")
    image_widget = PhotoImage(file=ruta_img)

    entry_bg_3 = canvas.create_image(
        830.0,
        130.0,
        image=image_widget
    )
    entry_3 = Entry(
        bd=0,
        bg="#acdccc",
        fg="#000716",
        highlightthickness=0,
        state="normal",
        font="Calibri 13"
    )
    entry_3.place(
        x=780.0,
        y=110.0,
        width=100.0,
        height=35.0
    )
    canvas.create_text(
        720.0,
        120,
        anchor="nw",
        text="Sexo",
        fill="#000000",
        font="Calibri 13"
    )
    return entry_3, image_widget  # Keep a reference to the video to avoid garbage collection


def weight_entry_widget(canvas):
    ruta_img = relative_to_assets("Text_bar1.png")
    image_widget = PhotoImage(file=ruta_img)

    entry_bg_4 = canvas.create_image(
        1075.0,
        130.0,
        image=image_widget
    )
    entry_4 = Entry(
        bd=0,
        bg="#acdccc",
        fg="#000716",
        highlightthickness=0,
        state="normal",
        font="Calibri 13"
    )
    entry_4.place(
        x=1030.0,
        y=110.0,
        width=100.0,
        height=35.0
    )
    canvas.create_text(
        960.0,
        120,
        anchor="nw",
        text="Edad",
        fill="#000000",
        font="Calibri 13"
    )
    return entry_4, image_widget  # Keep a reference to the video to avoid garbage collection


def toggle_button_color(button):
    global active_button

    # If the clicked button is already green, do nothing
    if button.cget("bg") == "green":
        return
    button.config(bg="green", fg="white")

    # If there was a previously active button, set it to red
    if active_button and active_button != button:
        active_button.config(bg="red", fg="white")
    active_button = button


def buttons_widget(canvas):
    # Variable to track the currently active button
    global active_button
    active_button = None

    # Create the first button
    button1 = tk.Button(
        canvas,
        text="1",
        bg="blue",  # Initial background color (red)
        fg="white",  # Text color
        font=("Arial", 12),
        relief="flat",  # Remove button border (optional)
        command=lambda: toggle_button_color(button1)  # Pass the button to the function
    )
    button1.place(x=120, y=260, width=80, height=80)

    # Create the second button
    button2 = tk.Button(
        canvas,
        text="2",
        bg="blue",
        fg="white",
        font=("Arial", 12),
        relief="flat",
        command=lambda: toggle_button_color(button2)
    )
    button2.place(x=230, y=260, width=80, height=80)

    # Create the third button
    button3 = tk.Button(
        canvas,
        text="3",
        bg="blue",
        fg="white",
        font=("Arial", 12),
        relief="flat",
        command=lambda: toggle_button_color(button3)
    )
    button3.place(x=340, y=260, width=80, height=80)

    button4 = tk.Button(
        canvas,
        text="4",
        bg="blue",  # Initial background color (red)
        fg="white",  # Text color
        font=("Arial", 12),
        relief="flat",  # Remove button border (optional)
        command=lambda: toggle_button_color(button4)  # Pass the button to the function
    )
    button4.place(x=175, y=360, width=80, height=80)


    return button1, button2, button3, button4


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


def interface():
    global window, entry_image1, entry_image2, entry_image3, entry_image4, active_button,\
    button1, button2, button3, button4

    window = tk.Tk()
    window.geometry("1280x720")
    window.configure(bg="white")
    window.protocol("WM_DELETE_WINDOW")
    canvas = create_canvas(window)
    video_path = r"C:\Users\Anton\PycharmProjects\GUI_KneeBrace\video\Leg sequence (4).mp4"  # Use raw string

    # Initialize the LegAnimation and TextUpdate classes
    LegAnimation(window, canvas, video_path)
    TextUpdate(window, canvas)

    entry_1, entry_image1 = name_entry_widget(canvas)  # Enter name widget
    entry_2, entry_image2 = age_entry_widget(canvas)  # Enter age widget
    entry_3, entry_image3 = sex_entry_widget(canvas)  # Enter sex widget
    entry_4, entry_image4 = weight_entry_widget(canvas)  # Enter weight widget
    button1, button2, button3, button4 = buttons_widget(canvas)


    window.resizable(False, False)
    window.mainloop()


# Run the interface
interface()

# La pela ptm
# YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa
# Pruebas en mi branch rontu

# Ya se pudo, TRAAAAKAAAS
