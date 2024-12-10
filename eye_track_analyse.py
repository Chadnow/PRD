import pandas as pd
import matplotlib.pyplot as plt
from tkinter import filedialog, Tk

class EyeTrackingAnalysis:
    def __init__(self):
        self.data = None

    def load_file(self):
        # Ouvrir une fenêtre pour sélectionner le fichier
        Tk().withdraw()  # Masquer la fenêtre principale de Tkinter
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier TSV",
            filetypes=[("TSV files", "*.tsv")]
        )
        if file_path:
            self.load_data(file_path)

    def load_data(self, file_path):
        try:
            self.data = pd.read_csv(file_path, sep='\t')
            self.clean_data()
            print(f"Données chargées avec succès depuis : {file_path}")
        except Exception as e:
            print(f"Erreur lors du chargement des données : {e}")

    def clean_data(self):
        # Convertir les colonnes numériques au bon format
        for col in ['Average_duration_of_whole_fixations',
                    'Number_of_whole_fixations',
                    'Average_amplitude_of_saccades',
                    'Average_peak_velocity_of_saccades']:
            if col in self.data.columns:
                self.data[col] = self.data[col].replace(',', '.', regex=True).astype(float)

    def analyze_metrics(self):
        if self.data is None:
            print("Veuillez charger un fichier avant d'analyser les métriques.")
            return

        metrics = {
            "Durée Moyenne des Fixations": "Average_duration_of_whole_fixations",
            "Nombre Total de Fixations": "Number_of_whole_fixations",
            "Amplitude Moyenne des Saccades": "Average_amplitude_of_saccades",
            "Vitesse Moyenne de Pointe des Saccades": "Average_peak_velocity_of_saccades",
        }
        
        for metric_name, column in metrics.items():
            if column in self.data.columns:
                self.plot_metric(metric_name, self.data[column])
            else:
                print(f"Métrique '{metric_name}' introuvable dans les données.")

    def plot_metric(self, metric_name, values):
        plt.figure(figsize=(8, 5))
        plt.bar(range(len(values)), values, color="skyblue")
        plt.title(metric_name)
        plt.xlabel("Intervalle")
        plt.ylabel(metric_name)
        plt.tight_layout()
        plt.show()


# Exemple d'utilisation
eye_tracker = EyeTrackingAnalysis()
eye_tracker.load_file()  # Sélection du fichier via une fenêtre de dialogue
eye_tracker.analyze_metrics()
