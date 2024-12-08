import cv2
from tkinter import Canvas
from PIL import Image, ImageTk
import customtkinter as ctk

class VideoBackgroundApp(ctk.CTk):
    def __init__(self, video_path):
        super().__init__()

        self.title("Background Video Loop")
        self.geometry("800x600")

        # Load the video
        self.cap = cv2.VideoCapture(video_path)

        # Create a canvas for video
        self.canvas = Canvas(self, width=800, height=600)
        self.canvas.pack(fill="both", expand=True)

        # Start playing the video
        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()

        if not ret:  # Loop the video when it ends
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()

        # Convert frame (BGR to RGB) and display it
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (800, 600))  # Adjust to fit canvas
        img = ImageTk.PhotoImage(Image.fromarray(frame))

        self.canvas.create_image(0, 0, anchor="nw", image=img)
        self.canvas.image = img

        # Schedule next frame update
        self.after(10, self.update_frame)  # ~100 FPS (adjust as needed)

    def on_close(self):
        self.cap.release()  # Release video capture when closing
        self.destroy()

if __name__ == "__main__":
    app = VideoBackgroundApp("bgloop.mp4")
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
