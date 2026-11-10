import java.util.*;

public class Harness {
    public static void main(String[] a) {
        Runner.run(a[0], Harness::t);
    }

    static void t(String id) throws Throwable {
        Solution s = new Solution();
        switch (id) {
            case "example": {
                Check.eq("elephant", s.longestFirst(new String[]{"cat", "elephant", "dog", "hippo", "bee"}), "ejemplo");
                return;
            }
            case "ties": {
                Check.eq("aaa", s.longestFirst(new String[]{"aaa", "bbb", "c"}), Check.t("empate al inicio", "tie at the start"));
                Check.eq("bb", s.longestFirst(new String[]{"a", "bb", "cc", "d"}), Check.t("empate en medio", "tie in the middle"));
                Check.eq("xyz", s.longestFirst(new String[]{"xyz", "abc", "def"}), Check.t("todos iguales", "all equal"));
                return;
            }
            case "edge": {
                Check.eq("", s.longestFirst(null), "null");
                Check.eq("", s.longestFirst(new String[0]), "vacio");
                Check.eq("solo", s.longestFirst(new String[]{"solo"}), "un elemento");
                Check.eq("a", s.longestFirst(new String[]{"", "a", ""}), Check.t("con cadenas vacias", "with empty strings"));
                return;
            }
            case "nomutate": {
                String[] in = {"bb", "a", "ccc", "dd"};
                String[] copy = in.clone();
                s.longestFirst(in);
                Check.eq(copy, in, Check.t("no debes ordenar ni modificar el arreglo de entrada", "you must not sort or modify the input array"));
                return;
            }
            case "large": {
                String[] a = new String[1_000_000];
                Arrays.fill(a, "ab");
                a[400_000] = "abcde";
                a[700_000] = "vwxyz";
                Check.eq("abcde", s.longestFirst(a), Check.t("un millon de elementos", "one million items"));
                return;
            }
            default: throw new AssertionError(Check.t("prueba desconocida", "unknown test"));
        }
    }

}
