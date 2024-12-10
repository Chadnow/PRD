import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

class PerformanceAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Analyse de Performance")
        self.data = None

        # Dictionnaire de traduction des métriques
        self.metric_translations = {
            'ErreurQ1': "Erreur Q1",
            'ErreurQ2': "Erreur Q2",
            'ErreurQ3': "Erreur Q3",
            'ErreurQ4': "Erreur Q4",
            'ErreurMoyenne': "Erreur Moyenne",
            'Number_of_saccades': "Nombre de saccades",
            'Number_of_whole_fixations': "Nombre de fixations",
            'Average_duration_of_whole_fixations': "Durée moyenne des fixations (ms)",
            'Average_peak_velocity_of_saccades': "Vitesse de pointe moyenne des saccades",
            'Average_amplitude_of_saccades': "Amplitude moyenne des saccades",
            'Time_to_first_saccade': "Temps jusqu'à la première saccade"
        }

        # Traduction des sessions
        self.session_translations = {
            'Pretest': 'Prétest',
            'Posttest': 'Posttest',
            'Retention': 'Rétention'
        }

        # Boutons de l'interface
        self.load_button = tk.Button(root, text="Charger un fichier CSV", command=self.load_file)
        self.load_button.pack(pady=10)

        self.plot_avg_error_button = tk.Button(
            root, text="Graphique : Comparaison Erreur Moyenne", command=self.plot_average_error_graph
        )
        self.plot_avg_error_button.pack(pady=10)

        # Graphique du nombre de saccades
        self.plot_saccades_button = tk.Button(
            root, text="Graphique : Nombre moyen de saccades", 
            command=lambda: self.plot_metric_graph('Number_of_saccades', 
                                                   "Comparaison du nombre moyen de saccades", 
                                                   "Nombre moyen de saccades")
        )
        self.plot_saccades_button.pack(pady=10)

        # Graphique du nombre moyen de fixations
        self.plot_fixations_button = tk.Button(
            root, text="Graphique : Nombre moyen de fixations", 
            command=lambda: self.plot_metric_graph('Number_of_whole_fixations', 
                                                   "Comparaison du nombre moyen de fixations", 
                                                   "Nombre moyen de fixations")
        )
        self.plot_fixations_button.pack(pady=10)

        # Graphique de la durée moyenne des fixations
        self.plot_fix_dur_button = tk.Button(
            root, text="Graphique : Durée moyenne des fixations", 
            command=lambda: self.plot_metric_graph('Average_duration_of_whole_fixations', 
                                                   "Comparaison de la durée moyenne des fixations", 
                                                   "Durée moyenne (ms)")
        )
        self.plot_fix_dur_button.pack(pady=10)

        # Graphique du nombre de fixations par minute (supposant 1 essai = 1 minute)
        self.plot_fix_per_min_button = tk.Button(
            root, text="Graphique : Nombre moyen de fixations par minute", 
            command=self.plot_fixations_per_minute
        )
        self.plot_fix_per_min_button.pack(pady=10)

        self.plot_correlation_button = tk.Button(
            root, text="Matrice de corrélation (métriques sélectionnées)", command=self.plot_correlation_heatmap
        )
        self.plot_correlation_button.pack(pady=10)

    def translate_metric(self, metric):
        return self.metric_translations.get(metric, metric)

    def translate_session(self, session_list):
        return [self.session_translations.get(s, s) for s in session_list]

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Fichiers CSV", "*.csv")])
        if not file_path:
            return
        try:
            self.data = pd.read_csv(file_path, sep=';', decimal=',', na_values=['', 'NaN', 'nan'])
            messagebox.showinfo("Succès", "Fichier chargé avec succès!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement du fichier : {e}")

    def plot_average_error_graph(self):
        """Afficher un graphique en barres avec barres d'erreurs pour la moyenne des erreurs ((Q1+Q2+Q3+Q4))."""
        if self.data is None:
            messagebox.showerror("Erreur", "Aucune donnée chargée!")
            return

        required_cols = ['ErreurQ1', 'ErreurQ2', 'ErreurQ3', 'ErreurQ4']
        for col in required_cols:
            if col not in self.data.columns:
                messagebox.showerror("Erreur", f"La colonne '{col}' est introuvable.")
                return

        if 'Session' not in self.data.columns or 'Groupe' not in self.data.columns:
            messagebox.showerror("Erreur", "Les colonnes 'Session' et 'Groupe' sont introuvables.")
            return

        try:
            self.data['ErreurMoyenne'] = (self.data['ErreurQ1'] + self.data['ErreurQ2'] + self.data['ErreurQ3'] + self.data['ErreurQ4'])

            session_order = ['Pretest', 'Posttest', 'Retention']
            unique_sessions = list(self.data['Session'].unique())
            actual_sessions = [s for s in session_order if s in unique_sessions]
            if not actual_sessions:
                actual_sessions = unique_sessions

            self.data['Session'] = pd.Categorical(self.data['Session'], categories=actual_sessions, ordered=True)

            grouped = self.data.groupby(['Session', 'Groupe'], observed=False)['ErreurMoyenne']
            means = grouped.mean().unstack()
            errors = grouped.sem().unstack()

            if means.empty:
                messagebox.showerror("Erreur", "Aucune donnée pour tracer le graphique.")
                return

            translated_sessions = self.translate_session(actual_sessions)

            ax = means.plot(
                kind='bar', yerr=errors, figsize=(10, 6), capsize=4, alpha=0.8, error_kw=dict(ecolor='black', capsize=5)
            )
            ax.set_title("Comparaison de l'erreur moyenne par groupe (avec barres d'erreur)")
            ax.set_xlabel("Sessions")
            ax.set_ylabel("Erreur moyenne")
            ax.set_xticks(range(len(translated_sessions)))
            ax.set_xticklabels(translated_sessions, rotation=0)
            ax.legend(title="Groupe")  # Pas de changement ici
            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du graphique : {e}")

    def plot_metric_graph(self, metric_name, title, ylabel):
        """Tracer un barplot (moyenne + SEM) pour une métrique donnée, par Session et par Groupe."""
        if self.data is None:
            messagebox.showerror("Erreur", "Aucune donnée chargée!")
            return

        if metric_name not in self.data.columns:
            messagebox.showerror("Erreur", f"La colonne '{metric_name}' est introuvable.")
            return

        if 'Session' not in self.data.columns or 'Groupe' not in self.data.columns:
            messagebox.showerror("Erreur", "Les colonnes 'Session' et 'Groupe' sont introuvables.")
            return

        try:
            unique_sessions = list(self.data['Session'].unique())
            session_order = ['Pretest', 'Posttest', 'Retention']
            actual_sessions = [s for s in session_order if s in unique_sessions]
            if not actual_sessions:
                actual_sessions = unique_sessions

            self.data['Session'] = pd.Categorical(self.data['Session'], categories=actual_sessions, ordered=True)

            grouped = self.data.groupby(['Session', 'Groupe'], observed=False)[metric_name]
            means = grouped.mean().unstack()
            errors = grouped.sem().unstack()

            if means.empty:
                messagebox.showerror("Erreur", "Aucune donnée pour tracer le graphique.")
                return

            translated_sessions = self.translate_session(actual_sessions)

            ax = means.plot(
                kind='bar', yerr=errors, figsize=(10, 6), capsize=4, alpha=0.8, error_kw=dict(ecolor='black', capsize=5)
            )
            ax.set_title(title)
            ax.set_xlabel("Sessions")
            ax.set_ylabel(ylabel)
            ax.set_xticks(range(len(translated_sessions)))
            ax.set_xticklabels(translated_sessions, rotation=0)

            # Déplacement de la légende en haut à droite pour la durée moyenne des fixations et le nombre moyen de fixations
            if metric_name in ['Average_duration_of_whole_fixations', 'Number_of_whole_fixations']:
                ax.legend(title="Groupe", loc='upper right')
            else:
                ax.legend(title="Groupe")

            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du graphique '{metric_name}' : {e}")

    def plot_fixations_per_minute(self):
        """Tracer un barplot pour le nombre de fixations par minute (si on considère 1 essai = 1 minute)."""
        if self.data is None:
            messagebox.showerror("Erreur", "Aucune donnée chargée!")
            return

        metric_name = 'Number_of_whole_fixations'
        title = "Comparaison du nombre moyen de fixations par minute"
        ylabel = "Nombre moyen de fixations/minute"

        if metric_name not in self.data.columns:
            messagebox.showerror("Erreur", f"La colonne '{metric_name}' est introuvable.")
            return

        if 'Session' not in self.data.columns or 'Groupe' not in self.data.columns:
            messagebox.showerror("Erreur", "Les colonnes 'Session' et 'Groupe' sont introuvables.")
            return

        try:
            unique_sessions = list(self.data['Session'].unique())
            session_order = ['Pretest', 'Posttest', 'Retention']
            actual_sessions = [s for s in session_order if s in unique_sessions]
            if not actual_sessions:
                actual_sessions = unique_sessions

            self.data['Session'] = pd.Categorical(self.data['Session'], categories=actual_sessions, ordered=True)

            grouped = self.data.groupby(['Session', 'Groupe'], observed=False)[metric_name]
            means = grouped.mean().unstack()
            errors = grouped.sem().unstack()

            if means.empty:
                messagebox.showerror("Erreur", "Aucune donnée pour tracer le graphique.")
                return

            translated_sessions = self.translate_session(actual_sessions)

            ax = means.plot(
                kind='bar', yerr=errors, figsize=(10, 6), capsize=4, alpha=0.8, error_kw=dict(ecolor='black', capsize=5)
            )
            ax.set_title(title)
            ax.set_xlabel("Sessions")
            ax.set_ylabel(ylabel)
            ax.set_xticks(range(len(translated_sessions)))
            ax.set_xticklabels(translated_sessions, rotation=0)
            # Ici, on pourrait aussi mettre la légende en haut à droite si on le souhaite,
            # mais ce n'est pas demandé. On la laisse par défaut.
            ax.legend(title="Groupe")

            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du graphique fixations/minute : {e}")

    def plot_correlation_heatmap(self):
        """Afficher une matrice de corrélation des métriques sélectionnées."""
        if self.data is None:
            messagebox.showerror("Erreur", "Aucune donnée chargée!")
            return

        columns_to_keep = [
            'ErreurQ1', 'ErreurQ2', 'ErreurQ3', 'ErreurQ4',
            'Average_duration_of_whole_fixations',
            'Number_of_whole_fixations',
            'Number_of_saccades',
            'Average_peak_velocity_of_saccades',
            'Average_amplitude_of_saccades',
            'Time_to_first_saccade'
        ]
        existing_columns = [col for col in columns_to_keep if col in self.data.columns]
        if len(existing_columns) == 0:
            messagebox.showerror("Erreur", "Aucune métrique sélectionnée n'est présente.")
            return

        try:
            filtered_data = self.data[existing_columns]
            corr = filtered_data.corr()

            # On va renommer les colonnes pour l'affichage dans le heatmap
            col_map = {col: self.translate_metric(col) for col in existing_columns}
            corr_renamed = corr.rename(columns=col_map, index=col_map)

            plt.figure(figsize=(12, 8))
            sns.heatmap(corr_renamed, annot=True, fmt=".2f", cmap="coolwarm", square=True, cbar=True)
            plt.title("Matrice de corrélation (métriques sélectionnées)")
            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la corrélation : {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PerformanceAnalyzer(root)
    root.mainloop()
