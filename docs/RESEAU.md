# Réseau social : faire répondre sans effort, et montrer ce qu'on partage

Personne ne notera 700 films. Chaque minute passée doit rapporter tout de suite quelque chose,
surtout une comparaison avec les autres membres.

## Répondre en un toucher

- **⚡ Express** (accueil, Boussole, statistiques) : une carte par film, avec l'affiche TMDB.
  « Pas vu », ou « Adoré · Bien · Pas aimé » (9 · 7 · 4) ; « Vu, sans avis », « Passer »
  et « ← Annuler » restent discrets. Chaque réponse est enregistrée aussitôt. Clavier : 1 à 4.
- **Ordre** : les quinze films les plus vus du club d'abord (presque toujours « Vu »), puis
  en alternance des films qui départagent les goûts (notes très différentes d'un membre à
  l'autre) et d'autres films connus. Les affiches suivantes se préparent en avance.
- **Précision de la boussole** plutôt qu'un compteur : 1 − e^(−notes/30) ; 25 notes ≈ 57 %,
  50 ≈ 81 %, 100 ≈ 96 %. Affichée dans Express, la Boussole et les statistiques.
- **Import** Letterboxd (export .zip, ou ratings.csv, watched.csv, diary.csv) et IMDb (Internet
  Movie Database, export .csv) : aperçu avant écriture, notes Letterboxd sur 5 doublées, réponses
  déjà présentes gardées, films absents du carnet listés. Écriture groupée (150 champs par envoi).
  La bibliothèque de lecture des .zip (JSZip) n'est chargée qu'au moment d'ouvrir un .zip.

## Récompenser tout de suite

- **Toutes les dix réponses** : la précision, et les trois membres les plus proches
  (« Toi et Camille : 78 % d'affinité · 34 films en commun », adorés tous les deux).
- **Profils** : affinité, films adorés tous les deux, désaccords (au moins 4 points d'écart),
  ses coups de cœur que tu n'as pas vus. L'affinité apparaît aussi dans la liste des membres.
  Rien n'est montré si l'un des deux est « dans sa bulle ».
- **Soirée ciné** (onglet de la Communauté) : on choisit une à quatre personnes ; douze films
  qu'aucun n'a vus, classés par estimation moyenne moins l'écart entre les estimations, avec
  le chiffre de chacun.

## Invitation « Compare-toi à moi »

Le lien emporte jusqu'à 120 de mes notes (les films les plus vus du club d'abord), sans
identifiant ni adresse. Il ouvre Express titré « Compare-toi à … », qui commence par ces films ;
au bout de dix réponses, l'affinité apparaît, et un bouton propose de créer un compte. Les
réponses données sans compte sont gardées sur l'appareil et rejoignent le carnet à la connexion.

## À vérifier en vrai

Les essais utilisent une base fictive toujours connectée : l'invitation ouverte sans compte
et la fusion des réponses à la connexion restent à éprouver sur le site.
