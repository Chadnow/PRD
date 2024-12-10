import datetime
import json
import os

def save_results(username, difficulty_level=None, num_grids=None, grid_configs=None, user_responses=None):
    """
    Sauvegarde les résultats d'une session dans un fichier JSON.
    
    Args:
        username (str): Nom de l'utilisateur.
        difficulty_level (str, optional): Niveau de difficulté du test.
        num_grids (int, optional): Nombre de grilles dans le test.
        grid_configs (list, optional): Configuration des grilles (cibles et distractions par quadrant).
        user_responses (list, optional): Réponses de l'utilisateur pour chaque grille.

    Returns:
        str: Chemin complet du fichier dans lequel les résultats ont été sauvegardés.
    """
    # Obtenir la date et l'heure actuelles pour l'horodatage
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Nettoyer le nom d'utilisateur pour éviter des caractères invalides dans le nom de fichier
    username_cleaned = ''.join(c for c in username if c.isalnum() or c in ('-', '_'))
    if not username_cleaned:
        username_cleaned = "anonymous"

    # Définir le chemin du fichier de résultats
    results_dir = os.path.expanduser("~/results_visual_scanning")  # Dossier utilisateur (modulable)
    os.makedirs(results_dir, exist_ok=True)  # Crée le dossier s'il n'existe pas
    filename = os.path.join(results_dir, f"results_{username_cleaned}.json")

    # Charger les données existantes si le fichier existe
    if os.path.exists(filename):
        with open(filename, "r") as file:
            results_data = json.load(file)
    else:
        results_data = {"username": username_cleaned, "sessions": []}

    # Déterminer l'ID de la nouvelle session
    session_id = len(results_data["sessions"]) + 1

    # Préparer les données de la nouvelle session
    session_data = {
        "session_id": session_id,
        "timestamp": timestamp,
        "difficulty_level": difficulty_level or "Non spécifié",
        "num_grids": num_grids or len(grid_configs) if grid_configs else 0,
        "grids": []
    }

    # Collecter les données pour chaque grille
    for i, config in enumerate(grid_configs or []):
        # Récupérer les informations sur les quadrants
        quadrants = config.get("quadrants", {})
        grid_data = {
            "grid_id": i + 1,
            "num_targets_quadrant": [quadrants.get(f'quadrant_{j+1}', 0) for j in range(4)],
            "user_responses_quadrant": [],
            "error_per_quadrant": []
        }

        # Ajouter les réponses utilisateur
        if i < len(user_responses or []):
            for response in user_responses[i]:
                try:
                    grid_data["user_responses_quadrant"].append(int(response))
                except (ValueError, TypeError):
                    grid_data["user_responses_quadrant"].append(0)  # Valeur par défaut si non valide
        else:
            grid_data["user_responses_quadrant"] = ["Non disponible"]

        # Calculer les erreurs pour chaque quadrant
        for j in range(4):
            correct_targets = grid_data["num_targets_quadrant"][j]
            user_response = grid_data["user_responses_quadrant"][j] if j < len(grid_data["user_responses_quadrant"]) else 0
            if isinstance(user_response, str) and user_response != "Non disponible":
                try:
                    user_response = int(user_response)
                except ValueError:
                    user_response = 0
            error = abs(correct_targets - user_response)
            grid_data["error_per_quadrant"].append(error)

        # Ajouter les données de la grille à la session
        session_data["grids"].append(grid_data)

    # Calculer les statistiques globales pour la session
    total_correct_responses = 0
    over_estimation = 0
    under_estimation = 0

    for grid in session_data["grids"]:
        for correct, user in zip(grid["num_targets_quadrant"], grid["user_responses_quadrant"]):
            if user == correct:
                total_correct_responses += 1
            elif user > correct:
                over_estimation += 1
            elif user < correct:
                under_estimation += 1

    # Ajouter les statistiques globales aux données de la session
    session_data["total_correct_responses"] = total_correct_responses
    session_data["over_estimation"] = over_estimation
    session_data["under_estimation"] = under_estimation

    # Ajouter la nouvelle session aux résultats
    results_data["sessions"].append(session_data)

    # Sauvegarder les résultats mis à jour dans le fichier JSON
    with open(filename, "w") as file:
        json.dump(results_data, file, indent=4)

    return filename
