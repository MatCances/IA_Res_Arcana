# IA_Res_Arcana - Project Overview

**Date:** 2026-04-07
**Type:** Jeu de société (Python)
**Architecture:** Monolithe en couches

## Résumé

IA_Res_Arcana est une implémentation en Python du jeu de société **Res Arcana**. Le projet a deux objectifs :
1. Fournir un **moteur de jeu complet** fidèle aux règles (draft, collecte, actions, victoire)
2. Développer une **IA** capable d'apprendre à jouer en s'affrontant elle-même

## Classification du projet

- **Type de dépôt :** Monolithe
- **Type de projet :** Jeu (Python pur, pas de moteur graphique)
- **Langage principal :** Python 3.x
- **Architecture :** Couches distinctes (engine / cards / players / cli / utils)

## Stack technique

| Composant        | Technologie              |
|------------------|--------------------------|
| Langage          | Python 3.x               |
| Tests            | pytest                   |
| CI/CD            | GitHub Actions           |
| IA actuelle      | Random (base à étendre)  |
| Interface        | CLI (terminal)           |

## Fonctionnalités clés

1. **Phase de draft** — 2 tours de 4 cartes, chaque joueur choisit 1 carte et passe les autres
2. **Phase de collecte** — collecte fixe des cartes + récupération des ressources stockées
3. **Phase d'actions** — jouer artefacts, activer pouvoirs, acheter monuments/lieux de puissance, défausser, passer
4. **Système d'événements** — `dispatch_event` / `on_event` pour les réactions des cartes
5. **Gestion des ressources** — 6 types : LIFE, DEATH, GOLD, CALM, ELAN, PEARL
6. **Vérification de victoire** — premier à 13 points gagne
7. **Joueur humain (CLI)** + **Joueur IA (random pour l'instant)**
8. **Logger configurable** — 5 niveaux de verbosité (0=silencieux → 4=debug complet)
9. **Réductions de coût** — système de réduction applicable sur les cartes
10. **Tests unitaires** — nombreux tests pytest par carte/mécanique

## Points d'architecture importants

- `GameState` a des méthodes `clone()`, `is_terminal()`, `get_winner()` déclarées mais **non implémentées** — requis pour l'IA avancée
- `AIPlayer` utilise actuellement des choix **aléatoires** — c'est la base à remplacer par un vrai algorithme (MCTS, etc.)
- Les cartes héritent toutes de `Card` (base_card.py) et surchargent `collect_base`, `get_abilities`, `score`, `on_event`
- L'`Engine` gère le flux de partie et délègue les décisions aux joueurs via des méthodes `choose_*`

## Structure du dépôt

```
IA_Res_Arcana/
├── main.py                   # Point d'entrée
├── implemented_cards.py      # Script de comptage des cartes implémentées
├── game/
│   ├── engine.py             # Moteur de jeu (phases, setup, victoire)
│   ├── game_state.py         # État global de la partie
│   ├── player.py             # Classe de base joueur
│   ├── human_player.py       # Joueur humain (saisie CLI)
│   ├── ai_player.py          # Joueur IA (random actuellement)
│   ├── action.py             # Actions disponibles
│   ├── ability.py            # Pouvoirs des cartes
│   └── rules.py              # (vide - réservé)
├── cards/
│   ├── base_card.py          # Classe de base Card
│   ├── artifacts.py          # Artefacts
│   ├── mages.py              # Mages
│   ├── monuments.py          # Monuments
│   ├── objects.py            # Objets
│   ├── place_of_power.py     # Lieux de puissance
│   └── scrolls.py            # Parchemins
├── cli/
│   └── display.py            # Affichage de l'état du jeu
├── utils/
│   ├── constant.py           # Enums : Resource, GameEvent, CardType
│   ├── resource_pool.py      # Gestion des ressources d'un joueur
│   └── logger.py             # Logger avec niveaux de verbosité
├── tests/                    # Tests pytest (un fichier par carte/mécanique)
└── docs/                     # Documentation (ce dossier)
```

## Commandes

- **Lancer le jeu :** `python main.py`
- **Voir les cartes implémentées :** `python implemented_cards.py`
- **Lancer les tests :** `pytest tests/`

---

_Généré par BMAD Method `document-project` workflow — 2026-04-07_
