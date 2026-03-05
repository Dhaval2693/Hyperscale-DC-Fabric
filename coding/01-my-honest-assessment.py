# Problem: Two Sum (classic baseline)

# Given a list of integers and a target, return the indices of two numbers that add up to the target. Assume exactly one solution exists.


# Input:  nums = [2, 7, 11, 15], target = 9
# Output: [0, 1]

# Input:  nums = [3, 2, 4], target = 6
# Output: [1, 2]
# Write the most efficient Python solution you can, and also tell me:

# What is its time and space complexity?
# Why did you choose that approach?

# def indices_target(nums, target):
#     for i in nums:
#         for j in nums(1:):
#             if num 

## MY SOLUTION
nums = [2, 7, 11, 15]
target = 9

# def indices_fun(nums, target, start):
#     for i in range(start, len(nums)):
#         for j in range(i+1, len(nums)):
#             if nums[i] + nums[j] == target:
#                 return ([i, j])

# print(indices_fun(nums, target, start))

## AI SOLUTION
def two_sum(nums, target):
    seen = {}  # value -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i

print (two_sum(nums, target))