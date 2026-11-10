import java.util.*;

class LatencyTracker {
    private final PriorityQueue<Integer> low = new PriorityQueue<>(Collections.reverseOrder());
    private final PriorityQueue<Integer> high = new PriorityQueue<>();

    public LatencyTracker() {
    }

    public void record(int num) {
        low.offer(num);
        high.offer(low.poll());
        if (high.size() > low.size()) low.offer(high.poll());
    }

    public double median() {
        if (low.size() > high.size()) return low.peek();
        return (low.peek() + (double) high.peek()) / 2.0;
    }
}
