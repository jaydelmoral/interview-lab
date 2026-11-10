addStrings({
  es: {
    heroBadge: 'Código abierto · Apache-2.0 · 100 % local', heroTitle: 'Entrevistas técnicas a la medida, ejecutadas en tu propia computadora',
    heroSub: 'Sube tu CV o pega la vacante. Interview Lab detecta qué te van a preguntar, arma el simulacro con tiempo por sección y califica tu código de verdad.',
    ctaBuild: 'Crear mi simulacro', ctaEval: 'Ver cómo se evalúa',
    evalNote: 'Datos de ejemplo. Tu reporte real aparece aquí mismo al terminar cada simulacro.',
    c1t: 'Cada sección vale de 0 a 100 %', c1p: 'Tu resultado global es el promedio de las secciones. Desde 60 % una sección cuenta como aprobada.',
    c2t: 'El código se ejecuta de verdad', c2p: 'Tu solución se compila y corre contra pruebas ocultas. Cada prueba suma puntos en una categoría: resolución de problemas, fiabilidad o conocimiento del lenguaje.',
    c3t: 'Preguntas con corrección exacta', c3p: 'Las de opción múltiple y «predice la salida» se corrigen al momento, con la explicación. Las tarjetas son de autoevaluación.',
    c4t: 'Cronómetro por sección', c4p: 'Cada sección tiene su propio tiempo. Si se agota, la sección se cierra con lo que respondiste y el reporte compara el tiempo usado con el asignado.',
    howEyebrow: 'Cómo funciona', howTitle: 'De la vacante al simulacro en minutos', howSub: 'Todo el análisis ocurre en tu equipo. Esto es lo que verás al usarlo.',
    termCaption: 'Ilustración del flujo. Se usa desde el navegador, en localhost; nada sale de tu equipo.',
    tVac: 'vacante recibida', tLevel: 'nivel', tLang: 'lenguaje', tMods: 'módulos', tSim: 'simulacro', tSec: 'secciones', tSecN: 'sección', tHidden: 'pruebas ocultas', tEdge: 'caso borde: lista vacía', tLocal: 'escuchando en http://127.0.0.1:8765 · solo local', tChars: 'caracteres',
    pilTitle: 'Practica como si fuera la entrevista real', pilSub: 'Cuatro ideas simples detrás de todo el producto.',
    p1t: 'Hecho a la medida', p1p: 'Pega la descripción de la vacante o sube tu CV. El análisis detecta seniority, lenguaje y versión, y los módulos que piden, y arma un simulacro solo con lo que te van a preguntar. Tú corriges lo que no cuadre antes de empezar.',
    p2t: 'Privacidad total', p2p: 'Todo corre en tu máquina. Tu CV, tus respuestas y tu código no viajan a ningún servidor. La IA es opcional y usa tu propia llave, nunca la nuestra.',
    p3t: 'Feedback real', p3p: 'Tu solución se compila y se ejecuta contra pruebas ocultas, con límites de tiempo y memoria. Ves qué casos fallan y por qué: no una opinión, un resultado.',
    p4t: 'Con reloj y reporte', p4p: 'Cada sección tiene su cronómetro, con ritmo exigente, estándar o relajado. Al final, un tablero te dice qué temas reforzar. Disponible en español e inglés.',
    buildEyebrow: 'Empieza ahora', ctaFinalTitle: 'Prepárate para la vacante que sí quieres', ctaFinalSub: 'Gratis, abierto y en tu equipo. Instálalo en minutos con Python o Docker.',
    title: 'Crea tu simulacro de entrevista', sub: 'Sube tu CV o pega la vacante: analizamos el contenido en tu equipo y armamos un examen con temporizador por sección, a la medida del puesto que buscas.',
    h1: '1. Tu perfil o la vacante', kindJd: 'Es una vacante (Job Description)', kindCv: 'Es mi CV', srcPh: 'Pega aquí el texto… o sube un archivo (.txt, .md, .docx, .pdf). El PDF requiere la herramienta pdftotext; si no la tienes, copia y pega el texto.',
    analyze: 'Analizar', privacy: 'El análisis es local, sin IA ni internet: busca tecnologías, años de experiencia y nivel. No se guarda tu CV ni se envía a ningún lado.',
    analyzing: 'Analizando…', foundTitle: 'Esto detectamos (puedes corregirlo abajo):', empty: 'Escribe o sube algo primero.', badFile: 'Formato no admitido. Usa .txt, .md, .docx o .pdf, o pega el texto.',
    h2: '2. Configura tu simulacro', fSeniority: 'Seniority', fLanguage: 'Lenguaje', fVersion: 'Versión', fPace: 'Ritmo del temporizador', fTitle: 'Nombre (opcional)', titlePh: 'Ej. Entrevista Senior Java — Banco X',
    optOther: 'Otro (solo preguntas conceptuales)', paceTight: 'Exigente (−20 %)', paceStd: 'Estándar', paceRelax: 'Relajado (+25 %)', fModules: 'Módulos',
    timers: 'Cada sección tiene su propio temporizador: código = el tiempo de cada ejercicio; preguntas = 1.5 min cada una (1 min las de «predice la salida»).',
    langNoteCode: 'Los ejercicios de código y «predice la salida» son solo de Java por ahora; con este lenguaje se omitirán esos módulos.',
    langNoteDetected: n => `Detectamos ${n}. Los ejercicios de código son de Java por ahora.`,
    mCount: n => `${n} preguntas/ejercicios`, mDetected: 'detectado', mNone: 'sin contenido todavía', soon: 'IA / LLMs — próximamente',
    h3: '3. Material extra (opcional): tu banco de memoria', bankHelp: 'Pega enlaces (uno por línea) o tus apuntes. Se convierten en preguntas de opción múltiple y tarjetas, y quedan guardadas solo en tu equipo.',
    fLinks: 'Enlaces (máx. 5, páginas HTML o texto)', linksPh: 'https://…', fNotes: 'O pega tus apuntes', notesPh: 'Pega aquí texto de estudio…', bankTitlePh: 'Nombre del banco (ej. Resilience4j)',
    bankAdd: 'Agregar a mi banco', bankWorking: 'Leyendo y generando preguntas…', bankDone: (n, e) => `Banco creado con ${n} preguntas.${e ? ' Hubo errores en ' + e + ' enlace(s).' : ''}`,
    bankNote: 'Generación básica sin IA: llena huecos con términos técnicos y crea tarjetas de los títulos. Úsalo con material que puedas estudiar para ti; respeta los derechos de autor y las condiciones de cada sitio. Con un modelo de IA las preguntas serán mejores (está en el plan).',
    bankItems: n => `${n} preguntas`, bankDel: 'Borrar', bankDelConfirm: '¿Borrar este banco?', bankUse: 'incluir', noBanks: 'Aún no tienes bancos.', fetchOff: 'La lectura de enlaces está desactivada en este equipo; pega tus apuntes.',
    create: 'Crear simulacro', creating: 'Armando tu simulacro…', pickModule: 'Elige al menos un módulo.', h4: 'Mis simulacros', open: 'Abrir', retry: 'Repetir', last: 'Último', never: 'sin intentos',
    min: 'min', secs: 'secciones',
    rtTitle: 'Instalado en este equipo', rtMissing: 'sin instalar', rtHow: 'Para instalar otro lenguaje, usa en una terminal:', rtGrader: 'con calificador', rtNoGrader: 'sin calificador aún',
    genLocalAi: 'Generador activo: IA local (Ollama). Tu texto no sale de tu equipo; la calidad depende del modelo que tengas instalado y las preguntas salen como borrador.', genOffline: 'Generador activo: local (sin IA). Tu texto no sale de tu equipo.', genAi: 'Generador activo: IA (proveedor externo con tu propia llave). El texto que agregues se envía al proveedor y el costo es de tu cuenta.'
  },
  en: {
    heroBadge: 'Open source · Apache-2.0 · 100% local', heroTitle: 'Interview simulations tailored to the job, running on your own machine',
    heroSub: 'Upload your CV or paste the job post. Interview Lab detects what you will be asked, builds the simulation with a timer per section and grades your code for real.',
    ctaBuild: 'Build my simulation', ctaEval: 'See how you are scored',
    evalNote: 'Sample data. Your real report appears right here after each simulation.',
    c1t: 'Every section is worth 0 to 100%', c1p: 'Your overall result is the average of the sections. From 60% a section counts as passed.',
    c2t: 'Your code really runs', c2p: 'Your solution is compiled and run against hidden tests. Each test earns points in a category: problem solving, reliability or language knowledge.',
    c3t: 'Questions graded exactly', c3p: 'Multiple-choice and “predict the output” are graded instantly, with the explanation. Flashcards are self-assessed.',
    c4t: 'A timer per section', c4p: 'Each section has its own time. If it runs out, the section closes with what you answered and the report compares time used with time allotted.',
    howEyebrow: 'How it works', howTitle: 'From the job post to a simulation in minutes', howSub: 'All the analysis happens on your machine. This is what you will see when you use it.',
    termCaption: 'Illustration of the flow. You use it from the browser, on localhost; nothing leaves your machine.',
    tVac: 'job post received', tLevel: 'level', tLang: 'language', tMods: 'modules', tSim: 'simulation', tSec: 'sections', tSecN: 'section', tHidden: 'hidden tests', tEdge: 'edge case: empty list', tLocal: 'listening on http://127.0.0.1:8765 · local only', tChars: 'characters',
    pilTitle: 'Practise as if it were the real interview', pilSub: 'Four simple ideas behind the whole product.',
    p1t: 'Tailored to the job', p1p: 'Paste the job description or upload your CV. The analysis detects seniority, language and version, and the modules required, and builds a simulation with only what you will be asked. You correct anything that does not fit before starting.',
    p2t: 'Total privacy', p2p: 'Everything runs on your machine. Your CV, your answers and your code never travel to a server. AI is optional and uses your own key, never ours.',
    p3t: 'Real feedback', p3p: 'Your solution is compiled and run against hidden tests, with time and memory limits. You see which cases fail and why: not an opinion, a result.',
    p4t: 'With a clock and a report', p4p: 'Each section has its own timer, at a tight, standard or relaxed pace. At the end, a dashboard tells you which topics to reinforce. Available in Spanish and English.',
    buildEyebrow: 'Start now', ctaFinalTitle: 'Get ready for the job you really want', ctaFinalSub: 'Free, open and on your machine. Install it in minutes with Python or Docker.',
    title: 'Build your interview simulation', sub: 'Upload your CV or paste the job description: we analyze it on your machine and build an exam with a timer per section, tailored to the role you want.',
    h1: '1. Your profile or the job post', kindJd: 'It is a job description', kindCv: 'It is my CV', srcPh: 'Paste the text here… or upload a file (.txt, .md, .docx, .pdf). PDF needs the pdftotext tool; without it, copy and paste the text.',
    analyze: 'Analyze', privacy: 'The analysis is local, with no AI or internet: it looks for technologies, years of experience and level. Your CV is not stored or sent anywhere.',
    analyzing: 'Analyzing…', foundTitle: 'We detected this (you can correct it below):', empty: 'Write or upload something first.', badFile: 'Unsupported format. Use .txt, .md, .docx or .pdf, or paste the text.',
    h2: '2. Configure your simulation', fSeniority: 'Seniority', fLanguage: 'Language', fVersion: 'Version', fPace: 'Timer pace', fTitle: 'Name (optional)', titlePh: 'E.g. Senior Java interview — Bank X',
    optOther: 'Other (concept questions only)', paceTight: 'Tight (−20%)', paceStd: 'Standard', paceRelax: 'Relaxed (+25%)', fModules: 'Modules',
    timers: 'Each section has its own timer: coding = each exercise\'s own limit; questions = 1.5 min each (1 min for “predict the output”).',
    langNoteCode: 'Coding exercises and “predict the output” are Java-only for now; with this language those modules will be skipped.',
    langNoteDetected: n => `We detected ${n}. Coding exercises are Java-only for now.`,
    mCount: n => `${n} questions/exercises`, mDetected: 'detected', mNone: 'no content yet', soon: 'AI / LLMs — coming soon',
    h3: '3. Extra material (optional): your memory bank', bankHelp: 'Paste links (one per line) or your notes. They become multiple-choice questions and flashcards, stored only on your machine.',
    fLinks: 'Links (max 5, HTML or text pages)', linksPh: 'https://…', fNotes: 'Or paste your notes', notesPh: 'Paste study text here…', bankTitlePh: 'Bank name (e.g. Resilience4j)',
    bankAdd: 'Add to my bank', bankWorking: 'Reading and generating questions…', bankDone: (n, e) => `Bank created with ${n} questions.${e ? ' Errors in ' + e + ' link(s).' : ''}`,
    bankNote: 'Basic generation without AI: it blanks out technical terms and makes flashcards from headings. Use it with material you may study for yourself; respect copyright and each site\'s terms. With an AI model the questions will be better (it is on the plan).',
    bankItems: n => `${n} questions`, bankDel: 'Delete', bankDelConfirm: 'Delete this bank?', bankUse: 'include', noBanks: 'You have no banks yet.', fetchOff: 'Fetching links is disabled on this machine; paste your notes.',
    create: 'Create simulation', creating: 'Building your simulation…', pickModule: 'Pick at least one module.', h4: 'My simulations', open: 'Open', retry: 'Retake', last: 'Last', never: 'no attempts',
    min: 'min', secs: 'sections',
    rtTitle: 'Installed on this machine', rtMissing: 'not installed', rtHow: 'To install another language, run in a terminal:', rtGrader: 'with grader', rtNoGrader: 'no grader yet',
    genLocalAi: 'Active generator: local AI (Ollama). Your text stays on your machine; quality depends on the model you installed and questions are drafts.', genOffline: 'Active generator: local (no AI). Your text never leaves your machine.', genAi: 'Active generator: AI (external provider with your own key). The text you add is sent to the provider and billed to your account.'
  }
});

