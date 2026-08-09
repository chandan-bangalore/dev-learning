# ============================================================
#  file_io.py
#  Concepts: open/close, read/write/append, with statement,
#            file modes, reading line by line, CSV, JSON,
#            os module, exception handling with files
# ============================================================

import os
import json


# ============================================================
#  PART 1 — WRITING A FILE
# ============================================================

# open(filename, mode)
# "w" = write  — creates file if not exists, OVERWRITES if exists
# Always use "with" — it automatically closes the file even if an error occurs
# Like RAII in C++ or try/finally — no need to call f.close() manually

with open("hello.txt", "w") as f:
    f.write("Hello, World!\n")      # \n needed — write() doesn't add it
    f.write("Python file I/O\n")
    f.write("Line 3\n")

print("File written!")

# Without "with" — old style, avoid this:
# f = open("hello.txt", "w")
# f.write("hello")
# f.close()           # easy to forget, causes bugs!


# ============================================================
#  PART 2 — READING A FILE
# ============================================================

# "r" = read (default mode)

# Read entire file as one string
with open("hello.txt", "r") as f:
    content = f.read()
print(content)                      # Hello, World!\nPython file I/O\n...

# Read all lines into a LIST
with open("hello.txt", "r") as f:
    lines = f.readlines()
print(lines)                        # ['Hello, World!\n', 'Python file I/O\n', ...]

# Read line by line — best for large files (memory efficient)
with open("hello.txt", "r") as f:
    for line in f:                  # f is iterable — like looping a list!
        print(line.strip())         # .strip() removes the \n at end of each line


# ============================================================
#  PART 3 — APPENDING TO A FILE
# ============================================================

# "a" = append — adds to end, does NOT overwrite
with open("hello.txt", "a") as f:
    f.write("This line was appended!\n")


# ============================================================
#  PART 4 — FILE MODES SUMMARY
# ============================================================

# "r"  — read only (default). Error if file doesn't exist.
# "w"  — write. Creates file. OVERWRITES existing content!
# "a"  — append. Creates file. Adds to end.
# "r+" — read AND write. Error if file doesn't exist.
# "x"  — create. Error if file already exists (safe write).

# For binary files (images, exe etc) add "b":
# "rb", "wb", "ab" etc.


# ============================================================
#  PART 5 — CHECK IF FILE EXISTS
# ============================================================

if os.path.exists("hello.txt"):
    print("File exists!")
else:
    print("File not found.")

print(os.path.getsize("hello.txt"))         # file size in bytes
print(os.path.abspath("hello.txt"))         # full absolute path


# ============================================================
#  PART 6 — EXCEPTION HANDLING WITH FILES
# ============================================================

# Always handle file errors — file might not exist, no permission etc.

try:
    with open("nonexistent.txt", "r") as f:
        content = f.read()
except FileNotFoundError:
    print("Error: file not found!")
except PermissionError:
    print("Error: no permission to read file!")
except Exception as e:
    print(f"Unexpected error: {e}")


# ============================================================
#  PART 7 — WORKING WITH JSON  (very common in real projects!)
# ============================================================

# JSON = JavaScript Object Notation
# Python dicts map perfectly to JSON — most APIs use JSON

# Write dict to JSON file
data = {
    "name" : "Alice",
    "age"  : 25,
    "scores": [92, 88, 95]
}

with open("data.json", "w") as f:
    json.dump(data, f, indent=4)    # indent=4 makes it human-readable

# Read JSON file back into a dict
with open("data.json", "r") as f:
    loaded = json.load(f)

print(loaded["name"])               # Alice
print(loaded["scores"])             # [92, 88, 95]


# ============================================================
#  PART 8 — APPLIED: Calculator history saved to file
# ============================================================

HISTORY_FILE = "calc_history.json"

def load_history():
    """Load history from file — returns empty list if file doesn't exist."""
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []                   # first run — no history yet

def save_history(history):
    """Save history list to JSON file."""
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def add_to_history(history, op, a, b, result):
    """Add one calculation to history and save."""
    history.append({
        "op"    : op,
        "a"     : a,
        "b"     : b,
        "result": result
    })
    save_history(history)

def print_history(history):
    """Print all calculations from history."""
    if not history:
        print("No history yet.")
        return
    print("\n--- Calculation History ---")
    symbols = {"add": "+", "sub": "-", "mul": "*", "div": "/"}
    for i, entry in enumerate(history, 1):
        sym = symbols.get(entry["op"], "?")
        print(f"{i}. {entry['a']} {sym} {entry['b']} = {entry['result']}")

# Simulate a session
history = load_history()            # load from file (persists between runs!)
add_to_history(history, "add", 10, 5, 15)
add_to_history(history, "mul",  4, 7, 28)
add_to_history(history, "div",  9, 3,  3)
print_history(history)

# The history is now saved in calc_history.json
# Next time you run the program, it loads the previous history!
