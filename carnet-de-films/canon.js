/* Le Canon des artistes, dans le Ciné-club : les quatre classements, et un lien vers la fiche quand le film est au catalogue. */
(function(){
var inDir = {}, inImg = {}, inCut = {}, inNyt = {};
DIR.forEach(function(id,i){ inDir[id] = i+1; });
NYT.forEach(function(id,i){ inNyt[id] = i+1; });
IMG.forEach(function(r,i){ inImg[r[0]] = { rank: i < 10 ? i+1 : null, who: r[1] }; });
CUT.forEach(function(r){ inCut[r[1]] = { rank: r[0], who: r[2] }; });

function esc(s){ return String(s).replace(/[&<>"]/g, function(c){ return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]; }); }
function norm(s){ return String(s).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }
function tkey(s){ return norm(s).replace(/\(serie\)/g, "").replace(/^(le|la|les|l'|the|un|une) /, "").replace(/[^a-z0-9]+/g, ""); }

// Films du canon présents au catalogue du Ciné-club : même titre (français ou original) et même année, à un an près.
var CC = {};
function matchCatalogue(rows){
  var idx = {};
  rows.forEach(function(r){ var k = tkey(r.t); if (k) (idx[k] = idx[k] || []).push(r); });
  Object.keys(F).forEach(function(id){
    var f = F[id], found = null;
    [f[0], f[1]].forEach(function(t){
      if (found || !t) return;
      (idx[tkey(t)] || []).forEach(function(r){ if (!found && Math.abs((+r.y || 0) - f[2]) <= 1) found = r.id; });
    });
    if (found) CC[id] = found;
  });
  render();
}
function csvRows(text){
  var out = [], lines = text.split(/\r?\n/).slice(1);
  lines.forEach(function(l){ var c = l.split(";"); if (c.length > 3 && c[0]) out.push({ id:c[0], t:c[1].replace(/^"|"$/g, ""), y:c[2] }); });
  return out;
}
Promise.all([
  fetch("../donnees/catalogue-films.csv", { cache:"no-cache" }).then(function(r){ return r.ok ? r.text() : ""; }).then(csvRows).catch(function(){ return []; }),
  fetch("complements.json", { cache:"no-cache" }).then(function(r){ return r.ok ? r.json() : null; }).then(function(j){
    var out = []; if (!j) return out;
    Object.keys(j.sections || {}).forEach(function(s){ (j.sections[s].films || []).forEach(function(f){ out.push({ id:f.id, t:f.t, y:f.y }); }); });
    return out;
  }).catch(function(){ return []; })
]).then(function(r){ matchCatalogue(r[0].concat(r[1])); });

function chips(id){
  var h = "";
  if (inDir[id]) h += '<span class="chip c-dir">Cinéastes ' + inDir[id] + "</span>";
  if (inImg[id]) h += '<span class="chip c-img">Image ' + (inImg[id].rank ? inImg[id].rank : "sélection") + "</span>";
  if (inCut[id]) h += '<span class="chip c-cut">Montage ' + inCut[id].rank + "</span>";
  if (inNyt[id]) h += '<span class="chip c-new">Depuis 2000 ' + inNyt[id] + "</span>";
  if (CC[id]) h += '<a class="chip c-cc" href="./#film=' + encodeURIComponent(CC[id]) + '">Fiche ↗</a>';
  return h;
}
function nLists(id){ return (inDir[id]?1:0) + (inImg[id]?1:0) + (inCut[id]?1:0) + (inNyt[id]?1:0); }

function rows(view){
  if (view === "cineastes") return DIR.map(function(id,i){ return { id:id, rank:String(i+1) }; });
  if (view === "image") return IMG.map(function(r,i){ return { id:r[0], rank: i<10 ? String(i+1) : "·", small: i>=10, credit:"Image : " + r[1] }; });
  if (view === "montage") return CUT.map(function(r){ return { id:r[1], rank:String(r[0]), credit:"Montage : " + r[2] }; });
  if (view === "siecle") return NYT.map(function(id,i){ return { id:id, rank:String(i+1) }; });
  var ids = Object.keys(F).filter(function(id){ return nLists(id) >= 2; });
  ids.sort(function(a,b){
    var d = nLists(b) - nLists(a); if (d) return d;
    var ra = inDir[a] || 999, rb = inDir[b] || 999; if (ra !== rb) return ra - rb;
    var na = inNyt[a] || 999, nb = inNyt[b] || 999; if (na !== nb) return na - nb;
    var ca = inCut[a] ? inCut[a].rank : 999, cb = inCut[b] ? inCut[b].rank : 999; if (ca !== cb) return ca - cb;
    return F[a][2] - F[b][2];
  });
  return ids.map(function(id){ return { id:id, rank: nLists(id) + "/4", small:true }; });
}

function filmsBy(name){
  return Object.keys(F).filter(function(id){ return F[id][3] === name && nLists(id) > 0; }).sort(function(a,b){
    function key(id){
      if (inDir[id]) return inDir[id];
      if (inNyt[id]) return 100 + inNyt[id];
      if (inCut[id]) return 200 + inCut[id].rank;
      return 300 + (inImg[id].rank || 50);
    }
    return key(a) - key(b);
  });
}
function groupsFrom(list){
  var count = {}, first = {}, order = [];
  list.forEach(function(id,i){
    var n = F[id][3];
    if (!count[n]) { count[n] = 0; first[n] = i; order.push(n); }
    count[n]++;
  });
  return order.filter(function(n){ return count[n] >= 2; })
    .sort(function(a,b){ return (count[b] - count[a]) || (first[a] - first[b]); })
    .map(function(n){ return { name:n, n:count[n] }; });
}
var MASTERS = groupsFrom(DIR);
var masterNames = {}; MASTERS.forEach(function(g){ masterNames[g.name] = 1; });
var TODAY = groupsFrom(NYT).filter(function(g){ return !masterNames[g.name]; });

// Même mémoire « Vu » que l'artefact d'origine.
var KEY = "canonArtistesVu", seen = {};
try { seen = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch(e) { seen = {}; }
function save(){ try { localStorage.setItem(KEY, JSON.stringify(seen)); } catch(e) {} }

var view = "cineastes";
var valid = { cineastes:1, image:1, montage:1, siecle:1, auteurs:1, consensus:1 };
var h = (location.hash || "").slice(1);
if (valid[h]) view = h;

function render(){
  var a = ABOUT[view];
  document.documentElement.style.setProperty("--accent", a[1]);
  var about = document.getElementById("about");
  about.querySelector("h2").textContent = a[0];
  about.querySelector("p").textContent = a[2];
  document.querySelectorAll(".tab").forEach(function(t){ t.setAttribute("aria-selected", t.dataset.v === view ? "true" : "false"); });

  var q = norm(document.getElementById("q").value.trim());
  var hide = document.getElementById("hide").checked, only = document.getElementById("onlycc").checked;
  var listEl = document.getElementById("list");
  var emptyMsg = '<p class="empty">Aucun film ne correspond. Efface la recherche ou décoche les cases.</p>';

  function keep(r, extra){
    var f = F[r.id];
    if (hide && seen[r.id]) return false;
    if (only && !CC[r.id]) return false;
    if (q && norm(f[0] + " " + f[1] + " " + f[3] + " " + (r.credit || "") + " " + (extra || "")).indexOf(q) < 0) return false;
    return true;
  }
  function rowHtml(r){
    var f = F[r.id];
    var alt = f[1] ? ' · <i>' + esc(f[1]) + '</i>' : "";
    var title = CC[r.id] ? '<a href="./#film=' + encodeURIComponent(CC[r.id]) + '">' + esc(f[0]) + '</a>' : esc(f[0]);
    return '<li class="' + (seen[r.id] ? "is-seen" : "") + '">' +
      '<div class="rank' + (r.small ? " small" : "") + '">' + esc(r.rank) + '</div>' +
      '<div><div class="t">' + title + ' <span class="y">' + f[2] + '</span></div>' +
      '<div class="meta">' + (r.noDir ? "" : esc(f[3])) + (r.noDir ? (f[1] ? '<i>' + esc(f[1]) + '</i>' : "") : alt) + (r.credit ? '<br>' + esc(r.credit) : "") + '</div>' +
      '<div class="chips">' + chips(r.id) + '</div></div>' +
      '<button class="seen" data-id="' + r.id + '" aria-pressed="' + (seen[r.id] ? "true" : "false") + '">' + (seen[r.id] ? "Vu ✓" : "Vu ?") + '</button>' +
      '</li>';
  }

  if (view === "auteurs") {
    var html = "", total = 0, seenCount = 0, shown = 0;
    [["Les maîtres, selon 480 cinéastes", MASTERS], ["Aujourd'hui, selon le vote du New York Times", TODAY]].forEach(function(part){
      var partHtml = "";
      part[1].forEach(function(g){
        var ids = filmsBy(g.name), items = [];
        ids.forEach(function(id, i){
          total++; if (seen[id]) seenCount++;
          var r = { id:id, rank:String(i+1), small:true, noDir:true };
          if (keep(r, g.name + " " + (BLURB[g.name] || ""))) items.push(rowHtml(r));
        });
        if (!items.length) return;
        shown += items.length;
        partHtml += '<section class="group"><h3>' + esc(g.name) + '</h3>' +
          (BLURB[g.name] ? '<p class="blurb">' + esc(BLURB[g.name]) + '</p>' : "") +
          '<ol>' + items.join("") + '</ol></section>';
      });
      if (partHtml) html += '<h2 class="part">' + esc(part[0]) + '</h2>' + partHtml;
    });
    listEl.innerHTML = html || emptyMsg;
    document.getElementById("count").textContent = (MASTERS.length + TODAY.length) + " cinéastes · " + total + " films · " + seenCount + " déjà vus" + (shown !== total ? " · " + shown + " affichés" : "");
    return;
  }

  var all = rows(view), out = [], shown2 = 0, seen2 = 0, inCc = 0;
  all.forEach(function(r){
    if (seen[r.id]) seen2++;
    if (CC[r.id]) inCc++;
    if (!keep(r)) return;
    shown2++;
    out.push(rowHtml(r));
  });
  listEl.innerHTML = out.length ? '<ol>' + out.join("") + '</ol>' : emptyMsg;
  document.getElementById("count").textContent = all.length + " films · " + inCc + " dans le Ciné-club · " + seen2 + " déjà vus" + (shown2 !== all.length ? " · " + shown2 + " affichés" : "");
}

document.getElementById("tabs").addEventListener("click", function(e){
  var t = e.target.closest(".tab"); if (!t) return;
  view = t.dataset.v;
  try { history.replaceState(null, "", "#" + view); } catch(err) {}
  render();
});
document.getElementById("list").addEventListener("click", function(e){
  var b = e.target.closest(".seen"); if (!b) return;
  var id = b.dataset.id;
  if (seen[id]) delete seen[id]; else seen[id] = 1;
  save(); render();
});
document.getElementById("q").addEventListener("input", render);
document.getElementById("hide").addEventListener("change", render);
document.getElementById("onlycc").addEventListener("change", render);
render();
})();
