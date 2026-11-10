import java.util.*;

public class Harness {
    public static void main(String[] a) {
        Runner.run(a[0], Harness::t);
    }

    static void t(String id) throws Throwable {
        Solution s = new Solution();
        switch (id) {
            case "basic": {
                Check.eq(Optional.of('w'), s.firstUnique("swiss"), "swiss");
                Check.eq(Optional.of('c'), s.firstUnique("aabbc"), "aabbc");
                Check.eq(Optional.of('a'), s.firstUnique("abc"), "abc");
                Check.eq(Optional.of('x'), s.firstUnique("x"), "x");
                return;
            }
            case "edge": {
                Check.eq(Optional.empty(), s.firstUnique(null), "null");
                Check.eq(Optional.empty(), s.firstUnique(""), Check.t("cadena vacia", "empty string"));
                Check.eq(Optional.empty(), s.firstUnique("aabb"), Check.t("todo repetido", "everything repeated"));
                return;
            }
            case "order": {
                Check.eq(Optional.of('c'), s.firstUnique("cbaa"), Check.t("cbaa (primero en aparecer, no el menor alfabeticamente)", "cbaa (first to appear, not the alphabetically smallest)"));
                Check.eq(Optional.of('z'), s.firstUnique("aabbzcc"), "aabbzcc");
                return;
            }
            case "large": {
                Check.eq(Optional.of('c'), s.firstUnique("ab".repeat(150_000) + "c"), "300001 caracteres");
                Check.eq(Optional.of('q'), s.firstUnique("q" + "ab".repeat(150_000)), "q al inicio");
                Check.eq(Optional.of('d'), s.firstUnique("a".repeat(100_000) + "b".repeat(100_000) + "c".repeat(100_000) + "d"), Check.t("bloques de 100000", "blocks of 100000"));
                return;
            }
            default: throw new AssertionError(Check.t("prueba desconocida", "unknown test"));
        }
    }

}
