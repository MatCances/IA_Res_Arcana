TODO: quand tous les artefacts seront implémenté, faire des tests en mode vrai game totale jusqu'a la victoire
pour tester plusieurs artefacts en meme temps. 

- Les on_event des cartes a faire adapté pour l'ia après. Voir
celui de source_elementaire pour comprendre

Voilà tous les on_event qui contiennent des choix dans ton code :
Reponse chatgpt, il peut avoir des erreur.
Dans artifacts.py :

LightFlask — réaction à DESTROY_ARTIFACT : demande si on veut activer (gagner 1 ressource)
ElementarySource — réaction à ATTACK : demande si on veut payer 1 CALM pour annuler
Dolfin — réaction à ATTACK : demande si on veut payer 1 CALM pour annuler
KeenSword — réaction à ATTACK : demande si on veut payer 1 ELAN pour poser 1 DEATH et annuler
GoldLion — réaction à ATTACK : demande si on veut engager la carte pour annuler
LifeChalice — réaction à ATTACK : demande si on veut engager la carte pour annuler
Moloss — réaction à ATTACK : demande si on veut engager la carte
LifeTree — réaction à ATTACK : demande si on veut payer 1 LIFE pour annuler

Dans artifacts.py aussi mais dans get_abilities avec des choix d'esquive :

BoneDragon, DurtDragon, FireDragon, OldDragon, SeaDragon, SeaSnake, WindDragon — demandent
à la cible si elle veut esquiver

Ces derniers sont un cas particulier car c'est target qui répond, pas player. Il
faudra bien appeler target.choose_yes_no(...) et non player.choose_yes_no(...).
