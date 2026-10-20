# Courriers de connexion

On peut améliorer les chances de réception ; un changement du fichier HTML ne
peut pas garantir l'arrivée dans la boîte principale. Aucun message de connexion
réel n'a été envoyé pendant les tests. L'application demande désormais les messages
Firebase en français.

L'état actuel du domaine d'envoi et de son authentification n'a pas été vérifié
dans la console Firebase. Une configuration centrale demande l'accès à cette
console et à un domaine dont on contrôle le système de noms de domaine (DNS).
Le site GitHub Pages ne fournit pas cet accès à lui seul.

La marche à suivre, une fois ces accès disponibles :

1. Dans Firebase Authentication, ouvrir les modèles de messages et relever le
   domaine expéditeur, le nom affiché et le domaine des liens.
2. Si un domaine personnel est retenu, suivre la procédure Firebase et publier
   exactement les enregistrements fournis par la console, puis lancer sa validation.
3. Vérifier l'autorisation des serveurs d'envoi (Sender Policy Framework, SPF),
   la signature des messages (DomainKeys Identified Mail, DKIM) et la politique
   d'authentification et de rapports (Domain-based Message Authentication, Reporting
   and Conformance, DMARC), selon la configuration du fournisseur d'envoi.
4. Effectuer un essai consenti sur les messageries des membres et examiner les
   résultats d'authentification du message reçu. Le filtre personnel peut aussi
   apprendre lorsqu'un destinataire marque un message légitime comme non indésirable.

Les réglages du domaine et de l'expéditeur n'ont pas été modifiés par cette PR.
Cette vérification reste distincte de l'évolution du site.

Sources officielles consultées le 20 octobre 2026 :

- [Firebase — domaine personnalisé pour les e-mails d'authentification](https://firebase.google.com/docs/auth/email-custom-domain?hl=fr).
- [Firebase — gestionnaires personnalisés et cohérence de la langue des messages](https://firebase.google.com/docs/auth/custom-email-handler).
- [Google — recommandations aux expéditeurs de messages](https://support.google.com/mail/answer/81126?hl=fr).
