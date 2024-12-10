import json
import pandas as pd
from tkinter import filedialog, Tk, messagebox, simpledialog

class JsonToCsvBatchProcessor:
    def __init__(self):
        self.data_rows = []

    def select_files(self):
        Tk().withdraw()  # Masquer la fenêtre principale
        file_paths = filedialog.askopenfilenames(
            title="Selectionner les fichiers JSON",
            filetypes=[("JSON files", "*.json")]
        )
        if file_paths:
            self.process_files(file_paths)
        else:
            messagebox.showinfo("Information", "Aucun fichier selectionne.")

    def process_files(self, file_paths):
        self.data_rows = []  # Reinitialiser les donnees

        for file_path in file_paths:
            # Extraire le nom du fichier sans extension
            subject_name = file_path.split("/")[-1].replace(".json", "")

            # Demander a l'utilisateur de specifier le groupe pour chaque fichier
            group = simpledialog.askstring(
                "Groupe du fichier",
                f"Specifiez le groupe pour le fichier suivant :\n{file_path}\n(Entrez 'Controle' ou 'Entraine')"
            )
            if group not in ["Controle", "Entraine"]:
                messagebox.showwarning("Attention", f"Groupe invalide pour le fichier : {file_path}. Il sera ignore.")
                continue

            with open(file_path, 'r') as file:
                data = json.load(file)
                for session in data['sessions']:
                    session_id = session['session_id']
                    session_name = {
                        1: "Pretest",
                        2: "Posttest",
                        3: "Retention"
                    }.get(session_id, f"Session{session_id}")
                    
                    timestamp = session.get("timestamp", "Non specifie")
                    
                    for grid in session['grids']:
                        trial = grid['grid_id']
                        difficulty = grid['difficulty']
                        errors = grid['error_per_quadrant']
                        
                        self.data_rows.append({
                            "Sujet": subject_name,
                            "Session": session_name,
                            "Trial": trial,
                            "ErreurQ1": errors[0],
                            "ErreurQ2": errors[1],
                            "ErreurQ3": errors[2],
                            "ErreurQ4": errors[3],
                            "Difficulte": difficulty,
                            "Groupe": group,
                            "DateHeure": timestamp
                        })

        if self.data_rows:
            self.save_csv()
        else:
            messagebox.showinfo("Information", "Aucune donnee traitee.")

    def save_csv(self):
        Tk().withdraw()
        save_path = filedialog.asksaveasfilename(
            title="Sauvegarder le fichier CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if save_path:
            try:
                csv_df = pd.DataFrame(self.data_rows)
                csv_df.to_csv(save_path, index=False)
                messagebox.showinfo("Succes", f"Fichier CSV sauvegarde avec succes : {save_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {e}")
        else:
            messagebox.showinfo("Information", "Sauvegarde annulee.")

# Exemple d'utilisation
if __name__ == "__main__":
    processor = JsonToCsvBatchProcessor()
    processor.select_files()
