# Langues du Ciné-club

Le site est écrit en français. Le réglage **Langue** du panneau « Aa » ouvre la liste des langues,
chacune écrite dans sa propre langue. Le choix est gardé sur l'appareil (`localStorage`, clé `ccLangueV1`) ;
au premier passage, le site reste en français. Changer de langue recharge la page.

## Comment ça marche

- Les traductions sont dans `carnet-de-films/i18n/<code>.json`, chargées seulement quand une autre langue
  que le français est choisie (le fichier `index.html` ne grossit pas).
- Chaque fichier contient :
  - `ui` : une table « texte français exact → traduction » (espaces resserrés, sans espaces au début ni à la fin) ;
  - `modeles` : des modèles avec `{0}`, `{1}` pour les textes qui contiennent des nombres ou des noms
    (par exemple `"{0} / {1} répondus": "{0} / {1} answered"`).
- Le script en bas de `index.html` applique la table aux nœuds de texte et aux attributs `placeholder`, `title`
  et `aria-label`, puis, avec un `MutationObserver`, à tout ce que la page redessine. Il ne remplace jamais
  un élément : un champ en cours de saisie garde le focus et le clavier reste ouvert.
- Les éléments marqués `data-noi18n` (noms des langues, par exemple) ne sont pas traduits. Les textes
  absents de la table restent en français.
- `<html lang>` suit la langue choisie, et `dir="rtl"` est posé pour l'arabe.
- Les langues sans fichier apparaissent dans la liste, grisées, avec la mention « bientôt » :
  la liste `PRETES` du script dit lesquelles sont disponibles.
- Le service worker (`sw.js`) met déjà en cache tous les fichiers de `/carnet-de-films/`, traductions comprises.
  La base factice des tests (`tests/cineclub_fixture.py`) sert les fichiers `i18n/*.json`.

## Ajouter une langue

1. Copier `i18n/en.json` en `i18n/<code>.json`, traduire les valeurs (jamais les clés françaises).
2. Ajouter `<code>:1` à `PRETES` dans le script de langue de `index.html`.
3. Vérifier sur téléphone et ordinateur, et pour l'arabe la mise en page de droite à gauche.

## Où on en est (31 octobre 2026)

| Langue | Code | Interface | Titres de listes et thèmes | Résumés des fiches |
|---|---|---|---|---|
| Français | fr | langue d'origine | langue d'origine | langue d'origine |
| English | en | 990 textes et 30 modèles | à faire | à faire |
| Español, Deutsch, Português, 한국어, 日本語, Монгол, 中文, हिन्दी, العربية, বাংলা, Русский | es, de, pt, ko, ja, mn, zh, hi, ar, bn, ru | à faire (« bientôt ») | à faire | à faire |

Les textes de l'interface ont été relevés dans le HTML, dans les chaînes du JavaScript et en parcourant
les écrans principaux avec Playwright (onglets, panneau « Aa », recherche, fiche d'un film, boîte à idées).

## Ce qui reste

- Les onze autres langues de l'interface (une ou deux à la fois, en partant de `en.json`).
- Les phrases que le JavaScript assemble avec des noms ou des nombres et qui n'ont pas encore de modèle :
  elles restent en français jusqu'à ce qu'on ajoute leur modèle.
- Les titres et sous-titres des listes et des thèmes (« Le monde de la fête », « Politique »…).
- Les résumés (`p`) et les phrases `r` des fiches : environ 900 films, par paquets, dans toutes les langues prêtes.
- Les écrans moins visités (import Letterboxd, outils de la propriétaire) : à relever et à compléter.
