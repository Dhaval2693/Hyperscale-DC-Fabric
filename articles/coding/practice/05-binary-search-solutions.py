# Solutions: 05-binary-search-practice.py


# --- Problem 1: Standard Binary Search ---
def binary_search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# Pattern used: 1 (Find a Target)
# Time:  O(log N)
# Space: O(1)
#
# Memorize this template. It's the foundation for every other binary search variant.


# --- Problem 2: First Occurrence of Target ---
def first_occurrence(nums, target):
    left, right = 0, len(nums) - 1
    result = -1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            result = mid          # record this match...
            right = mid - 1       # ...but keep searching left
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result

# Pattern used: 2 (Find a Boundary)
# Time:  O(log N)
# Space: O(1)
#
# The key difference vs Problem 1: when we find the target, we DON'T return
# — we record the match and narrow toward the left boundary.
#
# For LAST occurrence: same idea but `left = mid + 1` after recording match.


# --- Problem 3: Find Insert Position ---
def search_insert(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return left   # `left` is the insertion point when target isn't found

# Pattern used: 1 (Find a Target) with insertion trick
# Time:  O(log N)
# Space: O(1)
#
# Standard binary search, but when target isn't found, `left` ends up at
# the exact position where target would be inserted. This is because the
# loop narrows down to the point where everything left of `left` is < target.


# --- Problem 4: Find Peak Element ---
def find_peak(nums):
    left, right = 0, len(nums) - 1
    while left < right:
        mid = (left + right) // 2
        if nums[mid] > nums[mid + 1]:
            # Peak is at mid or somewhere to the left
            right = mid
        else:
            # Peak must be to the right (nums[mid+1] is bigger)
            left = mid + 1
    return left

# Pattern used: 1 (Find a Target) with peak-detection logic
# Time:  O(log N)
# Space: O(1)
#
# The trick: even though the array isn't sorted, comparing nums[mid] to
# nums[mid+1] tells us which half is "going up." A peak must exist on
# the going-up side (eventually it has to come down).


# --- Problem 5: Search in Rotated Sorted Array ---
def search_rotated(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid

        # Figure out which half is sorted
        if nums[left] <= nums[mid]:
            # Left half is sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            # Right half is sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1

# Pattern used: 1 (Find a Target) with rotation handling
# Time:  O(log N)
# Space: O(1)
#
# Key insight: at any point, one half of the array is sorted (even if
# the whole isn't). Identify which half, check if target is in that
# sorted range, and search accordingly.


# --- Challenge: Capacity to Ship Packages Within D Days ---
def min_capacity(packages, days):
    def can_deliver(cap):
        d, current = 1, 0
        for p in packages:
            if current + p > cap:
                d += 1
                current = p
            else:
                current += p
        return d <= days

    left, right = max(packages), sum(packages)
    while left < right:
        mid = (left + right) // 2
        if can_deliver(mid):
            right = mid       # this works — try smaller
        else:
            left = mid + 1    # too small — need bigger
    return left

# Pattern used: 3 (Binary Search on the Answer)
# Time:  O(N log S) where S = sum(packages) - max(packages)
# Space: O(1)
#
# The monotonic property: if capacity C works, then any capacity > C also works.
# So we binary search the capacity, with the feasibility check (can_deliver)
# at each midpoint.
#
# The range is [max(packages), sum(packages)] because:
#   - Minimum possible: can't be less than the biggest package
#   - Maximum needed: one truck holds everything (1-day delivery)


if __name__ == "__main__":
    print("Problem 1:", binary_search([1, 3, 5, 7, 9, 11], 7))
    print("Problem 1:", binary_search([1, 3, 5, 7, 9, 11], 4))
    print("Problem 2:", first_occurrence([1, 2, 2, 2, 3, 4], 2))
    print("Problem 2:", first_occurrence([1, 2, 2, 2, 3, 4], 5))
    print("Problem 3:", search_insert([1, 3, 5, 6], 5))
    print("Problem 3:", search_insert([1, 3, 5, 6], 2))
    print("Problem 4:", find_peak([1, 2, 3, 1]))
    print("Problem 5:", search_rotated([4, 5, 6, 7, 0, 1, 2], 0))
    print("Problem 5:", search_rotated([4, 5, 6, 7, 0, 1, 2], 3))
    print("Challenge:", min_capacity([1,2,3,4,5,6,7,8,9,10], 5))
    print("Challenge:", min_capacity([3,2,2,4,1,4], 3))
