"""Run with:  python3 -m unittest discover -s tests -v

Needs JDK 21 for the grading tests (they are skipped without it).
"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.environ["ILAB_HOME"] = tempfile.mkdtemp(prefix="ilab-test-")  # never touch a real workspace
sys.path.insert(0, str(ROOT / "grader"))
sys.path.insert(0, str(ROOT / "tools"))
import grade as G  # noqa: E402
import validate as V  # noqa: E402

HAS_JDK = bool(shutil.which("javac") and shutil.which("java"))
PROBLEMS = sorted(d for d in (ROOT / "problems").iterdir() if (d / "meta.json").exists())


class Structure(unittest.TestCase):
    def test_no_errors_or_warnings_in_builtin_content(self):
        for d in PROBLEMS:
            with self.subTest(problem=d.name):
                issues = V.validate(d, run=False)
                self.assertEqual([], issues, issues)

    def test_every_code_problem_is_bilingual(self):
        for d in PROBLEMS:
            m = json.loads((d / "meta.json").read_text())
            if m.get("kind") == "quiz":
                qs = json.loads((d / "quiz.json").read_text())
                self.assertTrue(all(q.get("topic_en") and q.get("explanation_en") for q in qs), d.name)
                continue
            with self.subTest(problem=d.name):
                self.assertTrue((d / "problem.es.md").exists())
                self.assertTrue(all(t.get("fail_why_en") and t.get("fail_how_en") for t in m["tests"]))

    def test_content_is_licensed_and_original(self):
        for d in PROBLEMS:
            m = json.loads((d / "meta.json").read_text())
            self.assertEqual("CC-BY-4.0", m.get("license"), d.name)
            self.assertEqual("original", m.get("origin"), d.name)


@unittest.skipUnless(HAS_JDK, "JDK 21 not installed")
class Grading(unittest.TestCase):
    def test_reference_solutions_score_100_and_starters_do_not(self):
        for d in PROBLEMS:
            m = json.loads((d / "meta.json").read_text())
            if m.get("kind") == "quiz":
                continue
            with self.subTest(problem=d.name):
                ref = sorted((d / "reference").glob("*.java"))[0]
                rep = G.grade(d.name, ref, lang="en")
                self.assertTrue(rep["compile"]["ok"], rep["compile"])
                self.assertEqual(rep["max"], rep["score"], [t for t in rep["tests"] if not t["passed"]])
                self.assertLess(G.grade(d.name, d / "starter.java")["score"], rep["max"])

    def test_submitted_code_does_not_see_your_environment(self):
        os.environ["ILAB_SECRET_PROBE"] = "top-secret"
        code = ('class Solution { static boolean isBooked(int[] s, int k) { '
                'if (System.getenv("ILAB_SECRET_PROBE") != null) throw new RuntimeException("LEAK"); return java.util.Arrays.binarySearch(s, k) >= 0; } }')
        tmp = Path(tempfile.mkdtemp()) / "Solution.java"
        tmp.write_text(code)
        rep = G.grade("001-seat-lookup", tmp)
        self.assertEqual(rep["max"], rep["score"], [t["detail"] for t in rep["tests"] if not t["passed"]])

    def test_infinite_loop_times_out(self):
        tmp = Path(tempfile.mkdtemp()) / "Solution.java"
        tmp.write_text("class Solution { static boolean isBooked(int[] s, int k) { while (true) {} } }")
        rep = G.grade("001-seat-lookup", tmp, lang="en")
        self.assertTrue(any("TIMEOUT" in t["detail"] for t in rep["tests"]))



class TestWebPages(unittest.TestCase):
    """The UI must stay self-contained: the CSP and the local-first promise forbid external assets (ADR-0006, ADR-0015)."""

    PAGES = ("landing.html", "exam.html", "index.html", "history.html")

    def test_pages_load_theme_and_shared_styles_and_nothing_external(self):
        import re
        for name in self.PAGES:
            html = (ROOT / "web" / name).read_text()
            self.assertIn('<script src="/theme.js">', html, name)
            self.assertIn('href="/common.css"', html, name)
            self.assertIsNone(re.search(r'(?:src|href)="https?://', html), f"{name} loads an external resource")
        for asset in ("common.js", "common.css", "theme.js"):
            text = (ROOT / "web" / asset).read_text()
            self.assertIsNone(re.search(r"@import|url\(['\"]?https?://|fetch\(['\"]https?://", text), f"{asset} reaches out to the network")

    def test_both_logo_variants_exist_for_the_theme_switch(self):
        brand = json.loads((ROOT / "web" / "brand" / "brand.json").read_text())
        for key in ("logo_mark", "logo_full"):
            for theme in ("light", "dark"):
                self.assertTrue((ROOT / "web" / "brand" / brand[key][theme]).is_file(), f"{key}/{theme}")

    def test_no_inline_scripts_or_event_handlers_so_the_csp_can_forbid_them(self):
        """P7: every script is a file served from 'self'; an inline script, an on*= attribute or a javascript: URL would be blocked by the CSP."""
        import re
        sources = {n: (ROOT / "web" / n).read_text() for n in self.PAGES}
        sources.update({n: (ROOT / "web" / n).read_text() for n in ("common.js", "theme.js", "editor.js", "exam.js", "history.js", "index.js", "landing.js")})
        for name, text in sources.items():
            if name.endswith(".html"):
                for tag in re.findall(r"<script\b[^>]*>(.*?)</script>", text, re.S):
                    self.assertEqual("", tag.strip(), f"{name} has an inline script")
                self.assertTrue(all("src=" in t for t in re.findall(r"<script\b[^>]*>", text)), f"{name}: script without src")
            self.assertIsNone(re.search(r"[\s'\"]on[a-z]+\s*=\s*[\"']", text), f"{name} sets an inline event handler")
            self.assertIsNone(re.search(r"(?:href|src|action)\s*=\s*[\"']\s*javascript:", text, re.I), f"{name} has a javascript: URL")
        for name in self.PAGES:
            js = name.replace(".html", ".js")
            self.assertIn(f'<script src="/{js}"></script>', (ROOT / "web" / name).read_text(), name)

    def test_csp_does_not_allow_inline_scripts(self):
        from interview_lab.web.security import SECURITY_HEADERS
        directives = dict(d.strip().split(" ", 1) for d in SECURITY_HEADERS["Content-Security-Policy"].split(";") if d.strip())
        self.assertEqual("'self'", directives["script-src"])
        self.assertNotIn("unsafe-eval", directives["script-src"])


def _strings(text, lang):
    """Keys of the addStrings() block for one language (loose: enough to prove a data-t key exists)."""
    import re
    start = text.index(f"  {lang}: {{")
    end = text.index("  en: {", start + 1) if lang == "es" and "  en: {" in text[start:] else len(text)
    return set(re.findall(r"(?:^|[\s,{])([A-Za-z][A-Za-z0-9]*):\s", text[start:end]))


class TestLandingPro(unittest.TestCase):
    """The 'Pro' landing (ADR-0022, ADR-0023): the animated O, the anchors, the texts, the typeface and the weight budgets."""

    LANDING = (ROOT / "web" / "landing.html").read_text()
    CSS = (ROOT / "web" / "common.css").read_text()
    COMMON_JS = (ROOT / "web" / "common.js").read_text()
    LANDING_JS = (ROOT / "web" / "landing.js").read_text()

    def test_o_layer_is_decorative_and_has_the_three_strokes(self):
        import re
        layer = self.LANDING[self.LANDING.index('class="orbit-layer'):self.LANDING.index('<section class="hero"')]
        self.assertIn('aria-hidden="true"', layer.split(">")[0], "the layer must be hidden from assistive technology")
        for arc in ("oA", "oB", "oC"):
            self.assertIn(f'href="#{arc}"', layer)
            self.assertEqual(1, self.COMMON_JS.count(f'<path id="{arc}"'), f"{arc} must be defined exactly once")
        self.assertEqual(3, len(re.findall(r'class="arc arc-[abc]"', layer)))

    def test_anchors_survive(self):
        for anchor in ("inicio", "evaluacion", "porque", "pasos", "crear", "cierre", "pilares", "como"):
            self.assertIn(f'id="{anchor}"', self.LANDING, anchor)
        self.assertEqual(1, self.LANDING.count("<h1"), "one h1 per page")

    def test_every_form_id_still_exists(self):
        for i in ("c1", "c2", "c3", "c4", "src", "file", "analyzeBtn", "seniority", "language", "version", "pace", "title", "modules", "links", "notes", "bankTitle", "bankBtn", "banks", "createBtn", "exams"):
            self.assertIn(f'id="{i}"', self.LANDING, i)

    def test_every_text_key_exists_in_both_languages(self):
        import re
        keys = set(re.findall(r'data-tp?="([A-Za-z0-9]+)"', self.LANDING))
        for lang in ("es", "en"):
            known = _strings(self.LANDING_JS, lang) | _strings(self.COMMON_JS, lang)
            self.assertEqual(set(), keys - known, f"missing in {lang}")
        for lang in ("es", "en"):   # keys read from JS with T('...')
            known = _strings(self.LANDING_JS, lang) | _strings(self.COMMON_JS, lang)
            used = set(re.findall(r"T\('([A-Za-z0-9]+)'\)", self.LANDING_JS))
            self.assertEqual(set(), used - known, f"T() keys missing in {lang}")

    def test_no_inline_styles_outside_the_form_and_no_hardcoded_domain(self):
        import re
        before_form = self.LANDING[:self.LANDING.index('id="crear"')]
        self.assertIsNone(re.search(r'\sstyle\s*=', before_form), "the new sections use classes and CSS variables, not style attributes")
        for name in ("landing.html", "landing.js", "common.js", "common.css", "theme.js"):
            self.assertNotIn("collaboration.mx", (ROOT / "web" / name).read_text(), name)
        brand = json.loads((ROOT / "web" / "brand" / "brand.json").read_text())
        self.assertEqual("collaboration-o", brand["isotype"])
        self.assertIn("link", brand)

    def test_o_animation_only_moves_transform_and_opacity(self):
        import re
        blocks = 0
        for m in re.finditer(r"@keyframes (orbit-[a-z]+)\{", self.CSS):   # every orbit-* keyframes, including the phone override
            depth, i = 1, m.end()
            while depth:
                depth += {"{": 1, "}": -1}.get(self.CSS[i], 0)
                i += 1
            props = set(re.findall(r"[{;]\s*([a-z-]+)\s*:", self.CSS[m.end():i - 1]))
            self.assertLessEqual(props - {"transform", "opacity"}, set(), m.group(1))
            blocks += 1
        self.assertGreaterEqual(blocks, 6)
        o_css = self.CSS[self.CSS.index("/* ---------- Collaboration isotype"):self.CSS.index("@media print{")]
        for banned in ("filter", "backdrop-filter", "box-shadow:", "stroke-dashoffset"):
            self.assertNotIn(banned, re.sub(r"/\*.*?\*/", "", o_css, flags=re.S), banned)
        self.assertEqual(1, self.LANDING_JS.count("addEventListener('scroll'"), "at most one scroll listener")
        self.assertIn("{passive: true}", self.LANDING_JS)

    def test_primary_buttons_are_gold_and_tokens_exist_in_both_themes(self):
        import re
        self.assertRegex(self.CSS, r"button\.primary,\.btn\.primary\{background:linear-gradient\(135deg,var\(--gold-2\),var\(--gold\)\)")
        dark = self.CSS[self.CSS.index(':root, html[data-theme="dark"]'):self.CSS.index('html[data-theme="light"]')]
        light = self.CSS[self.CSS.index('html[data-theme="light"]'):self.CSS.index("*{box-sizing")]
        for token in ("--o-a1", "--o-b2", "--o-c1", "--gold:", "--gold-2", "--gold-fg", "--gold-line", "--gold-ink", "--glint-1", "--glint-2"):
            self.assertIn(token, dark, f"dark {token}")
            self.assertIn(token, light, f"light {token}")
        self.assertIn("--font-display", self.CSS)

    def test_heading_typeface_is_hosted_licensed_and_under_budget(self):
        fonts = ROOT / "web" / "fonts"
        woff = fonts / "Outfit-latin-400-600.woff2"
        self.assertTrue(woff.is_file())
        self.assertLess(woff.stat().st_size, 40 * 1024)
        self.assertEqual(b"wOF2", woff.read_bytes()[:4])
        self.assertIn("SIL OPEN FONT LICENSE", (fonts / "OFL.txt").read_text().upper())
        origin = (fonts / "ORIGEN.md").read_text()
        import hashlib
        self.assertIn(hashlib.sha256(woff.read_bytes()).hexdigest(), origin, "ORIGEN.md must carry the SHA-256 of the shipped file")
        self.assertIn("font-display:swap", self.CSS)
        self.assertIn('rel="preload" href="/fonts/Outfit-latin-400-600.woff2" as="font" type="font/woff2" crossorigin', self.LANDING)
        self.assertIn("font-src 'self'", __import__("interview_lab.web.security", fromlist=["x"]).SECURITY_HEADERS["Content-Security-Policy"])

    def test_o_and_panels_stay_under_12_kb_uncompressed(self):
        """ADR-0022 budget: SVG + CSS + JS of the O and the panels, comments and indentation excluded (what a minifier would drop)."""
        import re
        css = lambda t: len(re.sub(r"\s+", " ", re.sub(r"/\*.*?\*/", "", t, flags=re.S)).strip().encode())   # noqa: E731
        js = lambda t: len(re.sub(r"\n\s*", "\n", re.sub(r"^\s*//.*$", "", re.sub(r"/\*.*?\*/", "", t, flags=re.S), flags=re.M)).encode())   # noqa: E731
        c, l, h = self.CSS, self.LANDING_JS, self.LANDING
        total = (css(c[c.index("/* ---------- Collaboration isotype"):c.index("@media print{")])
                 + css(c[c.index('/* "Why": a fixed list'):c.index("/* Three steps = three arcs */")])
                 + js(self.COMMON_JS[self.COMMON_JS.index("const ISOTYPE_DEFS"):self.COMMON_JS.index("const ISOTYPE_MARK")])
                 + js(l[l.index("/* ---- the animated O"):l.index("(async function init")])
                 + js(l[l.index('/* The visuals of the "why"'):l.index("function renderVersions")])
                 + len(h[h.index('<div class="orbit-layer'):h.index('<section class="hero"')].encode()))
        self.assertLess(total, 12 * 1024, f"{total} bytes")


if __name__ == "__main__":
    unittest.main()
