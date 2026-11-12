/* Cap Logement · organisation des pages : une partie à la fois, textes longs repliés, listes par 15. */
(function(){
"use strict";
if(document.documentElement.dataset.dz)return;document.documentElement.dataset.dz="1";
var page=(location.pathname.split("/").pop()||"index.html").replace(".html","");
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
var SHORT={"Coins à viser":"Coins","Mes critères":"Critères","Classement":"Zones","Plan d'arrivée":"Plan","Pour toi":"Pour toi"};
var store={get:function(k){try{return sessionStorage.getItem(k)}catch(e){return null}},set:function(k,v){try{sessionStorage.setItem(k,v)}catch(e){}}};

/* ---------- Pages de session : onglets ---------- */
function sessionTabs(){
 var nav=$(".jump");if(!nav)return;
 var links=$$("a[href^='#']",nav),ids=links.map(function(a){return a.getAttribute("href").slice(1)}).filter(function(id){return document.getElementById(id)});
 if(!ids.length)return;
 links.forEach(function(a){var t=a.lastChild;if(t&&t.nodeType===3){var s=t.textContent.replace(/\s+/g," ").trim();if(SHORT[s])t.textContent=SHORT[s]}a.title=a.textContent.trim()});
 var key="dz-tab-"+page,cur=store.get(key);if(ids.indexOf(cur)<0)cur=ids[0];
 function show(id,scroll){cur=id;store.set(key,id);
  ids.forEach(function(x){var el=document.getElementById(x);if(el){el.style.display=x!==id?"none":"";if(x===id&&el.tagName==="DETAILS")el.open=true}});
  links.forEach(function(a){a.setAttribute("aria-current",a.getAttribute("href")==="#"+id?"true":"false")});
  if(scroll!==false)window.scrollTo(0,0)}
 links.forEach(function(a){a.addEventListener("click",function(e){e.preventDefault();show(a.getAttribute("href").slice(1))})});
 show(cur,false);
 /* Choisir un quartier ailleurs que sur la carte : on revient à la carte */
 var fiche=document.getElementById("fiche"),lastClick=0;
 document.addEventListener("click",function(){lastClick=Date.now()},true);
 if(fiche&&ids.indexOf("carte")>=0)new MutationObserver(function(){if(cur!=="carte"&&Date.now()-lastClick<600){show("carte",false);setTimeout(function(){fiche.scrollIntoView({block:"start"})},30)}}).observe(fiche,{childList:true,subtree:true});
}

/* ---------- Annonces : onglets créés depuis les titres ---------- */
function annTabs(){
 var wrap=$(".wrap");if(!wrap||$(".dz-tabs"))return;
 var secs=$$(":scope > section",wrap).filter(function(s){return $("h2",s)});if(secs.length<2)return;
 var NAMES=["Nouvelles","Chercher","Suivies","Prompt","Critères"];
 var bar=document.createElement("nav");bar.className="dz-tabs";bar.setAttribute("aria-label","Parties");
 secs.forEach(function(s,i){var b=document.createElement("button");b.type="button";var h=$("h2",s);
  var full=(h.firstChild&&h.firstChild.nodeType===3?h.firstChild.textContent:h.textContent).trim();
  b.textContent=secs.length===5?NAMES[i]:full.split(" ")[0];b.title=full;b.dataset.i=i;bar.appendChild(b)});
 var head=$("header",wrap);(head?head:wrap.firstChild).insertAdjacentElement(head?"afterend":"beforebegin",bar);
 var key="dz-tab-annonces",cur=parseInt(store.get(key)||"0",10)||0;if(cur>=secs.length)cur=0;
 function show(i){cur=i;store.set(key,String(i));secs.forEach(function(s,j){s.style.display=j!==i?"none":""});
  $$("button",bar).forEach(function(b){b.setAttribute("aria-current",+b.dataset.i===i?"true":"false")});
  var reset=$("#resetBtn");if(reset&&reset.parentElement)reset.parentElement.style.display=i!==secs.length-1?"none":""}
 bar.addEventListener("click",function(e){var b=e.target.closest("button");if(b){show(+b.dataset.i);window.scrollTo(0,0)}});
 show(cur);
}

/* ---------- Textes longs repliés ---------- */
function foldSubs(){
 $$("section p.sub").forEach(function(p){
  if(p.closest("details")||p.closest("h2")||p.tagName!=="P")return;
  var d=document.createElement("details");d.className="dz-why";var s=document.createElement("summary");s.textContent="Comment c'est calculé";
  d.appendChild(s);p.parentNode.insertBefore(d,p);d.appendChild(p);
  var sync=function(){d.style.display=p.textContent.trim()?"":"none"};sync();new MutationObserver(sync).observe(p,{childList:true,characterData:true,subtree:true});
 });
}

/* ---------- Listes par 15 ---------- */
function limit(list,step){
 if(!list||list.dataset.dzLim)return;step=step||15;list.dataset.dzLim=String(step);
 var box=document.createElement("div");box.className="dz-more";var b=document.createElement("button");b.type="button";b.className="dz-key";
 box.appendChild(b);list.insertAdjacentElement("afterend",box);
 function apply(){var items=Array.prototype.filter.call(list.children,function(x){return x.nodeType===1&&!x.classList.contains("empty")}),lim=parseInt(list.dataset.dzLim,10);
  items.forEach(function(x,i){x.style.display=i<lim?"":"none"});var rest=items.length-lim;box.style.display=rest<=0?"none":"";
  if(rest>0)b.textContent="Voir "+Math.min(step,rest)+" de plus ("+rest+")"}
 b.addEventListener("click",function(){list.dataset.dzLim=String(parseInt(list.dataset.dzLim,10)+step);apply()});
 new MutationObserver(apply).observe(list,{childList:true});apply();
}

/* ---------- Accueil : barre sur une ligne ---------- */
function indexBar(){
 var bar=$("#bar");if(!bar||$(".dz-theme",bar))return;
 var home=$("#home",bar);if(home){var t=home.lastChild;if(t&&t.nodeType===3){var sp=document.createElement("span");sp.className="dz-hide";sp.textContent=t.textContent;home.replaceChild(sp,t)}home.title="Changer de session"}
 var add=$("#addbtn",bar);if(add){var tn=Array.prototype.filter.call(add.childNodes,function(n){return n.nodeType===3&&n.textContent.trim()})[0];if(tn){var s2=document.createElement("span");s2.className="dz-lbl";s2.textContent=tn.textContent;add.replaceChild(s2,tn)}add.title="Mes infos"}
 var calc=$("#calcbtn",bar);if(calc){var tc=Array.prototype.filter.call(calc.childNodes,function(n){return n.nodeType===3&&n.textContent.trim()})[0];if(tc)tc.textContent="Calcul";calc.title="Calculateur"}
 ["#annbtn","#calcbtn","#newsbtn"].forEach(function(q){var b=$(q,bar);if(b){var ic=$("svg",b);if(ic)ic.style.display="none"}});
 var modes=$(".modes",bar);if(!modes)return;var mb=$$("button",modes);if(!mb.length)return;
 var ic={light:"☀︎",soft:"💡",dark:"☾"};var tb=document.createElement("button");tb.type="button";tb.className="dz-key dz-theme";
 function lab(){var on=mb.filter(function(b){return b.getAttribute("aria-pressed")==="true"})[0]||mb[0];var sv=$("svg",on);tb.innerHTML="";if(sv)tb.appendChild(sv.cloneNode(true));else tb.textContent=ic[on.dataset.th]||"☀";tb.title="Affichage : "+(on.title||"")}
 tb.addEventListener("click",function(){var i=mb.findIndex(function(b){return b.getAttribute("aria-pressed")==="true"});mb[(i+1)%mb.length].click();lab()});
 modes.insertAdjacentElement("afterend",tb);lab();new MutationObserver(lab).observe(modes,{attributes:true,subtree:true,attributeFilter:["aria-pressed"]});
}

function run(){
 try{if($(".jump"))sessionTabs()}catch(e){}
 try{if(page==="annonces"){annTabs();limit($("#feed"));limit($("#annList"))}}catch(e){}
 try{foldSubs()}catch(e){}
 try{if(page!=="calculateur"){limit($("#toi"));limit($("ol#rank"))}}catch(e){}
 try{if(page==="index"||page==="")indexBar()}catch(e){}
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run);else run();
})();
