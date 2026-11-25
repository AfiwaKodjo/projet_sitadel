# Qualification des demandeurs de permis de construire – Yvelines (78)

Cas métier pour le stage IA agentique de Buddimm.

Objectif : à partir de la base Sitadel, repérer les structures médico-sociales qui construisent dans les Yvelines, et dire pour chacune ce que la base sait de ses projets.

## Comment les fichiers s'enchaînent

```
Fichier Sitadel (data.gouv.fr, non inclus)
        │
        ▼
TrierDemande.py ──► permis_78_classes.csv   (un permis par ligne)
        │       └─► demandeurs_78.csv        (un demandeur par ligne)
        ▼
qui_contacter.py ──► qui_contacter_78.csv    (les cibles médico-sociales)
```

| Fichier | Créé par | Ce qu'il contient |
|---|---|---|
| `TrierDemande.py` | – | Script 1 : filtre les permis du 78 et classe chaque demandeur dans une famille |
| `permis_78_classes.csv` | `TrierDemande.py` | Les 4 245 permis du 78, avec la famille du demandeur, l'état du projet et les liens sources. Sert d'entrée à `qui_contacter.py` |
| `demandeurs_78.csv` | `TrierDemande.py` | Les 2 439 demandeurs (un par SIREN), avec leur famille et leur nombre de permis |
| `qui_contacter.py` | – | Script 2 : garde les cibles médico-sociales et donne le dernier état connu de leurs projets |
| `qui_contacter_78.csv` | `qui_contacter.py` | Les 48 cibles médico-sociales, avec le dernier état connu et l'année |

`demandeurs_78.csv` et `qui_contacter_78.csv` s'ouvrent directement dans Excel (séparateur `;`).

Chaque ligne renvoie à sa source : numéro du permis et lien vers la fiche publique de l'organisme sur l'annuaire des entreprises.

## Données

- Fichier « Liste des autorisations d'urbanisme créant des locaux non résidentiels », version 2026-10 :
  https://www.data.gouv.fr/datasets/liste-des-permis-de-construire-et-autres-autorisations-durbanisme?resource_id=8f23d65f-7142-4ac5-94c1-077b028255bf)
- Note de présentation du ministère :
  https://data.statistiques.developpement-durable.gouv.fr/dido/api/files/52ce326b-45b2-42ce-a2e7-4a60554ef559
- Dictionnaire des variables :
  https://www.data.gouv.fr/datasets/liste-des-permis-de-construire-et-autres-autorisations-durbanisme?resource_id=c863c9e3-070c-49e2-91de-92c8d58cc807

Le fichier source n'est pas dans le dépôt : il faut le télécharger depuis data.gouv.fr et le site direct est écrit ci-dessus.

## Lancer

```
pip install pandas
python TrierDemande.py Liste-des-autorisations-durbanisme-creant-des-locaux-non-residentiels.2026-10.csv
python qui_contacter.py
```

Il faut lancer `TrierDemande.py` en premier : `qui_contacter.py` lit le fichier qu'il crée.

## Limites

- Fichier logements non traité.
- Le classement par codes laisse passer quelques erreurs.
- La base ne donne pas la situation actuelle d'un projet : on indique le dernier état connu, sans seuil inventé.