let RUNTIMES = [], MODS = [], DETECT = {}, BANKS = [], pendingFile = null, ANALYSIS = null, GEN = 'offline';
const VERSIONS = {java: [8, 11, 17, 21], python: [9, 10, 11, 12, 13], other: []};

function applyI18n(){
  document.querySelectorAll('[data-t]').forEach(el => { el.textContent = T(el.dataset.t); });
  document.querySelectorAll('[data-tp]').forEach(el => { el.placeholder = T(el.dataset.tp); });
  if ($('links').disabled) $('links').placeholder = T('fetchOff');
  $('genNote').textContent = T(GEN === 'offline' ? 'genOffline' : GEN === 'ollama' ? 'genLocalAi' : 'genAi');
  renderMarketing();
  renderVersions(); renderModules(); renderBanks(); renderFound(); langNote(); renderRuntimes(); loadExams();
}

/* ---- marketing blocks: sample dashboard, criteria, terminal, module tags ---- */
function sampleData(){
  const es = lang === 'es';
  const S = (title, pct, done, total, unit, used, allotted) => ({title, pct, done, total, unit, used, allotted});
  const sections = [S(es ? 'Código y Big O' : 'Coding & Big O', 72, 6, 8, 'tests', 21, 25), S('SQL', 40, 2, 5, 'questions', 8, 8),
                    S(es ? 'Microservicios' : 'Microservices', 80, 4, 5, 'questions', 6, 8), S(es ? 'Seguridad' : 'Security', 60, 3, 5, 'questions', 7, 8)];
  return {sample: true, title: es ? 'Entrevista Senior Java' : 'Senior Java interview', subtitle: es ? '· Java 21 · 4 secciones' : '· Java 21 · 4 sections',
    overall: Math.round(sections.reduce((a, x) => a + x.pct, 0) / sections.length), sections,
    weak: [{label: 'SQL', kind: 'section', pct: 40, tip: T('tipSection')},
           {label: es ? 'JOIN y agregaciones' : 'JOINs and aggregations', kind: 'tag', count: 3, tip: T('tipTag')},
           {label: (es ? 'Código · ' : 'Code · ') + T('catRel'), kind: 'skill', pct: 66, tip: T('tipRel')}],
    missed: [{section: 'SQL', q: es ? '¿Qué devuelve un LEFT JOIN cuando no hay coincidencia?' : 'What does a LEFT JOIN return when there is no match?',
              expected: es ? 'Las filas de la izquierda con NULL en las columnas de la derecha' : 'Left rows with NULL in the right-hand columns',
              explanation: es ? 'El LEFT JOIN conserva todas las filas de la tabla izquierda.' : 'A LEFT JOIN keeps every row of the left table.'}]};
}
function renderMarketing(){
  $('sampleDash').innerHTML = renderDashboard(sampleData()) + '<p class="caption">' + esc(T('evalNote')) + '</p>';
  $('criteria').innerHTML = [1, 2, 3, 4].map(n => '<article><b>' + esc(T('c' + n + 't')) + '</b><p>' + esc(T('c' + n + 'p')) + '</p></article>').join('');
  const w = '<span class="w">', d = '<span class="d">', g = '<span class="g">', r = '<span class="r">', x = '</span>', es = lang === 'es';
  $('termBody').innerHTML = [
    d + '$' + x + ' ' + w + 'python3 server.py' + x, d + esc(T('tLocal')) + x, '',
    d + '›' + x + ' ' + esc(T('tVac')) + ' ' + d + '(1 840 ' + esc(T('tChars')) + ')' + x,
    d + '›' + x + ' ' + esc(T('tLevel')) + '      ' + w + 'senior' + x,
    d + '›' + x + ' ' + esc(T('tLang')) + '   ' + w + 'Java 21' + x,
    d + '›' + x + ' ' + esc(T('tMods')) + '    ' + w + (es ? 'código · SQL · microservicios · seguridad' : 'coding · SQL · microservices · security') + x,
    d + '›' + x + ' ' + esc(T('tSim')) + '  ' + w + '4 ' + esc(T('tSec')) + ' · 95 min' + x, '',
    d + '›' + x + ' ' + esc(T('tSecN')) + ' 1/4 · ' + (es ? 'código' : 'coding') + ' ' + d + '· 25:00' + x,
    '  ' + g + '✓' + x + ' ' + esc(T('tHidden')) + ' 6/8', '  ' + r + '✗' + x + ' ' + esc(T('tEdge')),
    d + '$' + x + ' <span class="w cur">▍</span>'].join('\n');
  $('pilTags').innerHTML = MODS.filter(m => m.id !== 'mybank').map(m => '<span class="chip">' + esc(m.title) + '</span>').join('');
}

