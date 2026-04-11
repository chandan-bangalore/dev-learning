# ============================================================
#  lists_and_loops.py
#  Concepts: list creation, indexing, slicing, common methods,
#            for loop, while loop, enumerate, zip,
#            list comprehension, nested loops
# ============================================================


# ============================================================
#  PART 1 — CREATING LISTS
# ============================================================

# Like an array in C but dynamic — no fixed size, any type
nums   = [10, 20, 30, 40, 50]
names  = ["Alice", "Bob", "Charlie"]
mixed  = [1, "hello", 3.14, True]   # Python allows mixed types
empty  = []                          # start empty, grow later

print(nums)     # [10, 20, 30, 40, 50]
print(len(nums))  # 5  — length, like sizeof in C but simpler


# ============================================================
#  PART 2 — INDEXING
# ============================================================

#  Index:   0    1    2    3    4
#           10   20   30   40   50
# Neg idx: -5   -4   -3   -2   -1   ← Python bonus, C can't do this!

print(nums[0])    # 10  — first element (same as C)
print(nums[-1])   # 50  — last element  (no need for nums[len-1])
print(nums[-2])   # 40  — second to last


# ============================================================
#  PART 3 — SLICING  [start : stop]  (stop is EXCLUDED)
# ============================================================

print(nums[1:3])  # [20, 30]        index 1 up to (not including) 3
print(nums[:3])   # [10, 20, 30]    from start to index 2
print(nums[2:])   # [30, 40, 50]    from index 2 to end
print(nums[:])    # [10, 20, 30, 40, 50]  full copy
print(nums[::2])  # [10, 30, 50]    every 2nd element (step)
print(nums[::-1]) # [50, 40, 30, 20, 10] reversed!


# ============================================================
#  PART 4 — COMMON LIST METHODS
# ============================================================

fruits = ["apple", "banana", "cherry"]

fruits.append("mango")          # add to END
fruits.insert(1, "grape")       # insert at index 1
fruits.remove("banana")         # remove by VALUE (first match)
last   = fruits.pop()           # remove & return LAST item
first  = fruits.pop(0)          # remove & return item at index 0

fruits.sort()                   # sort in place A→Z (or low→high for nums)
fruits.reverse()                # reverse in place

print(fruits.index("cherry"))   # find index of a value
print("cherry" in fruits)       # True/False — check if value exists
print(fruits.count("apple"))    # count occurrences

nums_copy = nums.copy()         # safe copy (not just another reference)
nums.clear()                    # empties the list → []


# ============================================================
#  PART 5 — FOR LOOP
# ============================================================

scores = [85, 92, 78, 95, 60]

# Basic — loop over values directly (no index needed!)
# C: for(int i=0; i<5; i++) printf("%d", scores[i]);
for score in scores:
    print(score)

# Loop with range — when you need an index like C
for i in range(len(scores)):
    print(f"scores[{i}] = {scores[i]}")

# range(start, stop, step)
for i in range(0, 10, 2):      # 0 2 4 6 8
    print(i)

for i in range(10, 0, -1):     # 10 9 8 7 ... 1  (countdown)
    print(i)


# ============================================================
#  PART 6 — ENUMERATE  (index + value together)
# ============================================================

# When you need BOTH index and value — cleaner than range(len(...))
for i, score in enumerate(scores):
    print(f"Student {i+1}: {score}")

# Output:
# Student 1: 85
# Student 2: 92  ... etc.


# ============================================================
#  PART 7 — ZIP  (loop over two lists together)
# ============================================================

students = ["Alice", "Bob", "Charlie", "Diana", "Eve"]

for name, score in zip(students, scores):
    print(f"{name}: {score}")

# Output:
# Alice: 85
# Bob: 92  ... etc.


# ============================================================
#  PART 8 — WHILE LOOP
# ============================================================

# Same concept as C — runs while condition is True
i = 0
while i < len(scores):
    print(scores[i])
    i += 1                      # Python has no i++ — use i += 1

# Practical example: keep asking until valid input
numbers = []
while len(numbers) < 3:         # collect exactly 3 numbers
    try:
        n = float(input(f"Enter number {len(numbers)+1}: "))
        numbers.append(n)
    except ValueError:
        print("Numbers only!")

print(f"You entered: {numbers}")
print(f"Sum = {sum(numbers)}, Average = {sum(numbers)/len(numbers):.2f}")


# ============================================================
#  PART 9 — NESTED LOOPS
# ============================================================

# Loop inside a loop — useful for tables, grids, combinations
print("\nMultiplication table (1-3):")
for i in range(1, 4):
    for j in range(1, 4):
        print(f"{i*j:4}", end="")   # :4 = pad to 4 chars wide
    print()                          # newline after each row

# Output:
#    1   2   3
#    2   4   6
#    3   6   9


# ============================================================
#  PART 10 — LIST COMPREHENSION  (Python superpower!)
# ============================================================

# Old way (thinking in C):
squares = []
for n in range(1, 6):
    squares.append(n ** 2)

# Python way — one line, same result:
squares = [n ** 2 for n in range(1, 6)]
print(squares)          # [1, 4, 9, 16, 25]

# With a condition (filter):
evens   = [n for n in range(1, 11) if n % 2 == 0]
print(evens)            # [2, 4, 6, 8, 10]

# Applied to your calculator — get only passing scores:
passing = [s for s in scores if s >= 70]
print(passing)          # [85, 92, 78, 95]


# ============================================================
#  PUTTING IT ALL TOGETHER — Calculator history tracker
# ============================================================

def add(a, b): return a + b
def sub(a, b): return a - b
def mul(a, b): return a * b
def div(a, b): return a / b if b != 0 else "Error"

history = []    # stores every calculation as a string

def calculate(op, a, b):
    ops = {1: add, 2: sub, 3: mul, 4: div}
    if op not in ops:
        return None
    result = ops[op](a, b)
    entry  = f"{a} {'+-*/'[op-1]} {b} = {result}"
    history.append(entry)           # add to history list
    return result

# Simulate a few calculations
calculate(1, 10, 5)   # 10 + 5
calculate(3, 4, 7)    # 4  * 7
calculate(4, 9, 3)    # 9  / 3

print("\n--- Calculation History ---")
for i, entry in enumerate(history, start=1):   # start=1 makes i start at 1
    print(f"{i}. {entry}")

# Filter only multiplication/division from history
print("\n--- Only * and / ---")
mul_div = [e for e in history if "*" in e or "/" in e]
for entry in mul_div:
    print(entry)
