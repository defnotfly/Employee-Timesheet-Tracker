import customtkinter as ctk 
from tkinter import ttk  # Import the ttk module for Treeview/Table
from tkinter import messagebox # Import from ttk module for message box
from PIL import Image # from Pillow for the system image/logo
import mysql.connector
import datetime
import re;

# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",          # Replace with your MySQL username
        password="",          # Replace with your MySQL password
        database="timesheet"  # Database name
    )


# Clock In Function 
def clock_in(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    today = datetime.date.today().strftime('%Y-%m-%d')
    now = datetime.datetime.now().strftime('%H:%M:%S')

    # Check if the employee has already clocked in today
    cursor.execute("SELECT * FROM attendance WHERE employee_id = %s AND date = %s", (employee_id, today))
    record = cursor.fetchone()

    if record:
        # If there's a record, check if the employee has clocked out already
        if record[3] is not None:  # Check if clock_out is not None (indicating clocked out)
            return "You have already clocked in today."

    else:
        cursor.execute("INSERT INTO attendance (employee_id, date, clock_in) VALUES (%s, %s, %s)", (employee_id, today, now))
        conn.commit()
        return f"Clocked in at {now}"



# Clock Out Function
def clock_out(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    today = datetime.date.today().strftime('%Y-%m-%d')
    now = datetime.datetime.now().strftime('%H:%M:%S')

    # Fetch clock-in time
    cursor.execute("SELECT clock_in FROM attendance WHERE employee_id = %s AND date = %s", (employee_id, today))
    record = cursor.fetchone()

    if not record:
        return "You have not clocked in today. Cannot clock out."           

    clock_in_time = datetime.datetime.strptime(str(record[0]), '%H:%M:%S')
    clock_out_time = datetime.datetime.strptime(now, '%H:%M:%S')

    # Calculate total hours worked and overtime
    total_hours = (clock_out_time - clock_in_time).total_seconds() / 3600
    overtime = max(0, total_hours - 8)

    cursor.execute(""" 
        UPDATE attendance 
        SET clock_out = %s, hours_worked = %s, overtime = %s
        WHERE employee_id = %s AND date = %s
    """, (now, total_hours, overtime, employee_id, today))
    conn.commit()
    conn.close()

    return f"Clocked out at {now}. Total hours: {total_hours:.2f}, Overtime: {overtime:.2f}"



# Employee Authentication
def authenticate_employee(username, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to check username and password
        cursor.execute("SELECT employee_id, full_name FROM employees WHERE username = %s AND password = %s", (username, password))
        record = cursor.fetchone()

        conn.close()
        return record if record else None  # Return record (tuple) if found, otherwise None
    except Exception as e:
        print(f"Error during authentication: {e}")
        return None



# Fetch Attendance Records
def get_attendance(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch attendance records for the logged-in employee
    cursor.execute(""" 
        SELECT date, clock_in, clock_out, hours_worked, overtime 
        FROM attendance 
        WHERE employee_id = %s 
        ORDER BY date DESC 
    """, (employee_id,))
    records = cursor.fetchall()

    conn.close()
    return records



# GUI Class for Employee Timesheet Tracker
class TimesheetApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Hide the main window during the splash screen
        self.geometry(self.center_window(610, 470))
        self.employee_id = None
        self.show_splash_screen()  # Show the splash screen first

    def center_window(self, width, height): #Center Window for all windows
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height / 2 - height / 2)
        position_right = int(screen_width / 2 - width / 2)
        return f"{width}x{height}+{position_right}+{position_top}"
    
    def show_splash_screen(self): #Splash Screen
        # Create a new top-level window for the splash screen
        splash = ctk.CTkToplevel(self)
        splash.geometry(self.center_window(400, 300))  # Size for the splash screen
        splash.overrideredirect(True)  # Remove window decorations
        splash.attributes('-topmost', True)  # Ensure it stays on top
        
        # Add content to the splash screen
        splash_logo_image = ctk.CTkImage(Image.open("logo.png"), size=(300, 120))  # Replace 'splash_logo.png'
        splash_logo_label = ctk.CTkLabel(splash, image=splash_logo_image, text="")
        splash_logo_label.pack(pady=(10,15), anchor="center")

        splash_text = ctk.CTkLabel(splash, text="Welcome to Employee Timesheet Tracker", font=("Arial", 15), anchor="center")
        splash_text.pack(pady=(10,40), anchor="center")

        ctk.CTkLabel(splash, text="© 2024 Franz Lloyd A. Diaz", font=("Arial", 10)).pack(pady=(30,1), anchor="center")
        
        # Close the splash screen after 3 seconds and show the login screen
        self.after(2000, lambda: [splash.destroy(), self.deiconify(), self.show_login_screen()])



    def show_login_screen(self, from_admin_logout=False):
        # Display a logout message if the user is logging out
        if self.employee_id:  # Check if there's a logged-in user (indicates a logout action)
            messagebox.showinfo("Logout", "Logging out.")
            self.employee_id = None  # Clear the employee_id after logout
    
        # Display a logout message for admin mode
        if from_admin_logout:
            messagebox.showinfo("Admin Logout", "Admin mode logged out successfully.")

        for widget in self.winfo_children():
            widget.destroy()

        self.title("Employee Timesheet Tracker")
        self.geometry(self.center_window(610, 540))  # Original login window size
        
        self.resizable(width=False, height=False)
    
        # Load and display the PNG image
        logo_image = ctk.CTkImage(Image.open("logo.png"), size=(300, 100))  # Replace 'logo.png' with your file
        logo_label = ctk.CTkLabel(self, image=logo_image, text="")  # No text; just the image
        logo_label.pack(pady=10, anchor="center")
    
        # Initialize login_frame here
        self.login_frame = ctk.CTkFrame(self, width=300, height=335)  # Set frame size
        self.login_frame.pack_propagate(False)  # Prevent auto-resizing
        self.login_frame.pack()

        ctk.CTkLabel(self.login_frame, text="Username:").pack(pady=5, anchor="center")
        self.username_entry = ctk.CTkEntry(self.login_frame, width=180)
        self.username_entry.pack(pady=5, anchor="center")

        ctk.CTkLabel(self.login_frame, text="Password:").pack(pady=5, anchor="center")
        self.password_entry = ctk.CTkEntry(self.login_frame, show="*", width=180)
        self.password_entry.pack(pady=5, anchor="center")

        def toggle_password(): # For show/unshow password 
            if self.show_password_var.get():
                self.password_entry.configure(show="")  # Show password
            else:
                self.password_entry.configure(show="*")  # Hide password

        # Checkbox to show/hide password
        self.show_password_var = ctk.BooleanVar(value=False)  # Initialize as unchecked
        self.show_password_checkbox = ctk.CTkCheckBox(self.login_frame, text="Show Password", variable=self.show_password_var, command=toggle_password, checkbox_height=15, checkbox_width=15)
        self.show_password_checkbox.pack(pady=5, anchor="center")
    
        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.login, corner_radius=20)
        self.login_button.pack(pady=15, anchor="center")

        # Bind Enter key to login function
        self.username_entry.bind("<Return>", lambda event: self.login())
        self.password_entry.bind("<Return>", lambda event: self.login())

        self.register_button = ctk.CTkButton(self.login_frame, text="Register", command=self.show_register_screen, corner_radius=20)
        self.register_button.pack(anchor="center")

        self.admin_button = ctk.CTkButton(self.login_frame, text="Admin", command=self.admin_showeverything, corner_radius=20)
        self.admin_button.pack(pady=(16,10),anchor="center")
    
        # Add space below the login_frame and above the copyright text
        ctk.CTkLabel(self, text="© 2024 Franz Lloyd A. Diaz. All rights reserved.", font=("Arial", 10)).pack(pady=(57, 0), anchor="center")


        
    def show_register_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.title("Registration Form")
    
        # Load and display the PNG image
        logo_image = ctk.CTkImage(Image.open("logo.png"), size=(300, 100))  # Replace 'logo.png' with your file
        logo_label = ctk.CTkLabel(self, image=logo_image, text="")  # No text; just the image
        logo_label.pack(pady=(5, 5), anchor="center")
    
        self.register_frame = ctk.CTkFrame(self, width=330, height=525)  # Register Frame Size
        self.register_frame.pack_propagate(False)
        self.register_frame.pack(pady=(30, 5))
    
        # Placeholder handling function
        def add_placeholder(entry, placeholder_text):
            entry.insert(0, placeholder_text)
            entry.configure(fg_color="grey")  # Optional: set placeholder text color
        
            def on_focus_in(event):
                if entry.get() == placeholder_text:
                    entry.delete(0, "end")
                    entry.configure(fg_color="black")  # Reset to normal text color
        
            def on_focus_out(event):
                if entry.get() == "":
                    entry.insert(0, placeholder_text)
                    entry.configure(fg_color="grey")  # Reapply placeholder color
        
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
    
        # Username entry with placeholder
        ctk.CTkLabel(self.register_frame, text="Username:").pack(pady=(10, 5), anchor="center")
        self.new_username_entry = ctk.CTkEntry(self.register_frame, width=200)
        self.new_username_entry.pack(pady=5, anchor="center")
        add_placeholder(self.new_username_entry, "ex. test123")
    
        # Password entry with placeholder
        ctk.CTkLabel(self.register_frame, text="Password:").pack(pady=5, anchor="center")
        self.new_password_entry = ctk.CTkEntry(self.register_frame, show="*", width=200)
        self.new_password_entry.pack(pady=5, anchor="center")
        add_placeholder(self.new_password_entry, "ex. password123")
    
        # Full name entry with placeholder
        ctk.CTkLabel(self.register_frame, text="Full Name:").pack(pady=5, anchor="center")
        self.full_name_entry = ctk.CTkEntry(self.register_frame, width=200)
        self.full_name_entry.pack(pady=5, anchor="center")
        add_placeholder(self.full_name_entry, "ex. John Doe")
    
        # Phone number entry with placeholder
        ctk.CTkLabel(self.register_frame, text="Phone Number:").pack(pady=5, anchor="center")
        self.phone_number_entry = ctk.CTkEntry(self.register_frame, width=200)
        self.phone_number_entry.pack(pady=5, anchor="center")
        add_placeholder(self.phone_number_entry, "ex. 123-456-7890")
    
        # Email entry with placeholder
        ctk.CTkLabel(self.register_frame, text="Email:").pack(pady=5, anchor="center")
        self.email_entry = ctk.CTkEntry(self.register_frame, width=200)
        self.email_entry.pack(pady=5, anchor="center")
        add_placeholder(self.email_entry, "ex. john.doe@example.com")
    
        self.register_user_button = ctk.CTkButton(self.register_frame, text="Register", command=self.register_user, corner_radius=20)
        self.register_user_button.pack(pady=(30, 15), anchor="center")
        ctk.CTkLabel(self, text="© 2024 Franz Lloyd A. Diaz. All rights reserved.", font=("Arial", 10)).pack(pady=(90, 0), anchor="center")
    
        # Bind Enter key to register function
        self.new_username_entry.bind("<Return>", lambda event: self.register_user())
        self.new_password_entry.bind("<Return>", lambda event: self.register_user())
        self.full_name_entry.bind("<Return>", lambda event: self.register_user())
        self.phone_number_entry.bind("<Return>", lambda event: self.register_user())
        self.email_entry.bind("<Return>", lambda event: self.register_user())
    
        self.back_button = ctk.CTkButton(self.register_frame, text="Back", command=self.show_login_screen, corner_radius=20)
        self.back_button.pack(pady=(5, 20), anchor="center")
    
        self.geometry(self.center_window(700, 800))  # Center the register window




    def register_user(self):
        username = self.new_username_entry.get()
        password = self.new_password_entry.get()
        full_name = self.full_name_entry.get()
        phone_number = self.phone_number_entry.get()
        email = self.email_entry.get()

        
        # Validation patterns
        username_pattern = r"^[a-zA-Z0-9]+$"  # Alphanumeric only
        name_pattern = r"^[a-zA-Z\s]+$"  # Letters and spaces only
        phone_pattern = r"^\d+$"  # Digits only
        
        
        if not username or not password or not full_name or not phone_number or not email:
            messagebox.showwarning("Invalid Input", "All fields are required.")
            return

        # Validate username
        if not re.match(username_pattern, username):
            messagebox.showwarning("Invalid Input", "Username must not contain special characters.")
            return

        # Validate full name
        if not re.match(name_pattern, full_name):
            messagebox.showwarning("Invalid Input", "Full Name must not contain special characters or numbers.")
            return

        # Validate phone number
        if not re.match(phone_pattern, phone_number):
            messagebox.showwarning("Invalid Input", "Phone Number must contain only digits.")
            return
        
        # Check if the username, phone_number, or email already exists in the database
        conn = get_db_connection()
        cursor = conn.cursor()

        
        
        
        # Check if username already exists
        cursor.execute("SELECT * FROM employees WHERE username = %s", (username,))
        if cursor.fetchone():
            messagebox.showwarning("Username Taken", "Username already exists.")
            return
        # Check if phone number already exists
        cursor.execute("SELECT * FROM employees WHERE phone_number = %s", (phone_number,))
        if cursor.fetchone():
            messagebox.showwarning("Phone Number Taken", "Phone number already exists.")
            return

        # Check if email already exists
        cursor.execute("SELECT * FROM employees WHERE email = %s", (email,))
        if cursor.fetchone():
            messagebox.showwarning("Email Taken", "Email already exists.")
            return

        # If no existing records, proceed to register the user
        try:
            cursor.execute("INSERT INTO employees (username, password, full_name, phone_number, email) VALUES (%s, %s, %s, %s, %s)", 
                           (username, password, full_name, phone_number, email))
            conn.commit()
            
            messagebox.showinfo("Result", "Registration Successful.")
            
            self.show_login_screen()  # Go back to login screen after registration
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            conn.close()



    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Invalid Input", "Please enter both username and password.")
            return

        # Authenticate the employee
        record = authenticate_employee(username, password)

        if record:
            employee_id, full_name = record
            self.employee_id = employee_id  # Save employee ID
            messagebox.showinfo("Login Successful", f"Welcome, {full_name}!")
            self.show_main_menu()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

        


    def show_main_menu(self):
        for widget in self.winfo_children():
            widget.destroy()
        
        self.title("Main Menu")
        
        self.resizable(width=False, height=False)
        
        # Load and display the PNG image
        logo_image = ctk.CTkImage(Image.open("logo.png"), size=(300, 100))  # Replace 'logo.png' with your file
        logo_label = ctk.CTkLabel(self, image=logo_image, text="").pack(pady=(5, 25), anchor="center")   # No text; just the image
        
        # Create the label to display time
        self.time_label = ctk.CTkLabel(self, text="", font=("Arial", 15))
        self.time_label.pack(pady=3)

        # Function to update the time on the label
        self.update_time()



    def update_time(self):
        # Get the current date and time
        current_time = datetime.datetime.now()

        # Format the time as desired (Year-Month-Day Hour:Minute:Second)
        formatted_time = current_time.strftime("%Y-%m-%d || %H:%M:%S")

        # Update the text of the label
        self.time_label.configure(text=formatted_time)

        # Call this function every 1000 ms (1 second) to update the time
        self.after(1000, self.update_time)
        
        self.main_frame = ctk.CTkFrame(self, width=300, height=250)
        self.main_frame.pack_propagate(False)  # Prevent frame from resizing to fit its content
        self.main_frame.pack(anchor="center", pady=(30,0))  # Center the frame in the window

        # Add widgets with center alignment
        ctk.CTkButton(self.main_frame, text="Clock In", command=lambda: self.clock_in(self.employee_id)).pack(pady=(35, 11), anchor="center")
        ctk.CTkButton(self.main_frame, text="Clock Out", command=lambda: self.clock_out(self.employee_id)).pack(pady=11, anchor="center")
        ctk.CTkButton(self.main_frame, text="Attendance Records", command=lambda: self.show_attendance(self.employee_id)).pack(pady=11, anchor="center")
        ctk.CTkButton(self.main_frame, text="Logout", command=self.show_login_screen).pack(pady=(11, 35), anchor="center")
        ctk.CTkLabel(self, text="© 2024 Franz Lloyd A. Diaz. All rights reserved.", font=("Arial", 10)).pack(pady=(70,0),anchor="center")
        self.geometry(self.center_window(620, 550))  # Original login window size
        


    def clock_in(self, employee_id):
        message = clock_in(employee_id)
        messagebox.showinfo("Clock In", message)



    def clock_out(self, employee_id):
        message = clock_out(employee_id)
        messagebox.showinfo("Clock Out", message)



    def show_attendance(self, employee_id):
        records = get_attendance(employee_id)
        attendance_window = ctk.CTkToplevel(self)
        attendance_window.title("Attendance Records")
        attendance_window.geometry(self.center_window(650, 400))  # Center the attendance window
        attendance_window.grab_set()  # Prevent interaction with the main window while this window is open
        attendance_window.attributes('-topmost', True)  # Ensure it stays on top initially

        # Add Escape key binding to close the window
        attendance_window.bind("<Escape>", lambda event: attendance_window.destroy())
        
        # Frame to hold the Treeview and Scrollbar together
        frame = ctk.CTkFrame(attendance_window)
        frame.pack(fill="both", expand=True)

        # Create a Treeview widget
        columns = ("date", "clock_in", "clock_out", "hours_worked", "overtime")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
    
        style = ttk.Style()
        style.theme_use("default")  # Use default theme to customize
        style.configure("Treeview", 
                    background="#2D2F33",  # Dark background for rows
                    foreground="white",   # White text
                    rowheight=30,         # Height of rows
                    fieldbackground="#2D2F33",  # Background of fields
                    font=("Arial", 10))   # Font and size for text
        style.configure("Treeview.Heading", 
                    background="#0A84FF",  # Blue for header background
                    foreground="white",   # White header text
                    font=("Arial Bold", 10))  # Bold font for headers
        style.map("Treeview", background=[("selected", "#1C66CC")])  # Highlight color for selected rows
    
        # Customizing the scrollbar style
        style.configure("Vertical.TScrollbar", 
                    gripcount=0, 
                    background="#2D2F33",  # Dark background for the scrollbar
                    troughcolor="#3C3F44",  # Background color of the scrollbar track
                    thumbcolor="#0A84FF",  # Blue thumb color
                    buttoncolor="#2D2F33",  # Button color
                    arrowcolor="#FFFFFF")   # White arrows

        # Define headings and column widths
        tree.heading("date", text="Date")
        tree.heading("clock_in", text="Clock In")
        tree.heading("clock_out", text="Clock Out")
        tree.heading("hours_worked", text="Hours Worked")
        tree.heading("overtime", text="Overtime")

        tree.column("date", width=100, anchor="center")
        tree.column("clock_in", width=100, anchor="center")
        tree.column("clock_out", width=100, anchor="center")
        tree.column("hours_worked", width=100, anchor="center")
        tree.column("overtime", width=100, anchor="center")

        # Add rows to the Treeview
        for record in records:
            tree.insert("", "end", values=record)

        # Add vertical scrollbar for the table
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview, style="Vertical.TScrollbar")
        tree.configure(yscroll=scrollbar.set)

        # Pack Treeview and Scrollbar side by side
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")



    def admin_showeverything(self):
        messagebox.showinfo("Login Successful", "Welcome Admin!")
        for widget in self.winfo_children():
            widget.destroy()

        self.title("Admin Dashboard")

        self.resizable(width=False, height=False)
        
        # Load and display the PNG image
        logo_image = ctk.CTkImage(Image.open("logo.png"), size=(300, 100))
        logo_label = ctk.CTkLabel(self, image=logo_image, text="")
        logo_label.pack(pady=(5, 25), anchor="center")

        ctk.CTkLabel(self, text="Admin Mode", font=("Arial", 15)).pack(anchor="center")
        
        # Frame to hold the buttons
        admin_frame = ctk.CTkFrame(self, width=300, height=250)
        admin_frame.pack_propagate(False)
        admin_frame.pack(pady=(40, 0))

        # Button to show attendance of all users
        ctk.CTkButton(admin_frame, text="View Attendance Records", width=200, height=30, command=self.show_all_attendance_records).pack(pady=(50,15), anchor="center")

        # Button to show all registered users
        ctk.CTkButton(admin_frame, text="View Registered Users", width=180, height=30, command=self.show_all_registered_users).pack(pady=15, anchor="center")

        # Button to log out
        ctk.CTkButton(admin_frame, text="Logout", command=lambda: self.show_login_screen(from_admin_logout=True), height=30).pack(pady=(15, 50), anchor="center")   

        ctk.CTkLabel(self, text="© 2024 Franz Lloyd A. Diaz. All rights reserved.", font=("Arial", 10)).pack(pady=(50, 0), anchor="center")



    def show_all_attendance_records(self):
        # Create a new window for viewing attendance records
        attendance_window = ctk.CTkToplevel(self)
        attendance_window.title("All Attendance Records")
        attendance_window.geometry(self.center_window(850, 500))
        attendance_window.grab_set()  # Prevent interaction with the main window while this window is open
        attendance_window.attributes('-topmost', True)  # Ensure it stays on top initially

        # Frame to hold the Treeview and Scrollbar together
        frame = ctk.CTkFrame(attendance_window)
        frame.pack(fill="both", expand=True)

        # Create a style for the Treeview widget
        style = ttk.Style()
        style.theme_use("default")  # Use default theme to customize
        style.configure("Treeview", 
                    background="#2D2F33",  # Dark background for rows
                    foreground="white",   # White text
                    rowheight=30,         # Height of rows
                    fieldbackground="#2D2F33",  # Background of fields
                    font=("Arial", 10))   # Font and size for text
        style.configure("Treeview.Heading", 
                    background="#0A84FF",  # Blue for header background
                    foreground="white",   # White header text
                    font=("Arial Bold", 10))  # Bold font for headers
        style.map("Treeview", background=[("selected", "#1C66CC")])  # Highlight color for selected rows
    
        # Customizing the scrollbar style
        style.configure("Vertical.TScrollbar", 
                    gripcount=0, 
                    background="#2D2F33",  # Dark background for the scrollbar
                    troughcolor="#3C3F44",  # Background color of the scrollbar track
                    thumbcolor="#0A84FF",  # Blue thumb color
                    buttoncolor="#2D2F33",  # Button color
                    arrowcolor="#FFFFFF")   # White arrows

        # Create a Treeview widget
        columns = ("employee_id", "date", "clock_in", "clock_out", "hours_worked", "overtime")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=20, style="Treeview")

        # Define headings and column widths
        tree.heading("employee_id", text="Employee ID")
        tree.heading("date", text="Date")
        tree.heading("clock_in", text="Clock In")
        tree.heading("clock_out", text="Clock Out")
        tree.heading("hours_worked", text="Hours Worked")
        tree.heading("overtime", text="Overtime")

        tree.column("employee_id", width=100, anchor="center")
        tree.column("date", width=100, anchor="center")
        tree.column("clock_in", width=100, anchor="center")
        tree.column("clock_out", width=100, anchor="center")
        tree.column("hours_worked", width=100, anchor="center")
        tree.column("overtime", width=100, anchor="center")

        # Add Escape key binding to close the window
        attendance_window.bind("<Escape>", lambda event: attendance_window.destroy())
        
        # Fetch and display all attendance records
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT employee_id, date, clock_in, clock_out, hours_worked, overtime FROM attendance ORDER BY date DESC""")
        records = cursor.fetchall()
        conn.close()

        # Add alternating row colors (white and light grey)
        for index, record in enumerate(records):
            if index % 2 == 0:
                tree.insert("", "end", values=record, tags=("evenrow",))
            else:
                tree.insert("", "end", values=record, tags=("oddrow",))
        
        # Configure tag styles for alternating rows
        style.configure("evenrow", background="#f9f9f9")
        style.configure("oddrow", background="#ffffff")

        # Add vertical scrollbar for the table
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        # Pack Treeview and Scrollbar side by side
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")



    def show_all_registered_users(self):
        # Create a new window for viewing registered users
        users_window = ctk.CTkToplevel(self)
        users_window.title("All Registered Users")
        users_window.geometry(self.center_window(850, 400))
        users_window.grab_set()  # Prevent interaction with the main window while this window is open
        users_window.attributes('-topmost', True)  # Ensure it stays on top initially
        
        # Frame to hold the Treeview and Scrollbar together
        frame = ctk.CTkFrame(users_window)
        frame.pack(fill="both", expand=True)

        # Create a style for the Treeview widget
        style = ttk.Style()
        style.theme_use("default")  # Use default theme to customize
        style.configure("Treeview", 
                    background="#2D2F33",  # Dark background for rows
                    foreground="white",   # White text
                    rowheight=30,         # Height of rows
                    fieldbackground="#2D2F33",  # Background of fields
                    font=("Arial", 10))   # Font and size for text
        style.configure("Treeview.Heading", 
                    background="#0A84FF",  # Blue for header background
                    foreground="white",   # White header text
                    font=("Arial Bold", 10))  # Bold font for headers
        style.map("Treeview", background=[("selected", "#1C66CC")])  # Highlight color for selected rows
    
        # Customizing the scrollbar style
        style.configure("Vertical.TScrollbar", 
                    gripcount=0, 
                    background="#2D2F33",  # Dark background for the scrollbar
                    troughcolor="#3C3F44",  # Background color of the scrollbar track
                    thumbcolor="#0A84FF",  # Blue thumb color
                    buttoncolor="#2D2F33",  # Button color
                    arrowcolor="#FFFFFF")   # White arrows

        # Create a Treeview widget
        columns = ("id", "username", "full_name", "phone_number", "email")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15, style="Treeview")

        # Define headings and column widths
        tree.heading("id", text="Employee ID")
        tree.heading("username", text="Username")
        tree.heading("full_name", text="Full Name")
        tree.heading("phone_number", text="Phone Number")
        tree.heading("email", text="Email")

        tree.column("id", width=80, anchor="center")
        tree.column("username", width=150, anchor="center")
        tree.column("full_name", width=150, anchor="center")
        tree.column("phone_number", width=150, anchor="center")
        tree.column("email", width=200, anchor="center")

        # Add Escape key binding to close the window
        users_window.bind("<Escape>", lambda event: users_window.destroy())
        
        # Fetch and display all registered users
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT employee_id, username, full_name, phone_number, email FROM employees ORDER BY employee_id""")
        users = cursor.fetchall()
        conn.close()

        # Add alternating row colors (white and light grey)
        for index, user in enumerate(users):
            if index % 2 == 0:
                tree.insert("", "end", values=user, tags=("evenrow",))
            else:
                tree.insert("", "end", values=user, tags=("oddrow",))

        # Configure tag styles for alternating rows
        style.configure("evenrow", background="#f9f9f9")
        style.configure("oddrow", background="#ffffff")

        # Add vertical scrollbar for the table
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        # Pack Treeview and Scrollbar side by side
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")



    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height / 2 - height / 2)
        position_right = int(screen_width / 2 - width / 2)
        return f'{width}x{height}+{position_right}+{position_top}' 
    

if __name__ == "__main__":
    app = TimesheetApp()
    app.mainloop()
