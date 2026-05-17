# Solutions: 03-two-pointers-practice.py
#
# Read AFTER attempting (or skim if you're in fast-familiarize mode).


# --- Problem 1: Reverse a List In-Place ---
def reverse_list(s):
    left, right = 0, len(s) - 1
    while left < right:
        s[left], s[right] = s[right], s[left]
        left += 1
        right -= 1

# Pattern used: 1 (Opposite Ends)
# Time:  O(N)
# Space: O(1)
#
# Classic opposite-ends swap. Stop when pointers meet.


# --- Problem 2: Valid Palindrome ---
def is_palindrome(s):
    left, right = 0, len(s) - 1
    while left < right:
        # Skip non-alphanumeric on the left
        while left < right and not s[left].isalnum():
            left += 1
        # Skip non-alphanumeric on the right
        while left < right and not s[right].isalnum():
            right -= 1
        # Compare (case-insensitive)
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True

# Pattern used: 1 (Opposite Ends)
# Time:  O(N)
# Space: O(1)
#
# The nested whiles look scary but each character is visited at most
# twice (once by left, once by right) across the entire run. Still O(N).


# --- Problem 3: Two Sum Sorted ---
def two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        current = nums[left] + nums[right]
        if current == target:
            return (left, right)
        elif current < target:
            left += 1
        else:
            right -= 1
    return (-1, -1)

# Pattern used: 1 (Opposite Ends)
# Time:  O(N)
# Space: O(1)
#
# Compare to unsorted Two Sum (hash map): same time but O(N) space.
# When sorted, two pointers wins on space.


# --- Problem 4: Remove Duplicates from Sorted Array ---
def remove_duplicates(nums):
    if not nums:
        return 0
    slow = 0
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    return slow + 1

# Pattern used: 2 (Fast/Slow)
# Time:  O(N)
# Space: O(1)
#
# slow tracks "end of unique values so far."
# fast scans for the next new value to copy into position slow+1.


# --- Problem 5: Move Zeros to End ---
def move_zeros(nums):
    slow = 0
    for fast in range(len(nums)):
        if nums[fast] != 0:
            nums[slow], nums[fast] = nums[fast], nums[slow]
            slow += 1

# Pattern used: 2 (Fast/Slow)
# Time:  O(N)
# Space: O(1)
#
# slow points to the next position where a non-zero should land.
# Swap (not overwrite) ensures zeros pile up at the back as non-zeros move forward.


# --- Challenge: Three Sum ---
def three_sum(nums):
    nums.sort()    # O(N log N) — required for two pointers
    result = []
    for i in range(len(nums) - 2):
        # Skip duplicate values for i (otherwise we'd get duplicate triplets)
        if i > 0 and nums[i] == nums[i-1]:
            continue
        target = -nums[i]
        left, right = i + 1, len(nums) - 1
        while left < right:
            current = nums[left] + nums[right]
            if current == target:
                result.append([nums[i], nums[left], nums[right]])
                # Skip duplicates at left and right
                while left < right and nums[left] == nums[left+1]:
                    left += 1
                while left < right and nums[right] == nums[right-1]:
                    right -= 1
                left += 1
                right -= 1
            elif current < target:
                left += 1
            else:
                right -= 1
    return result

# Pattern used: 1 (Opposite Ends, inside an outer loop)
# Time:  O(N²)  — outer N × inner two-pointer scan N
# Space: O(1) extra (sort is in-place; output doesn't count)
#
# The trick: fix nums[i], then Two Sum Sorted on the rest with target = -nums[i].
# Sorting first enables both the two pointers AND easy duplicate-skipping at all
# three levels (i, left, right).
#
# Brute force is O(N³). Sort + two pointers brings it to O(N²) — significant.


if __name__ == "__main__":
    s = ['h', 'e', 'l', 'l', 'o']
    reverse_list(s)
    print("Problem 1:", s)
    print("Problem 2:", is_palindrome("A man, a plan, a canal: Panama"))
    print("Problem 2:", is_palindrome("race a car"))
    print("Problem 3:", two_sum_sorted([1, 3, 4, 5, 7, 11], 9))
    nums = [1, 1, 2, 2, 3]
    k = remove_duplicates(nums)
    print("Problem 4:", k, nums[:k])
    nums = [0, 1, 0, 3, 12]
    move_zeros(nums)
    print("Problem 5:", nums)
    print("Challenge:", three_sum([-1, 0, 1, 2, -1, -4]))
