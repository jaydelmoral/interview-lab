import java.util.*;

class Solution {

    public TreeNode closestCommonManager(TreeNode root, TreeNode p, TreeNode q) {
        if (root == null || root == p || root == q) return root;
        TreeNode left = closestCommonManager(root.left, p, q);
        TreeNode right = closestCommonManager(root.right, p, q);
        if (left != null && right != null) return root;
        return left != null ? left : right;
    }
}
