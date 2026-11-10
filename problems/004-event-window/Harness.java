import java.util.*;

public class Harness {
    public static void main(String[] a) {
        Runner.run(a[0], Harness::t);
    }

    static void t(String id) throws Throwable {
        Solution s = new Solution();
        switch (id) {
            case "examples": {
                Check.eq(5, s.longestDistinctWindow("ABCADEB"), "ABCADEB");
                Check.eq(1, s.longestDistinctWindow("zzzz"), "zzzz");
                Check.eq(4, s.longestDistinctWindow("QWWKEWQ"), "QWWKEWQ");
                return;
            }
            case "edge": {
                Check.eq(0, s.longestDistinctWindow(""), "vacia");
                Check.eq(1, s.longestDistinctWindow(" "), "un espacio");
                Check.eq(1, s.longestDistinctWindow("a"), "un caracter");
                return;
            }
            case "window": {
                Check.eq(2, s.longestDistinctWindow("abba"), Check.t("abba (la ventana no debe retroceder)", "abba (the window must never move backwards)"));
                Check.eq(3, s.longestDistinctWindow("dvdf"), "dvdf");
                Check.eq(5, s.longestDistinctWindow("tmmzuxt"), "tmmzuxt");
                return;
            }
            case "large": {
                Check.eq(26, s.longestDistinctWindow("abcdefghijklmnopqrstuvwxyz".repeat(20_000)), "520000 caracteres");
                Check.eq(1, s.longestDistinctWindow("a".repeat(500_000)), "500000 iguales");
                StringBuilder sb = new StringBuilder();
                for (int rep = 0; rep < 25; rep++) for (int c = 0; c < 20_000; c++) sb.append((char) (256 + c));
                Check.eq(20_000, s.longestDistinctWindow(sb.toString()), Check.t("500000 caracteres con 20000 distintos", "500000 characters with 20000 distinct"));
                return;
            }
            default: throw new AssertionError(Check.t("prueba desconocida", "unknown test"));
        }
    }

}
