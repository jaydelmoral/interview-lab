# Gerente común más cercano

El organigrama de una empresa es un árbol binario: cada `TreeNode` es una persona y sus hijos son las personas que dirige directamente (máximo dos). Dados dos empleados `p` y `q` que existen en el organigrama, devuelve su gerente común más cercano: el nodo más bajo que tiene a ambos por debajo. Una persona cuenta como estar por debajo de sí misma, así que si `p` dirige a `q`, la respuesta es `p`.

`TreeNode` ya está definido (no lo vuelvas a declarar):

```java
class TreeNode { int val; TreeNode left, right; TreeNode(int val) { this.val = val; } }
```

Implementa `TreeNode closestCommonManager(TreeNode root, TreeNode p, TreeNode q)` en la clase `Solution`. Objetivo: O(n).
