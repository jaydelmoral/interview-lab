# Closest Common Manager

A company's org chart is a binary tree: each `TreeNode` is a person and its children are the people they directly manage (at most two). Given two employees `p` and `q` that exist in the chart, return their closest common manager: the lowest node that has both of them below it. A person counts as being below themselves, so if `p` manages `q`, the answer is `p`.

`TreeNode` is already defined for you (do not redeclare it):

```java
class TreeNode { int val; TreeNode left, right; TreeNode(int val) { this.val = val; } }
```

Implement `TreeNode closestCommonManager(TreeNode root, TreeNode p, TreeNode q)` in class `Solution`. Target: O(n).
