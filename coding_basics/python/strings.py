# ============================================================
#  strings.py
#  Concepts: creation, indexing, slicing, methods,
#            f-strings, multiline, raw strings,
#            string as a sequence, common patterns
# ============================================================


# ============================================================
#  PART 1 — CREATING STRINGS
# ============================================================

# Single or double quotes — both work, just be consistent
s1 = 'Hello'
s2 = "World"

# Use the other quote type to avoid escaping
s3 = "it's easy"          # single quote inside double — no escape needed
s4 = 'He said "hello"'    # double quote inside single — no escape needed
s5 = "He said \"hello\""  # or escape with backslash like C

# Multiline string — triple quotes (very useful for long text)
msg = """
Dear Alice,
Welcome to Python.
Regards, Bob
"""
print(msg)

# Raw string — backslashes are NOT escape characters
# Very useful for file paths on Windows!
path1 = "C:\\Users\\Alice\\file.txt"   # C way — escape backslashes
path2 = r"C:\Users\Alice\file.txt"     # raw string — much cleaner!
print(path1 == path2)                   # True — same result


# ============================================================
#  PART 2 — STRINGS ARE SEQUENCES (like lists!)
# ============================================================

word = "Python"

# Indexing — exactly like lists
print(word[0])      # P
print(word[-1])     # n  (last char)
print(word[-3])     # h  (third from end)

# Slicing — exactly like lists
print(word[0:3])    # Pyt
print(word[2:])     # thon
print(word[::-1])   # nohtyP  (reversed!)

# Length
print(len(word))    # 6

# Loop over characters — strings are iterable
for ch in word:
    print(ch)       # P y t h o n  (one per line)

# Check if substring exists
print("Py" in word)         # True
print("java" in word)       # False


# ============================================================
#  PART 3 — STRINGS ARE IMMUTABLE (like tuples!)
# ============================================================

s = "Hello"
# s[0] = "h"     # ❌ TypeError — can't modify in place

# To "change" a string, create a new one
s = "h" + s[1:]  # "hello"
print(s)


# ============================================================
#  PART 4 — COMMON STRING METHODS
# ============================================================

text = "  Hello, World!  "

# Case
print(text.upper())         # "  HELLO, WORLD!  "
print(text.lower())         # "  hello, world!  "
print(text.title())         # "  Hello, World!  "  (each word capitalised)

# Whitespace
print(text.strip())         # "Hello, World!"  (removes both ends)
print(text.lstrip())        # "Hello, World!  "  (left only)
print(text.rstrip())        # "  Hello, World!"  (right only)

# Search
print(text.find("World"))   # 9  — index where found (-1 if not found)
print(text.count("l"))      # 3  — count occurrences

# Check content
print("hello123".isalnum()) # True  — letters and/or numbers only
print("hello".isalpha())    # True  — letters only
print("123".isdigit())      # True  — digits only
print("  ".isspace())       # True  — whitespace only

# Replace
print(text.replace("World", "Python"))   # "  Hello, Python!  "

# Starts / ends with
print(text.strip().startswith("Hello"))  # True
print(text.strip().endswith("!"))        # True


# ============================================================
#  PART 5 — SPLIT AND JOIN  (very powerful combo!)
# ============================================================

# split() — breaks a string into a LIST
sentence = "one two three four"
words = sentence.split()        # split on whitespace by default
print(words)                    # ['one', 'two', 'three', 'four']

csv_line = "Alice,25,New York"
parts = csv_line.split(",")     # split on comma
print(parts)                    # ['Alice', '25', 'New York']

# join() — combines a LIST into a string (opposite of split)
words = ["one", "two", "three"]
print(" ".join(words))          # "one two three"
print(", ".join(words))         # "one, two, three"
print("-".join(words))          # "one-two-three"

# Classic pattern: split → process → join
sentence = "hello world python"
result = " ".join(w.title() for w in sentence.split())
print(result)                   # "Hello World Python"


# ============================================================
#  PART 6 — F-STRINGS IN DEPTH (you already know basics!)
# ============================================================

name  = "Alice"
score = 3.14159
val   = 1000000

# Basic
print(f"Name: {name}")                  # Name: Alice

# Expressions inside {}
print(f"Double: {10 * 2}")             # Double: 20
print(f"Upper: {name.upper()}")        # Upper: ALICE

# Number formatting
print(f"{score:.2f}")                  # 3.14      (2 decimal places)
print(f"{score:10.2f}")               #       3.14 (width 10, 2 decimals)
print(f"{val:,}")                      # 1,000,000 (comma separator)
print(f"{42:05d}")                     # 00042     (zero padded)
print(f"{42:>10}")                     #         42 (right align width 10)
print(f"{42:<10}")                     # 42         (left align width 10)
print(f"{42:^10}")                     #     42     (centre width 10)

# Debug shortcut — variable name + value (Python 3.8+)
x = 42
print(f"{x=}")                         # x=42  (great for debugging!)


# ============================================================
#  PART 7 — COMMON PATTERNS
# ============================================================

# Check if input is a number safely
user_input = "123"
if user_input.isdigit():
    n = int(user_input)

# Remove unwanted characters
raw   = "  $1,234.56  "
clean = raw.strip().replace("$", "").replace(",", "")
print(float(clean))                    # 1234.56

# Count words in a sentence
sentence = "the quick brown fox jumps over the lazy dog"
word_count = len(sentence.split())
print(f"Word count: {word_count}")     # 9

# Check palindrome
word = "racecar"
print(word == word[::-1])              # True — reversed equals original


# ============================================================
#  PART 8 — APPLIED TO YOUR CALCULATOR
# ============================================================

def format_result(op, a, b, result):
    """Format a calculation as a clean readable string."""
    symbols = {"add": "+", "sub": "-", "mul": "*", "div": "/"}
    symbol  = symbols.get(op, "?")
    return f"{a:>8} {symbol} {b:<8} = {result:.4f}".rstrip("0").rstrip(".")

history = [
    ("add", 10,   5,   15.0),
    ("mul",  4,   7,   28.0),
    ("div",  9,   3,    3.0),
    ("div", 22,   7,   3.142857),
]

print("\n--- Calculation History ---")
print("-" * 35)
for op, a, b, result in history:        # tuple unpacking!
    print(format_result(op, a, b, result))
print("-" * 35)

# Output:
#       10 + 5        = 15
#        4 * 7        = 28
#        9 / 3        = 3
#       22 / 7        = 3.142857
