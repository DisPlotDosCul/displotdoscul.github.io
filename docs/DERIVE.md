# Dérive onirique — note d'intention

Écrit avant l'implémentation.

On entre par une image : un bleu profond, une peur sans visage, une chaleur dans
les mains, un souvenir d'enfance. Aucun questionnaire ni profil à remplir. Un film
répond à cette image ; trois portes permettent de poursuivre : « plus étrange »,
« plus doux », « plus profond ». Le lien importe davantage que le classement.

La page montre un titre, son année, son cinéaste et une phrase courte. Le résumé
se découvre à la demande. La trace du parcours s'écrit comme un carnet de rêves :
on peut lui donner un nom, revenir sur ses pas, le garder, le relire et le partager.
L'interface comporte des boutons et des espaces, sans mode d'emploi en haut.

## Ce que fait le parcours

L'image initiale se rapproche des mots du catalogue grâce à un petit vocabulaire
d'associations : couleurs, sensations, souvenirs, émotions et craintes. Les films
sont reliés par leurs mots-clés, résumés, mouvements et parts dans les cinq familles.
Les mots rares pèsent davantage. Les titres déjà traversés sont exclus de la suite.

Les trois chemins infléchissent une même association :

- **Plus étrange** : rêve, doubles, transformations, formes insolites.
- **Plus doux** : relations et attention, en écartant les mots-clés d'horreur,
  de violence et de malaise. Ce n'est pas une garantie d'absence de contenu sensible.
- **Plus profond** : mémoire, société, temps, questions humaines et contemplation.

Chaque phrase est une variation poétique construite sur les données disponibles,
pas un résumé inventé ni une justification chiffrée. Aucune intelligence artificielle
distante ni nouvelle dépendance n'est nécessaire.

## Le carnet et le partage

Les rêves sont gardés sur l'appareil, séparément pour chaque compte du navigateur.
Vingt rêves de quarante films au maximum peuvent être conservés. Ils restent
consultables sans compte ; le partage transporte le nom choisi, l'image, les films
et les chemins dans un lien. Il n'inclut aucune note personnelle, aucun profil,
aucun identifiant de membre ni adresse électronique. Un lien reçu n'est pas
enregistré dans le carnet tant que la personne ne choisit pas de le garder.

Cette approche permet d'ajouter le carnet sans écrire dans les données des membres
ni modifier les règles Firebase. Une synchronisation entre appareils constituerait
une évolution distincte, à décider plus tard.

## À éprouver

Les associations sont littérales lorsque le catalogue est peu descriptif. Une
couleur peut évoquer une lumière plutôt qu'un sujet ; le parcours doit garder cette
liberté, sans promettre de comprendre les souvenirs intimes de la personne.

La validation utilisera le catalogue public et des profils fictifs : départ libre
et départ par une image proposée, trois chemins distincts, absence de répétition,
retour en arrière, nom, conservation, relecture, reprise, partage sur un nouveau
navigateur, lien malformé, téléphone à 360 pixels, ordinateur, jour et néon.

## Questions à valider

- [ ] Le ton des images et des phrases laisse-t-il assez de place à l'imaginaire ?
- [ ] Les trois chemins se distinguent-ils assez sans devenir un questionnaire ?
- [ ] Le carnet gardé sur l'appareil et le partage par lien conviennent-ils ?
