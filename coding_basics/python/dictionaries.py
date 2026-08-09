# ============================================================
#  dictionaries.py
#  Concepts: creation, access, add/update/delete,
#            looping, common methods, nested dicts,
#            dict as a switch (you already did this!)
# ============================================================


# ============================================================
#  PART 1 — CREATING A DICTIONARY
# ============================================================

# Syntax: {key: value, key: value, ...}
# Keys must be unique. Values can be anything.

person = {
    "name": "Alice",
    "age" : 25,
    "city": "New York"
}

empty = {}                          # empty dict, add later
empty2 = dict()                     # same thing, different syntax


# ============================================================
#  PART 2 — ACCESSING VALUES
# ============================================================

print(person["name"])               # Alice  — direct access by key
print(person["age"])                # 25

# .get() — safe access, returns None instead of crashing
print(person.get("city"))          # New York
print(person.get("phone"))         # None   — key doesn't exist, no crash!
print(person.get("phone", "N/A"))  # N/A    — default value if key missing

# Direct access on missing key → crashes
# print(person["phone"])           # KeyError: 'phone'  ← don't do this without checking


# ============================================================
#  PART 3 — ADD, UPDATE, DELETE
# ============================================================

person["email"] = "alice@email.com"     # add new key
person["age"]   = 26                    # update existing key
del person["city"]                      # delete a key

removed = person.pop("email")           # remove & return value (like list.pop)
print(removed)                          # alice@email.com

print(person)                           # {"name": "Alice", "age": 26}


# ============================================================
#  PART 4 — CHECKING IF KEY EXISTS
# ============================================================

if "name" in person:                    # like "in" for lists
    print("Has name!")

if "phone" not in person:
    print("No phone key")


# ============================================================
#  PART 5 — LOOPING OVER A DICTIONARY
# ============================================================

scores = {"Alice": 92, "Bob": 78, "Charlie": 85}

# Loop over keys only (default)
for name in scores:
    print(name)                         # Alice, Bob, Charlie

# Loop over values only
for score in scores.values():
    print(score)                        # 92, 78, 85

# Loop over BOTH key and value — most common!
for name, score in scores.items():
    print(f"{name}: {score}")           # Alice: 92 etc.

# Find highest scorer using a loop
best_name  = None
best_score = 0
for name, score in scores.items():
    if score > best_score:
        best_score = score
        best_name  = name
print(f"Top scorer: {best_name} with {best_score}")


# ============================================================
#  PART 6 — COMMON METHODS
# ============================================================

print(scores.keys())                    # dict_keys(['Alice', 'Bob', 'Charlie'])
print(scores.values())                  # dict_values([92, 78, 85])
print(scores.items())                   # dict_items([('Alice', 92), ...])
print(len(scores))                      # 3

# Merge two dicts (Python 3.9+)
defaults = {"theme": "dark", "lang": "en"}
user_prefs = {"lang": "fr", "font": "mono"}
merged = defaults | user_prefs          # user_prefs wins on conflict
print(merged)                           # {'theme': 'dark', 'lang': 'fr', 'font': 'mono'}

# Copy (same rule as lists — use .copy() not =)
scores_copy = scores.copy()


# ============================================================
#  PART 7 — NESTED DICTIONARIES
# ============================================================

# A dict where the values are also dicts — very common in real data (APIs, JSON)

students = {
    "Alice": {"age": 20, "grade": "A", "scores": [92, 88, 95]},
    "Bob"  : {"age": 22, "grade": "B", "scores": [78, 82, 80]},
}

# Access nested values
print(students["Alice"]["grade"])           # A
print(students["Bob"]["scores"][0])         # 78  (first score)

# Loop over nested dict
for name, info in students.items():
    avg = sum(info["scores"]) / len(info["scores"])
    print(f"{name} | grade: {info['grade']} | avg score: {avg:.1f}")


# ============================================================
#  PART 8 — DICT COMPREHENSION  (like list comprehension)
# ============================================================

# Build a dict in one line
squares = {n: n**2 for n in range(1, 6)}
print(squares)                          # {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

# With a condition
high_scores = {name: s for name, s in scores.items() if s >= 85}
print(high_scores)                      # {'Alice': 92, 'Charlie': 85}

# Convert two lists into a dict using zip
names  = ["Alice", "Bob", "Charlie"]
points = [92, 78, 85]
score_dict = dict(zip(names, points))
print(score_dict)                       # {'Alice': 92, 'Bob': 78, 'Charlie': 85}


# ============================================================
#  PART 9 — DICT AS A SWITCH (you already used this!)
# ============================================================

# Remember from your calculator — storing functions in a dict:
def add(a, b): return a + b
def sub(a, b): return a - b
def mul(a, b): return a * b
def div(a, b): return a / b if b != 0 else "Error"

operations = {
    1: add,
    2: sub,
    3: mul,
    4: div
}

result = operations[1](10, 5)           # calls add(10, 5)
print(result)                           # 15


# ============================================================
#  PART 10 — REAL EXAMPLE: Calculator with history
# ============================================================

# Store each calculation as a structured dict entry
history = []

def calculate(op_name, a, b, result):
    history.append({
        "op"    : op_name,
        "a"     : a,
        "b"     : b,
        "result": result
    })

calculate("add", 10, 5, 15)
calculate("mul",  4, 7, 28)
calculate("div",  9, 3,  3)

print("\n--- History ---")
for i, entry in enumerate(history, 1):
    print(f"{i}. {entry['a']} {entry['op']} {entry['b']} = {entry['result']}")

# Filter only additions
adds = [e for e in history if e["op"] == "add"]
print(f"\nAdditions only: {adds}")
