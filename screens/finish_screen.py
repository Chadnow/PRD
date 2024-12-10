import tkinter as tk
from utils.helpers import clear_screen
from utils.file_operations import save_results

def finish_test(master, username, grid_configs, user_responses):
    """
    Fonction pour afficher les résultats après la fin du test, enregistrer les résultats dans un fichier JSON,
    et permettre à l'utilisateur de naviguer entre les pages des résultats.
    """

    # Sauvegarder les résultats en appelant `save_results`
    filename = save_results(username, difficulty_level=None, num_grids=len(grid_configs),
                            grid_configs=grid_configs, user_responses=user_responses)

    # Variables pour la pagination
    current_page = [0]  # Utiliser une liste pour permettre la modification dans les fonctions internes
    grids_per_page = 4

    def display_page(page):
        clear_screen(master)

        # Afficher un message de remerciement
        message_label = tk.Label(master, text=f"Merci {username}, vous avez terminé le test.", font=("Helvetica", 16))
        message_label.pack(pady=20)

        # Afficher les résultats dans un cadre
        results_frame = tk.Frame(master)
        results_frame.pack()

        start_index = page * grids_per_page
        end_index = min(start_index + grids_per_page, len(grid_configs))

        for i in range(start_index, end_index):
            grid = grid_configs[i]
            difficulty = grid.get('difficulty', 'Inconnu')  # Récupérer la difficulté de la grille

            # Afficher le numéro et la difficulté de la grille
            tk.Label(results_frame, text=f"Grille {i + 1} (Difficulté : {difficulty})", font=("Helvetica", 12, "bold")).pack(pady=5)

            # Afficher les détails par quadrant
            for j in range(4):  # Supposons qu'il y a toujours 4 quadrants
                num_targets = grid.get('quadrants', {}).get(f'quadrant_{j+1}', 0)
                user_response = user_responses[i][j] if i < len(user_responses) and j < len(user_responses[i]) else "Non disponible"
                error = abs(num_targets - (int(user_response) if isinstance(user_response, int) or user_response.isdigit() else 0))

                result_text = (f"  Quadrant {j + 1} : "
                               f"Cibles prévues = {num_targets}, "
                               f"Réponse utilisateur = {user_response}, "
                               f"Erreur = {error}")
                tk.Label(results_frame, text=result_text, font=("Helvetica", 12)).pack(pady=2)

        # Afficher un message sur l'enregistrement du fichier
        file_label = tk.Label(master, text=f"Vos résultats ont été enregistrés dans le fichier : {filename}", font=("Helvetica", 12))
        file_label.pack(pady=10)

        # Ajouter les boutons de navigation
        nav_frame = tk.Frame(master)
        nav_frame.pack(pady=10)

        if page > 0:
            prev_button = tk.Button(nav_frame, text="Page précédente", command=lambda: display_page(page - 1))
            prev_button.pack(side=tk.LEFT, padx=5)

        if end_index < len(grid_configs):
            next_button = tk.Button(nav_frame, text="Page suivante", command=lambda: display_page(page + 1))
            next_button.pack(side=tk.LEFT, padx=5)

        # Bouton pour quitter l'application
        quit_button = tk.Button(master, text="Quitter", command=master.quit, font=("Helvetica", 12), bg="#d9534f", fg="white", padx=10, pady=5)
        quit_button.pack(pady=20)

    # Afficher la première page
    display_page(current_page[0])
