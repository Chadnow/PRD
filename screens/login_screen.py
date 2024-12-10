import tkinter as tk
from screens.config_screen import setup_config_screen  # Import the config screen function

class VisualScanningTest:
    def __init__(self, master):
        self.master = master
        self.master.title("Test de Balayage Visuel")

        # Enable full-screen mode globally
        self.master.attributes('-fullscreen', True)

        self.username = ""  # To store the username
        self.login_screen()

    def clear_screen(self):
        # Clear the current screen (removes all widgets)
        for widget in self.master.winfo_children():
            widget.destroy()

    def login_screen(self):
        # Clear the login screen if necessary
        self.clear_screen()

        # Username input
        self.username_label = tk.Label(self.master, text="Nom d'utilisateur:")
        self.username_label.pack(pady=10)
        self.username_entry = tk.Entry(self.master)
        self.username_entry.pack(pady=10)
        self.username_entry.focus_set()  # Auto-focus on the username entry

        # Login button
        self.login_button = tk.Button(self.master, text="Se connecter", command=self.check_login)
        self.login_button.pack(pady=10)

        # Allow pressing Enter to submit login form
        self.master.bind('<Return>', lambda event: self.check_login())

    def check_login(self):
        # No password check, just store the username
        self.username = self.username_entry.get()  # Store the username
        # After entering the username, transition to the config screen
        setup_config_screen(self.master, self.username)
