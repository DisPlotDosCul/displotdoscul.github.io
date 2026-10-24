# Ciel de films

Une nuit commune à tout le catalogue. Les étoiles pâles attendent encore ; les
films vus tracent des constellations, et les notes d'au moins neuf deviennent des
points plus lumineux. On peut poser le ciel d'un autre membre sur le sien.

Les positions sont calculées dans le fichier HTML, sans bibliothèque ni service :
vecteurs pondérés de mots-clés, mouvements, pays, décennies, cinéastes et parts des
cinq familles ; pondération des caractéristiques selon leur fréquence ; analyse
en composantes principales par itération de puissance, puis rapprochement progressif
des voisins et légère répulsion pour rendre les étoiles accessibles. Les calculs
se répartissent entre les images du navigateur. Le rendu utilise un canevas unique.

Les positions dépendent du catalogue, jamais des notes ou du membre superposé.
Elles sont déterministes pour un catalogue identique. Deux dimensions ne peuvent
conserver toutes les ressemblances : les voisinages sont une invitation à explorer,
pas une classification absolue.

Zoom et déplacement : doigt, pincement, souris et boutons ; navigation au clavier
et recherche d'un titre pour accéder à un film sans viser une petite étoile.
Les superpositions respectent les masquages existants. Aucun nouvel enregistrement
Firebase n'est nécessaire.

## Validation

Le test `python3 tests/cineclub_ciel.py` charge le catalogue public et des profils
fictifs, puis un catalogue de plus de 1 000 films. Il contrôle le dessin, la recherche,
l'ouverture d'une fiche, la superposition, le zoom, le déplacement, la stabilité des
positions, les erreurs de console et le débordement horizontal. Les mesures de durée
concernent le navigateur de test, pas un téléphone physique.

Essais du 20 octobre 2026 : téléphone à 360 pixels et ordinateur à 1 440 pixels,
jour et néon ; tous les contrôles ci-dessus passent, ainsi que Grand confort et
la boucle de navigation au clavier. Sur 1 233 films dont plus de 1 200 vus,
les douze dessins mesurés pendant le zoom ont pris au maximum 2,8 ms dans le dernier
essai local. Le fichier `captures/ciel/mesures.json` contient la mesure la plus récente.

| | Jour | Néon |
|---|---|---|
| Téléphone | [Capture](captures/ciel/telephone-jour.png) | [Capture](captures/ciel/telephone-neon.png) |
| Ordinateur | [Capture](captures/ciel/ordinateur-jour.png) | [Capture](captures/ciel/ordinateur-neon.png) |

## Questions à valider

- [ ] Le ciel assez sombre et la luminosité des films vus conviennent-ils ?
- [ ] Les liens fins entre voisins vus et la superposition violette se lisent-ils bien ?
- [ ] L'exploration poétique peut-elle conserver des voisinages parfois inattendus ?

## Refonte du 22 octobre 2026

Les positions calculées étaient difficiles à lire. Chaque liste de la famille « Thèmes »
devient une constellation qui porte son nom ; un film va dans la liste la plus précise qui
le contient, les autres films forment « Autres films ». Les constellations se posent sur
une spirale sans se chevaucher. Une légende d'une ligne explique les trois tailles d'étoile.
Les fils relient seulement les films vus d'une même constellation. Les positions ne
dépendent toujours ni des notes ni du membre superposé.

## Toutes les étoiles rangées (22 octobre 2026, soir)

Il n'y a plus de groupe « Autres films » : après les listes de thèmes viennent les autres
listes (école, cours, envies…), puis le courant du film, puis sa décennie ; un courant de
moins de quatre films rejoint sa décennie. Chaque constellation prend la couleur de sa
catégorie, ses étoiles pas encore vues aussi. Les noms ne se chevauchent jamais : les plus
grandes constellations sont nommées d'abord, les autres en rapprochant le ciel.

## Galaxie (23 octobre 2026)

- **Trois rangements** : par catégories, par courants (chaque courant et mouvement a sa
  constellation, colorée selon sa famille), par décennies. Le choix est gardé sur l'appareil.
- **Placement** : chaque constellation se pose contre celles qui lui ressemblent le plus
  (mots-clés, familles de goût, courants, époques), sans chevauchement, avec un écart réduit.
- **Cinq lumières** selon la note : 0–2, 2–4, 4–6, 6–8, 8–10. Un film vu sans note reste une
  petite étoile pâle ; un film pas vu, une poussière de la couleur de sa constellation.
- **Décor** : étoiles lointaines qui glissent plus lentement (profondeur), nébuleuse de la
  couleur de chaque constellation, voie lactée en nuages qui relie les constellations
  musicales, dansées et animées, trous noirs à disque lumineux près des plus sombres
  (traumatismes, phobies, cauchemars…). Animation lente, coupée en Calme et avec la
  réduction des animations.
- **Recherche** : le ciel glisse jusqu'à l'étoile, qui pulse ; son étiquette ouvre la fiche.

## Ciel plein écran (23 octobre 2026, après-midi)

- **Fond** : les étoiles lointaines couvrent tout l'écran (tuiles répétées), un peu plus
  discrètes ; elles glissent et s'écartent toujours moins vite que les constellations au zoom.
- **Espace** : écart minimal plus grand entre constellations, plus un écart irrégulier propre
  à chaque paire ; le ciel n'est plus tassé au centre.
- **Forme de l'écran** : les constellations s'écartent dans le sens le plus long de l'écran
  (paysage sur ordinateur ou appareil tourné, portrait sur téléphone). Le ciel se recalcule
  quand on tourne l'appareil, et se cadre entre la barre du haut et la légende.

## Idées du 24 octobre 2026

- **Recherche** : le ciel glisse jusqu'au premier film trouvé pendant qu'on tape.
- **Fiche dans le ciel** : toucher une étoile ouvre une fiche compacte et translucide (en bas
  sur téléphone, à droite sur ordinateur). Le ciel reste visible et explorable ; toucher le
  ciel vide la referme. Courant, avis des membres, « Ma liste ».
- **Dé** : un film pas encore vu dans la constellation choisie (bouton 🎲 de la fiche, ou à
  côté du zoom pour la constellation la plus proche du centre).
- **Décor** : plus de trous noirs ni de voie lactée. Deux couches d'étoiles lointaines qui
  s'écartent au zoom (profondeur), sur tout l'écran.
- **Couleurs « Par catégories »** : les mêmes teintes douces que « Par courants ».
- **Bas de l'écran** : légende au-dessus des boutons de zoom ; à gauche, flèches ← → pour
  revenir aux endroits du ciel déjà visités.
