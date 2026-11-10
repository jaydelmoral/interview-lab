/* Shared helpers for landing.html and exam.html (no dependencies). */
const $ = id => document.getElementById(id);
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
/* Links that come from content files (question sources): only http(s) may become a clickable link, never javascript: or data: */
const safeUrl = u => (/^https?:\/\//i.test(String(u == null ? '' : u).trim()) ? String(u).trim() : '#');

function store(key, val){
  try { if (val === undefined) return JSON.parse(localStorage.getItem(key)); localStorage.setItem(key, JSON.stringify(val)); }
  catch (e) { return null; }
}

/* ---- language and strings ---- */
let lang = store('lang') || ((navigator.language || 'es').toLowerCase().startsWith('en') ? 'en' : 'es');
const STR = {es: {}, en: {}};
function addStrings(o){ for (const l of ['es', 'en']) Object.assign(STR[l], o[l] || {}); }
const T = k => (STR[lang][k] !== undefined ? STR[lang][k] : (STR.es[k] !== undefined ? STR.es[k] : k));

addStrings({
  es: {navHome: 'Inicio', navEval: 'Cómo se evalúa', navBuild: 'Crear simulacro', navPractice: 'Práctica libre', navHistory: 'Historial', cta: 'Iniciar simulación', theme: 'Cambiar entre modo claro y oscuro',
       foot: 'Interview Lab · código Apache-2.0 · ejercicios CC BY 4.0 · Javier Morales Barrera (@jaydelmoral) con Claude (Anthropic). Logotipos: © Collaboration, todos los derechos reservados. Proyecto independiente, sin relación con Oracle, plataformas de pruebas ni empresas mencionadas. El código que escribes se ejecuta en tu equipo.',
       translate: '🌐 Convertir al español para mayor ayuda', original: '🌐 Ver el original en inglés', hover: 'Traducir al pasar el cursor',
       noTr: 'Este problema no tiene traducción (falta problem.es.md)', err: 'Error',
       dSample: 'Ejemplo ilustrativo', dSampleNote: 'Datos de muestra: así se verá tu reporte al terminar el simulacro.', dOverall: 'Resultado global', dSectionsOk: 'Secciones aprobadas',
       dTime: 'Tiempo usado', dHits: 'Aciertos', dOf: 'de', dPass: 'umbral 60 %', dBySection: 'Resultado por sección', dTimeBy: 'Tiempo por sección', dRadar: 'Perfil por módulo',
       dOpp: 'Áreas de oportunidad', dOppNone: 'Sin áreas débiles detectadas: mantén el ritmo y sube la dificultad.', dPrio: 'Prioritaria', dReinf: 'Reforzar', dWatch: 'Vigilar',
       dMissed: 'Preguntas para repasar', dMissedNone: 'No fallaste ninguna pregunta de opción múltiple.', dStrong: 'Sólido', dMid: 'En camino', dWeak: 'A reforzar', dExpected: 'Respuesta correcta',
       dPrint: 'Guardar como PDF', dSources: 'Fuentes', dMin: 'min', dTests: 'pruebas', dQuestions: 'preguntas', dFails: n => (n === 1 ? '1 fallo' : n + ' fallos'),
       tipTag: 'Repasa este tema: abajo están las preguntas que fallaste, con su explicación.', tipSection: 'Quedó bajo el umbral de 60 %. Practica sus ejercicios en «Práctica libre» y repite el simulacro.',
       tipPS: 'Descompón el problema y escribe los casos límite antes de codificar.', tipRel: 'Cubre entradas vacías, nulos y límites: ahí fallan las pruebas ocultas.', tipLang: 'Repasa la API y la semántica del lenguaje que usaste.',
       catPS: 'Resolución de problemas', catRel: 'Fiabilidad', catLang: 'Conocimiento del lenguaje'},
  en: {navHome: 'Home', navEval: 'How you are scored', navBuild: 'Build a simulation', navPractice: 'Free practice', navHistory: 'History', cta: 'Start simulation', theme: 'Switch between light and dark mode',
       foot: 'Interview Lab · code Apache-2.0 · exercises CC BY 4.0 · Javier Morales Barrera (@jaydelmoral) with Claude (Anthropic). Logos: © Collaboration, all rights reserved. Independent project, not affiliated with Oracle, testing platforms or any company mentioned. The code you write runs on your machine.',
       translate: '🌐 Show in Spanish for extra help', original: '🌐 Show the English original', hover: 'Translate on hover',
       noTr: 'This problem has no Spanish translation (problem.es.md is missing)', err: 'Error',
       dSample: 'Illustrative example', dSampleNote: 'Sample data: this is how your report will look when you finish the simulation.', dOverall: 'Overall result', dSectionsOk: 'Sections passed',
       dTime: 'Time used', dHits: 'Correct', dOf: 'of', dPass: '60 % line', dBySection: 'Result by section', dTimeBy: 'Time by section', dRadar: 'Profile by module',
       dOpp: 'Opportunity areas', dOppNone: 'No weak areas detected: keep the pace and raise the difficulty.', dPrio: 'Priority', dReinf: 'Reinforce', dWatch: 'Watch',
       dMissed: 'Questions to review', dMissedNone: 'You did not miss any multiple-choice question.', dStrong: 'Solid', dMid: 'On track', dWeak: 'Needs work', dExpected: 'Correct answer',
       dPrint: 'Save as PDF', dSources: 'Sources', dMin: 'min', dTests: 'tests', dQuestions: 'questions', dFails: n => (n === 1 ? '1 miss' : n + ' misses'),
       tipTag: 'Review this topic: the questions you missed are below, with their explanation.', tipSection: 'It fell under the 60 % line. Practise its exercises in “Free practice” and retake the simulation.',
       tipPS: 'Break the problem down and write the edge cases before coding.', tipRel: 'Cover empty inputs, nulls and limits: that is where the hidden tests fail.', tipLang: 'Review the API and semantics of the language you used.',
       catPS: 'Problem solving', catRel: 'Reliability', catLang: 'Language knowledge'}
});

/* ---- API ---- */
async function api(path, opt){
  const r = await fetch(path, opt);
  const j = await r.json().catch(() => ({}));
  if (!r.ok) { const e = new Error(j.error || ('HTTP ' + r.status)); e.data = j; throw e; }
  return j;
}
const post = (path, payload) => api(path, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});

