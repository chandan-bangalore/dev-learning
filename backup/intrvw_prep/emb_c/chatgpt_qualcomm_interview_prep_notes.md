# 📘 Qualcomm Interview Preparation — Advanced (Converted from Your Notes)

---

# 🧵 C PROGRAMMING — INTERVIEW MASTER SHEET

This is a **concept → insight → traps → patterns** version of your notes.

---

## 🔹 Strings: Array vs Pointer

### ✅ Concept
```c
char a[] = "hello";   // modifiable
char *b = "hello";    // read-only literal
```

### 🧠 Insight
- Array → stored in stack/data → writable
- Literal → stored in read-only section → not writable

### ❌ Trap
```c
b[0] = 'H';  // undefined behavior
```

### 🔥 Follow-ups
- Where is literal stored?
- Why does it crash sometimes and sometimes not?

---

## 🔹 Pass by Value vs Pointer

### ✅ Concept
- C is always pass-by-value
- Pointer = pass address → modify original

### 🧠 Insight
```c
void foo(int *p) {
    p = NULL;  // does NOT affect caller
}
```

👉 pointer itself passed by value

---

## 🔹 NULL Pointer

### ✅ Concept
- Points to no valid memory

### ❌ Trap
```c
int *p = NULL;
*p = 10;  // crash
```

---

## 🔹 const Variants (VERY IMPORTANT)

```c
const int *p;     // value const
int *const p;     // pointer const
const int *const p; // both const
```

### 🧠 Rule
👉 read right to left

---

## 🔹 Declaration vs Definition

- Declaration → tells compiler
- Definition → allocates memory / body

---

## 🔹 static Keyword

### 🧠 Insight
- Static local → persists across calls
- Stored in data segment

---

## 🔹 extern

- Refers to variable defined elsewhere
- No new memory allocated

---

## 🔹 I/O (printf vs fprintf)

- printf → stdout
- fprintf → any stream

---

## 🔹 gets() vs fgets()

### ❌ gets()
- No bounds checking → buffer overflow

### ✅ fgets()
- Safe (limits size)

---

## 🔹 malloc() Failure

- Returns NULL → MUST check

---

# 🔥 CORE ALGORITHMIC PATTERNS (FROM YOUR QUESTIONS)

---

## 🔸 Reverse String

### Pattern
- Two pointers: start + end

---

## 🔸 String Length

- Count until '\0'

---

## 🔸 Reverse Array

- Swap i and j

---

## 🔸 Largest + Second Largest

- Track two variables

---

## 🔸 Sorting (Bubble Sort)

### Insight
- Not for production → but tests basics

---

## 🔸 Linear vs Binary Search

### Binary Search Requirement
- MUST be sorted

---

## 🔹 sizeof Trap

### ❗ Question
```c
void func(int arr[]) {
    sizeof(arr);
}
```

### 🧠 Answer
- Inside → pointer size
- Outside → actual array

---

## 🔹 Buffer Overflow

### 🧠 Insight
- Writing beyond memory → corruption
- Security risk

---

## 🔹 malloc vs calloc

| Feature | malloc | calloc |
|--------|--------|--------|
| Init | garbage | zero |

---

## 🔹 Swap using Pointer

- Basic pointer manipulation test

---

## 🔹 Dangling Pointer

- Pointer to freed memory

### ✅ Fix
```c
p = NULL;
```

---

## 🔹 Double free

- Undefined behavior

---

## 🔹 Dynamic Allocation Pattern

```c
malloc(n * sizeof(type))
```

---

## 🔹 Cleanup Pattern (IMPORTANT IN SYSTEMS)

```c
goto cleanup;
```

👉 Common in embedded systems

---

## 🔹 struct vs union

| Feature | struct | union |
|--------|--------|------|
| Memory | separate | shared |

---

## 🔹 Struct Pointer Access

```c
p->member;
```

---

## 🔹 Linked List (VERY IMPORTANT)

### Insert Front Pattern
- new → next = head
- head = new

---

## 🔹 Reverse Linked List (MUST KNOW)

```c
prev = NULL;
curr = head;
while (curr) {
    next = curr->next;
    curr->next = prev;
    prev = curr;
    curr = next;
}
```

---

## 🔹 File Handling

- fopen
- fgets
- fprintf
- fclose

---

# 🔥 BIT MANIPULATION (UPGRADED)

---

## 🔸 Basic Ops
```c
&  |  ^  <<  >>
```

---

## 🔸 Remove Lowest Set Bit
```c
n = n & (n - 1);
```

---

## 🔸 Power of 2
```c
n && !(n & (n - 1))
```

---

## 🔸 Reverse Bits
```c
rev = (rev << 1) | (n & 1);
```

---

## 🔸 XOR Trick
```c
x ^ x = 0
x ^ 0 = x
```

---

## 🔸 Endianness

- Little → LSB first
- Big → MSB first

---

## 🔸 volatile (VERY IMPORTANT)

- Prevents compiler optimization
- Used in:
  - ISR
  - hardware registers

---

## 🔸 Function Pointer

```c
int (*fp)(int, int);
```

---

## 🔸 Pointer Arithmetic

```c
p + 1 → moves by sizeof(type)
```

---

## 🔸 Macros

```c
#define SQUARE(x) ((x)*(x))
```

### ❌ Trap
- missing parentheses

---

# ⚙️ EMBEDDED + RTOS + ARCHITECTURE

---

## 🔹 Embedded Basics

- Bare-metal vs RTOS
- Memory-mapped I/O

```c
*(volatile int*)addr
```

---

## 🔹 RTOS Concepts

### Scheduling
- Preemptive
- Priority-based

---

### Synchronization

| Primitive | Use |
|----------|-----|
| Mutex | lock |
| Semaphore | signal |

---

### Priority Inversion

- Low holds resource
- High waits

### ✅ Solution
- Priority inheritance

---

## 🔹 Interrupts (CRITICAL)

### Flow
1. Interrupt
2. ISR
3. Return

### Rules
- No blocking
- Keep short

---

## 🔹 Interrupt vs Polling

| Interrupt | Polling |
|----------|--------|
| efficient | wasteful |

---

## 🔹 Computer Architecture

### ARM
- RISC
- Registers: PC, SP, LR

---

### Cache
- L1/L2
- hit/miss
- write-through vs write-back

---

### Multiprocessing Issues
- Race condition
- Deadlock
- False sharing

---

# 🔥 DEBUGGING (QUALCOMM FOCUS)

---

## 🔹 Common Issues
- Segfault
- Memory leak
- Deadlock
- Race condition

---

## 🔹 Structured Approach
1. Reproduce
2. Logs
3. Debugger
4. Narrow down
5. Root cause

---

## 🔹 Example: Segfault
- invalid pointer
- out-of-bounds

---

## 🔹 Example: Memory Leak
- missing free

Tools:
- Valgrind
- ASan

---

# 🚀 FINAL STRATEGY

## Focus
- C (deep)
- Bit manipulation
- Interrupts
- Debugging

## Answer Style
1. Define
2. Explain
3. Example
4. Edge case

---

💡 This is now optimized for **Qualcomm-style interviews**.

---

_End of Converted Advanced Notes_

