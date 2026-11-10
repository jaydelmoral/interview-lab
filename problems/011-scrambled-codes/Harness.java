import java.util.*;

public class Harness {
    public static void main(String[] a) {
        Runner.run(a[0], Harness::t);
    }

    static void t(String id) throws Throwable {
        Solution s = new Solution();
        switch (id) {
            case "example": {
                Check.eq(norm(List.of(List.of("A7B", "7BA", "B7A"), List.of("XY", "YX"), List.of("Q9"))),
                         norm(s.groupScrambled(new String[]{"A7B", "XY", "7BA", "YX", "Q9", "B7A"})), "ejemplo");
                return;
            }
            case "edge": {
                Check.eq(norm(List.of(List.of(""))), norm(s.groupScrambled(new String[]{""})), Check.t("una cadena vacia", "one empty string"));
                Check.eq(norm(List.of(List.of("a"))), norm(s.groupScrambled(new String[]{"a"})), "un caracter");
                Check.eq(0, s.groupScrambled(new String[0]).size(), Check.t("arreglo vacio", "empty array"));
                return;
            }
            case "duplicates": {
                Check.eq(norm(List.of(List.of("ab", "ab", "ba"), List.of("c"))),
                         norm(s.groupScrambled(new String[]{"ab", "ba", "c", "ab"})), Check.t("palabras repetidas", "repeated codes"));
                return;
            }
            case "large": {
                Random rnd = new Random(5);
                int n = 100_000;
                String[] in = new String[n];
                Map<String, List<String>> exp = new HashMap<>();
                for (int i = 0; i < n; i++) {
                    int len = 1 + rnd.nextInt(6);
                    char[] c = new char[len];
                    for (int j = 0; j < len; j++) c[j] = (char) ('a' + rnd.nextInt(4));
                    in[i] = new String(c);
                    char[] k = c.clone();
                    Arrays.sort(k);
                    exp.computeIfAbsent(new String(k), x -> new ArrayList<>()).add(in[i]);
                }
                Check.eq(norm(new ArrayList<>(exp.values())), norm(s.groupScrambled(in)), "100000 palabras");
                return;
            }
            default: throw new AssertionError(Check.t("prueba desconocida", "unknown test"));
        }
    }

    static Set<List<String>> norm(List<List<String>> groups) {
        Set<List<String>> out = new HashSet<>();
        for (List<String> g : groups) {
            List<String> c = new ArrayList<>(g);
            Collections.sort(c);
            out.add(c);
        }
        return out;
    }
}