/* ---- Collaboration isotype (ADR-0022): the three crescents, the glint and their gradients are defined ONCE here and reused with <use>
        by the bar (every page), the animated layer and the step cards (landing). viewBox 0 0 480 480, ring centre (250, 240). ---- */
const ISOTYPE_DEFS = '<svg class="iso-defs" aria-hidden="true" focusable="false"><defs>'
  + '<linearGradient id="gA" gradientUnits="userSpaceOnUse" x1="10" y1="60" x2="300" y2="430"><stop class="s-a1" offset="0"/><stop class="s-a2" offset="1"/></linearGradient>'
  + '<linearGradient id="gB" gradientUnits="userSpaceOnUse" x1="200" y1="80" x2="470" y2="380"><stop class="s-b2" offset="0"/><stop class="s-b1" offset="1"/></linearGradient>'
  + '<linearGradient id="gC" gradientUnits="userSpaceOnUse" x1="120" y1="380" x2="380" y2="170"><stop class="s-c2" offset="0"/><stop class="s-c1" offset="1"/></linearGradient>'
  + '<linearGradient id="gG" gradientUnits="userSpaceOnUse" x1="19" y1="310" x2="19" y2="170"><stop class="s-g0" offset="0"/><stop class="s-g2" offset=".3"/><stop class="s-g1" offset=".7"/><stop class="s-g0" offset="1"/></linearGradient>'
  + '<path id="oA" d="M360.63 55.23A224 224 0 1 0 360.63 424.77A202 202 0 1 1 360.63 55.23Z"/>'
  + '<path id="oB" d="M179.5 89.25A184 184 0 1 1 179.5 390.75A166 166 0 1 0 179.5 89.25Z"/>'
  + '<path id="oC" d="M122.12 161.88A149 149 0 1 0 375.88 161.88A135 135 0 1 1 122.12 161.88Z"/></defs></svg>';
