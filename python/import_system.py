# ============================================================
#  import_system.py
#  Concepts: import, from, as, __name__, packages,
#            relative imports, __init__.py, sys.path
# ============================================================

# ============================================================
#  PART 1 — BASIC IMPORT
# ============================================================

import math                         # import entire module

print(math.pi)                      # 3.14159...
print(math.sqrt(16))                # 4.0
print(math.ceil(3.2))               # 4
print(math.floor(3.9))              # 3

# Must use "math." prefix — like a namespace in C++
# This avoids name clashes with your own functions


# ============================================================
#  PART 2 — FROM ... IMPORT  (import specific things)
# ============================================================

from math import sqrt, pi           # import only what you need

print(sqrt(25))                     # 5.0   — no "math." prefix needed
print(pi)                           # 3.14159...

# Import everything — avoid this in real code!
from math import *                  # pollutes your namespace
print(sin(0))                       # works but confusing — where did sin come from?


# ============================================================
#  PART 3 — IMPORT AS  (alias)
# ============================================================

import math as m                    # alias the module
print(m.sqrt(9))                    # 3.0

from math import sqrt as sq         # alias a specific function
print(sq(9))                        # 3.0

# You'll see this constantly in data science:
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt


# ============================================================
#  PART 4 — IMPORTING YOUR OWN FILE
# ============================================================

# Suppose you have calculator.py in the same folder.
# Python treats every .py file as a module!

# import calculator                 # imports your calculator.py
# calculator.add(10, 5)             # call its functions with prefix
# calculator.show_menu()

# Or import specific functions:
# from calculator import add, sub, mul
# add(10, 5)                        # no prefix needed


# ============================================================
#  PART 5 — THE __name__ GUARD  (you already know this!)
# ============================================================

# When Python imports a file, it runs ALL the code in it.
# The __name__ guard prevents certain code from running on import.

# In calculator.py:
# def add(a, b):
#     return a + b
#
# if __name__ == "__main__":
#     main()                        # only runs when file is run directly
#                                   # NOT when imported by another file

# When run directly:  __name__ == "__main__"
# When imported:      __name__ == "calculator"


# ============================================================
#  PART 6 — PACKAGES  (folders of modules)
# ============================================================

# A package is just a FOLDER with an __init__.py file inside.
# Like a library in C — groups related modules together.

# Folder structure:
# myapp/
# │
# ├── __init__.py          ← marks this folder as a package
# ├── calculator.py        ← module
# ├── history.py           ← module
# └── utils.py             ← module

# Importing from a package:
# import myapp.calculator
# myapp.calculator.add(1, 2)

# from myapp import calculator
# calculator.add(1, 2)

# from myapp.calculator import add
# add(1, 2)


# ============================================================
#  PART 7 — __init__.py
# ============================================================

# __init__.py runs when the package is imported.
# Use it to control what's available from your package.

# myapp/__init__.py:
# from .calculator import add, sub, mul, div   # expose these directly
# from .history    import load_history, save_history

# Now users can do:
# from myapp import add          # instead of from myapp.calculator import add


# ============================================================
#  PART 8 — SPLITTING YOUR CALCULATOR INTO MODULES
# ============================================================

# Good real-world structure for your calculator project:
#
# math/                        ← your project folder
# ├── main.py                  ← entry point, runs the app
# ├── operations.py            ← add, sub, mul, div, mod, pwr
# ├── history.py               ← load_history, save_history, print_history
# └── utils.py                 ← show_menu, get_input, format_result

# operations.py:
# def add(a, b): return a + b
# def sub(a, b): return a - b
# ...

# history.py:
# import json
# HISTORY_FILE = "calc_history.json"
# def load_history(): ...
# def save_history(history): ...

# utils.py:
# def show_menu(): ...
# def get_input(): ...

# main.py:
# from operations import add, sub, mul, div
# from history    import load_history, save_history
# from utils      import show_menu, get_input
#
# def main():
#     history = load_history()
#     while True:
#         show_menu()
#         ...
#
# if __name__ == "__main__":
#     main()


# ============================================================
#  PART 9 — sys.path  (where Python looks for modules)
# ============================================================

import sys

print(sys.path)                     # list of folders Python searches

# Python searches in this order:
# 1. Current directory
# 2. PYTHONPATH environment variable folders
# 3. Standard library folders
# 4. Site-packages (where pip installs go)

# Add a custom folder to the search path:
sys.path.append("/path/to/my/modules")
import my_custom_module             # now Python can find it


# ============================================================
#  PART 10 — COMMON STANDARD LIBRARY IMPORTS
# ============================================================

import os                           # file system, environment
import json                         # JSON read/write (you know this!)
import math                         # sqrt, pi, trig functions
import random                       # random numbers
import datetime                     # dates and times
import sys                          # interpreter, sys.exit()
import re                           # regular expressions
import time                         # sleep, timing
import collections                  # Counter, defaultdict, deque
import itertools                    # combinations, permutations
import functools                    # reduce, lru_cache

# Quick examples of ones you haven't seen yet:
import random
print(random.randint(1, 10))        # random int between 1 and 10
print(random.choice(["a","b","c"])) # random item from list
nums = [1, 2, 3, 4, 5]
random.shuffle(nums)                # shuffle list in place
print(nums)

import datetime
today = datetime.date.today()
print(today)                        # 2026-04-05
now   = datetime.datetime.now()
print(now)                          # 2026-04-05 14:23:01.123456

import time
time.sleep(1)                       # pause for 1 second
start = time.time()                 # current time in seconds
# ... do something ...
end   = time.time()
print(f"Took {end - start:.2f} seconds")
