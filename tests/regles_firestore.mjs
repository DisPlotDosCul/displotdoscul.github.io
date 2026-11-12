// Vérifie firestore.rules dans l'émulateur Firestore (12 novembre) : 59 cas (profils, carnets privés, amis,
// commentaires privés, playlists, films ajoutés, messages, catalogue).
// Lancer : npm i firebase-tools @firebase/rules-unit-testing firebase
//          npx firebase emulators:exec --project demo-cineclub --only firestore "node tests/regles_firestore.mjs"
// L'adresse de l'administratrice n'est jamais écrite : pour le test, son empreinte est remplacée par celle d'une adresse fictive.
import { createHash } from "node:crypto";
import { initializeTestEnvironment, assertSucceeds, assertFails } from "@firebase/rules-unit-testing";
import { doc, setDoc, getDoc, updateDoc, deleteDoc, collection, query, where, getDocs, deleteField, arrayUnion, writeBatch } from "firebase/firestore";
import fs from "node:fs";
const ADMIN_TEST = createHash("sha256").update("admin@test.invalid").digest("base64");
const RULES = fs.readFileSync(new URL("../firestore.rules", import.meta.url), "utf8").replace(/toBase64\(\) == '[^']+'/, "toBase64() == '" + ADMIN_TEST + "'");
const env = await initializeTestEnvironment({ projectId: "demo-cineclub", firestore: { rules: RULES, host: "127.0.0.1", port: 8085 } });
let ok = 0, ko = 0;
async function t(name, p) { try { await p; ok++; } catch (e) { ko++; console.log("ÉCHEC", name, e.message.slice(0, 200)); } }
const db = (uid, extra) => uid ? env.authenticatedContext(uid, extra || {}).firestore() : env.unauthenticatedContext().firestore();
const admin = db("adm", { email: "admin@test.invalid", email_verified: true });
const A = db("alice"), B = db("bob"), C = db("carol"), Z = db(null);
// Données de départ (sans règles)
await env.withSecurityRulesDisabled(async (ctx) => {
  const f = ctx.firestore();
  await setDoc(doc(f, "profils/alice"), { pseudo: "Alice", pid: "m_alice", slug: "m_alice", amis: ["bob"] });
  await setDoc(doc(f, "profils/bob"), { pseudo: "Bob", pid: "m_bob", slug: "m_bob", amis: ["alice"], recoit: "amis" });
  await setDoc(doc(f, "profils/carol"), { pseudo: "Carol", pid: "m_carol", slug: "m_carol" });
  await setDoc(doc(f, "profils/arthur"), { pseudo: "Arthur", pid: "arthur", slug: "m_arthur" });
  await setDoc(doc(f, "profils/vieux"), { pseudo: "Vieux", slug: "vieux" });
  await setDoc(doc(f, "profils/bulle"), { pseudo: "Bulle", pid: "m_bulle", bulle: true });
  await setDoc(doc(f, "conseils/arthur__matrix-1999"), { prenom: "arthur", film: "matrix-1999", uid: "adm", ajout: "x" });
  await setDoc(doc(f, "conseils/vieux__a"), { prenom: "arthur", film: "a" });
  await setDoc(doc(f, "carnets/bob__rep"), { uid: "bob", part: "rep", vis: "amis", lect: ["alice"], data: { x: { note10: 8 } } });
  await setDoc(doc(f, "carnets/bob__liste"), { uid: "bob", part: "liste", vis: "tous", lect: [], data: {} });
  await setDoc(doc(f, "carnets/bob__reglages"), { uid: "bob", part: "reglages", vis: "moi", lect: [], data: { voir: {} } });
  await setDoc(doc(f, "commentairesPrives/c1"), { uid: "bob", film: "x", texte: "secret", vis: "amis", lect: ["alice"] });
});
// Profils
await t("profil créé par un autre", assertFails(setDoc(doc(C, "profils/carol2"), { pseudo: "x" })));
await t("profil créé avec m_", assertSucceeds(setDoc(doc(db("carol2"), "profils/carol2"), { pseudo: "C2", pid: "m_carol2", slug: "m_carol2", rep: {}, liste: {} })));
await t("profil créé avec la playlist d'un autre", assertFails(setDoc(doc(db("dan"), "profils/dan"), { pseudo: "Dan", pid: "arthur", slug: "arthur" })));
await t("profil créé licia par un membre", assertFails(setDoc(doc(db("eve"), "profils/eve"), { pseudo: "Eve", pid: "licia", slug: "licia" })));
await t("admin crée licia", assertSucceeds(setDoc(doc(admin, "profils/adm"), { pseudo: "Licia", pid: "licia", slug: "licia", rep: {}, liste: {} })));
await t("changer son pseudo", assertSucceeds(updateDoc(doc(A, "profils/alice"), { pseudo: "Alix", vis: "perso", recoit: "amis", amis: arrayUnion("carol") })));
await t("changer son pid soi-même", assertFails(updateDoc(doc(A, "profils/alice"), { pid: "arthur" })));
await t("changer son slug", assertFails(updateDoc(doc(A, "profils/alice"), { slug: "arthur" })));
await t("ancien compte : pid = slug", assertSucceeds(updateDoc(doc(db("vieux"), "profils/vieux"), { pid: "vieux" })));
await t("admin relie un compte", assertSucceeds(updateDoc(doc(admin, "profils/carol"), { pid: "jean" })));
await t("admin ne change pas le pseudo", assertFails(updateDoc(doc(admin, "profils/carol"), { pseudo: "Z" })));
await t("profils non lus sans compte", assertFails(getDoc(doc(Z, "profils/alice"))));
await t("migration en un lot", assertSucceeds((() => { const b = writeBatch(A); b.set(doc(A, "carnets/alice__rep"), { uid: "alice", part: "rep", vis: "tous", lect: [], data: { m: { note10: 9 } } }, { merge: true });
  b.set(doc(A, "carnets/alice__reglages"), { uid: "alice", part: "reglages", vis: "moi", lect: [] }, { merge: true });
  b.update(doc(A, "profils/alice"), { carnet: 1, rep: deleteField(), liste: deleteField() }); return b.commit(); })()));
