import java.util.*;

class Solution {

    public int[][] mergeWindows(int[][] intervals) {
        if (intervals == null || intervals.length == 0) return new int[0][];
        int[][] sorted = intervals.clone();
        Arrays.sort(sorted, Comparator.comparingInt(a -> a[0]));
        List<int[]> out = new ArrayList<>();
        for (int[] cur : sorted) {
            if (out.isEmpty() || out.getLast()[1] < cur[0]) out.add(new int[]{cur[0], cur[1]});
            else out.getLast()[1] = Math.max(out.getLast()[1], cur[1]);
        }
        return out.toArray(new int[0][]);
    }
}
