/* Optional Monaco code editor (installed with tools/fetch_monaco.py). If it is not installed, or anything fails to load,
   the page keeps its plain <textarea>: nothing else in the app depends on it.

   The textarea stays in the DOM as the source of truth for the rest of the code: its `value` property is redirected to
   the editor, so existing code that reads or assigns textarea.value keeps working unchanged. */
const EditorKit = (() => {
  const BASE = '/vendor/monaco/vs';
  let loading = null, current = null, observer = null;

  function load(){
    if (loading) return loading;
    loading = new Promise((resolve, reject) => {          // a missing loader.js simply fires onerror: no probe request needed
      const s = document.createElement('script');
      s.src = BASE + '/loader.js';
      s.onload = () => { try { window.require.config({paths: {vs: BASE}}); window.require(['vs/editor/editor.main'], () => resolve(window.monaco), reject); } catch (e) { reject(e); } };
      s.onerror = reject;
      document.head.appendChild(s);
    }).catch(e => { console.info('Monaco not available, using the plain editor:', e && e.message ? e.message : e); return null; });
    return loading;
  }

  const themeName = () => ((document.documentElement.getAttribute('data-theme') || 'dark') === 'dark' ? 'vs-dark' : 'vs');
  const langOf = l => ({java: 'java', python: 'python', javascript: 'javascript', sql: 'sql', shell: 'shell'}[l] || 'plaintext');

  /* Replace `textarea` by a Monaco editor. Interview mode: no autocompletion, no hints, like a plain whiteboard. */
  async function attach(textarea, language){
    const monaco = await load();
    if (!monaco || !textarea || !textarea.isConnected) return null;
    if (current) { try { current.dispose(); } catch (e) { /* already gone */ } current = null; }
    const host = document.createElement('div');
    host.className = 'monaco-host';
    textarea.parentNode.insertBefore(host, textarea);
    const initial = textarea.value;
    textarea.style.display = 'none';
    const editor = monaco.editor.create(host, {
      value: initial, language: langOf(language), theme: themeName(), automaticLayout: true, minimap: {enabled: false},
      fontSize: 14, tabSize: 4, insertSpaces: true, scrollBeyondLastLine: false, renderWhitespace: 'none',
      quickSuggestions: false, suggestOnTriggerCharacters: false, parameterHints: {enabled: false}, wordBasedSuggestions: 'off',
      tabCompletion: 'off', acceptSuggestionOnEnter: 'off', snippetSuggestions: 'none', inlineSuggest: {enabled: false}, hover: {enabled: false},
      lightbulb: {enabled: 'off'}, ariaLabel: textarea.getAttribute('aria-label') || 'code'
    });
    Object.defineProperty(textarea, 'value', {configurable: true, get: () => editor.getValue(), set: v => editor.setValue(String(v == null ? '' : v))});
    editor.onDidChangeModelContent(() => textarea.dispatchEvent(new Event('input')));
    if (!observer) {
      observer = new MutationObserver(() => monaco.editor.setTheme(themeName()));
      observer.observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});
    }
    current = editor;
    return editor;
  }

  return {attach, available: () => load().then(Boolean)};
})();
