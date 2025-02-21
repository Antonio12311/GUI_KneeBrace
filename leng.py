import tkinter as tk
import cv2
from tkinter import ttk, messagebox
from pathlib import Path
import os


_DIR = os.path.dirname(__file__)
OUTPUT_PATH = Path(__file__).resolve().parent


def find_video_file(directory, video_name):

    search_dir = Path(directory)

    # Search for the video file recursively
    for file in search_dir.rglob(video_name):
        if file.is_file():  # Ensure it's a file (not a directory)
            return str(file)  # Return the full path as a string

    return None


def load_video_frames(video_path):
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


def create_frames(input_folder, output_folder):
    frames = load_video_frames(input_folder)

    for i, frame in enumerate(frames):
        # Convert RGB back to BGR (OpenCV uses BGR for saving images)
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # Save the frame as an image file
        output_path = Path(output_folder) / f"frame_{i:04d}.png"  # Use :04d for zero-padding
        cv2.imwrite(str(output_path), frame_bgr)
        print(f"Saved: {output_path}")


def main():
    video_directory = Path(__file__).resolve().parent / "video"  # Search in the "video" folder
    output_directory = Path(__file__).resolve().parent / "light_video"
    video_name = "Leg_video.mp4"  # Name of the video file

    search_dir1 = Path(output_directory)

    # Automatically detect the video path
    video_path = find_video_file(video_directory, video_name)

    if video_path:
        print(f"Video found: {video_path}")
    else:
        print(f"Error: Video file '{video_name}' not found in '{video_directory}'.")
        messagebox.showerror("Error", f"Video file '{video_name}' not found in '{video_directory}'.")
        return

    create_frames(video_path, search_dir1)


main()