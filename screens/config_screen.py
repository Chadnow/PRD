import tkinter as tk
import random
import os
import json
from logic.grid_logic import start_visual_test, SingleGridTest
from screens.finish_screen import finish_test
from utils.helpers import clear_screen

# Nom du fichier de sauvegarde des paramètres
PARAM_FILE = 'config_params.json'

# Paramètres par défaut si le fichier de sauvegarde n'existe pas
default_settings = {
    "Facile": (5, 30),  # Valeurs par défaut (cibles, distracteurs)
    "Moyen": (8, 40),
    "Difficile": (15, 60),
    "num_grids": 9  # Nombre total de grilles (un multiple de 3)
}

# Charger les paramètres de configuration à partir du fichier, s'il existe
def load_settings():
    if os.path.exists(PARAM_FILE):
        with open(PARAM_FILE, 'r') as file:
            return json.load(file)
    return default_settings

settings = load_settings()

def setup_config_screen(master, username):
    clear_screen(master)

    config_frame = tk.Frame(master)
    config_frame.pack(pady=20)

    tk.Label(config_frame, text="Bienvenue!", font=("Helvetica", 16, "bold")).pack(pady=10)
    tk.Label(config_frame, text="Veuillez choisir une option:", font=("Helvetica", 14)).pack(pady=5)

    # Bouton pour démarrer le test
    start_button = tk.Button(config_frame, text="Démarrer le test", command=lambda: start_test(master, username),
                             font=("Helvetica", 12), bg="#4CAF50", fg="white", padx=10, pady=5)
    start_button.pack(pady=10)

    # Bouton pour le tutoriel
    tutorial_button = tk.Button(config_frame, text="Tutoriel", command=lambda: start_tutorial(master),
                                font=("Helvetica", 12), bg="#2196F3", fg="white", padx=10, pady=5)
    tutorial_button.pack(pady=10)

    # Bouton pour les paramètres
    settings_button = tk.Button(config_frame, text="Paramètres", command=lambda: open_settings_window(master),
                                font=("Helvetica", 12), bg="#FFC107", fg="black", padx=10, pady=5)
    settings_button.pack(pady=10)

    master.unbind('<Return>')
    master.bind('<Return>', lambda event: start_test(master, username))

def open_settings_window(master):
    settings_window = tk.Toplevel(master)
    settings_window.title("Paramètres de difficulté")
    settings_window.geometry("400x500")
    settings_window.configure(bg="#f0f0f0")

    def add_difficulty_entries(frame, difficulty, default_targets, default_distractions):
        tk.Label(frame, text=f"Paramètres pour {difficulty}", font=("Helvetica", 14, "bold"), bg="#f0f0f0").pack(pady=5)
        tk.Label(frame, text="Total des cibles par quadrant:", bg="#f0f0f0").pack()
        target_entry = tk.Entry(frame)
        target_entry.insert(0, str(default_targets))
        target_entry.pack()

        tk.Label(frame, text="Total des perturbateurs par quadrant:", bg="#f0f0f0").pack()
        distraction_entry = tk.Entry(frame)
        distraction_entry.insert(0, str(default_distractions))
        distraction_entry.pack()

        return target_entry, distraction_entry

    settings_frame = tk.Frame(settings_window, bg="#f0f0f0")
    settings_frame.pack(pady=10)

    # Entrées pour chaque niveau de difficulté
    easy_targets_entry, easy_distractions_entry = add_difficulty_entries(settings_frame, "Facile", *settings["Facile"])
    medium_targets_entry, medium_distractions_entry = add_difficulty_entries(settings_frame, "Moyen", *settings["Moyen"])
    hard_targets_entry, hard_distractions_entry = add_difficulty_entries(settings_frame, "Difficile", *settings["Difficile"])

    # Entrée pour le nombre de grilles
    tk.Label(settings_frame, text="Nombre total de grilles (un multiple de 3):", font=("Helvetica", 14, "bold"), bg="#f0f0f0").pack(pady=10)
    num_grids_entry = tk.Entry(settings_frame)
    num_grids_entry.insert(0, str(settings["num_grids"]))
    num_grids_entry.pack()

    def save_settings():
        global settings
        settings = {
            "Facile": (int(easy_targets_entry.get()), int(easy_distractions_entry.get())),
            "Moyen": (int(medium_targets_entry.get()), int(medium_distractions_entry.get())),
            "Difficile": (int(hard_targets_entry.get()), int(hard_distractions_entry.get())),
            "num_grids": int(num_grids_entry.get())
        }
        with open(PARAM_FILE, 'w') as file:
            json.dump(settings, file)
        settings_window.destroy()

    save_button = tk.Button(settings_frame, text="Sauvegarder", command=save_settings, font=("Helvetica", 12),
                            bg="#4CAF50", fg="white", padx=10, pady=5)
    save_button.pack(pady=20)

    settings_window.grab_set()

