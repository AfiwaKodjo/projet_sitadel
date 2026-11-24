import pandas as pd

df = pd.read_csv("permis_78_classes.csv", dtype=str)

# On garde seulement les cibles médico-sociales (associations, fondations, public)
df = df[df["famille"].str.contains("médico-social", case=False)].copy()
df["annee_depot"] = df["Année de dépôt de la DAU"].astype(int)
df["annee_ouverture"] = df["Date réelle d'ouverture de chantier"].str[:4]
etat = df["Etat d'avancement du projet"]

# Pour chaque permis, on note l'année seulement s'il est dans l'état concerné
df["depot_si_autorise"] = df["annee_depot"].where(etat == "2")
df["ouverture_si_commence"] = df["annee_ouverture"].where(etat == "5")

# On regroupe par demandeur
cibles = (
    df.groupby("Numéro SIREN d'un demandeur avéré en tant que personne morale")
    .agg(nom=("Dénomination d'un demandeur avéré en tant que personne morale", "first"),
         famille=("famille", "first"),
         nb_permis=("Numéro d'enregistrement de la DAU", "count"),
         nb_autorises=("Etat d'avancement du projet", lambda e: (e == "2").sum()),
         nb_commences=("Etat d'avancement du projet", lambda e: (e == "5").sum()),
         nb_annules=("Etat d'avancement du projet", lambda e: (e == "4").sum()),
         dernier_autorise=("depot_si_autorise", "max"),
         dernier_commence=("ouverture_si_commence", "max"),
         dernier_depot=("annee_depot", "max"),
         fiche=("fiche_entreprise", "first"))
    .reset_index()
)


# Pour chaque demandeur, on note ce que dit la base et quel service proposer
def recommandation(c):
    if c.nb_commences > 0:
        return (f"Chantier commencé (dernier en {c.dernier_commence}), fin non connue à ce jour",
                "Gestion de projet, si le chantier est toujours en cours")
    if c.nb_autorises > 0:
        return (f"Autorisé (dernier déposé en {int(c.dernier_autorise)}), aucun début de chantier connu",
                "Gestion de projet avant le démarrage, si le projet est toujours actif")
    if (c.nb_permis - c.nb_annules) == 0:
        return "Projets annulés", "À écarter"
    return "Projets terminés", "Relancer plus tard : stratégie immobilière"


cibles[["signal", "service_buddimm"]] = cibles.apply(recommandation, axis=1, result_type="expand")

# Un patrimoine qui bouge beaucoup = besoin d'une direction immobilière régulière
cibles.loc[cibles.nb_permis >= 3, "service_buddimm"] += " + direction immobilière (patrimoine actif)"

cibles = cibles.sort_values(["nb_commences", "nb_autorises", "nb_permis"], ascending=False)

# Colonnes les plus utiles en premier, noms lisibles
cibles = cibles.rename(columns={"Numéro SIREN d'un demandeur avéré en tant que personne morale": "siren"})
cibles = cibles[["nom", "famille", "signal", "service_buddimm", "nb_permis", "nb_autorises",
                 "nb_commences", "nb_annules", "dernier_depot", "fiche", "siren"]]

# sep=";" et utf-8-sig pour que le fichier s'ouvre bien dans Excel en français (colonnes et accents)
cibles.to_csv("qui_contacter_78.csv", index=False, sep=";", encoding="utf-8-sig")

print(f"{len(cibles)} cibles\n")
print(cibles["signal"].str.split(" \\(").str[0].value_counts().to_string(), "\n")  # comptage sans l'année
print(cibles[["nom", "nb_permis", "signal", "service_buddimm"]].to_string(index=False))