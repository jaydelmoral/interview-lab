"""DOMAIN: offline analysis of a CV or a job description. Pure functions, no I/O, no network, no AI: keyword and pattern matching.
Análisis local de un CV o una vacante: palabras clave y patrones, sin red ni IA. Nada se envía a ningún lado.
"""
import io
import re
import zipfile

MODULES = {
    "coding": ["algorithm", "algoritmo", "data structure", "estructuras de datos", "big o", "complexity", "complejidad",
               "problem solving", "coding challenge", "leetcode", "hackerrank", "competitive", "hashmap", "sorting"],
    "java-trivia": ["java", "jvm", "jdk", "spring", "hibernate", "jpa", "maven", "gradle", "stream api", "collections"],
    "qa": ["tdd", "bdd", "cucumber", "gherkin", "junit", "testng", "mockito", "selenium", "cypress", "playwright",
           "test automation", "automatización de pruebas", "sdet", "qa", "rest assured", "jacoco", "unit test", "pruebas unitarias"],
    "sql": ["sql", "postgres", "postgresql", "mysql", "oracle", "pl/sql", "plsql", "stored procedure", "procedimientos almacenados",
            "joins", "query optimization", "database", "base de datos", "bases de datos", "sql server", "mariadb"],
    "microservices": ["microservice", "microservicio", "spring boot", "spring cloud", "rest api", "restful", "kafka", "rabbitmq",
                      "eureka", "resilience4j", "circuit breaker", "api gateway", "grpc", "saga", "event driven"],
    "devops": ["docker", "kubernetes", "k8s", "jenkins", "ci/cd", "terraform", "ansible", "gitlab", "github actions", "helm",
               "aws", "gcp", "azure", "prometheus", "grafana", "devops", "pipeline", "openshift"],
    "architecture": ["architecture", "arquitectura", "design pattern", "patrones de diseño", "ddd", "domain-driven", "hexagonal",
                     "clean architecture", "cqrs", "solid", "system design", "scalability", "escalabilidad", "event sourcing",
                     "arquitecto", "architect"],
    "security": ["security", "seguridad", "owasp", "oauth", "oauth2", "jwt", "tls", "ssl", "encryption", "cifrado", "pentest",
                 "sast", "dast", "secure coding", "sso", "iam", "ceh", "cissp", "vulnerability", "vulnerabilidad", "keycloak"],
    "unix": ["linux", "unix", "bash", "shell", "awk", "sed", "grep", "cron", "command line", "línea de comandos", "ssh", "ubuntu", "red hat", "rhel"],
}
# Future modules shown as "coming soon" in the UI (not selectable yet)
COMING = {"ai": ["llm", "rag", "openai", "langchain", "vector", "prompt", "machine learning", "embedding", "genai"]}

LANGS = {
    "java": [r"\bjava\b", r"\bjvm\b", r"\bjdk\b", r"\bspring\b", r"\bhibernate\b"],
    "python": [r"\bpython\b", r"\bdjango\b", r"\bflask\b", r"\bfastapi\b", r"\bpandas\b"],
    "javascript": [r"\bjavascript\b", r"\btypescript\b", r"\bnode\.?js\b", r"\breact\b", r"\bangular\b"],
    "csharp": [r"c#", r"\.net\b", r"\basp\.net\b"],
    "go": [r"\bgolang\b"],
    "kotlin": [r"\bkotlin\b"],
}
JR = re.compile(r"\b(junior|jr\.?|trainee|entry[- ]level|becario|practicante)\b")
SR = re.compile(r"\b(senior|sr\.?|lead|principal|staff|architect|arquitecto|líder|lider)\b")
STAFF = re.compile(r"\bstaff\s+(?:software\s+|backend\s+|platform\s+)?(?:engineer|developer|architect|swe)\b")
PRINCIPAL = re.compile(r"\b(?:principal\s+(?:software\s+|backend\s+|platform\s+)?(?:engineer|developer|architect|consultant)|distinguished\s+engineer|ingeniero\s+principal|arquitecto\s+principal)\b")
YEARS = re.compile(r"(\d{1,2})\s*\+?\s*(?:years?|años?|yrs?)\b(?!\s+(?:en\s+el\s+mercado|de\s+(?:historia|trayectoria)|in\s+(?:business|the\s+market)|of\s+(?:history|innovation)|on\s+the\s+market))")
JAVA_V = re.compile(r"\b(?:java|jdk)\s*(?:se\s*)?(?:v\.?\s*)?(1\.8|8|11|17|21|22|23|24)\b")
PY_V = re.compile(r"\bpython\s*(?:v\.?\s*)?3\.(\d{1,2})\b")
MAX_TEXT = 200_000


def _has(text, kw):
    pat = r"(?<![a-z0-9])" + re.escape(kw) + r"(?![a-z0-9])"
    return re.search(pat, text) is not None


def docx_text(data: bytes) -> str:
    """Extracts the text of a .docx (a zip with word/document.xml) using only the standard library."""
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.getinfo("word/document.xml").file_size > 20_000_000:
            raise ValueError("document too large")
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<[^>]+>", "", xml)
    return re.sub(r"&amp;", "&", re.sub(r"&lt;", "<", re.sub(r"&gt;", ">", xml)))


def analyze(text: str) -> dict:
    text = (text or "")[:MAX_TEXT]
    low = text.lower()
    counts = {k: sum(len(re.findall(p, low)) for p in pats) for k, pats in LANGS.items()}
    language = max(counts, key=counts.get) if any(counts.values()) else "java"
    jv = [8 if v == "1.8" else int(v) for v in JAVA_V.findall(low)]
    pv = [int(v) for v in PY_V.findall(low)]
    version = None
    if language == "java" and jv:
        version = max(jv)
    elif language == "python" and pv:
        version = max(pv)
    years_list = [int(y) for y in YEARS.findall(low) if 0 < int(y) <= 40]
    years = max(years_list) if years_list else None
    senior_kw, junior_kw = bool(SR.search(low)), bool(JR.search(low))
    if years is not None:
        seniority = "jr" if years < 3 else "mid" if years < 6 else "sr"
    else:
        seniority = "sr" if senior_kw and not junior_kw else "jr" if junior_kw and not senior_kw else "mid"
    if years is None and senior_kw and junior_kw:
        seniority = "mid"
    if PRINCIPAL.search(low):                       # explicit, role-shaped titles only ("staff augmentation" must not match)
        seniority = "principal"
    elif STAFF.search(low):
        seniority = "staff"
    modules = []
    for mid, kws in MODULES.items():
        hits = [k for k in kws if _has(low, k)]
        if hits:
            modules.append({"id": mid, "score": len(hits), "hits": hits[:8]})
    modules.sort(key=lambda m: -m["score"])
    coming = [{"id": mid, "hits": [k for k in kws if _has(low, k)][:6]} for mid, kws in COMING.items()]
    coming = [c for c in coming if c["hits"]]
    if not any(m["id"] == "coding" for m in modules):
        modules.append({"id": "coding", "score": 0, "hits": []})  # coding practice is always useful
    return {"language": language, "language_counts": {k: v for k, v in counts.items() if v},
            "version": version, "seniority": seniority, "years": years,
            "modules": modules, "coming": coming, "chars": len(text)}
