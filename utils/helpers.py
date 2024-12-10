def clear_screen(master):
    for widget in master.winfo_children():
        widget.destroy()
