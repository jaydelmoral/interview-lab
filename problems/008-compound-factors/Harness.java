import java.util.*;

public class Harness {
    public static void main(String[] a) {
        Runner.run(a[0], Harness::t);
    }

    static void t(String id) throws Throwable {
        Solution s = new Solution();
        switch (id) {
            case "example": {
                Check.eq(new int[]{60, 40, 30, 24}, s.factorsExcludingSelf(new int[]{2, 3, 4, 5}), "ejemplo");
                Check.eq(new int[]{4, 3}, s.factorsExcludingSelf(new int[]{3, 4}), Check.t("dos elementos", "two elements"));
                return;
            }
            case "zeros": {
                Check.eq(new int[]{0, 12, 0, 0}, s.factorsExcludingSelf(new int[]{1, 0, 3, 4}), "un cero");
                Check.eq(new int[]{0, 0, 0}, s.factorsExcludingSelf(new int[]{0, 0, 5}), Check.t("dos ceros", "two zeros"));
                return;
            }
            case "negatives": {
                Check.eq(new int[]{-6, 3, -2}, s.factorsExcludingSelf(new int[]{1, -2, 3}), "negativos");
                Check.eq(new int[]{-24, 12, -8, 6}, s.factorsExcludingSelf(new int[]{-1, 2, -3, 4}), "negativos 2");
                return;
            }
            case "large": {
                int n = 1_000_000;
                int[] a = new int[n];
                for (int i = 0; i < n; i++) a[i] = (i % 2 == 0) ? 1 : -1;
                int[] r = s.factorsExcludingSelf(a);
                Check.eq(n, r.length, "largo");
                // 500000 elementos -1 -> producto total +1; output[i] = 1 / a[i] = a[i]
                Check.eq(1, r[0], "primero");
                Check.eq(-1, r[1], "segundo");
                Check.eq(-1, r[n - 1], "ultimo");
                return;
            }
            default: throw new AssertionError(Check.t("prueba desconocida", "unknown test"));
        }
    }

}
