import tkinter as tk
import random
import math
from utils.helpers import clear_screen  # Import de la fonction clear_screen

def start_visual_test(master, username, grid_configs, finish_callback):
    current_grid = 0
    user_responses = []

    def run_test():
        nonlocal current_grid
        clear_screen(master)
        if current_grid < len(grid_configs):
            # Obtenir la configuration pour la grille courante
            grid_config = grid_configs[current_grid]
            difficulty = grid_config["difficulty"]
            quadrants = grid_config["quadrants"]
            num_distractions = grid_config["num_distractions"]

            quadrant_configs = []
            for i in range(4):
                quadrant_configs.append({
                    'num_targets': quadrants[f'quadrant_{i+1}'],
                    'num_distractions': num_distractions
                })

            show_countdown(master, 3, lambda: SingleGridTest(master, quadrant_configs, finish_grid))
            current_grid += 1
        else:
            # Pass all necessary parameters to finish_callback
            finish_callback(master, username, grid_configs, user_responses)

    def finish_grid():
        show_response_screen()

    def show_response_screen():
        clear_screen(master)
        response_frame = tk.Frame(master)
        response_frame.pack()

        response_entries = []

        tk.Label(response_frame, text="Indiquez le nombre de cibles que vous avez vues dans chaque quadrant :", font=("Helvetica", 14)).pack(pady=10)

        for i in range(4):
            frame = tk.Frame(response_frame)
            frame.pack(pady=5)
            tk.Label(frame, text=f"Quadrant {i + 1} :", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)
            entry = tk.Entry(frame)
            entry.pack(side=tk.LEFT, padx=5)
            response_entries.append(entry)

        # Function to handle automatic focus movement
        def move_focus(event, current_entry_index):
            value = response_entries[current_entry_index].get()
            if value.isdigit() and current_entry_index < len(response_entries) - 1:
                response_entries[current_entry_index + 1].focus_set()

        # Bind the focus movement for each entry field
        for index, entry in enumerate(response_entries):
            entry.bind('<KeyRelease>', lambda event, idx=index: move_focus(event, idx))

        # Set the focus on the first entry field initially
        response_entries[0].focus_set()

        def validate_responses():
            nonlocal user_responses
            responses = []
            for entry in response_entries:
                value = entry.get()
                if value.isdigit():
                    responses.append(int(value))
                else:
                    responses.append(0)
            user_responses.append(responses)
            run_test()

        validate_button = tk.Button(response_frame, text="Valider", command=validate_responses)
        validate_button.pack(pady=20)

        master.unbind('<Return>')
        master.bind('<Return>', lambda event: validate_responses())

    run_test()

def generate_target_distribution(num_grids, num_targets_per_quadrant):
    grid_configs = [[{'num_targets': 0} for _ in range(4)] for _ in range(num_grids)]
    
    for quadrant_index in range(4):
        targets_distribution = distribute_targets(num_targets_per_quadrant, num_grids)
        for grid_index in range(num_grids):
            grid_configs[grid_index][quadrant_index]['num_targets'] = targets_distribution[grid_index]

    return grid_configs

def distribute_targets(total_targets, num_grids):
    targets = [0] * num_grids

    for _ in range(total_targets):
        grid_index = random.randint(0, num_grids - 1)
        targets[grid_index] += 1

    return targets

def show_countdown(master, seconds, callback):
    countdown_label = tk.Label(master, font=("Helvetica", 48), fg="red")
    countdown_label.pack()

    def update_countdown(sec):
        if sec > 0:
            countdown_label.config(text=str(sec))
            master.after(1000, update_countdown, sec - 1)
        else:
            countdown_label.pack_forget()
            callback()

    update_countdown(seconds)

class SingleGridTest:
    def __init__(self, master, quadrants_config, callback):
        self.master = master
        self.quadrants_config = quadrants_config
        self.callback = callback
        self.targets = []
        self.distractions = []

        self.canvas = tk.Canvas(master, width=master.winfo_screenwidth(), height=master.winfo_screenheight(), bg='white')
        self.canvas.pack()

        self.draw_quadrants()
        self.generate_objects()

        self.master.after(5000, self.finish_test)

    def draw_quadrants(self):
        self.width = self.canvas.winfo_screenwidth()
        self.height = self.canvas.winfo_screenheight()

        self.canvas.create_line(self.width // 2, 0, self.width // 2, self.height, fill="gray", width=1)
        self.canvas.create_line(0, self.height // 2, self.width, self.height // 2, fill="gray", width=1)

        self.quadrant_bounds = [
            (0, 0, self.width // 2, self.height // 2),
            (self.width // 2, 0, self.width, self.height // 2),
            (0, self.height // 2, self.width // 2, self.height),
            (self.width // 2, self.height // 2, self.width, self.height)
        ]

    def generate_objects(self):
        for i, (x_min, y_min, x_max, y_max) in enumerate(self.quadrant_bounds):
            config = self.quadrants_config[i]
            num_targets = config['num_targets']
            num_distractions = config['num_distractions']

            for _ in range(num_targets):
                self.place_circle(x_min, y_min, x_max, y_max, radius=10, fill_color='red', outline_color='red', target=True)

            for _ in range(num_distractions):
                self.place_circle(x_min, y_min, x_max, y_max, radius=15, fill_color='blue', outline_color='blue', target=False)

    def place_circle(self, x_min, y_min, x_max, y_max, radius, fill_color, outline_color, target):
        max_attempts = 100
        attempts = 0

        while attempts < max_attempts:
            x = random.randint(x_min + radius + 10, x_max - radius - 10)
            y = random.randint(y_min + radius + 10, y_max - radius - 10)

            if self.is_position_valid(x, y, radius):
                circle = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                                 fill=fill_color, outline=outline_color)
                if target:
                    self.targets.append(circle)
                else:
                    self.distractions.append(circle)
                break

            attempts += 1

    def is_position_valid(self, x, y, radius):
        for item in self.targets + self.distractions:
            existing_coords = self.canvas.coords(item)
            existing_x = (existing_coords[0] + existing_coords[2]) / 2
            existing_y = (existing_coords[1] + existing_coords[3]) / 2
            existing_radius = (existing_coords[2] - existing_coords[0]) / 2

            distance = math.sqrt((x - existing_x) ** 2 + (y - existing_y) ** 2)
            if distance < (radius + existing_radius + 10):
                return False

        return True

    def finish_test(self):
        self.canvas.pack_forget()
        self.callback()

def finish_callback(master, username, grid_configs, user_responses):
    print(f"Test finished for {username}.")
    print(f"User Responses: {user_responses}")
    master.quit()
