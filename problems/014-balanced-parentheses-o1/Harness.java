import java.util.*;

public class Harness {
    public static void main(String[] a) {
        Runner.run(a[0], Harness::t);
    }

    static void t(String id) throws Throwable {
        Solution s = new Solution();
        switch (id) {
            case "basic": {
                Check.ok(s.isBalanced("(())"), "(())");
                Check.ok(s.isBalanced("()()"), "()()");
                Check.ok(!s.isBalanced("(()"), "(()");
                Check.ok(!s.isBalanced("())"), "())");
                return;
            }
            case "order": {
                Check.ok(!s.isBalanced(")("), Check.t(")( tiene el mismo conteo pero es invalida", ")( has the same count but is invalid"));
                Check.ok(!s.isBalanced("())("), "())(");
                return;
            }
            case "edge": {
                Check.ok(s.isBalanced(""), "vacia");
                Check.ok(!s.isBalanced("("), Check.t("una apertura", "one opening"));
                Check.ok(!s.isBalanced(")"), "un cierre");
                return;
            }
            case "large": {
                Check.ok(s.isBalanced("()".repeat(2_500_000)), Check.t("5 millones de caracteres", "5 million characters"));
                return;
            }
            default: throw new AssertionError(Check.t("prueba desconocida", "unknown test"));
        }
    }

}