def start_test(master, username):
    clear_screen(master)

    try:
        if settings["num_grids"] % 3 != 0:
            raise ValueError("Le nombre de grilles doit être un multiple de 3.")

        # Générer une matrice contenant les niveaux de difficulté, les cibles et les distracteurs
        grid_configs = []

        # Nombre de grilles pour chaque niveau de difficulté
        num_each = settings["num_grids"] // 3

        # Générer les grilles pour chaque niveau de difficulté
        for difficulty in ["Facile", "Moyen", "Difficile"]:
            num_targets, num_distractions = settings[difficulty]

            # Initialiser le total des cibles pour chaque quadrant
            total_targets_per_quadrant = [num_targets * num_each] * 4

            # Générer les grilles avec une répartition pseudo-aléatoire pour chaque quadrant
            if difficulty == "Facile":
                target_limit = 2
            elif difficulty == "Moyen":
                target_limit = 2
            else:
                target_limit = 3

            quadrant_targets = distribute_targets_across_grids(total_targets_per_quadrant, num_each, target_limit)
            for i in range(num_each):
                grid_configs.append({
                    "difficulty": difficulty,
                    "quadrants": {f"quadrant_{j+1}": quadrant_targets[j][i] for j in range(4)},
                    "num_distractions": num_distractions
                })

        # Mélanger les grilles
        random.shuffle(grid_configs)

        # Réorganiser les grilles pour l'échauffement : 2 faciles et 1 moyenne devant pour que l'utilisateur commence avec des grilles plutot facile
        warmup_grids = []
        for grid in grid_configs:
            if grid["difficulty"] == "Moyen" and len(warmup_grids) < 1:
                warmup_grids.append(grid)
            elif grid["difficulty"] == "Facile" and len(warmup_grids) < 3:
                warmup_grids.append(grid)

        remaining_grids = [grid for grid in grid_configs if grid not in warmup_grids]

        # Les grilles finales commencent par les grilles d'échauffement suivies du reste
        grid_configs = warmup_grids + remaining_grids

        # Démarrer le test visuel avec la configuration des grilles
        start_visual_test(master, username, grid_configs, finish_test)

    except ValueError as e:
        error_label = tk.Label(master, text=f"Erreur : {e}", fg="red", font=("Helvetica", 12))
        error_label.pack()

