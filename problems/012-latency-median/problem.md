# Running Latency Median

A telecom network monitor receives response times (in milliseconds) one by one and must report the median of everything received so far at any moment. With an even count, the median is the average of the two middle values.

Implement class `LatencyTracker` with `void record(int ms)` (target O(log n)) and `double median()` (target O(1)).

```java
LatencyTracker t = new LatencyTracker();
t.record(40); t.record(60);
t.median();   // 50.0
t.record(100);
t.median();   // 60.0
```
