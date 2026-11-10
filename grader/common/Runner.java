import java.util.*;

interface Body {
    void run(String id) throws Throwable;
}

/** Ejecuta una prueba, captura el resultado e imprime la línea RESULT que lee el calificador. */
final class Runner {
    static void run(String id, Body body) {
        long t0 = System.nanoTime();
        String res;
        try {
            body.run(id);
            res = "PASS";
        } catch (AssertionError e) {
            res = "FAIL " + e.getMessage();
        } catch (Throwable t) {
            res = "FAIL " + t.getClass().getSimpleName() + (t.getMessage() == null ? "" : ": " + t.getMessage());
        }
        System.out.println("RESULT " + id + " " + ((System.nanoTime() - t0) / 1_000_000) + " " + res.replace('\n', ' '));
    }
}

/** Minimal assertions with clear messages in Spanish or English (-Dilab.lang=es|en). */
final class Check {
    static final boolean EN = "en".equals(System.getProperty("ilab.lang"));

    static String t(String es, String en) {
        return EN ? en : es;
    }

    static void ok(boolean cond, String msg) {
        if (!cond) throw new AssertionError(msg);
    }

    static void eq(Object expected, Object actual, String ctx) {
        if (!Objects.deepEquals(expected, actual)) {
            throw new AssertionError(ctx + ": " + t("esperado ", "expected ") + show(expected) + t(" pero obtuve ", " but got ") + show(actual));
        }
    }

    static void raises(Class<? extends Throwable> type, Runnable r, String ctx) {
        try {
            r.run();
        } catch (Throwable t) {
            if (type.isInstance(t)) return;
            throw new AssertionError(ctx + ": " + t("esperaba ", "expected ") + type.getSimpleName() + t(" y fue ", " but got ") + t.getClass().getSimpleName());
        }
        throw new AssertionError(ctx + ": " + t("esperaba ", "expected ") + type.getSimpleName() + t(" y no lanzó nada", " but nothing was thrown"));
    }

    static String show(Object o) {
        if (o == null) return "null";
        if (o instanceof int[] a) return Arrays.toString(a);
        if (o instanceof Object[] a) return Arrays.deepToString(a);
        return String.valueOf(o);
    }
}
