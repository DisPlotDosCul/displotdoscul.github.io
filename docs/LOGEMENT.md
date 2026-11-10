# Cap Logement

Espaces privés de recherche de logement : Licia, Cloche, Violette. Chaque personne se connecte
(Google ou lien par e-mail) et ne voit que son espace. Licia voit tout et gère les accès.

## Comment c'est protégé

- Le dépôt est public : les pages de chaque espace y sont **chiffrées** (`logement/espaces/<espace>.json`,
  AES-GCM — Advanced Encryption Standard en mode Galois/Counter).
- La clé de chaque espace est dans Firestore (projet Firebase **à part**, sans lien avec le Ciné-club).
  Les règles (`firestore-logement.rules`) ne la donnent qu'aux adresses autorisées pour cet espace et à Licia.
- Les clés des espaces sont dérivées d'une **clé de maintenance** que seule Licia détient.
  Elle n'est écrite nulle part dans le dépôt. Sans elle, personne (Claude compris) ne peut modifier les pages.
- Le calculateur (`logement/calcul.html`) est public et générique ; les réglages de chacune sont dans son espace chiffré.

## Mise en route (une seule fois, console Firebase)

1. Créer un projet Firebase (par exemple `cap-logement-displotdoscul`).
2. Authentication › Méthode de connexion : activer **Google** et **Adresse e-mail / Lien par e-mail (sans mot de passe)**.
3. Authentication › Paramètres › Domaines autorisés : ajouter `displotdoscul.github.io`.
4. Firestore Database : créer la base (mode production, région Europe), puis Règles : coller `firestore-logement.rules` › Publier.
5. Paramètres du projet › Vos applications › Web : enregistrer une application, recopier `apiKey`, `authDomain`,
   `projectId`, `appId` dans `logement/firebase-config.js`.
6. Sur le site, se connecter avec l'adresse de Licia › menu ⋯ › Accès › coller la clé de maintenance › Installer les clés.
7. Ajouter l'adresse de Cloche et celle de Violette dans leur espace (ou valider leur demande quand elles se connectent).

## Modifier un espace (Claude)

```
CAP_CLE='<clé de maintenance>' python3 outils/cap_logement.py dechiffrer /tmp/cap
# modifier /tmp/cap/<espace>/*.html ou calc.json
CAP_CLE='<clé de maintenance>' python3 outils/cap_logement.py chiffrer /tmp/cap
```

Chaque fichier `.html` d'un espace devient un onglet (`carte`, `annonces`, `bondy`…), `calc.json` règle le calculateur.

## Sauvegardes

- Code et pages : tout l'historique est sur GitHub ; la branche `main` est protégée contre l'effacement
  et la réécriture. Une copie du dépôt part aussi chaque mois dans le Google Drive de Licia.
- Ciné-club : les données vivent dans Firebase, pas sur GitHub. Bouton **💾 Tout sauvegarder**
  (profil de l'administratrice) une fois par mois, et ranger le fichier dans Google Drive.
- Cap Logement : Firestore ne contient que les clés et la liste des accès ; tout se reconstruit avec la clé de maintenance.

Ancienne version (avant novembre 2026) : pages chiffrées avec un code commun, toujours présentes dans l'historique Git.