const ISOTYPE_MARK = '<use href="#oA" fill="url(#gA)"/><use href="#oB" fill="url(#gB)"/><use href="#oC" fill="url(#gC)"/>';
/* Only brands that declare "isotype": "collaboration-o" get the vector mark and the animated O; any other brand keeps its PNG logo. */
function installIsotype(b){
  if (!b || b.isotype !== 'collaboration-o') return false;
  if (!document.querySelector('.iso-defs')) document.body.insertAdjacentHTML('afterbegin', ISOTYPE_DEFS);
  document.documentElement.classList.add('has-iso');
  return true;
}

/* ---- brand header / footer ---- */
const SVG_SUN = '<svg class="ico-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
const SVG_MOON = '<svg class="ico-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.8A8.5 8.5 0 1 1 11.2 3a6.6 6.6 0 0 0 9.8 9.8z"/></svg>';
function logoPair(set, h, name){
  if (!set) return esc(name);
  return `<img class="logo-d" src="/brand/${esc(set.dark)}" alt="${esc(name)}" style="height:${h}px"><img class="logo-l" src="/brand/${esc(set.light)}" alt="${esc(name)}" style="height:${h}px">`;
}
async function renderChrome(active, onLangChange){
  let b = {name: 'Interview Lab', logo_mark: null, logo_full: null};
  try { b = await api('/api/brand'); } catch (e) {}
  window.BRAND = b;
  installIsotype(b);
  const bar = $('appbar');
  bar.className = 'appbar';
  const lk = (id, href, key, on) => `<a href="${href}" id="${id}" class="${active === on ? 'active' : ''}"></a>`;
  bar.innerHTML = `<div class="appbar-in"><a class="brand" href="/" aria-label="${esc(b.name)}">${logoPair(b.logo_mark, 30, b.name)}</a>
    <nav class="pill-nav" aria-label="Main">${lk('navHome', '/', 'navHome', 'home')}${lk('navEval', '/#evaluacion', 'navEval', 'eval')}${lk('navBuild', '/#crear', 'navBuild', 'build')}${lk('navPractice', '/practice', 'navPractice', 'practice')}${lk('navHistory', '/history', 'navHistory', 'history')}</nav>
    <div class="actions"><select id="langSel" aria-label="Language / Idioma"><option value="es">Español</option><option value="en">English</option></select>
    <button class="icon-btn" id="themeBtn" type="button">${SVG_SUN}${SVG_MOON}</button></div></div>`;
  $('langSel').value = lang;
  $('langSel').onchange = () => { lang = $('langSel').value; store('lang', lang); chromeText(); if (onLangChange) onLangChange(); };
  $('themeBtn').onclick = () => window.setTheme(window.currentTheme() === 'dark' ? 'light' : 'dark');
  window.brandFull = h => logoPair(b.logo_full, h, b.name);
  chromeText();
}
function chromeText(){
  document.documentElement.lang = lang;
  if ($('navHome')) { for (const k of ['navHome', 'navEval', 'navBuild', 'navPractice', 'navHistory']) $(k).textContent = T(k); }
  if ($('themeBtn')) { $('themeBtn').title = T('theme'); $('themeBtn').setAttribute('aria-label', T('theme')); }
  if ($('foot')) { $('foot').className = 'foot'; $('foot').textContent = T('foot'); }
}

