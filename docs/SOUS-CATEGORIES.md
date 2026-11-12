# Sous-catégories des listes

Idée de Licia du 5 novembre 2026 : les « Petits cours de cinéma » sont répartis ailleurs, et chaque liste
de plus de 25 films est découpée en sous-catégories, parfois en sous-sous-catégories.

## Affichage

En haut d'une liste découpée, un seul menu sur une ligne : « Toutes les sous-catégories », puis chaque
sous-catégorie et, en retrait (↳), ses sous-sous-catégories, avec le nombre de films. Le choix filtre la liste
sans changer l'ordre des notes estimées. Sans choix, chaque film rappelle sa sous-catégorie dans sa petite note.
Un film qu'aucune sous-catégorie ne cite (ajouté plus tard) apparaît dans « Autres films ».

Depuis le 12 novembre 2026, un film peut être dans plusieurs sous-catégories (Pauvres Créatures :
« Cordes et voix déformées » et « Grands compositeurs › Jerskin Fendrix »). Il est compté et affiché dans
chacune ; sa petite note reprend la première qui le cite, ou celle de la partie choisie dans le menu.

Depuis le 12 novembre, le panneau d'une catégorie ouvre aussi les sous-catégories d'une liste juste sous son nom,
puis leurs sous-catégories, avec le nombre de films ; toucher la dernière affiche ses films.

## Données

Dans `complements.json → sections → <liste>` :

- `parties` : `[{ "titre", "aide", "ids": [...] }]`, ou `"sous": [{ "titre", "ids": [...] }]` à la place de `ids`.
  Les sous-catégories des compléments remplacent celles de la base.
- `cache: true` : la liste est cachée (ses films sont rangés ailleurs). Une catégorie sans liste visible disparaît.
- `notes` : `{ "identifiant": "petite note" }` pour les films de la base qui n'en avaient pas dans cette liste.

## Petits cours de cinéma, répartis

- « Grands mouvements avant 1980 » et « Courants de 1980 à 2010 » → École de cinéma (selon l'année),
  avec la note du cours ; ils restent aussi dans « Courants ».
- « Le son et la musique » → « Musique de film » (les notes du cours sont reprises).
- « Couleurs et musique sur mesure » → « Couleurs vives » et « Musique de film » (déjà présents).
- Quelques films y gagnent aussi un thème : Hellraiser, Funny Games, Seul contre tous, Delicatessen, Happy Together.

## Listes découpées

Musique de film (9 sous-catégories depuis le 12 novembre, dont « Grands compositeurs » et ses 35 compositeurs), Rêve et étrangeté, Couleurs vives, Cirque et
acrobates, Films qui émeuvent, Fins à rebondissement, Malaise et folie, Liste cauchemar, Danse, Mer et apnée,
Erreur sur la personne, Politique (12 sous-catégories depuis le 12 novembre, dont « Courants politiques »), Cinéma coréen, Vengeance aveugle, Paranoïa et folie à deux, et les trois
listes de l'École de cinéma (par courant). Rave, Le monde de la fête et Sous la menace avaient déjà les leurs.
