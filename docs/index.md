# IA_Res_Arcana — Index de documentation

**Type :** Monolithe
**Langage principal :** Python 3.x
**Architecture :** Moteur de jeu en couches
**Dernière mise à jour :** 2026-04-07

## Description du projet

Implémentation Python du jeu de société **Res Arcana** avec deux objectifs :
- Un moteur de jeu complet et fidèle aux règles
- Une IA entraînable par auto-play

## Référence rapide

- **Stack :** Python 3.x, pytest, GitHub Actions
- **Point d'entrée :** `main.py`
- **Architecture :** Engine → GameState → Players → Cards
- **Base de données :** Aucune
- **Déploiement :** Local / CI GitHub Actions

## Documentation générée

### Documentation principale

- [Project Overview](./project-overview.md) — Résumé exécutif et architecture
- [Architecture](./architecture.md) — Architecture technique détaillée _(à générer)_
- [Inventaire des composants](./component-inventory.md) — Catalogue des modules _(à générer)_
- [Guide de développement](./development-guide.md) — Setup et workflow _(à générer)_

## Documentation existante

- `README.txt` — Description en 2 lignes (moteur de jeu + IA auto-play)

## Pour démarrer

### Prérequis

- Python 3.x
- pip install pytest

### Lancer le jeu

```bash
python main.py
```

### Lancer les tests

```bash
pytest tests/
```

### Voir les cartes implémentées

```bash
python implemented_cards.py
```

## Pour le développement assisté par IA

Cette documentation a été générée pour permettre aux agents IA de comprendre et étendre ce projet.

### Ajouter une nouvelle carte :
→ Référence : `docs/project-overview.md` (section Architecture), `cards/base_card.py`

### Améliorer l'IA :
→ Référence : `game/ai_player.py`, `game/game_state.py` (méthodes `clone`, `is_terminal`, `get_winner` à implémenter)

### Modifier le moteur de jeu :
→ Référence : `game/engine.py`, `game/action.py`, `game/ability.py`

### Ajouter des tests :
→ Référence : `tests/conftest.py`, exemples dans `tests/test_*.py`

---

_Documentation générée par BMAD Method `document-project` workflow — 2026-04-07_
