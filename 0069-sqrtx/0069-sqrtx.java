class Solution {
    public int mySqrt(int x) {
        if (x == 0) {
            return 0; // The square root of 0 is 0
        }
        
        int left = 1, right = x;
        
        // Binary search for the integer square root of x
        while (left <= right) {
            int mid = left + (right - left) / 2;
            long square = (long) mid * mid; // To prevent overflow
            
            if (square == x) {
                return mid; // Found exact square root
            } else if (square < x) {
                left = mid + 1; // We need a larger mid value
            } else {
                right = mid - 1; // We need a smaller mid value
            }
        }
        
        // The largest integer whose square is less than x
        return right;
    }
}