/* ---- minimal markdown (blocks aligned between problem.md and problem.es.md) ---- */
function splitBlocks(src){
  const out = []; let cur = [], fence = false;
  for (const line of src.split('\n')) {
    if (line.startsWith('```')) { cur.push(line); if (fence) { out.push(cur.join('\n')); cur = []; } fence = !fence; continue; }
    if (fence) cur.push(line);
    else if (!line.trim()) { if (cur.length) { out.push(cur.join('\n')); cur = []; } }
    else cur.push(line);
  }
  if (cur.length) out.push(cur.join('\n'));
  return out;
}
const inline = t => esc(t).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/`([^`]+)`/g, '<code>$1</code>');
function renderBlock(b){
  if (b.startsWith('```')) return '<pre><code>' + esc(b.split('\n').slice(1, -1).join('\n')) + '</code></pre>';
  if (/^# /.test(b)) return '<h3>' + inline(b.slice(2)) + '</h3>';
  const lines = b.split('\n');
  if (lines.every(l => /^- /.test(l))) return '<ul>' + lines.map(l => '<li>' + inline(l.slice(2)) + '</li>').join('') + '</ul>';
  return '<p>' + lines.map(inline).join('<br>') + '</p>';
}

/* Renders a problem statement into `el`; mode 'en' (original) or 'es'; hover = show Spanish paragraph on hover. */
function renderStatementInto(el, problem, mode, hover){
  const hasEs = !!problem.statement_es;
  const en = splitBlocks(problem.statement), es = hasEs ? splitBlocks(problem.statement_es) : [];
  if (mode === 'es' && hasEs) { el.innerHTML = es.map(renderBlock).join(''); return; }
  const aligned = hasEs && en.length === es.length;
  el.innerHTML = en.map((b, i) => `<div class="blk${hover && aligned && !b.startsWith('```') ? ' hoverable' : ''}" data-i="${i}">${renderBlock(b)}</div>`).join('');
  if (hover && aligned) {
    const tip = $('tip');
    el.querySelectorAll('.blk.hoverable').forEach(node => {
      const show = () => {
        tip.innerHTML = renderBlock(es[+node.dataset.i]); tip.style.display = 'block';
        const r = node.getBoundingClientRect(), h = tip.offsetHeight;
        tip.style.left = Math.max(8, Math.min(r.left, innerWidth - tip.offsetWidth - 8)) + 'px';
        tip.style.top = (r.bottom + h + 12 < innerHeight ? r.bottom + 6 : Math.max(8, r.top - h - 6)) + 'px';
      };
      node.addEventListener('mouseenter', show);
      node.addEventListener('mouseleave', () => { tip.style.display = 'none'; });
      node.addEventListener('click', show);
    });
  }
}
function hideTip(){ const t = $('tip'); if (t) t.style.display = 'none'; }
function fmtTime(ms){ const left = Math.max(0, ms); const m = Math.floor(left / 60000), s = Math.floor(left % 60000 / 1000); return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0'); }

/* ---------------------------------------------------------------------------
   Results dashboard — one renderer for the landing sample and the real final report.
   data = { sample, title, subtitle, overall (0-100),
            sections: [{title, pct, done, total, unit: 'tests'|'questions', used, allotted}],
            weak: [{label, count, tip, kind: 'section'|'tag'|'skill', pct}],
            missed: [{section, q, expected, explanation}] }
   --------------------------------------------------------------------------- */
const PASS_LINE = 60;
const levelOf = p => (p >= 80 ? 'strong' : p >= PASS_LINE ? 'mid' : 'weak');
const levelName = p => T({strong: 'dStrong', mid: 'dMid', weak: 'dWeak'}[levelOf(p)]);

function dashDonut(pct){
  const r = 52, c = 2 * Math.PI * r, lv = levelOf(pct), col = {strong: 'var(--ok)', mid: 'var(--accent)', weak: 'var(--bad)'}[lv];
  return `<svg viewBox="0 0 132 132" role="img" aria-label="${pct}%"><circle cx="66" cy="66" r="${r}" fill="none" stroke="var(--surface-2)" stroke-width="12"/>
    <circle cx="66" cy="66" r="${r}" fill="none" stroke="${col}" stroke-width="12" stroke-linecap="round" stroke-dasharray="${(c * pct / 100).toFixed(1)} ${c.toFixed(1)}" transform="rotate(-90 66 66)"/>
    <text class="t" x="66" y="66" text-anchor="middle" dominant-baseline="central">${pct}%</text></svg>`;
}
function dashRadar(items){
  const n = items.length, cx = 150, cy = 140, R = 90, pt = (i, f) => [cx + R * f * Math.sin(2 * Math.PI * i / n), cy - R * f * Math.cos(2 * Math.PI * i / n)];
  const ring = f => items.map((_, i) => pt(i, f).map(v => v.toFixed(1)).join(',')).join(' ');
  const rings = [0.3, 0.6, 1].map(f => `<polygon points="${ring(f)}" fill="none" stroke="${f === 0.6 ? 'var(--line-strong)' : 'var(--line)'}" ${f === 0.6 ? 'stroke-dasharray="3 3"' : ''}/>`).join('');
  const axes = items.map((_, i) => { const [x, y] = pt(i, 1); return `<line x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" stroke="var(--line)"/>`; }).join('');
  const data = items.map((it, i) => pt(i, Math.max(0.03, it.pct / 100)).map(v => v.toFixed(1)).join(',')).join(' ');
  const labels = items.map((it, i) => { const [x, y] = pt(i, 1.2), a = x < cx - 8 ? 'end' : x > cx + 8 ? 'start' : 'middle';
    const t = it.title.length > 16 ? it.title.slice(0, 15) + '…' : it.title; return `<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" text-anchor="${a}" dominant-baseline="middle">${esc(t)}</text>`; }).join('');
  const dots = items.map((it, i) => { const [x, y] = pt(i, Math.max(0.03, it.pct / 100)); return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3" fill="var(--accent)"/>`; }).join('');
  return `<svg class="radar" viewBox="-40 0 380 280" role="img">${rings}${axes}<polygon points="${data}" fill="var(--accent)" fill-opacity=".2" stroke="var(--accent)" stroke-width="1.5"/>${dots}${labels}</svg>`;
}
function dashBar(pct, allotted){
  return `<div class="track"><div class="bar lv-${levelOf(pct)}"><i style="width:${Math.min(100, pct)}%"></i></div>${allotted ? '' : `<span class="mark" style="left:${PASS_LINE}%"></span>`}</div>`;
}

function renderDashboard(d){
  const secs = d.sections || [], n = secs.length || 1;
  const okCount = secs.filter(s => s.pct >= PASS_LINE).length;
  const done = secs.reduce((a, s) => a + (s.done || 0), 0), total = secs.reduce((a, s) => a + (s.total || 0), 0);
  const used = Math.round(secs.reduce((a, s) => a + (s.used || 0), 0)), allot = Math.round(secs.reduce((a, s) => a + (s.allotted || 0), 0));
  const lv = levelOf(d.overall);
  const bars = secs.map(s => `<div class="hrow"><span class="n" title="${esc(s.title)}">${esc(s.title)}</span>${dashBar(s.pct)}
      <span class="p t-${levelOf(s.pct)}">${s.pct}% · ${esc(levelName(s.pct))}</span></div>`).join('');
  const times = secs.map(s => { const f = s.allotted ? Math.round(100 * s.used / s.allotted) : 0;
    return `<div class="hrow" style="grid-template-columns:minmax(96px,1.3fr) 1.5fr auto"><span class="n" title="${esc(s.title)}">${esc(s.title)}</span>
      <div class="bar"><i style="width:${Math.min(100, f)}%;background:${f >= 95 ? 'var(--warn)' : 'var(--accent-2)'}"></i></div><span class="p muted">${Math.round(s.used)}/${Math.round(s.allotted)} ${esc(T('dMin'))}</span></div>`; }).join('');
  const prLabel = {hi: T('dPrio'), mid: T('dReinf'), lo: T('dWatch')};
  const opp = (d.weak || []).length ? d.weak.map(w => { const pr = w.kind === 'section' || w.count >= 3 ? 'hi' : w.count === 2 || (w.pct != null && w.pct < 80) ? 'mid' : 'lo';
      return `<div class="opp"><span class="pr pr-${pr}">${esc(prLabel[pr])}</span><div><b>${esc(w.label)}${w.pct != null ? ' · ' + w.pct + '%' : ''}${w.count ? ' · ' + esc(T('dFails')(w.count)) : ''}</b><span class="tip">${esc(w.tip || '')}</span></div></div>`; }).join('')
    : `<p class="muted">${esc(T('dOppNone'))}</p>`;
  const miss = d.missed === undefined ? '' : `<div class="panel p-missed"><h4>${esc(T('dMissed'))}</h4>${d.missed.length ? d.missed.map(m => `<details class="miss"><summary>${esc(m.section)} — ${esc(m.q)}</summary>
      <p class="why-txt"><b>${esc(T('dExpected'))}:</b> ${esc(m.expected)}</p>${m.explanation ? `<p class="why-txt">${esc(m.explanation)}</p>` : ''}${(m.sources || []).length ? `<p class="why-txt">${esc(T('dSources'))}: ${m.sources.map(x => `<a href="${esc(safeUrl(x.url))}" target="_blank" rel="noopener noreferrer">${esc(x.title)}</a>`).join(' · ')}</p>` : ''}</details>`).join('') : `<p class="muted">${esc(T('dMissedNone'))}</p>`}</div>`;
  const radar = n >= 3 ? `<div class="panel p-radar"><h4>${esc(T('dRadar'))}</h4>${dashRadar(secs)}</div>` : '';
  return `<div class="dash"><div class="dash-top"><div><h3>${esc(d.title)}<span class="sub">${esc(d.subtitle || '')}</span></h3></div>
      ${d.sample ? `<span class="badge sample" title="${esc(T('dSampleNote'))}">${esc(T('dSample'))}</span>` : `<span class="badge">${esc(T('dOverall'))}: ${esc(levelName(d.overall))}</span>`}</div>
    <div class="dash-body${n < 3 ? ' no-radar' : ''}">
      <div class="panel kpi"><div class="v t-${lv}">${d.overall}%</div><div class="l">${esc(T('dOverall'))}</div></div>
      <div class="panel kpi"><div class="v">${okCount}<small>${esc(T('dOf'))} ${secs.length}</small></div><div class="l">${esc(T('dSectionsOk'))} (${esc(T('dPass'))})</div></div>
      <div class="panel kpi"><div class="v">${used}<small>/ ${allot} ${esc(T('dMin'))}</small></div><div class="l">${esc(T('dTime'))}</div></div>
      <div class="panel kpi"><div class="v">${done}<small>${esc(T('dOf'))} ${total}</small></div><div class="l">${esc(T('dHits'))}</div></div>
      <div class="panel p-bars"><h4>${esc(T('dBySection'))}</h4>${bars}<div class="axis-note"><span>0 %</span><span>${esc(T('dPass'))}</span><span>100 %</span></div>
        <h4 style="margin-top:24px">${esc(T('dTimeBy'))}</h4>${times}</div>
      <div class="panel p-opp"><h4>${esc(T('dOpp'))}</h4>${opp}</div>
      <div class="panel p-donut"><h4>${esc(T('dOverall'))}</h4><div class="donut">${dashDonut(d.overall)}
        <div class="legend"><span><i style="background:var(--ok)"></i>≥ 80 % ${esc(T('dStrong'))}</span><span><i style="background:var(--accent)"></i>60–79 % ${esc(T('dMid'))}</span><span><i style="background:var(--bad)"></i>&lt; 60 % ${esc(T('dWeak'))}</span></div></div></div>
      ${radar}
      ${miss}
    </div></div>`;
}