function renderVersions(){
  const l = $('language').value, cur = $('version').value;
  const opts = VERSIONS[l] || [];
  $('version').innerHTML = opts.map(v => `<option value="${v}">${l === 'java' ? 'Java ' + v : 'Python 3.' + v}</option>`).join('') || '<option value="">—</option>';
  $('version').disabled = !opts.length;
  if (opts.map(String).includes(cur)) $('version').value = cur; else if (opts.length) $('version').value = String(opts[opts.length - 1]);
}
function renderRuntimes(){
  const rows = RUNTIMES.filter(r => r.kind === 'language').map(r => `${esc(r.name)}: ${r.installed ? '<b>' + esc(r.version || 'ok') + '</b> · ' + esc(T(r.grader ? 'rtGrader' : 'rtNoGrader')) : esc(T('rtMissing'))}`);
  $('runtimeNote').innerHTML = rows.length ? `${esc(T('rtTitle'))} — ${rows.join(' · ')}. ${esc(T('rtHow'))} <code>python3 install.py list</code>` : '';
}
function langNote(){
  const l = $('language').value, n = $('langNote');
  const msg = l !== 'java' ? T('langNoteCode') : '';
  n.style.display = msg ? '' : 'none'; n.textContent = msg;
}

function renderModules(){
  const checked = new Set([...document.querySelectorAll('#modules input:checked')].map(i => i.value));
  const first = !document.querySelector('#modules input');
  const hasBank = BANKS.length > 0;
  $('modules').innerHTML = MODS.map(m => {
    const count = m.id === 'mybank' ? BANKS.reduce((a, b) => a + b.items, 0) : m.count;
    const det = DETECT[m.id];
    const on = first ? (m.id === 'coding' || m.id === 'java-trivia') : checked.has(m.id);
    const disabled = count === 0;
    return `<label class="mod ${on && !disabled ? 'on' : ''} ${disabled ? 'off' : ''}"><input type="checkbox" value="${esc(m.id)}" ${on && !disabled ? 'checked' : ''} ${disabled ? 'disabled' : ''}>
      <span><b>${esc(m.title)}</b><span class="muted">${disabled ? esc(T('mNone')) : esc(T('mCount')(count))}</span>
      ${det ? `<br><span class="chip hit">${esc(T('mDetected'))}: ${esc(det.join(', '))}</span>` : ''}</span></label>`;
  }).join('') + `<label class="mod off"><input type="checkbox" disabled><span><b>${esc(T('soon'))}</b></span></label>`;
  document.querySelectorAll('#modules input').forEach(i => i.onchange = () => i.closest('.mod').classList.toggle('on', i.checked));
}

