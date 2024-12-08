import tkinter as tk
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk

class MyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.title("Employee Timesheet Tracker")
        self.geometry(self.center_window(610, 540))  # Original login window size

        # Start video in the background
        self.canvas = tk.Canvas(self, width=610, height=540)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.bg_video = cv2.VideoCapture("bgloop.mp4")

        # Create a video loop to display as background
        self.update_video_background()

        # Load logo image and display it
        logo_image = ctk.CTkImage(Image.open("logo.png"), size=(300, 100))  # Replace 'logo.png' with your file
        logo_label = ctk.CTkLabel(self, image=logo_image, text="")  # No text; just the image
        logo_label.pack(pady=10, anchor="center")

        # Set up the login form on top of the video
        self.login_frame = ctk.CTkFrame(self, width=300, height=335)  # Set frame size
        self.login_frame.pack_propagate(False)  # Prevent auto-resizing
        self.login_frame.pack()

        ctk.CTkLabel(self.login_frame, text="Username:").pack(pady=5, anchor="center")
        self.username_entry = ctk.CTkEntry(self.login_frame, width=180)
        self.username_entry.pack(pady=5, anchor="center")

        ctk.CTkLabel(self.login_frame, text="Password:").pack(pady=5, anchor="center")
        self.password_entry = ctk.CTkEntry(self.login_frame, show="*", width=180)
        self.password_entry.pack(pady=5, anchor="center")

    def center_window(self, width, height):
        # Method to center the window on the screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()   
        position_top = int(screen_height / 2 - height / 2)
        position_right = int(screen_width / 2 - width / 2)
        return f'{width}x{height}+{position_right}+{position_top}'

    def update_video_background(self):
        # Function to play the video and update canvas with each frame
        ret, frame = self.bg_video.read()
        if ret:
            # Convert frame to Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = ImageTk.PhotoImage(img)

            # Update the canvas with the new frame
            self.canvas.create_image(0, 0, anchor="nw", image=img)
            self.canvas.img = img  # Keep a reference to the image

            # Loop the video
            self.after(10, self.update_video_background)
        else:
            self.bg_video.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video if finished
            self.update_video_background()

# Run the application
if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
