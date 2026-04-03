class Logger:
    """Gère les logs d'une partie de Res Arcana.
    
    Permet d'enregistrer et d'afficher les événements d'une partie
    avec un niveau de verbosité configurable.
    
    Niveaux de verbosité :
        0 : silencieux - rien n'est affiché (pour l'entraînement en masse)
        1 : actions principales - cartes jouées, pouvoirs activés, fin de partie
        2 : décisions - tous les choix effectués par les joueurs (choose_*)
        3 : état du jeu - ressources et board de chaque joueur à chaque tour
        4 : debug complet - main, pioche, ressources sur les cartes, événements
    
    Attributes:
        level (int): niveau de verbosité (0-4)
        logs (list[str]): historique des messages enregistrés
    
    Example:
        logger = Logger(level=2)
        engine = Engine(players, logger=logger)
        engine.run()
        logger.save("logs/partie_1.log")
        logger.reset()
    """
    def __init__(self, level=0):
        self.level = level
        self.logs = []  # pour garder un historique en mémoire si besoin
    
    def log(self, message, level=1):
        """Affiche et enregistre un message si le niveau est suffisant."""
        if self.level >= level:
            print(message)
            self.logs.append(message)
    
    def action(self, message):
        """Niveau 1 — actions principales."""
        self.log(f"[ACTION] {message}", level=1)
    
    def decision(self, message):
        """Niveau 2 — décisions des joueurs."""
        self.log(f"[DECISION] {message}", level=2)
    
    def state(self, message):
        """Niveau 3 — état du jeu."""
        self.log(f"[ETAT] {message}", level=3)
    
    def debug(self, message):
        """Niveau 4 — debug complet."""
        self.log(f"[DEBUG] {message}", level=4)

    def save(self, filepath):
        """Sauvegarde les logs dans un fichier."""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(self.logs))
    
    def reset(self):
        """Vide l'historique entre deux parties."""
        self.logs = []