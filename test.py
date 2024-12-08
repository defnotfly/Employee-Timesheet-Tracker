import customtkinter as ctk

def show_message():
    # This will print a message to the terminal when the button is clicked
    print("CONGRATS REAL NIGGAS")

# Create the main window
root = ctk.CTk()

# Set the title of the window
root.title("CLICK ME")

# Set window size
root.geometry("300x200")

# Create a button that triggers the show_message function when clicked
button = ctk.CTkButton(root, text="Click Me", command=show_message)
button.pack(pady=50)

# Run the main event loop
root.mainloop()
