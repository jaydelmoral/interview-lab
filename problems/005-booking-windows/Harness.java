import java.util.*;

public class Harness {
    public static void main(String[] a) {
        Runner.run(a[0], Harness::t);
    }

    static void t(String id) throws Throwable {
        Solution s = new Solution();
        switch (id) {
            case "example": {
                Check.eq(new int[][]{{9, 14}, {16, 18}, {20, 22}}, s.mergeWindows(new int[][]{{9, 12}, {11, 14}, {16, 18}, {20, 22}}), "ejemplo");
                return;
            }
            case "touching": {
                Check.eq(new int[][]{{8, 12}}, s.mergeWindows(new int[][]{{8, 10}, {10, 12}}), "[8,10] y [10,12] se tocan");
                Check.eq(new int[][]{{1, 10}}, s.mergeWindows(new int[][]{{1, 10}, {2, 3}, {4, 5}}), "contenidos");
                return;
            }
            case "unsorted": {
                Check.eq(new int[][]{{1, 6}, {8, 10}}, s.mergeWindows(new int[][]{{8, 10}, {1, 3}, {2, 6}}), "desordenados");
                return;
            }
            case "empty": {
                Check.eq(new int[0][], s.mergeWindows(new int[0][]), "vacio");
                Check.eq(new int[][]{{5, 7}}, s.mergeWindows(new int[][]{{5, 7}}), Check.t("uno solo", "a single one"));
                return;
            }
            case "large": {
                int n = 200_000;
                int[][] chain = new int[n][];
                for (int i = 0; i < n; i++) chain[i] = new int[]{i, i + 2};
                shuffle(chain);
                Check.eq(new int[][]{{0, n + 1}}, s.mergeWindows(chain), Check.t("cadena que se solapa (200000)", "overlapping chain (200000)"));
                int[][] apart = new int[n][];
                for (int i = 0; i < n; i++) apart[i] = new int[]{i * 3, i * 3 + 2};
                shuffle(apart);
                int[][] r = s.mergeWindows(apart);
                Check.eq(n, r.length, Check.t("intervalos separados: cantidad", "separate windows: count"));
                Check.eq(new int[]{0, 2}, r[0], "primero");
                Check.eq(new int[]{(n - 1) * 3, (n - 1) * 3 + 2}, r[n - 1], "ultimo");
                return;
            }
            default: throw new AssertionError(Check.t("prueba desconocida", "unknown test"));
        }
    }

    static void shuffle(int[][] a) {
        Random rnd = new Random(1);
        for (int i = a.length - 1; i > 0; i--) {
            int j = rnd.nextInt(i + 1);
            int[] tmp = a[i]; a[i] = a[j]; a[j] = tmp;
        }
    }
}
