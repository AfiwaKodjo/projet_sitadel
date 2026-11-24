import sys
import pandas as pd

SOURCE = "https://www.data.gouv.fr/datasets/liste-des-permis-de-construire-et-autres-autorisations-durbanisme"

#Lecture du fichier
fichier = sys.argv[1]

colonnes_utiles = [
    "Code du département du lieu des travaux - Code de la zone",
    "Type de DAU -- demande d'autorisation d'urbanisme (PC ou DP généralement, rarement PA)",
    "Numéro d'enregistrement de la DAU",
    "Etat d'avancement du projet",
    "Date réelle d'ouverture de chantier",
    "Année de dépôt de la DAU",
    "Code d'activité principale de l'établissement d'un demandeur avéré en tant que personne morale",
    "Catégorie juridique d'un demandeur avéré en tant que personne morale",
    "Dénomination d'un demandeur avéré en tant que personne morale",
    "Numéro SIREN d'un demandeur avéré en tant que personne morale",
]
df = pd.read_csv(fichier, sep=";", dtype=str, usecols=colonnes_utiles)

# On filtre pour ne garder des demandes dans le departement 78, de type PC et avec un SIREN renseigné
df = df[
    (df["Code du département du lieu des travaux - Code de la zone"] == "78")
    & (df["Type de DAU -- demande d'autorisation d'urbanisme (PC ou DP généralement, rarement PA)"] == "PC")
    & df["Numéro SIREN d'un demandeur avéré en tant que personne morale"].notna()
].copy()

#On classe ensuite chaque demandeur dans une famille
def famille(ligne):
    cj = str(ligne["Catégorie juridique d'un demandeur avéré en tant que personne morale"])
    ape = str(ligne["Code d'activité principale de l'établissement d'un demandeur avéré en tant que personne morale"])

    medico_social = ape.startswith(("86.", "87.", "88."))  #santé, hébergement médico-social, action sociale

    #associations, fondations, mutuelles
    if cj.startswith(("92", "93")) or cj.startswith("82"):
        return "Médico-social (association / fondation)" if medico_social else "Association / fondation (autre)"
     #SA d'HLM, coopérative HLM, office public de l'habitat
    if cj in ("5546", "5547", "7371"): 
        return "Bailleur social"
    if cj.startswith("7"):
        return "Public médico-social (hôpital, CCAS...)" if medico_social else "Collectivité / public"
    if ape.startswith(("41.10", "68.")) or cj.startswith("65"):
        return "Promoteur /immobilier/ SCI"
    if cj.startswith(("5", "6")):
        return "Entreprise"
    return "Non déterminé"

df["famille"] = df.apply(famille, axis=1)


#Etat du projet
ETATS = {"2": "Autorisé", "4": "Annulé", "5": "Commencé", "6": "Terminé"}
df["etat_libelle"] = df["Etat d'avancement du projet"].map(ETATS).fillna("Inconnu")

#Chaque ligne renvoie à sa source publique
df["source_permis"] = SOURCE + " (n° " + df["Numéro d'enregistrement de la DAU"] + ")"
df["fiche_entreprise"] = (
    "https://annuaire-entreprises.data.gouv.fr/entreprise/"
    + df["Numéro SIREN d'un demandeur avéré en tant que personne morale"]
)

df.to_csv("permis_78_classes.csv", index=False)

#On regroupe par demandeur suivant le nombre de permis, pas commencés, en chantier, dernière année de dépôt
demandeurs = (
    df.groupby("Numéro SIREN d'un demandeur avéré en tant que personne morale")
    .agg(nom=("Dénomination d'un demandeur avéré en tant que personne morale", "first"),
         famille=("famille", "first"),
         nb_permis=("Numéro d'enregistrement de la DAU", "count"),
         pas_commences=("Etat d'avancement du projet", lambda e: (e == "2").sum()),
         en_chantier=("Etat d'avancement du projet", lambda e: (e == "5").sum()),
         dernier_depot=("Année de dépôt de la DAU", "max"),
         fiche=("fiche_entreprise", "first"))
    .reset_index()
    .sort_values("nb_permis", ascending=False)
)
#Colonnes lisibles et fichier qui s'ouvre bien dans Excel en français
demandeurs = demandeurs.rename(columns={"Numéro SIREN d'un demandeur avéré en tant que personne morale": "siren"})
demandeurs = demandeurs[["nom", "famille", "nb_permis", "pas_commences", "en_chantier", "dernier_depot", "fiche", "siren"]]
demandeurs.to_csv("demandeurs_78.csv", index=False, sep=";", encoding="utf-8-sig")

print(f"{len(df)} permis, {demandeurs.shape[0]} demandeurs\n")
print(demandeurs["famille"].value_counts().to_string(), "\n")
cibles = demandeurs[demandeurs["famille"].str.contains("médico-social", case=False)]
print("Cibles médico-sociales :")
print(cibles.head(20).drop(columns="fiche").to_string(index=False))


