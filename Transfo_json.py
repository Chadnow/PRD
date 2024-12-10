import json
from tkinter import filedialog, Tk, messagebox

class JsonDifficultyAdder:
    def __init__(self):
        self.data = None

    def select_file(self):
        # Ouvrir une fenêtre pour sélectionner le fichier JSON
        Tk().withdraw()  # Masquer la fenêtre principale
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier JSON",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            self.load_json(file_path)

    def load_json(self, file_path):
        try:
            with open(file_path, 'r') as file:
                self.data = json.load(file)
            print(f"Fichier chargé avec succès : {file_path}")
            self.add_difficulty()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement du fichier : {e}")

    def add_difficulty(self):
        if not self.data or "sessions" not in self.data:
            messagebox.showerror("Erreur", "Le fichier JSON n'est pas au bon format.")
            return

        for session in self.data["sessions"]:
            grids = session["grids"]

            # Calculer le nombre total de cibles par grille
            total_targets = [sum(grid["num_targets_quadrant"]) for grid in grids]

            # Ordonner les indices des grilles en fonction du nombre de cibles (croissant)
            sorted_indices = sorted(range(len(total_targets)), key=lambda x: total_targets[x])

            # Déterminer les seuils pour les catégories de difficulté
            num_grids = len(grids)
            num_per_difficulty = num_grids // 3

            # Affecter les niveaux de difficulté
            for idx, grid_index in enumerate(sorted_indices):
                if idx < num_per_difficulty:
                    grids[grid_index]["difficulty"] = "Facile"
                elif idx < 2 * num_per_difficulty:
                    grids[grid_index]["difficulty"] = "Moyen"
                else:
                    grids[grid_index]["difficulty"] = "Difficile"

        messagebox.showinfo("Succès", "Les niveaux de difficulté ont été ajoutés.")
        self.save_json()

    def save_json(self):
        # Ouvrir une fenêtre pour sélectionner le répertoire de sauvegarde
        Tk().withdraw()
        save_path = filedialog.asksaveasfilename(
            title="Sauvegarder le fichier JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if save_path:
            try:
                with open(save_path, 'w') as file:
                    json.dump(self.data, file, indent=4)
                messagebox.showinfo("Succès", f"Fichier sauvegardé avec succès : {save_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {e}")

# Exemple d'utilisation
if __name__ == "__main__":
    app = JsonDifficultyAdder()
    app.select_file()