// Carnets
await t("carnet : mauvais identifiant", assertFails(setDoc(doc(A, "carnets/bob__rep2"), { uid: "alice", part: "rep", vis: "tous", lect: [] })));
await t("carnet : écrire chez un autre", assertFails(setDoc(doc(A, "carnets/bob__quiz"), { uid: "bob", part: "quiz", vis: "tous", lect: [] })));
await t("carnet : partie inconnue", assertFails(setDoc(doc(A, "carnets/alice__x"), { uid: "alice", part: "x", vis: "tous", lect: [] })));
await t("réglages lisibles par tous refusés", assertFails(setDoc(doc(A, "carnets/alice__reglages"), { uid: "alice", part: "reglages", vis: "tous", lect: [] })));
await t("ami lit le carnet amis", assertSucceeds(getDoc(doc(A, "carnets/bob__rep"))));
await t("non-ami ne lit pas", assertFails(getDoc(doc(C, "carnets/bob__rep"))));
await t("tous lisent le public", assertSucceeds(getDoc(doc(C, "carnets/bob__liste"))));
await t("sans compte : rien", assertFails(getDoc(doc(Z, "carnets/bob__liste"))));
await t("réglages d'un autre illisibles", assertFails(getDoc(doc(A, "carnets/bob__reglages"))));
await t("requête vis == tous", assertSucceeds(getDocs(query(collection(C, "carnets"), where("vis", "==", "tous")))));
await t("requête lect contient moi", assertSucceeds(getDocs(query(collection(A, "carnets"), where("lect", "array-contains", "alice")))));
await t("requête lect contient un autre", assertFails(getDocs(query(collection(A, "carnets"), where("lect", "array-contains", "carol")))));
await t("requête uid == moi", assertSucceeds(getDocs(query(collection(A, "carnets"), where("uid", "==", "alice")))));
await t("requête sans filtre", assertFails(getDocs(collection(A, "carnets"))));
await t("mise à jour d'une note", assertSucceeds(updateDoc(doc(A, "carnets/alice__rep"), { "data.m": { note10: 7 } })));
await t("changer ses lecteurs", assertSucceeds(setDoc(doc(A, "carnets/alice__rep"), { uid: "alice", part: "rep", vis: "amis", lect: ["bob"] }, { merge: true })));
await t("le public ne voit plus", assertFails(getDoc(doc(C, "carnets/alice__rep"))));
await t("bob voit", assertSucceeds(getDoc(doc(B, "carnets/alice__rep"))));
// Commentaires privés
await t("commentaire privé lu par l'ami", assertSucceeds(getDoc(doc(A, "commentairesPrives/c1"))));
await t("commentaire privé caché aux autres", assertFails(getDoc(doc(C, "commentairesPrives/c1"))));
await t("requête commentaires privés", assertSucceeds(getDocs(query(collection(A, "commentairesPrives"), where("lect", "array-contains", "alice")))));
await t("créer un commentaire privé", assertSucceeds(setDoc(doc(A, "commentairesPrives/c2"), { uid: "alice", film: "x", texte: "t", vis: "proches", lect: ["bob"] })));
await t("commentaire privé au nom d'un autre", assertFails(setDoc(doc(A, "commentairesPrives/c3"), { uid: "bob", film: "x", texte: "t", vis: "amis", lect: [] })));
await t("admin supprime un commentaire privé", assertSucceeds(deleteDoc(doc(admin, "commentairesPrives/c2"))));
// Playlists
await t("ajouter à sa playlist", assertSucceeds(setDoc(doc(B, "conseils/m_bob__x"), { prenom: "m_bob", film: "x", uid: "bob" })));
await t("ajouter à la playlist d'un autre", assertFails(setDoc(doc(B, "conseils/arthur__x"), { prenom: "arthur", film: "x", uid: "bob" })));
await t("modifier la playlist d'un autre", assertFails(setDoc(doc(B, "conseils/arthur__matrix-1999"), { prenom: "m_bob", film: "matrix-1999", uid: "bob" })));
await t("Arthur modifie son ancienne playlist", assertSucceeds(setDoc(doc(db("arthur"), "conseils/arthur__matrix-1999"), { prenom: "arthur", film: "matrix-1999", uid: "arthur", mot: "génial" })));
await t("Arthur retire un ancien film sans uid", assertSucceeds(deleteDoc(doc(db("arthur"), "conseils/vieux__a"))));
await t("Bob ne retire pas chez Arthur", assertFails(deleteDoc(doc(B, "conseils/arthur__matrix-1999"))));
await t("admin écrit dans une playlist", assertSucceeds(setDoc(doc(admin, "conseils/jean__y"), { prenom: "jean", film: "y", uid: "adm" })));
// Ajouts
await t("ajout par un membre", assertSucceeds(setDoc(doc(A, "ajouts/film-2020"), { fid: "film-2020", t: "Un titre très long ".repeat(30), uid: "alice" })));
await t("ajout lu sans compte", assertSucceeds(getDoc(doc(Z, "ajouts/film-2020"))));
await t("ajout sans compte refusé", assertFails(setDoc(doc(Z, "ajouts/f2"), { fid: "f2", t: "x" })));
await t("ajout modifié par un autre", assertFails(updateDoc(doc(B, "ajouts/film-2020"), { t: "y" })));
await t("ajout retiré par l'admin", assertSucceeds(deleteDoc(doc(admin, "ajouts/film-2020"))));
// Messages
const m = (to, type, extra) => Object.assign({ from: "carol", to, type, mot: "", ajout: "x" }, extra || {});
await t("conseil à Bob (amis seulement) d'une non-amie", assertFails(setDoc(doc(C, "messages/m1"), m("bob", "conseil", { mot: "vois-le" }))));
await t("demande d'ami à Bob", assertSucceeds(setDoc(doc(C, "messages/m2"), m("bob", "ami-dem"))));
await t("conseil d'Alice (amie) à Bob", assertSucceeds(setDoc(doc(A, "messages/m3"), { from: "alice", to: "bob", type: "conseil", mot: "x" })));
await t("demande d'ami dans la bulle", assertFails(setDoc(doc(C, "messages/m4"), m("bulle", "ami-dem"))));
await t("Bob marque lu", assertSucceeds(updateDoc(doc(B, "messages/m2"), { lu: true })));
await t("Bob ne change pas le type", assertFails(updateDoc(doc(B, "messages/m2"), { type: "x" })));
await t("Carol annule sa demande", assertSucceeds(deleteDoc(doc(C, "messages/m2"))));
await t("conseil à tous", assertSucceeds(setDoc(doc(C, "messages/m5"), m("*", "conseil", { mot: "x" }))));
// Catalogue
await t("catalogue lu sans compte", assertSucceeds(getDoc(doc(Z, "films/x"))));
await t("catalogue écrit par un membre", assertFails(setDoc(doc(A, "films/x"), { a: 1 })));
await t("catalogue écrit par l'admin", assertSucceeds(setDoc(doc(admin, "films/rangement"), { a: 1 })));
console.log(`${ok} réussis, ${ko} échoués`);
await env.cleanup();
process.exit(ko ? 1 : 0);
