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

## Dictée de la boîte à idées (12 novembre 2026)

Idée de Licia du 10 novembre : sur téléphone, la dictée écrivait plusieurs fois le même mot et
s'arrêtait quand on continuait de parler ; sur ordinateur, elle ne se lançait pas.

- Mots répétés : sur Android, chaque résultat de la reconnaissance reprend le précédent en plus
  long (« je », « je veux », « je veux un film »). Un résultat qui prolonge le précédent le remplace
  au lieu de s'y ajouter ; sur Android, l'écoute se fait phrase par phrase.
- Arrêt en cours de route : la reconnaissance se relance seule après une pause, tant qu'on n'a pas
  appuyé sur « ⏹ Arrêter la dictée » ; elle s'arrête d'elle-même après environ une minute de silence.
- Ne se lance pas : la raison s'affiche maintenant dans le panneau (micro refusé, aucun micro,
  dictée du navigateur injoignable…), avec une autre solution : touche Windows + H sur ordinateur
  Windows, micro du clavier sur téléphone. Un point clignote pendant l'écoute.
- Corriger à la main pendant la dictée reprend à partir du texte corrigé.

Essai : `tests/cineclub_idees.py` simule une reconnaissance qui répète les mots comme Android,
une pause, l'arrêt et un micro refusé. La dictée réelle reste à essayer sur le Huawei et le MateBook.

## Accueil plus simple et avis de recherche (12 novembre 2026)

Idées de Licia du 10 novembre, pour qu'une personne âgée ou très jeune ne se perde pas :

