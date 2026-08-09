# ============================================================
#  tuples_and_sets.py
#  Concepts: tuple creation, immutability, packing/unpacking,
#            set creation, set operations, when to use each
# ============================================================


# ============================================================
#  PART 1 — TUPLES: CREATION
# ============================================================

# Tuples use () instead of []
coords   = (10, 20)
rgb      = (255, 128, 0)
person   = ("Alice", 25, "New York")
single   = (42,)          # single-element tuple NEEDS trailing comma
                           # without comma: (42) is just an int, not a tuple!
empty    = ()

# Parentheses are actually optional — commas make the tuple
coords2  = 10, 20         # same as (10, 20)
print(type(coords2))       # <class 'tuple'>


# ============================================================
#  PART 2 — TUPLES: IMMUTABLE (can't change after creation)
# ============================================================

point = (3, 7)
print(point[0])            # 3  — indexing works same as list
print(point[1])            # 7

# point[0] = 99            # ❌ TypeError: tuple does not support item assignment
# point.append(5)          # ❌ AttributeError: tuple has no append

# You CAN read, slice, loop — just not modify
for val in point:
    print(val)

print(point[0:2])          # (3, 7)  — slicing works


# ============================================================
#  PART 3 — TUPLE UNPACKING (very common in Python!)
# ============================================================

# Assign tuple values to variables in one line
x, y = (10, 20)
print(x, y)                # 10  20

name, age, city = ("Alice", 25, "New York")
print(name, age, city)     # Alice  25  New York

# You already used this with enumerate and zip!
# for i, val in enumerate(list)  ← i,val is tuple unpacking
# for name, score in zip(...)    ← same thing

# Swap two variables — classic Python trick
a, b = 5, 10
a, b = b, a                # swap!
print(a, b)                # 10  5
# In C you'd need a temp variable — Python doesn't!

# Ignore values you don't need with _ (underscore convention)
first, _, third = (1, 2, 3)
print(first, third)        # 1  3


# ============================================================
#  PART 4 — WHEN TO USE TUPLE vs LIST
# ============================================================

# Use TUPLE when:
#   - data shouldn't change (coordinates, RGB, DB record)
#   - returning multiple values from a function (you saw this!)
#   - using as a dict key (lists can't be dict keys, tuples can!)

location = (40.7128, -74.0060)          # lat/lng — shouldn't change
lookup   = {location: "New York"}       # ✅ tuple as dict key
# lookup = {[40.7, -74.0]: "NY"}        # ❌ list as dict key — TypeError

# Use LIST when:
#   - data will be added/removed/changed
#   - order matters and may shift


# ============================================================
#  PART 5 — SETS: CREATION
# ============================================================

# Sets use {} like dicts but with NO key:value pairs — just values
fruits  = {"apple", "banana", "cherry"}
nums    = {1, 2, 3, 4, 5}
empty_set = set()          # IMPORTANT: {} creates empty DICT not set!
                           # you must use set() for empty set

# Duplicates are automatically removed
dupes = {1, 2, 2, 3, 3, 3}
print(dupes)               # {1, 2, 3}  — duplicates gone!

# Convert a list to set to remove duplicates (very common trick!)
scores = [92, 78, 92, 85, 78, 92]
unique_scores = set(scores)
print(unique_scores)       # {92, 78, 85}  — each score once


# ============================================================
#  PART 6 — SETS: NO ORDER, NO INDEX
# ============================================================

fruits = {"apple", "banana", "cherry"}

# print(fruits[0])         # ❌ TypeError: set is not subscriptable
                           # sets have no index — no guaranteed order!

# You CAN loop over them
for fruit in fruits:
    print(fruit)           # order may vary each run!

# Check membership — sets are FAST at this (faster than lists)
print("apple" in fruits)   # True
print("mango" in fruits)   # False


# ============================================================
#  PART 7 — SET OPERATIONS (mathematical sets)
# ============================================================

a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

# Union — all elements from both (no duplicates)
print(a | b)               # {1, 2, 3, 4, 5, 6, 7, 8}
print(a.union(b))          # same thing

# Intersection — only elements in BOTH
print(a & b)               # {4, 5}
print(a.intersection(b))   # same thing

# Difference — in a but NOT in b
print(a - b)               # {1, 2, 3}
print(a.difference(b))     # same thing

# Symmetric difference — in either but NOT both
print(a ^ b)               # {1, 2, 3, 6, 7, 8}


# ============================================================
#  PART 8 — ADDING AND REMOVING FROM SETS
# ============================================================

tags = {"python", "coding", "beginner"}

tags.add("tutorial")       # add one element
tags.discard("beginner")   # remove if exists — no error if missing
tags.remove("coding")      # remove — raises KeyError if missing!

print(len(tags))            # 2


# ============================================================
#  PART 9 — REAL EXAMPLE: Using all three together
# ============================================================

# Calculator — track which operations were used (set = no duplicates)
history = [
    {"op": "add", "a": 10, "b": 5,  "result": 15},
    {"op": "mul", "a":  4, "b": 7,  "result": 28},
    {"op": "add", "a":  3, "b": 2,  "result":  5},
    {"op": "div", "a":  9, "b": 3,  "result":  3},
    {"op": "mul", "a":  2, "b": 6,  "result": 12},
]

# Which unique operations were used?
ops_used = {entry["op"] for entry in history}   # set comprehension!
print(f"Operations used: {ops_used}")            # {'add', 'mul', 'div'}

# Return result + metadata as a tuple (immutable snapshot)
def summarise(history):
    total = len(history)
    ops   = {e["op"] for e in history}
    avg   = sum(e["result"] for e in history) / total
    return total, ops, round(avg, 2)              # returns a tuple

count, unique_ops, average = summarise(history)   # tuple unpacking!
print(f"Total: {count}, Ops: {unique_ops}, Avg result: {average}")
