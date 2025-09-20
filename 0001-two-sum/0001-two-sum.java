import java.util.Arrays; // needed for Arrays.toString

class Solution {
    public int[] twoSum(int[] nums, int target) {
        // Try all pairs of numbers
        for (int i = 0; i < nums.length; i++) {
            for (int j = i + 1; j < nums.length; j++) {
                if (nums[i] + nums[j] == target) {
                    // return indices when pair is found
                    return new int[] { i, j };
                }
            }
        }
        // If no pair found (LeetCode guarantees one exists)
        throw new IllegalArgumentException("No two sum solution");
    }

    // Test
    public static void main(String[] args) {
        Solution ts = new Solution();  // create object of Solution
        int[] nums = {2, 7, 11, 15};
        int target = 9;
        int[] res = ts.twoSum(nums, target);
        System.out.println(Arrays.toString(res)); // prints [0, 1]
    }
}
