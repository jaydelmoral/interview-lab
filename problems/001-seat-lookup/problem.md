# Booked Seat Lookup

An airline keeps the booked seat numbers of a flight in a sorted array. Before offering a seat to a customer, the booking service checks whether it is already taken.

**Specifications:**

- Seat numbers are integers sorted in ascending order. Duplicates may appear.
- The array can hold up to 1 million items; it is never `null` but it may be empty.
- Many queries run against the same array, so wasted CPU cycles matter.

Implement `static boolean isBooked(int[] seats, int seat)` in class `Solution`: it returns `true` when `seat` is in `seats`, and `false` otherwise.

**Example:**

```java
int[] seats = {12, 18, 33, 47};
Solution.isBooked(seats, 33)  // true
Solution.isBooked(seats, 20)  // false
```
