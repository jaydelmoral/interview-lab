# Gift Card Pairing

An online store lets customers pay an order with a gift card that must be used **exactly**. Given the prices (in cents) of the items in a cart and the card balance, return the **indices** of two different items whose prices add up to the balance. If several pairs work, any of them is accepted. If no pair works, throw `IllegalArgumentException`.

Implement `int[] pairForBalance(int[] prices, int balance)` in class `Solution`. Target complexity: O(n).

```java
pairForBalance(new int[]{1200, 350, 899, 4500}, 1550)  // [0, 1]
pairForBalance(new int[]{500, 500, 250}, 1000)         // [0, 1]
```
