import random

def generate_quadrant_targets(total_targets, num_grids, deviation_limit):
    """
    Répartit les cibles de manière pseudo-aléatoire pour un quadrant sur un nombre donné de grilles.

    Args:
        total_targets (int): Nombre total de cibles à répartir.
        num_grids (int): Nombre total de grilles.
        deviation_limit (int): Limite de déviation autour de la moyenne pour chaque grille.

    Returns:
        list: Liste des cibles réparties sur chaque grille.
    """
    average = total_targets // num_grids
    quadrant_targets = [0] * num_grids
    remaining_targets = total_targets

    for i in range(num_grids - 1):
        min_targets = max(0, average - deviation_limit)
        max_targets = min(remaining_targets, average + deviation_limit)
        assigned = random.randint(min_targets, max_targets)
        quadrant_targets[i] = assigned
        remaining_targets -= assigned

    # Assigner les cibles restantes à la dernière grille
    quadrant_targets[-1] = remaining_targets

    return quadrant_targets


def generate_grids_for_difficulty(num_grids, num_targets_per_quadrant, deviation_limit, num_distractions):
    """
    Génère une liste de grilles pour un niveau de difficulté donné.

    Args:
        num_grids (int): Nombre de grilles à générer.
        num_targets_per_quadrant (int): Nombre moyen de cibles par quadrant.
        deviation_limit (int): Limite de déviation autour de la moyenne pour chaque grille.
        num_distractions (int): Nombre de distractions dans chaque grille.

    Returns:
        list: Liste des grilles avec leur configuration.
    """
    grids = []

    for _ in range(num_grids):
        grid = {
            "quadrants": {
                f"quadrant_{i+1}": generate_quadrant_targets(
                    num_targets_per_quadrant * num_grids,
                    num_grids,
                    deviation_limit
                )[_]
                for i in range(4)
            },
            "num_distractions": num_distractions
        }
        grids.append(grid)

    return grids


def generate_all_grids(settings):
    """
    Génère toutes les grilles en fonction des paramètres de difficulté.

    Args:
        settings (dict): Paramètres contenant les informations sur les niveaux de difficulté,
                         cibles et distractions par grille, et le nombre total de grilles.

    Returns:
        list: Liste complète des grilles.
    """
    num_grids_total = settings["num_grids"]
    grids = []
    num_each = num_grids_total // 3  # Répartition égale par difficulté

    difficulties = {
        "Facile": settings["Facile"],
        "Moyen": settings["Moyen"],
        "Difficile": settings["Difficile"]
    }

    for difficulty, (num_targets, num_distractions) in difficulties.items():
        if difficulty == "Facile":
            deviation_limit = 2
        elif difficulty == "Moyen":
            deviation_limit = 2
        else:  # Difficile
            deviation_limit = 3

        grids.extend(
            generate_grids_for_difficulty(num_each, num_targets, deviation_limit, num_distractions)
        )

    # Mélanger les grilles et ajouter des grilles d'échauffement au début
    random.shuffle(grids)
    warmup_grids = [grid for grid in grids if grid["quadrants"]["quadrant_1"] < 8][:3]  # Exemple de filtre pour échauffement
    remaining_grids = [grid for grid in grids if grid not in warmup_grids]

    return warmup_grids + remaining_grids
