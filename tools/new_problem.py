#!/usr/bin/env python3
"""Create a new problem in YOUR workspace from a working template.
Crea un problema nuevo en TU carpeta de trabajo a partir de una plantilla que funciona.

    python3 tools/new_problem.py my-first-problem "Sum of Even Orders" [--domain retail]

It creates  workspace/problems/<id>/  (or $ILAB_HOME/problems/<id>/) with every file filled with a small working example,
then runs the validator so you start from a green state. Edit the files, run `python3 tools/validate.py <id>` again, done.
Your problems stay on your machine (the workspace/ folder is git-ignored).

YOU are responsible for the rights of what you write here. Read docs/CONTENT-GUIDELINES.md first.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = Path(os.environ.get("ILAB_HOME", ROOT / "workspace")).resolve()

STATEMENT_EN = """# {title}

Describe the business situation in one or two sentences, using a SECTOR (airline, e-commerce, bank...) and never a real company name.

Implement `int sumEven(int[] nums)` in class `Solution`: it returns the sum of the even numbers in `nums`. Target complexity: O(n).

```java
sumEven(new int[]{3, 8, 5, 10})  // 18
sumEven(new int[]{})             // 0
```
"""
STATEMENT_ES = """# {title}

Describe la situación de negocio en una o dos frases, usando un GIRO (aerolínea, comercio electrónico, banco...) y nunca el nombre de una empresa real.

Implementa `int sumEven(int[] nums)` en la clase `Solution`: devuelve la suma de los números pares de `nums`. Complejidad objetivo: O(n).

```java
sumEven(new int[]{3, 8, 5, 10})  // 18
sumEven(new int[]{})             // 0
```
"""
STARTER = """import java.util.*;

class Solution {

    public int sumEven(int[] nums) {
        // TODO
        return -1;
    }
}
"""
REFERENCE = """import java.util.*;

class Solution {

    public int sumEven(int[] nums) {
        int sum = 0;
        for (int n : nums) if (n % 2 == 0) sum += n;
        return sum;
    }
}
"""
HARNESS = """import java.util.*;

/** Hidden tests. One process per test: java Harness <id>.  Runner and Check come from grader/common/. */
public class Harness {
    public static void main(String[] a) {
        Runner.run(a[0], Harness::t);
    }

    static void t(String id) throws Throwable {
        Solution s = new Solution();
        switch (id) {
            case "basic": {
                Check.eq(18, s.sumEven(new int[]{3, 8, 5, 10}), "example");
                Check.eq(6, s.sumEven(new int[]{2, 4}), "all even");
                return;
            }
            case "edge": {
                Check.eq(0, s.sumEven(new int[]{}), Check.t("arreglo vacio", "empty array"));
                Check.eq(-4, s.sumEven(new int[]{-4, 3}), Check.t("negativos", "negative numbers"));
                return;
            }
            case "large": {
                int[] big = new int[2_000_000];
                Arrays.fill(big, 2);
                Check.eq(4_000_000, s.sumEven(big), "2M items");
                return;
            }
            default: throw new AssertionError("unknown test");
        }
    }
}
"""


def test(tid, cat, title, pts, why_es, how_es, why_en, how_en):
    return {"id": tid, "category": cat, "title": title, "points": pts, "fail_why": why_es, "fail_how": how_es,
            "fail_why_en": why_en, "fail_how_en": how_en}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    domain = ""
    if "--domain" in sys.argv:
        domain = sys.argv[sys.argv.index("--domain") + 1]
        args = [a for a in args if a != domain]
    if len(args) < 2:
        print(__doc__)
        return 2
    pid, title = args[0], args[1]
    if not re.match(r"^[a-z0-9][a-z0-9-]{2,63}$", pid):
        print("The id must be 3-64 chars: lowercase letters, digits and hyphens. / El id: minúsculas, números y guiones.")
        return 2
    d = HOME / "problems" / pid
    if d.exists():
        print(f"{d} already exists. / Ya existe.")
        return 1
    (d / "reference").mkdir(parents=True)
    (d / "problem.md").write_text(STATEMENT_EN.replace("{title}", title))
    (d / "problem.es.md").write_text(STATEMENT_ES.replace("{title}", title))
    (d / "starter.java").write_text(STARTER)
    (d / "reference" / "Solution.java").write_text(REFERENCE)
    (d / "Harness.java").write_text(HARNESS)
    meta = {"id": pid, "title": title, "class": "Solution", "time_limit_min": 20, "domain": domain,
            "tags": ["arrays", "o(n)"], "timeout_ms": 2000,
            "tests": [
                test("basic", "Problem solving", "Works with the examples", 40,
                     "Fallan los ejemplos del enunciado.", "Traza los ejemplos a mano antes de enviar.",
                     "The statement's examples fail.", "Trace the examples by hand before submitting."),
                test("edge", "Reliability", "Handles empty input and negative numbers", 30,
                     "Falla con arreglo vacío o negativos.", "Revisa 0 elementos, 1 elemento y números negativos.",
                     "Fails with empty input or negative numbers.", "Check 0 items, 1 item and negative numbers."),
                test("large", "Problem solving", "O(n): works with two million items in reasonable time", 80,
                     "Tu solución es demasiado lenta para 2 millones de elementos.", "Un solo recorrido: O(n).",
                     "Your solution is too slow for 2 million items.", "A single pass: O(n)."),
            ],
            "author": "YOUR NAME", "license": "YOUR LICENSE (e.g. CC-BY-4.0, or 'private')", "origin": "original"}
    (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    print(f"Created {d}\nRunning the validator...\n")
    return subprocess.call([sys.executable, str(ROOT / "tools" / "validate.py"), pid])


if __name__ == "__main__":
    sys.exit(main())
