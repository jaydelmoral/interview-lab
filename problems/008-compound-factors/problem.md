# Compound Factors Excluding Self

A bank computes, for each product in a portfolio, the combined risk factor of **all the other** products. Given the array `factors` (length >= 2), return an array `result` where `result[i]` is the product of every element of `factors` except `factors[i]`. **Do not use division.** Target: O(n) time. Any product of a prefix or a suffix fits in an `int`.

Implement `int[] factorsExcludingSelf(int[] factors)` in class `Solution`.

```java
factorsExcludingSelf(new int[]{2, 3, 4, 5})  // {60, 40, 30, 24}
```
