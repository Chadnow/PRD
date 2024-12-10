# In main.py
import tkinter as tk
from screens.login_screen import VisualScanningTest  # Corrected import

if __name__ == "__main__":
    root = tk.Tk()
    app = VisualScanningTest(root)  # Initialize the login screen
    root.mainloop()
