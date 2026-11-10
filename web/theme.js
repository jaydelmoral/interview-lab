/* Theme bootstrap. Loaded synchronously in <head> so the page never flashes the wrong theme.
   Effective theme = the user's explicit choice (localStorage "theme") or the OS preference. */
(function () {
  var root = document.documentElement, mq = window.matchMedia ? matchMedia('(prefers-color-scheme: dark)') : null;
  function saved() { try { var v = JSON.parse(localStorage.getItem('theme')); return v === 'light' || v === 'dark' ? v : null; } catch (e) { return null; } }
  function effective() { return saved() || (mq && mq.matches ? 'dark' : 'light'); }
  function apply() { var t = effective(); root.setAttribute('data-theme', t); root.style.colorScheme = t; }
  window.setTheme = function (t) { try { localStorage.setItem('theme', JSON.stringify(t)); } catch (e) {} apply(); };
  window.currentTheme = effective;
  if (mq && mq.addEventListener) mq.addEventListener('change', function () { if (!saved()) apply(); });
  apply();
})();
