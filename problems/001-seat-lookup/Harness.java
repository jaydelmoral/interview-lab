import java.util.*;

/** Hidden tests. One process per test: java Harness <id>. */
public class Harness {

    public static void main(String[] a) {
        Runner.run(a[0], Harness::t);
    }

    static void t(String id) throws Throwable {
        switch (id) {
            case "small": {
                int[] seats = {12, 18, 33, 47};
                Check.ok(Solution.isBooked(seats, 33), "isBooked(seats, 33) must be true");
                Check.ok(!Solution.isBooked(seats, 20), "isBooked(seats, 20) must be false");
                Check.ok(Solution.isBooked(seats, 18), "isBooked(seats, 18) must be true");
                Check.ok(!Solution.isBooked(seats, 1000), "isBooked(seats, 1000) must be false");
                return;
            }
            case "empty": {
                Check.ok(!Solution.isBooked(new int[0], 5), "empty array must return false");
                return;
            }
            case "first": {
                int[] seats = {12, 18, 33, 47};
                Check.ok(Solution.isBooked(seats, 12), "first element not found");
                Check.ok(Solution.isBooked(seats, 47), "last element not found");
                Check.ok(!Solution.isBooked(seats, 11), "value below the minimum returned true");
                Check.ok(!Solution.isBooked(seats, 48), "value above the maximum returned true");
                Check.ok(Solution.isBooked(new int[]{7}, 7), "single element (hit)");
                Check.ok(!Solution.isBooked(new int[]{7}, 8), "single element (miss)");
                int[] dup = {1, 1, 1, 2, 2, 5};
                Check.ok(Solution.isBooked(dup, 2) && !Solution.isBooked(dup, 3), "repeated values");
                return;
            }
            case "large": {
                int n = 1_000_000;
                int[] seats = new int[n];
                for (int i = 0; i < n; i++) seats[i] = i * 3 - 1_000;
                Random rnd = new Random(42);
                for (int q = 0; q < 50_000; q++) {
                    int idx = rnd.nextInt(n);
                    boolean hit = (q % 2 == 0);
                    int k = seats[idx] + (hit ? 0 : 1);
                    Check.ok(Solution.isBooked(seats, k) == hit, "wrong result with 1M items (seat=" + k + ")");
                }
                return;
            }
            default: throw new AssertionError("unknown test");
        }
    }
}
