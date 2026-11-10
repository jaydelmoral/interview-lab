import java.util.*;

public class Harness {
    public static void main(String[] a) {
        Runner.run(a[0], Harness::t);
    }

    static void t(String id) throws Throwable {
        Solution s = new Solution();
        switch (id) {
            case "example": { chk(new int[]{1200, 350, 899, 4500}, 1550, s.pairForBalance(new int[]{1200, 350, 899, 4500}, 1550)); return; }
            case "duplicates": {
                chk(new int[]{500, 500}, 1000, s.pairForBalance(new int[]{500, 500}, 1000));
                chk(new int[]{300, 100, 500}, 600, s.pairForBalance(new int[]{300, 100, 500}, 600));
                return;
            }
            case "negatives": {
                chk(new int[]{-30, 40, 30, 900}, 0, s.pairForBalance(new int[]{-30, 40, 30, 900}, 0));
                chk(new int[]{-1, -2, -3, -4, -5}, -8, s.pairForBalance(new int[]{-1, -2, -3, -4, -5}, -8));
                return;
            }
            case "nosolution": {
                Check.raises(IllegalArgumentException.class, () -> s.pairForBalance(new int[]{1, 2, 3}, 99), Check.t("sin solucion", "no solution"));
                return;
            }
            case "large": {
                int n = 200_000;
                int[] a = new int[n];
                for (int i = 0; i < n; i++) a[i] = i * 2;
                int target = a[n - 1] + a[n - 2];
                chk(a, target, s.pairForBalance(a, target));
                return;
            }
            default: throw new AssertionError(Check.t("prueba desconocida", "unknown test"));
        }
    }

    static void chk(int[] nums, int target, int[] r) {
        Check.ok(r != null && r.length == 2, Check.t("debe devolver exactamente 2 indices", "must return exactly 2 indices"));
        Check.ok(r[0] != r[1], Check.t("no reutilices el mismo indice", "do not reuse the same index"));
        Check.ok(r[0] >= 0 && r[1] >= 0 && r[0] < nums.length && r[1] < nums.length, Check.t("indice fuera de rango", "index out of range"));
        Check.ok(nums[r[0]] + nums[r[1]] == target, Check.t("los indices ", "the indices ") + Arrays.toString(r) + " no suman " + target);
    }
}
