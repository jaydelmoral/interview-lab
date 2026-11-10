import java.util.*;

public class Harness {
    public static void main(String[] a) {
        Runner.run(a[0], Harness::t);
    }

    static void t(String id) throws Throwable {
        Solution s = new Solution();
        switch (id) {
            case "examples": {
                Check.ok(s.canSegment("redbluered", List.of("red", "blue")), "redbluered");
                Check.ok(s.canSegment("bluebluered", List.of("red", "blue")), Check.t("bluebluered (codigos reutilizables)", "bluebluered (reusable codes)"));
                Check.ok(!s.canSegment("redgreenblue", List.of("red", "blue", "gre")), "redgreenblue");
                return;
            }
            case "edge": {
                Check.ok(s.canSegment("", List.of("a")), Check.t("cadena vacia", "empty string"));
                Check.ok(!s.canSegment("a", List.of()), Check.t("diccionario vacio", "empty catalog"));
                Check.ok(s.canSegment("aaaa", List.of("a")), Check.t("una palabra repetida", "one repeated word"));
                return;
            }
            case "greedy": {
                Check.ok(s.canSegment("cars", List.of("car", "ca", "rs")), "cars: car+s no sirve, ca+rs si");
                Check.ok(s.canSegment("aaaaaaa", List.of("aaaa", "aaa")), "aaaaaaa");
                return;
            }
            case "large": {
                Check.ok(!s.canSegment("a".repeat(800) + "b", List.of("a", "aa", "aaa", "aaaa")), "800 a's y una b");
                Check.ok(s.canSegment("a".repeat(800), List.of("a", "aa", "aaa", "aaaa")), "800 a's");
                return;
            }
            default: throw new AssertionError(Check.t("prueba desconocida", "unknown test"));
        }
    }

}