function renderFound(){
  const a = ANALYSIS, box = $('found');
  if (!a) { box.innerHTML = ''; return; }
  const chips = a.modules.filter(m => m.score > 0).map(m => `<span class="chip hit">${esc((MODS.find(x => x.id === m.id) || {title: m.id}).title)}</span>`).join('');
  const lang0 = Object.entries(a.language_counts || {}).map(([k, v]) => `${k} ×${v}`).join(', ');
  box.innerHTML = `<div class="note"><b>${esc(T('foundTitle'))}</b><br>
    Seniority: <b>${esc(a.seniority.toUpperCase())}</b>${a.years ? ' (' + a.years + ' ' + (lang === 'es' ? 'años' : 'years') + ')' : ''} ·
    ${esc(T('fLanguage'))}: <b>${esc(a.language)}</b>${a.version ? ' ' + a.version : ''} ${lang0 ? '<span class="muted">(' + esc(lang0) + ')</span>' : ''}<br>${chips}</div>`;
}

async function analyze(){
  const text = $('src').value.trim();
  if (!text && !pendingFile) { $('analyzeMsg').textContent = T('empty'); return; }
  $('analyzeBtn').disabled = true; $('analyzeMsg').textContent = T('analyzing');
  try {
    const a = await post('/api/analyze', pendingFile ? {filename: pendingFile.name, data: pendingFile.b64} : {text});
    ANALYSIS = a; DETECT = {};
    a.modules.forEach(m => { if (m.score > 0) DETECT[m.id] = m.hits.slice(0, 4); });
    $('seniority').value = a.seniority;
    const l = ['java', 'python'].includes(a.language) ? a.language : 'java';
    $('language').value = l; renderVersions();
    if (a.version && (VERSIONS[l] || []).includes(a.version)) $('version').value = String(a.version);
    document.querySelectorAll('#modules input').forEach(i => { i.checked = !i.disabled && (a.modules.some(m => m.id === i.value) && (DETECT[i.value] || i.value === 'coding')); });
    renderModules(); renderFound(); langNote();
    if (!['java', 'python'].includes(a.language) && a.language) { $('langNote').style.display = ''; $('langNote').textContent = T('langNoteDetected')(a.language); }
    $('analyzeMsg').textContent = '';
    $('c2').scrollIntoView({behavior: 'smooth', block: 'start'});
  } catch (e) { $('analyzeMsg').textContent = T('err') + ': ' + e.message; }
  $('analyzeBtn').disabled = false;
}

