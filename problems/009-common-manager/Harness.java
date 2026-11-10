import java.util.*;

public class Harness {
    public static void main(String[] a) {
        Runner.run(a[0], Harness::t);
    }

    static void t(String id) throws Throwable {
        Solution s = new Solution();
        switch (id) {
            case "example": {
                TreeNode root = build(new Integer[]{3, 5, 1, 6, 2, 0, 8, null, null, 7, 4});
                Check.ok(s.closestCommonManager(root, find(root, 5), find(root, 1)) == root, Check.t("manager(5,1) debe ser 3", "manager(5,1) must be 3"));
                Check.ok(s.closestCommonManager(root, find(root, 6), find(root, 8)) == root, Check.t("manager(6,8) debe ser 3", "manager(6,8) must be 3"));
                Check.ok(s.closestCommonManager(root, find(root, 7), find(root, 4)) == find(root, 2), Check.t("manager(7,4) debe ser 2", "manager(7,4) must be 2"));
                return;
            }
            case "ancestor": {
                TreeNode root = build(new Integer[]{3, 5, 1, 6, 2, 0, 8, null, null, 7, 4});
                Check.ok(s.closestCommonManager(root, find(root, 5), find(root, 4)) == find(root, 5),
                        Check.t("manager(5,4) debe ser 5: un nodo es descendiente de si mismo", "manager(5,4) must be 5: a node counts as below itself"));
                return;
            }
            case "same": {
                TreeNode root = build(new Integer[]{3, 5, 1, 6, 2, 0, 8, null, null, 7, 4});
                TreeNode n = find(root, 7);
                Check.ok(s.closestCommonManager(root, n, n) == n, Check.t("manager(7,7) debe ser 7", "manager(7,7) must be 7"));
                return;
            }
            case "deep": {
                int depth = 3000;
                TreeNode root = new TreeNode(0), cur = root;
                TreeNode mid = null;
                for (int i = 1; i < depth; i++) {
                    cur.left = new TreeNode(i);
                    cur = cur.left;
                    if (i == 1500) mid = cur;
                }
                Check.ok(s.closestCommonManager(root, cur, mid) == mid, Check.t("arbol de 3000 niveles", "tree with 3000 levels"));
                return;
            }
            default: throw new AssertionError(Check.t("prueba desconocida", "unknown test"));
        }
    }

    static TreeNode build(Integer[] a) {
        if (a.length == 0 || a[0] == null) return null;
        TreeNode root = new TreeNode(a[0]);
        Deque<TreeNode> q = new ArrayDeque<>();
        q.add(root);
        int i = 1;
        while (!q.isEmpty() && i < a.length) {
            TreeNode n = q.poll();
            if (i < a.length && a[i] != null) { n.left = new TreeNode(a[i]); q.add(n.left); }
            i++;
            if (i < a.length && a[i] != null) { n.right = new TreeNode(a[i]); q.add(n.right); }
            i++;
        }
        return root;
    }

    static TreeNode find(TreeNode n, int v) {
        if (n == null) return null;
        if (n.val == v) return n;
        TreeNode l = find(n.left, v);
        return l != null ? l : find(n.right, v);
    }
}
