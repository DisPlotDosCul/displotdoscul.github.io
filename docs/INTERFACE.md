# Retouches demandées dans la boîte à idées

- La flèche de recherche précède désormais le libellé, associé au champ de recherche.
- « Passer » est remonté de 28 pixels, en gardant l'espace de sécurité du téléphone.
- La connexion demande les messages Firebase en français. Leur classement dans les
  courriers indésirables demande une vérification de l'expéditeur ; voir
  [Courriers de connexion](MAILS-CONNEXION.md).
- Le nom validé « Boussole cinéma » est conservé ; aucune liste de noms alternatifs
  n'est nécessaire après ce choix.
- « Ranger les catégories » est accessible dans le menu d'affichage pour
  l'administratrice. Il ouvre l'éditeur existant, qui enregistre dans Firebase et
  fonctionne indépendamment de Claude. Les droits d'accès sont conservés.
- Le top comporte vingt films, y compris dans le message de partage. Son ordre
  reste stable après l'ajustement d'une note, jusqu'au changement de catégorie,
  de recherche ou de membre.
- Un seul bouton encore peu exploré peut doucement s'éclairer puis s'éteindre.
  Le mouvement cesse à l'interaction, dans les fenêtres ouvertes, en affichage calme,
  en Grand confort et avec une préférence de réduction des animations. Les lettres
  du titre ne sont pas concernées.
- Les commandes du compte occupent une rangée à 360 pixels ; les explorations une
  seconde rangée. Les libellés restent complets et les cibles mesurent au moins
  44 pixels de haut.
- Les consignes des panneaux de catégories et la description de la boîte à idées
  sont raccourcies ; les boutons conservent leurs noms.
- L'écriteau néon perd son cadre et ses clous, avec huit ampoules (23 octobre). Les lettres,
  ampoules aléatoires, halos et contours en tirets gardent leurs effets existants.
- La recherche d'un film dans le ciel fonctionne aussi pendant le calcul des
  positions. Les fiches d'un autre carnet affichent le nom du membre consulté.

## Ce qui reste à vérifier

Le rangement est testé avec une administratrice fictive. La reconnaissance du
compte réel dépend toujours de sa connexion administratrice ; aucun droit n'a été
élargi. Le tri des courriers reste décidé par les fournisseurs de messagerie et
ne peut pas être garanti depuis ce fichier HTML.

## Vérification et captures

`python tests/cineclub_interface.py` exerce les commandes à 360 et 1 440 pixels,
en jour et néon : vingt films dans le classement et le partage, ordre stable après
les enregistrements différés puis actualisé au changement de catégorie, rangement
des catégories et des listes, Grand confort et absence de débordement horizontal.
Une horloge de test vérifie le clin d'œil et son arrêt à l'interaction, en Calme,
en Grand confort et avec la réduction des animations. Tous les accès Firebase sont
remplacés par une base fictive ; aucune erreur de console ni requête imprévue.

| | Jour | Néon |
|---|---|---|
| Téléphone | [Accueil](captures/interface/telephone-jour.png) · [Top 20](captures/interface/telephone-jour-top20.png) | [Accueil](captures/interface/telephone-neon.png) · [Top 20](captures/interface/telephone-neon-top20.png) |
| Ordinateur | [Accueil](captures/interface/ordinateur-jour.png) · [Top 20](captures/interface/ordinateur-jour-top20.png) | [Accueil](captures/interface/ordinateur-neon.png) · [Top 20](captures/interface/ordinateur-neon-top20.png) |

## Questions à valider

- [ ] Le regroupement des commandes à 360 pixels reste-t-il assez lisible ?
- [ ] La fréquence et la douceur du clin d'œil conviennent-elles ?
- [ ] Le néon sans cadre et les huit ampoules (23 octobre) retrouvent-ils l'esprit souhaité ?
- [ ] Le menu d'affichage permet-il bien de retrouver le rangement sur le compte administratrice ?

## Mode édition (22 octobre 2026)

« ✏️ Modifier le site », dans le menu Aa, est réservé à l'administratrice. Trois onglets :
**Disposition** (ordre des blocs du haut de page et de la barre), **Textes** (boutons,
aide et champ de recherche, filtres, noms des catégories, titres et sous-titres des listes ;
vide = texte d'origine) et **Couleurs** (sept couleurs, réglées pour l'ambiance affichée).
Tout s'applique en direct ; « Enregistrer pour tout le monde » écrit le document
`apparence` du catalogue, « Annuler les changements » revient à la dernière version.

## Images du film

Le bouton 🎞 affiche dans la fiche quatre images tirées du film, venues de TMDB
(The Movie Database), avec la mention « Images : TMDB ». Les résultats sont gardés sur
l'appareil. Ce site utilise l'API de TMDB sans être approuvé ni certifié par TMDB.

## Appli installable (24 octobre 2026)

Le Ciné-club s'installe comme une appli (PWA, Progressive Web App) sur Android, iPhone, iPad,
Windows et Mac : icône sur l'écran d'accueil, ouverture en plein écran, page gardée pour
s'ouvrir sans réseau. Bouton « 📲 Installer l'appli » dans le menu Aa (caché une fois installée) :
fenêtre d'installation du navigateur quand elle existe (Chrome, Edge, Android), sinon les
étapes propres à l'appareil (Safari sur iPhone et iPad, Safari sur Mac). Fichiers :
`manifest.webmanifest`, `sw.js` (réseau d'abord, copie gardée seulement hors connexion ;
Firebase et TMDB ne passent pas par lui) et `icones/`.
Sur iPhone et iPad, l'appli installée ne partage pas la connexion de Safari : le lien de
connexion par e-mail s'ouvre dans Safari, la connexion Google marche dans l'appli.

Express (24 octobre 2026) : synopsis très court (première phrase, environ 150 signes) et bouton
« Vu mais oublié ». Le bouton « 📲 Installer l'appli » est en tête du menu Aa et sur l'écran
d'accueil (« Choisissez votre affichage »). L'appli installée n'ouvre que le Ciné-club ; la
Boussole des IA et Cap Logement restent sur le site général.

Filtres (24 octobre 2026) : un seul bouton « Filtres ▾ » à côté de la recherche ; les cinq filtres
s'ouvrent dessous, sans icône ; le bouton affiche le filtre actif. Express : en grand l'affiche, le
titre, « Pas vu », « Adoré », « Bien », « Pas aimé » ; en discret « + » (ma liste) à côté de
l'affiche, « Vu mais oublié », « Noter /10 » (1 à 10) près de « Vu, sans avis ».