$('file').onchange = () => {
  const f = $('file').files[0]; pendingFile = null;
  if (!f) return;
  const name = f.name.toLowerCase();
  if (name.endsWith('.docx') || name.endsWith('.pdf')) {
    const r = new FileReader();
    r.onload = () => { const bytes = new Uint8Array(r.result); let bin = ''; for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
      pendingFile = {name: f.name, b64: btoa(bin)}; $('src').value = ''; $('analyzeMsg').textContent = f.name; };
    r.readAsArrayBuffer(f);
  } else if (name.endsWith('.txt') || name.endsWith('.md')) {
    const r = new FileReader(); r.onload = () => { $('src').value = String(r.result).slice(0, 200000); }; r.readAsText(f);
  } else { $('analyzeMsg').textContent = T('badFile'); $('file').value = ''; }
};
$('src').oninput = () => { if ($('src').value) pendingFile = null; };
$('analyzeBtn').onclick = analyze;
$('language').onchange = () => { renderVersions(); langNote(); };

/* ---- memory bank ---- */
async function loadBanks(){ try { BANKS = await api('/api/banks'); } catch (e) { BANKS = []; } renderBanks(); renderModules(); }
function renderBanks(){
  const box = $('banks');
  if (!BANKS.length) { box.innerHTML = `<p class="muted">${esc(T('noBanks'))}</p>`; return; }
  box.innerHTML = BANKS.map(b => `<div class="item"><div><b>${esc(b.title)}</b> <span class="muted">· ${esc(T('bankItems')(b.items))} · ${esc(b.created)}</span><br>
    <span class="muted">${esc(b.sources.map(s => s.title || s.url).join(' · ').slice(0, 160))}</span></div>
    <div class="row" style="margin:0"><label><input type="checkbox" class="bankUse" value="${esc(b.id)}" checked> ${esc(T('bankUse'))}</label>
    <button data-del="${esc(b.id)}">${esc(T('bankDel'))}</button></div></div>`).join('');
  box.querySelectorAll('[data-del]').forEach(btn => btn.onclick = async () => {
    if (!confirm(T('bankDelConfirm'))) return;
    await api('/api/banks/' + btn.dataset.del, {method: 'DELETE'}); loadBanks();
  });
}
$('bankBtn').onclick = async () => {
  const urls = $('links').value.split('\n').map(x => x.trim()).filter(Boolean), notes = $('notes').value;
  if (!urls.length && !notes.trim()) { $('bankMsg').textContent = T('empty'); return; }
  $('bankBtn').disabled = true; $('bankMsg').textContent = T('bankWorking');
  try {
    const r = await post('/api/banks', {title: $('bankTitle').value, urls, notes, lang});
    $('bankMsg').textContent = T('bankDone')(r.items, (r.errors || []).length);
    if ((r.errors || []).length) $('bankMsg').title = r.errors.map(e => e.url + ': ' + e.error).join('\n');
    $('links').value = ''; $('notes').value = ''; $('bankTitle').value = '';
    await loadBanks();
    const my = document.querySelector('#modules input[value="mybank"]'); if (my) { my.checked = true; my.closest('.mod').classList.add('on'); }
  } catch (e) {
    $('bankMsg').textContent = T('err') + ': ' + e.message + (e.data && e.data.errors ? ' — ' + e.data.errors.map(x => x.error).join('; ') : '');
  }
  $('bankBtn').disabled = false;
};