- En-tête : « ⚙ Réglages » en haut à droite (taille, ambiance, langue, installer l'appli) ; le bouton soleil, qui
  changeait l'écran d'un coup, est retiré (l'ambiance se choisit dans Réglages). « ← Retour » apparaît en haut à gauche
  dès qu'on a changé d'affichage, en plus du bouton du bas. Un Retour de trop à l'accueil (navigateur ou téléphone)
  ne fait plus quitter le site : un message propose d'appuyer encore pour le quitter.
- Compteur : seulement « répondus » en haut ; les vus, oubliés et notés sont en tête de « Mon carnet ».
- Santé mentale : n'est plus une catégorie à part, c'est un thème (`s54-sante-mentale`) avec une sous-catégorie par
  trouble ; les anciennes listes sont cachées (`cache: true`) et leurs films gardés.
- Dans le panneau d'une catégorie, toucher une liste découpée ouvre ses sous-catégories juste dessous, puis leurs
  sous-catégories ; chaque case donne son nombre de films. Les envies et leurs nuances aussi.
- Express, Boussole, Dérive et Ciel sont rangés derrière « ✨ Autres façons de choisir », chacun avec une phrase.
- Visite guidée en deux bulles au lieu de trois ; l'écran du premier affichage renvoie à « Réglages ».
- Pied de page : « 📤 Envoyer le Ciné-club à un ami » (partage du téléphone, sinon lien copié), « ✉️ Écrire à l'équipe »
  (la boîte à idées s'ouvre, prête pour un message), et « 💛 Soutenir le Ciné-club », caché tant que `DON_URL` est vide.
- Boutons : coins à peine arrondis et bord du bas plus marqué au lieu des pilules aux contours fins.

Avis de recherche (idée 4) : dans la communauté, onglet « 🔎 Avis de recherche ». On décrit un film, une série, un épisode
ou un documentaire dont on a oublié le titre ; pendant qu'on écrit, les films du catalogue qui ressemblent à la
description s'affichent. Les autres membres répondent « 💡 Je crois savoir » avec un titre ; la personne est prévenue
(compteur sur « Communauté » et sur l'onglet), peut ouvrir le film s'il est au catalogue ou le proposer s'il n'y est pas,
puis retirer son avis. Les avis et réponses sont des messages (`type: "avis"` à tout le monde, `type: "avis-rep"` à la
personne) : les règles Firebase actuelles suffisent. Une recherche sans résultat propose aussi de lancer un avis.
Quand on ajoute un film, un champ « Autres indices » (cinéaste, acteur, genre, détail…) accompagne le titre et l'année.

Essai : `tests/cineclub_avis.py`.

## Communauté en page entière, fil et playlists (12 novembre 2026)

Idées 5, 10 et 16 de Licia : la communauté s'ouvre en page entière avec « ← Retour » en haut (le Retour du navigateur
ou du téléphone la ferme aussi) ; ses onglets tiennent sur deux rangées au plus. Sur l'accueil, la carte
« 📰 Quoi de neuf chez les membres ? » ouvre directement le fil (membres connectés, hors bulle). Les playlists des
membres ne sont plus une catégorie de l'accueil : elles sont dans l'onglet « Playlists » de la communauté
(avec « Valider les conseils reçus » pour l'administratrice).

## Qui voit quoi, amis, films ajoutés par les membres, playlists (12 novembre 2026)

Idées 12, 13 et 18 de Licia, et sa demande sur les playlists.

**Quatre modes** (Mon compte › « 🔒 Qui peut voir mon carnet ? ») : 🌍 Public (tous les membres voient tout,
le mode des comptes existants), 👫 Privé (seulement les amis, qui sont aussi les seuls à pouvoir envoyer des conseils),
🎛️ Personnalisé, 🫧 Bulle (personne ne voit rien à part le pseudo et la playlist ; pas de fil, pas de conseils ;
les comptes qui étaient déjà « dans leur bulle » y restent).

**Mode personnalisé, élément par élément** : mes films vus, notes et avis ; ma liste de films à voir ; mes chiffres
(films vus, notés, moyenne) ; ma phrase de goûts ; mes réponses au questionnaire ; mes commentaires ; mon activité
dans le fil ; me proposer dans la Soirée ciné des autres ; qui peut m'envoyer des conseils. Pour chacun : tout le monde,
mes amis, mes proches (une partie des amis, cochés un par un) ou personne d'autre que moi. On peut par exemple
montrer ses chiffres sans montrer ses notes.

**Vraiment protégé, pas seulement caché** : les notes, la liste, les goûts, le questionnaire et les chiffres quittent
le profil (lu par tous les membres) pour des documents « carnets/{compte}__{partie} » ; chacun dit qui peut le lire
(« tous », ou la liste des amis ou des proches), et les règles de la base le vérifient. Les commentaires réservés vont
dans « commentairesPrives », lus seulement par leur auteur et les personnes choisies ; ils changent de collection quand
le réglage change. Le fil, la Soirée ciné et « qui peut m'envoyer des conseils » suivent aussi le réglage (ce dernier
est vérifié par les règles). Le déplacement se fait tout seul, au premier passage de chacun après la publication des
règles ; avant, rien ne change et le réglage est grisé avec une explication.

**Amis** : Communauté › Membres › un membre › « ➕ Demander en ami ». La demande arrive dans « Pour moi »
(Accepter, Refuser, Voir son profil) ; une fois acceptée, chacun ajoute l'autre à sa liste (deux demandes croisées
valent acceptation). « Retirer de mes amis » prévient l'autre. Chaque membre écrit seulement sa propre liste. Les
amis ont 👫 dans la liste des membres ; un carnet fermé affiche 🔒 et ses chiffres s'ils sont partagés.

**Films ajoutés par les membres** (idée 18) : un membre connecté ajoute lui-même un film absent (recherche, boîte à
idées ou sa playlist) ; il entre tout de suite dans la base (collection « ajouts »), visible par tous, dans la liste
« Films ajoutés par les membres » (Communauté › Playlists), avec « Ajouté par … » et ses indices. Si la base refuse
encore (règles pas publiées), le film part dans les propositions, comme avant.

**Chacun sa playlist, et seulement la sienne** : chaque membre a une playlist pour conseiller des films à tous,
ouverte depuis Mon carnet (« 🎁 Ma playlist ») ou Mon compte, avec un nom et une phrase facultatifs. On y ajoute,
modifie et retire librement ses films ; les règles refusent qu'on touche à celle d'un autre (l'administratrice peut
aider partout). Les anciennes playlists d'Arthur, Violette et Jean se relient toutes seules à leurs comptes quand
Licia ouvre le site (un compte dont le pseudo commence par ce prénom, s'il n'y en a qu'un) ; leurs films suivent.
Sinon : Communauté › Membres › le membre › « Relier ».

Vérifié par `tests/cineclub_confidentialite.py` (faux Firestore qui suit les filtres des requêtes) et par
`tests/regles_firestore.mjs` (60 cas dans l'émulateur Firestore, avec le vrai fichier `firestore.rules`).

