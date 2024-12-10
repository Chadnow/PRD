import tkinter as tk
from logic.grid_logic import SingleGridTest
from utils.helpers import clear_screen
from utils.file_operations import save_results
from screens.finish_screen import finish_test  # Correction de l'importation de la fonction finish_test

class GridTestScreen:
    def __init__(self, master, username, grid_configs):
        """
        Initialize the GridTestScreen with the master window, username, and grid configurations.
        
        Args:
            master: The Tkinter root or window.
            username: The username of the participant.
            grid_configs: List of tuples containing difficulty, num_targets, and num_distractions.
        """
        self.master = master
        self.username = username
        self.grid_configs = grid_configs  # List of tuples with configuration for each grid
        self.current_grid = 0
        self.user_responses = []
        self.start_test()

    def start_test(self):
        """
        Clears the screen and starts the first grid test.
        """
        clear_screen(self.master)
        self.run_test()

    def run_test(self):
        """
        Runs a test for the current grid. If all grids are completed, finishes the test.
        """
        if self.current_grid < len(self.grid_configs):
            # Get the configuration for the current grid
            difficulty, num_targets, num_distractions = self.grid_configs[self.current_grid]

            # Generate the target distribution for the current grid
            quadrant_configs = generate_target_distribution(1, num_targets)[0]
            for quadrant in quadrant_configs:
                quadrant['num_distractions'] = num_distractions

            # Pass the quadrant configuration to the SingleGridTest
            self.test = SingleGridTest(self.master, quadrant_configs, self.finish_grid)
            self.current_grid += 1
        else:
            self.finish_test()

    def finish_grid(self):
        """
        Callback function called after each grid is completed. Collects user responses and proceeds to the next grid.
        """
        self.collect_user_responses()
        self.run_test()

    def collect_user_responses(self):
        """
        Collects the user's responses for the current grid and appends them to the user_responses list.
        """
        clear_screen(self.master)
        response_frame = tk.Frame(self.master)
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

        def validate_responses():
            responses = []
            for entry in response_entries:
                value = entry.get()
                if value.isdigit():
                    responses.append(int(value))
                else:
                    responses.append(0)  # Default to 0 if the input is invalid or empty
            self.user_responses.append(responses)
            response_frame.pack_forget()  # Hide the response frame before continuing
            self.run_test()

        validate_button = tk.Button(response_frame, text="Valider", command=validate_responses)
        validate_button.pack(pady=20)

        # Supprimez tout ancien bind avant d'ajouter un nouveau pour éviter les erreurs
        self.master.unbind('<Return>')
        self.master.bind('<Return>', lambda event: validate_responses())

    def finish_test(self):
        """
        Called when all grids are completed. Saves results and displays the FinishScreen.
        """
        # Appeler la fonction finish_test du module finish_screen
        finish_test(self.master, self.username, "Mixte", len(self.grid_configs), self.grid_configs, self.user_responses)

