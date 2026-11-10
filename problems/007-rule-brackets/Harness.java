import java.util.*;

public class Harness {
    public static void main(String[] a) {
        Runner.run(a[0], Harness::t);
    }

    static void t(String id) throws Throwable {
        Solution s = new Solution();
        switch (id) {
            case "basic": {
                Check.ok(s.hasBalancedBrackets("()"), "()");
                Check.ok(s.hasBalancedBrackets("()[]{}"), "()[]{}");
                Check.ok(s.hasBalancedBrackets("{[]}"), "{[]}");
                Check.ok(!s.hasBalancedBrackets("(]"), "(]");
                Check.ok(!s.hasBalancedBrackets("([)]"), Check.t("([)] (el orden importa)", "([)] (order matters)"));
                return;
            }
            case "edge": {
                Check.ok(s.hasBalancedBrackets(""), Check.t("cadena vacia es valida", "an empty string is valid"));
                Check.ok(!s.hasBalancedBrackets(")"), Check.t("cierre sin apertura", "closing without an opening"));
                Check.ok(!s.hasBalancedBrackets("(("), Check.t("aperturas sin cerrar", "openings left unclosed"));
                Check.ok(!s.hasBalancedBrackets("("), Check.t("una apertura", "one opening"));
                Check.ok(!s.hasBalancedBrackets("}{"), "}{");
                return;
            }
            case "nested": {
                Check.ok(s.hasBalancedBrackets("{[()()]([])}"), "anidado");
                Check.ok(!s.hasBalancedBrackets("{[()()]([)]}"), Check.t("anidado con error", "nested with an error"));
                return;
            }
            case "large": {
                Check.ok(s.hasBalancedBrackets("(".repeat(500_000) + ")".repeat(500_000)), "1000000 caracteres");
                Check.ok(!s.hasBalancedBrackets("(".repeat(500_000) + ")".repeat(499_999)), Check.t("falta un cierre", "one closing is missing"));
                return;
            }
            default: throw new AssertionError(Check.t("prueba desconocida", "unknown test"));
        }
    }

}