/* ---- create and list simulations ---- */
$('createBtn').onclick = async () => {
  const modules = [...document.querySelectorAll('#modules input:checked')].map(i => i.value);
  if (!modules.length) { $('createMsg').textContent = T('pickModule'); return; }
  const banks = [...document.querySelectorAll('.bankUse:checked')].map(i => i.value);
  $('createBtn').disabled = true; $('createMsg').textContent = T('creating');
  try {
    const exam = await post('/api/exams', {seniority: $('seniority').value, language: $('language').value, version: $('version').value ? Number($('version').value) : null,
      pace: $('pace').value, modules, banks, title: $('title').value, lang});
    location.href = '/exam?id=' + encodeURIComponent(exam.id);
  } catch (e) {
    $('createMsg').textContent = T('err') + ': ' + e.message + (e.data && e.data.notes ? ' — ' + e.data.notes.map(n => n.text).join(' ') : '');
    $('createBtn').disabled = false;
  }
};
async function loadExams(){
  let list = []; try { list = await api('/api/exams?lang=' + lang); } catch (e) {}
  $('c4').style.display = list.length ? '' : 'none';
  $('exams').innerHTML = list.map(e => `<div class="item"><div><b>${esc(e.title || e.config.modules.join(' · '))}</b>
    <span class="muted">· ${esc(e.created)} · ${esc(e.config.seniority.toUpperCase())} ${esc(e.config.language)}${e.config.version ? ' ' + e.config.version : ''} · ${e.total_minutes} ${esc(T('min'))}</span><br>
    <span class="muted">${esc(T('last'))}: ${e.last ? Math.round(100 * e.last.score / Math.max(1, e.last.max)) + '% (' + esc(e.last.when) + ')' : esc(T('never'))}</span></div>
    <a href="/exam?id=${encodeURIComponent(e.id)}"><button>${esc(e.last ? T('retry') : T('open'))}</button></a></div>`).join('');
}

