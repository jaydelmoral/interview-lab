import java.util.*;

public class Harness {
    public static void main(String[] a) {
        Runner.run(a[0], Harness::t);
    }

    static void t(String id) throws Throwable {
        
        switch (id) {
            case "example": {
                LatencyTracker m = new LatencyTracker();
                m.record(40); m.record(60);
                Check.eq(50.0, m.median(), "[40,60]");
                m.record(100);
                Check.eq(60.0, m.median(), "[40,60,100]");
                return;
            }
            case "single": {
                LatencyTracker m = new LatencyTracker();
                m.record(-5);
                Check.eq(-5.0, m.median(), "un elemento");
                return;
            }
            case "duplicates": {
                LatencyTracker m = new LatencyTracker();
                for (int v : new int[]{5, 5, 5, 5}) m.record(v);
                Check.eq(5.0, m.median(), Check.t("todos iguales", "all equal"));
                LatencyTracker m2 = new LatencyTracker();
                m2.record(Integer.MAX_VALUE); m2.record(Integer.MAX_VALUE);
                Check.eq((double) Integer.MAX_VALUE, m2.median(), Check.t("desbordamiento al promediar", "overflow when averaging"));
                return;
            }
            case "large": {
                int n = 200_000;
                LatencyTracker up = new LatencyTracker();
                for (int i = 1; i <= n; i++) {
                    up.record(i);
                    if (up.median() != (i + 1) / 2.0) throw new AssertionError(Check.t("ascendente: mediana incorrecta tras ", "ascending: wrong median after ") + i);
                }
                LatencyTracker down = new LatencyTracker();
                for (int k = 1; k <= n; k++) {
                    down.record(n - k + 1);
                    double exp = ((n - k + 1) + (double) n) / 2.0;
                    if (down.median() != exp) throw new AssertionError(Check.t("descendente: mediana incorrecta tras ", "descending: wrong median after ") + k);
                }
                return;
            }
            default: throw new AssertionError(Check.t("prueba desconocida", "unknown test"));
        }
    }

}
