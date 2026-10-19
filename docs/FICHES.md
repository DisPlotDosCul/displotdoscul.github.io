# Fiches enrichies

863 films : les 838 identifiants du catalogue public et les 25 films ajoutés par
les compléments. Les listes, les parties et les familles existantes sont conservées.
Aucune lecture ni écriture des données réelles des membres n'est nécessaire aux essais.

## Données

Chaque entrée de `complements.json → fiches` contient :

- `duree` : minutes du montage usuel ; pour une série ou un groupe d'épisodes,
  durée indicative d'un épisode, signalée par `duree_episode: true`.
- `av` : tableau parmi « violence explicite », « violence sexuelle », « suicide »,
  « automutilation », « maltraitance », « drogue », « images choquantes ».
  Un tableau vide n'affirme pas une absence certifiée de tout contenu sensible.
- `th` : trois thèmes précis, en un ou deux mots.
- `fiab: "à vérifier"` : proposition éditoriale restant à relire. Ce marqueur est
  volontairement conservé sur toutes les fiches, même lorsqu'une durée a été sourcée,
  car les avertissements n'ont pas tous été vérifiés par visionnage ou source détaillée.

Les données ont été préparées à partir du catalogue public et de connaissances
cinématographiques, avec des recherches ponctuelles. Elles ne constituent pas une
vérification exhaustive des 863 films. Les différences de montage et les avertissements
nécessitent une relecture avant publication définitive.

Quelques vérifications du 19 octobre 2026 :

- [1917, British Film Institute](https://www.bfi.org.uk/film/83d6a46e-e55d-5b93-a820-f23a96eb5c77/1917) : 119 minutes ; le test utilise exprès une valeur Firebase différente pour vérifier sa priorité.
- [Fantastique, Ville de Paris](https://www.paris.fr/pages/fantastique-32394) : 71 minutes.
- [Full Phil, Festival de Cannes](https://www.festival-cannes.com/en/f/full-phil/) : 78 minutes.
- [Bébé colère, Côté court](https://www.cotecourt.org/film/bebe-colere) : 13 minutes.
- [Signal 8, Festival de Rotterdam](https://iffr.com/en/iffr/2020/films/signal-8) : 15 minutes ; certaines éditions annoncent 14 minutes.
- [Le Vertige, Diaphana](https://diaphana.fr/film/le-vertige/) : 68 minutes ; d'autres fiches annoncent 67 minutes.
- [4 mois, 3 semaines, 2 jours, British Board of Film Classification](https://www.bbfc.co.uk/release/4-luni-3-saptamani-si-2-zile-4-months-3-weeks-and-2-days-q29sbgvjdglvbjpwwc00mtgymdg) : violence sexuelle et images sensibles.

## Affichage

Titre, année, cinéaste, pays, durée, état et note restent accessibles directement.
Le résumé, le mouvement, les thèmes et les informations supplémentaires se replient
derrière « plus… ». Les avertissements disposent d'une ouverture distincte et discrète.
« Mes films notés » conserve son affichage compact. Les thèmes sont aussi recherchables.
Le questionnaire porte le nom validé « Boussole cinéma ».

Les fiches se fusionnent champ par champ : Firebase passe avant, y compris pour une
valeur explicitement vide. Aucun nouveau champ n'est écrit dans Firebase.

## Vérification

Contrôles des données et de la syntaxe, sans navigateur :

```sh
python3 tests/cineclub_fiches.py --donnees-seules
```

Essais et quatre captures avec Playwright disponible dans l'environnement de test :

```sh
python3 tests/cineclub_fiches.py
```

La page et les scripts Firebase sont interceptés avant le chargement : le catalogue
public est réparti entre `films/fiches-1` à `films/fiches-6`, les listes sont des
documents `s…`, les deux membres fictifs utilisent `profils/{uid}.rep`. Aucun appel
vers un service réel n'est laissé passer. Toute requête inattendue ou erreur de console
fait échouer le test. Le fichier HTML déployé ne gagne aucune dépendance.

Les captures attendues sont `telephone-jour.png`, `telephone-neon.png`,
`ordinateur-jour.png` et `ordinateur-neon.png`. Le workflow GitHub Actions les dépose
dans l'artefact `cineclub-fiches-captures`, même si un contrôle ultérieur échoue.

Dans l'environnement local de cette session, les essais du navigateur sont bloqués
par les restrictions système. Les contrôles sans navigateur sont passés ; le résultat
Playwright et les captures doivent être confirmés par le workflow.

## Questions à valider

- [ ] L'ouverture « plus… » et l'emplacement des avertissements conviennent-ils ?
- [ ] Les durées indicatives par épisode conviennent-elles pour les séries ?
- [ ] Les propositions signalées « à vérifier » peuvent-elles être relues par lots avant fusion ?

La pull request reste en brouillon jusqu'aux essais visuels et à cette relecture.
