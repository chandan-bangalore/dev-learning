# ============================================================
#  data_science_intro.py
#  numpy, pandas, matplotlib — the data science trio
# ============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
#  PART 1 — NUMPY  (numerical python)
# ============================================================
# Think of it as: supercharged arrays for math
# C equivalent: doing math on arrays with SIMD/vectorized ops
# "np" alias is universal convention — everyone uses it

# --- numpy array vs Python list ---
py_list  = [1, 2, 3, 4, 5]           # Python list
np_array = np.array([1, 2, 3, 4, 5]) # numpy array

# Python list math — works element by element only with a loop
doubled_list = [x * 2 for x in py_list]   # need list comprehension

# numpy — math applies to ALL elements at once (vectorized!)
doubled_arr  = np_array * 2               # [2, 4, 6, 8, 10]  — no loop needed!
print(doubled_arr)

# More math operations — all element-wise, no loops!
a = np.array([10, 20, 30, 40, 50])
b = np.array([1,   2,  3,  4,  5])

print(a + b)        # [11, 22, 33, 44, 55]
print(a - b)        # [ 9, 18, 27, 36, 45]
print(a * b)        # [10, 40, 90, 160, 250]
print(a / b)        # [10, 10, 10, 10, 10]
print(a ** 2)       # [100, 400, 900, 1600, 2500]

# Built-in statistics — no loops!
scores = np.array([85, 92, 78, 95, 60, 88])
print(np.mean(scores))    # 83.0   average
print(np.max(scores))     # 95     maximum
print(np.min(scores))     # 60     minimum
print(np.std(scores))     # standard deviation

# Create arrays quickly
zeros    = np.zeros(5)              # [0. 0. 0. 0. 0.]
ones     = np.ones(5)               # [1. 1. 1. 1. 1.]
rng      = np.arange(0, 10, 2)     # [0 2 4 6 8]  like range() but numpy
linspace = np.linspace(0, 1, 5)    # [0. 0.25 0.5 0.75 1.]  evenly spaced

# 2D arrays (matrices) — like 2D arrays in C
matrix = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
])
print(matrix[1][2])         # 6  — row 1, col 2
print(matrix.shape)         # (3, 3) — 3 rows, 3 cols
print(matrix.T)             # transpose (flip rows and cols)


# ============================================================
#  PART 2 — PANDAS  (panel data)
# ============================================================
# Think of it as: Excel/spreadsheet inside Python
# Two main types: Series (one column), DataFrame (full table)
# "pd" alias is universal convention

# --- Series — like a single column in Excel ---
s = pd.Series([85, 92, 78, 95, 60], index=["Alice","Bob","Charlie","Diana","Eve"])
print(s)
print(s["Alice"])           # 85  — access by label
print(s.mean())             # 82.0

# --- DataFrame — like a full Excel spreadsheet ---
data = {
    "name"  : ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "score" : [85, 92, 78, 95, 60],
    "grade" : ["B", "A", "C", "A", "D"],
    "passed": [True, True, True, True, False]
}
df = pd.DataFrame(data)
print(df)
#       name  score grade  passed
# 0    Alice     85     B    True
# 1      Bob     92     A    True
# 2  Charlie     78     C    True
# 3    Diana     95     A    True
# 4      Eve     60     D   False

# --- Accessing data ---
print(df["score"])              # entire score column (Series)
print(df["score"][0])           # 85  — first score
print(df.iloc[0])               # entire first row by index
print(df.loc[df["passed"]])     # only rows where passed=True

# --- Filtering — like SQL WHERE ---
high = df[df["score"] >= 85]    # rows where score >= 85
print(high)

grade_a = df[df["grade"] == "A"]
print(grade_a)

# --- Statistics ---
print(df["score"].mean())       # average score
print(df["score"].describe())   # count, mean, std, min, max etc.

# --- Add a new column ---
df["score_x2"] = df["score"] * 2
print(df)

# --- Read/write CSV (very common!) ---
df.to_csv("students.csv", index=False)          # save to CSV
df2 = pd.read_csv("students.csv")               # load from CSV
print(df2)

# --- Read/write Excel ---
# df.to_excel("students.xlsx", index=False)     # needs: pip install openpyxl
# df2 = pd.read_excel("students.xlsx")


# ============================================================
#  PART 3 — MATPLOTLIB  (math plot library)
# ============================================================
# Think of it as: plotting/graphing library — like Excel charts
# "plt" alias is universal convention

scores = [85, 92, 78, 95, 60, 88]
names  = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]

# --- Line plot ---
plt.figure(figsize=(8, 4))          # width=8 inches, height=4 inches
plt.plot(names, scores, marker="o") # line with dots at each point
plt.title("Student Scores")
plt.xlabel("Student")
plt.ylabel("Score")
plt.grid(True)
plt.show()                          # display the chart

# --- Bar chart ---
plt.figure(figsize=(8, 4))
plt.bar(names, scores, color="steelblue")
plt.title("Student Scores — Bar Chart")
plt.xlabel("Student")
plt.ylabel("Score")
plt.show()

# --- Multiple lines on one chart ---
months  = ["Jan", "Feb", "Mar", "Apr", "May"]
sales_a = [100, 120, 115, 140, 160]
sales_b = [ 80,  95, 110, 105, 130]

plt.figure(figsize=(8, 4))
plt.plot(months, sales_a, marker="o", label="Product A")
plt.plot(months, sales_b, marker="s", label="Product B")
plt.title("Monthly Sales")
plt.xlabel("Month")
plt.ylabel("Sales")
plt.legend()                        # shows the label legend
plt.show()

# --- Histogram (distribution of values) ---
data = np.random.normal(70, 10, 1000)   # 1000 random scores, mean=70, std=10
plt.figure(figsize=(8, 4))
plt.hist(data, bins=30, color="steelblue", edgecolor="white")
plt.title("Score Distribution")
plt.xlabel("Score")
plt.ylabel("Frequency")
plt.show()


# ============================================================
#  PART 4 — ALL THREE TOGETHER
# ============================================================
# Real workflow: numpy for math, pandas for data, matplotlib for charts

# Create student data with numpy
np.random.seed(42)                          # makes random repeatable
raw_scores = np.random.randint(50, 100, 20) # 20 random scores 50-100

# Put into a pandas DataFrame
df = pd.DataFrame({
    "student": [f"Student {i+1}" for i in range(20)],
    "score"  : raw_scores,
    "grade"  : ["A" if s >= 90 else "B" if s >= 80
                else "C" if s >= 70 else "D" for s in raw_scores]
})

print(f"Average: {df['score'].mean():.1f}")
print(f"Highest: {df['score'].max()}")
print(f"Lowest:  {df['score'].min()}")
print(df["grade"].value_counts())           # count of each grade

# Plot with matplotlib
plt.figure(figsize=(10, 4))
plt.bar(df["student"], df["score"], color="steelblue")
plt.axhline(y=df["score"].mean(), color="red",
            linestyle="--", label=f"Average: {df['score'].mean():.1f}")
plt.xticks(rotation=45)
plt.title("Class Scores")
plt.legend()
plt.tight_layout()
plt.show()