def distribute_targets_across_grids(total_targets_per_quadrant, num_grids, limit):
    """
    Répartit les cibles à travers les grilles tout en s'assurant que chaque quadrant atteint le total attendu
    et en respectant la déviation limite pour chaque grille.
    """
    quadrant_targets = [[0] * num_grids for _ in range(4)]

    for quadrant_index in range(4):
        remaining_targets = total_targets_per_quadrant[quadrant_index]

        for grid_index in range(num_grids - 1):
            min_targets = max(0, (remaining_targets // (num_grids - grid_index)) - limit)
            max_targets = min(remaining_targets, (remaining_targets // (num_grids - grid_index)) + limit)
            assigned = random.randint(min_targets, max_targets)
            quadrant_targets[quadrant_index][grid_index] = assigned
            remaining_targets -= assigned

        quadrant_targets[quadrant_index][-1] = remaining_targets

    return quadrant_targets



def start_tutorial(master):
    clear_screen(master)

    instructions_frame = tk.Frame(master)
    instructions_frame.pack(pady=20)

    instructions = ("Vous allez avoir 4 cadrants indépendants devant vous.\n"
                    "Votre but est de retenir le nombre de cibles dans chaque cadrant\n"
                    "et les restituer après chaque grille dans l'écran réponse.\n"
                    "Chaque grille dure 5 secondes.\n\n"
                    "Nous allons à présent vous montrer le numéro des cadrants\n"
                    "qui sont numérotés dans l'ordre de lecture.")

    tk.Label(instructions_frame, text=instructions, font=("Helvetica", 14), justify="center").pack(pady=20)

    continue_button = tk.Button(instructions_frame, text="Continuer", command=lambda: show_quadrants_numbered(master),
                                font=("Helvetica", 12), bg="#2196F3", fg="white", padx=10, pady=5)
    continue_button.pack(pady=20)

def show_quadrants_numbered(master):
    clear_screen(master)

    canvas = tk.Canvas(master, width=master.winfo_screenwidth(), height=master.winfo_screenheight(), bg='white')
    canvas.pack()

    width = master.winfo_screenwidth()
    height = master.winfo_screenheight()

    canvas.create_line(width // 2, 0, width // 2, height, fill="gray", width=1)
    canvas.create_line(0, height // 2, width, height // 2, fill="gray", width=1)

    quadrants = [
        (0, 0, width // 2, height // 2, "1"),
        (width // 2, 0, width, height // 2, "2"),
        (0, height // 2, width // 2, height, "3"),
        (width // 2, height // 2, width, height, "4")
    ]

    for x_min, y_min, x_max, y_max, num in quadrants:
        canvas.create_text((x_min + x_max) // 2, (y_min + y_max) // 2, text=num, font=("Helvetica", 48), fill="black")

    tk.Label(master, text="Voici les 4 cadrants dans lesquels vont s'afficher les cibles.", font=("Helvetica", 14)).pack(pady=20)
    tk.Label(master, text="Appuyez sur 'Entrée' pour passer à l'essai.", font=("Helvetica", 12)).pack(pady=10)

    master.unbind('<Return>')
    master.bind('<Return>', lambda event: start_trial_countdown(master))

def start_trial_countdown(master):
    clear_screen(master)

    countdown_label = tk.Label(master, font=("Helvetica", 48), fg="red")
    countdown_label.pack()

    def update_countdown(sec):
        if sec > 0:
            countdown_label.config(text=f"Essai dans {sec}...")
            master.after(1000, update_countdown, sec - 1)
        else:
            countdown_label.pack_forget()
            start_trial(master)

    update_countdown(3)

def start_trial(master):
    clear_screen(master)

    trial_config = [
        {'num_targets': 1, 'num_distractions': 10},
        {'num_targets': 2, 'num_distractions': 10},
        {'num_targets': 0, 'num_distractions': 10},
        {'num_targets': 3, 'num_distractions': 10},
    ]

    SingleGridTest(master, trial_config, lambda: show_trial_response(master, trial_config))

def show_trial_response(master, trial_config):
    clear_screen(master)

    response_frame = tk.Frame(master)
    response_frame.pack(pady=20)

    response_entries = []

    tk.Label(response_frame, text="Indiquez le nombre de cibles que vous avez vues dans chaque quadrant :", font=("Helvetica", 14)).pack(pady=10)

    for i in range(4):
        frame = tk.Frame(response_frame)
        frame.pack(pady=5)
        tk.Label(frame, text=f"Quadrant {i + 1} :", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)
        entry = tk.Entry(frame)
        entry.pack(side=tk.LEFT, padx=5)
        response_entries.append(entry)

    def validate_trial_responses():
        responses = []
        for entry in response_entries:
            value = entry.get()
            if value.isdigit():
                responses.append(int(value))
            else:
                responses.append(0)

        results = []
        for i in range(4):
            correct_value = trial_config[i]['num_targets']
            user_value = responses[i]
            results.append(f"Quadrant {i + 1} : Vous avez répondu {user_value}, il y avait {correct_value} cibles.")

        clear_screen(master)
        results_frame = tk.Frame(master)
        results_frame.pack()

        tk.Label(results_frame, text="Tutoriel terminé, vous êtes prêt à commencer !", font=("Helvetica", 14)).pack(pady=20)
        for result in results:
            tk.Label(results_frame, text=result, font=("Helvetica", 12)).pack(pady=5)

        finish_button = tk.Button(results_frame, text="Suivant", command=lambda: setup_config_screen(master, "Utilisateur"))
        finish_button.pack(pady=20)

    validate_button = tk.Button(response_frame, text="Valider", command=validate_trial_responses)
    validate_button.pack(pady=20)

    master.unbind('<Return>')
    master.bind('<Return>', lambda event: validate_trial_responses())

