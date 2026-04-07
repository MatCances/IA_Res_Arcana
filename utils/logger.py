import json


class Logger:
    """Gère les logs d'une partie de Res Arcana.

    Enregistre les événements sous forme structurée (pour l'IA)
    et peut les exporter en texte lisible ou en JSON.

    Paramètres :
        level (int) : verbosité des événements enregistrés (0-4)
            0 : rien enregistré
            1 : actions principales — cartes jouées, pouvoirs activés, achats, fin de manche
            2 : décisions — choix effectués par les joueurs
            3 : état du jeu — ressources et board à chaque tour
            4 : debug complet
        silent (bool) : si True, rien n'est affiché dans le terminal
            False (défaut) : affiche dans le terminal ce qui est enregistré
            True           : enregistre sans rien afficher (utile pour l'IA)

    Exemples :
        # Humain qui joue — affichage terminal + log léger
        Logger(level=1, silent=False)

        # IA — log détaillé dans un fichier, terminal silencieux
        Logger(level=4, silent=True)

        # Entraînement pur — rien du tout
        Logger(level=0, silent=True)
    """

    def __init__(self, level=0, silent=False):
        self.level = level
        self.silent = silent
        self.events = []
        self.current_turn = 0

    # ------------------------------------------------------------------
    # Enregistrement interne
    # ------------------------------------------------------------------

    def _record(self, min_level, category, message, data=None):
        if self.level < min_level:
            return
        event = {
            "turn": self.current_turn,
            "category": category,
            "message": message,
            "data": data or {},
        }
        self.events.append(event)
        if not self.silent:
            print(self._to_text(event))

    @staticmethod
    def _to_text(event):
        tag = event["category"].upper()
        return f"[Tour {event['turn']}][{tag}] {event['message']}"

    # ------------------------------------------------------------------
    # API publique — méthodes de log
    # ------------------------------------------------------------------

    def set_turn(self, turn):
        """Met à jour le numéro de tour courant."""
        self.current_turn = turn

    def action(self, message, data=None):
        """Niveau 1 — action principale (carte jouée, pouvoir activé, achat…)."""
        self._record(1, "action", message, data)

    def decision(self, message, data=None):
        """Niveau 2 — décision d'un joueur (ressource choisie, carte choisie…)."""
        self._record(2, "decision", message, data)

    def state(self, message, data=None):
        """Niveau 3 — snapshot de l'état du jeu."""
        self._record(3, "state", message, data)

    def debug(self, message, data=None):
        """Niveau 4 — debug complet."""
        self._record(4, "debug", message, data)

    # ------------------------------------------------------------------
    # Sauvegarde
    # ------------------------------------------------------------------

    def save(self, filepath, fmt="text"):
        """Sauvegarde les logs.

        Args:
            filepath (str): chemin de base (sans extension)
            fmt (str): "text" → .log  |  "json" → .json  |  "both" → les deux
        """
        if fmt in ("text", "both"):
            with open(filepath + ".log", "w", encoding="utf-8") as f:
                for event in self.events:
                    f.write(self._to_text(event) + "\n")

        if fmt in ("json", "both"):
            with open(filepath + ".json", "w", encoding="utf-8") as f:
                json.dump(self.events, f, ensure_ascii=False, indent=2)

    def reset(self):
        """Vide l'historique (entre deux parties, garde level et silent)."""
        self.events = []
        self.current_turn = 0
