import java.util.*;

class Solution {

    static boolean isBooked(int[] seats, int seat) {
        return Arrays.binarySearch(seats, seat) >= 0;
    }
}
