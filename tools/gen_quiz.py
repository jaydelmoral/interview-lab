#!/usr/bin/env python3
"""Genera problems/101-predice-la-salida/quiz.json.

The correct output is produced by the JVM (javac + java), it is not written by hand.
`creo` is what the author believed would be printed: if the JVM differs, the script reports it.
La salida correcta la produce la JVM; `creo` es lo que el autor creía que saldría.

    python3 tools/gen_quiz.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "problems" / "101-predice-la-salida"

# (id, tema, declaraciones, cuerpo de main, creo, explicación)
Q = [
    ("q01", "Strings y operadores", "",
     'System.out.println(10 + 20 + "Java" + 10 + 20);', "30Java1020",
     "Se evalúa de izquierda a derecha: 10 + 20 = 30 (ambos son números); luego 30 + \"Java\" ya es concatenación, y lo que sigue se concatena como texto: 10 y 20, sin sumar."),
    ("q02", "Caché de Integer", "",
     "Integer a = 120, b = 120;\nInteger c = 130, d = 130;\nSystem.out.println((a == b) + \" \" + (c == d));", "true false",
     "== compara referencias. Java reutiliza objetos Integer entre -128 y 127 (caché de autoboxing); 130 crea objetos distintos. Para comparar valores usa equals."),
    ("q03", "Postincremento", "",
     "int i = 5;\ni = i++;\nSystem.out.println(i);", "5",
     "i++ devuelve el valor viejo (5) y luego incrementa i a 6, pero la asignación i = ... escribe ese 5 encima. Resultado: 5."),
    ("q04", "String pool", "",
     'System.out.println("Java".substring(0, 0) == "");', "true",
     "Da true en Java 17/21 porque el substring vacío reutiliza el literal \"\", pero es un detalle de implementación. La lección: nunca compares Strings con ==; usa equals."),
    ("q05", "String pool", "",
     'String a = "ab";\nString b = "a" + "b";\nString x = "a";\nString c = new String("ab");\nString d = x + "b";\nSystem.out.println((a == b) + " " + (a == c) + " " + (a == d) + " " + (a == d.intern()));',
     "true false false true",
     "\"a\" + \"b\" es una constante en tiempo de compilación y apunta al mismo literal. new String(...) y la concatenación con una variable en ejecución crean objetos nuevos. intern() devuelve el literal del pool."),
    ("q06", "Punto flotante", "",
     "System.out.println(0.1 + 0.2 == 0.3);\nSystem.out.println(0.1 + 0.2);", "false\n0.30000000000000004",
     "double usa binario: 0.1 y 0.2 no son exactos. Compara con tolerancia (Math.abs(a - b) < 1e-9) o usa BigDecimal para dinero."),
    ("q07", "char y promoción numérica", "",
     "System.out.println('a' + 1);\nchar c = 'a';\nc += 1;\nSystem.out.println(c);", "98\nb",
     "'a' + 1 promueve a int (97 + 1 = 98). La asignación compuesta c += 1 hace un cast implícito a char, por eso queda 'b'."),
    ("q08", "Colecciones inmutables", "",
     "try {\n    List.of(1, 2).add(3);\n} catch (Exception e) {\n    System.out.println(e.getClass().getSimpleName());\n}", "UnsupportedOperationException",
     "List.of crea una lista inmutable: add, remove o set lanzan UnsupportedOperationException. Arrays.asList tampoco permite agregar ni quitar."),
    ("q09", "Desbordamiento", "",
     "System.out.println(Integer.MAX_VALUE + 1);", "-2147483648",
     "int no lanza error al desbordar: da la vuelta al mínimo. Para detectarlo usa Math.addExact (lanza ArithmeticException) o long."),
    ("q10", "try / finally", "static int f() {\n    try {\n        return 1;\n    } finally {\n        System.out.println(\"finally\");\n    }\n}\n",
     "System.out.println(f());", "finally\n1",
     "finally se ejecuta antes de que el método devuelva el valor. Primero imprime \"finally\" y después main imprime 1."),
    ("q11", "Math.round", "",
     "System.out.println(Math.round(2.5) + \" \" + Math.round(-2.5));", "3 -2",
     "Math.round redondea hacia +infinito en los empates (floor(x + 0.5)): 2.5 -> 3 y -2.5 -> -2."),
    ("q12", "Conversión numérica", "",
     "System.out.println((byte) 200);", "-56",
     "byte va de -128 a 127. 200 se trunca a los 8 bits bajos (11001000), que en complemento a dos es -56."),
    ("q13", "Streams: evaluación perezosa", "",
     "Stream.of(1, 2, 3).peek(x -> System.out.print(x)).map(x -> x * 2);\nSystem.out.println(\"done\");", "done",
     "Las operaciones intermedias (peek, map) no se ejecutan hasta que hay una operación terminal (collect, forEach, count...). Aquí no hay terminal, así que peek nunca imprime."),
    ("q14", "Pattern matching (Java 21)", "",
     'Object o = 42;\nString r = switch (o) {\n    case Integer i when i > 40 -> "big";\n    case Integer i -> "int";\n    default -> "other";\n};\nSystem.out.println(r);', "big",
     "Java 21 estabiliza el pattern matching en switch. Los casos se evalúan en orden: 42 es Integer y cumple la guarda i > 40."),
    ("q15", "Records", "record P(int x) {}\n",
     "P a = new P(1), b = new P(1);\nSystem.out.println(a.equals(b) + \" \" + (a == b) + \" \" + a);", "true false P[x=1]",
     "Un record genera equals, hashCode y toString por valor, así que equals da true. == sigue comparando referencias (false). toString imprime P[x=1]."),
    ("q16", "Unboxing y null", "",
     "Integer x = null;\ntry {\n    int y = true ? x : 0;\n} catch (Exception e) {\n    System.out.println(e.getClass().getSimpleName());\n}", "NullPointerException",
     "En el operador ternario con Integer e int, Java aplica promoción numérica y hace unboxing de x. Como x es null, lanza NullPointerException."),
    ("q17", "List.remove", "",
     "List<Integer> l = new ArrayList<>(List.of(1, 2, 3));\nl.remove(1);\nSystem.out.println(l);", "[1, 3]",
     "Con un int literal se llama remove(int index): quita el elemento de la posición 1 (el 2), no el valor 1. Para quitar por valor usa l.remove(Integer.valueOf(1))."),
    ("q18", "Sequenced collections (Java 21)", "",
     "List<Integer> l = List.of(1, 2, 3);\nSystem.out.println(l.reversed() + \" \" + l.getFirst());", "[3, 2, 1] 1",
     "Java 21 agrega SequencedCollection: reversed(), getFirst() y getLast() en List, Deque, LinkedHashSet, etc."),
    ("q19", "equals y hashCode en arreglos", "",
     "Set<int[]> s = new HashSet<>();\ns.add(new int[]{1});\nSystem.out.println(s.contains(new int[]{1}));", "false",
     "Los arreglos no sobrescriben equals/hashCode: comparan por identidad. Por eso un HashSet<int[]> no encuentra otro arreglo con el mismo contenido. Usa List<Integer> o Arrays.equals/hashCode."),
    ("q20", "final", "",
     "final List<Integer> l = new ArrayList<>();\nl.add(1);\nSystem.out.println(l);", "[1]",
     "final impide reasignar la referencia, no modificar el objeto. Para una lista realmente inmutable usa List.of o Collections.unmodifiableList."),
]

QEN = json.loads((ROOT / "tools" / "quiz_en.json").read_text())

HEADER = "import java.util.*;\nimport java.util.stream.*;\n\n"


def run_one(decls: str, body: str) -> str:
    src = HEADER + "public class Q {\n" + decls + "\npublic static void main(String[] args) {\n" + body + "\n}\n}\n"
    with tempfile.TemporaryDirectory(prefix="quiz-") as tmp:
        (Path(tmp) / "Q.java").write_text(src)
        c = subprocess.run(["javac", "Q.java"], cwd=tmp, capture_output=True, text=True)
        if c.returncode != 0:
            raise SystemExit("no compila:\n" + src + "\n" + c.stderr)
        r = subprocess.run(["java", "-cp", tmp, "Q"], capture_output=True, text=True, timeout=30)
        return r.stdout.strip()


def main():
    questions, bad = [], 0
    for qid, topic, decls, body, creo, why in Q:
        real = run_one(decls, body)
        if real != creo:
            bad += 1
            print(f"DIFERENCIA en {qid}: yo creía {creo!r} y la JVM dio {real!r}")
        code = (decls + ("\n" if decls else "") + body).strip()
        en = QEN.get(qid, {})
        questions.append({"id": qid, "topic": topic, "code": code, "expected": real, "explanation": why,
                          "topic_en": en.get("topic", ""), "explanation_en": en.get("explanation", ""),
                          "level": en.get("level", "mid"), "min_java": en.get("min_java", 8)})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "quiz.json").write_text(json.dumps(questions, ensure_ascii=False, indent=2) + "\n")
    (OUT / "meta.json").write_text(json.dumps({
        "id": "101-predice-la-salida", "kind": "quiz", "title": "Predice la salida (Java 17/21)",
        "time_limit_min": 15, "tags": ["trivia", "strings", "autoboxing", "streams", "java21"],
        "origin": "original", "license": "CC-BY-4.0", "author": "Javier Morales Barrera (@jaydelmoral), with Claude (Anthropic)",
    }, ensure_ascii=False, indent=2) + "\n")
    print(f"{len(questions)} preguntas generadas; diferencias con mi creencia: {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