/* ---- the animated O (ADR-0022). Only runs for brands with an isotype and when motion is allowed.
   Native path: CSS ties the keyframes to the scroll (animation-timeline), no JS per frame. Fallback: one passive scroll listener writes --p (0..1) per frame.
   Without this function (reduced motion, no JS, error) the O stays closed and still in the header. ---- */
function orbit(){
  const wrap = document.querySelector('.wrap');
  if (!wrap || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  wrap.classList.add('orbit-on');
  if (window.CSS && CSS.supports('animation-timeline: scroll()') && !/[?&]fallback/.test(location.search)) return;
  wrap.classList.add('orbit-js');
  let queued = false;
  const set = () => { queued = false; const max = document.documentElement.scrollHeight - innerHeight;
    wrap.style.setProperty('--p', max > 0 ? Math.min(.9999, Math.max(0, scrollY / max)).toFixed(4) : '0'); };
  const ask = () => { if (!queued) { queued = true; requestAnimationFrame(set); } };
  addEventListener('scroll', ask, {passive: true}); addEventListener('resize', ask); set();
}

(async function init(){
  await renderChrome('home', async () => { try { const m = await api('/api/modules?lang=' + lang); MODS = m.modules; GEN = m.generator || 'offline'; } catch (e) {} applyI18n(); });
  try { const m = await api('/api/modules?lang=' + lang); MODS = m.modules; GEN = m.generator || 'offline'; if (!m.fetch) { $('links').disabled = true; $('links').placeholder = T('fetchOff'); } } catch (e) {}
  try { RUNTIMES = await api('/api/runtimes?lang=' + lang); } catch (e) {}
  applyI18n(); loadBanks();
  if (document.documentElement.classList.contains('has-iso')) orbit();
})();
