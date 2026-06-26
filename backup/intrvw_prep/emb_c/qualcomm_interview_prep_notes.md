# 📘 Qualcomm Interview — ULTIMATE MASTER NOTES (FULL EXPANDED)

---

> This is a **complete, interview-grade document**:
> - All core C topics deeply explained
> - Each concept → insight → traps → follow-ups
> - Advanced embedded + RTOS + architecture
> - Debugging + real interview thinking

---

# 🧵 SECTION 1: C FUNDAMENTALS (DEEP + INTERVIEW)

---

## 🔹 Strings: Array vs Pointer

### Code
```c
char a[] = "hello";
char *b = "hello";
```

### 🧠 Explanation
- `a` → separate copy (modifiable)
- `b` → points to read-only memory

### ⚠️ Trap
```c
b[0] = 'H'; // UB
```

### 🔥 Follow-ups
- Where stored? → `.rodata`
- Why sometimes works? → undefined behavior depends on OS

---

## 🔹 Pass by Value (Core Concept)

### Code
```c
void foo(int *p) { p = NULL; }
```

### 🧠 Insight
- Pointer itself passed by value
- Original pointer unchanged

### 🔥 Fix
```c
void foo(int **p) { *p = NULL; }
```

---

## 🔹 const Deep Dive

```c
const int *p;     // data const
int *const p;     // pointer const
const int *const p;
```

### 🧠 Trick
👉 Read right-to-left

---

## 🔹 Memory Layout (CRITICAL)

| Section | Description |
|--------|------------|
| Text | code |
| Data | initialized globals |
| BSS | uninitialized |
| Heap | malloc |
| Stack | locals |

### 🔥 Interview Q
👉 Where is static variable stored? → Data segment

---

# 🔥 SECTION 2: POINTERS + MEMORY (MASTER LEVEL)

---

## 🔹 Pointer Arithmetic

```c
int arr[3];
int *p = arr;
p + 1; // jumps sizeof(int)
```

### ⚠️ Trap
- Not byte-wise increment

---

## 🔹 Dangling Pointer

### Cause
```c
free(p);
*p = 10; // UB
```

### ✅ Fix
```c
p = NULL;
```

---

## 🔹 Double Free

- Corrupts allocator
- Can crash or be exploited

---

## 🔹 malloc vs calloc

| Feature | malloc | calloc |
|--------|--------|--------|
| Init | garbage | zero |

---

## 🔹 Alignment + Padding

```c
struct A { char c; int i; };
```

### 🧠 Insight
- Compiler adds padding for alignment

---

# 🔥 SECTION 3: BIT MANIPULATION (ADVANCED)

---

## 🔹 Core Operators
```c
& | ^ << >>
```

---

## 🔸 Count Set Bits
```c
while (n) { n &= (n-1); count++; }
```

---

## 🔸 Reverse Bits
```c
rev = (rev << 1) | (n & 1);
```

---

## 🔸 Rotate Bits
```c
(n << d) | (n >> (32-d))
```

---

## 🔸 Power of 2
```c
n && !(n & (n-1))
```

---

## 🔸 Get Lowest Set Bit
```c
n & (-n)
```

---

## 🔸 Swap Odd/Even Bits
```c
((x & 0xAAAAAAAA)>>1) | ((x & 0x55555555)<<1)
```

---

## 🔥 Interview Traps
- Signed shift issues
- Overflow
- Mask mistakes

---

# 🔥 SECTION 4: ARRAYS + ALGORITHMS

---

## 🔹 Reverse String

- Two pointer approach

---

## 🔹 Binary Search

### ⚠️ Trap
- Requires sorted array

---

## 🔹 Edge Cases
- empty input
- overflow

---

# 🔥 SECTION 5: LINKED LISTS

---

## 🔹 Insert Front
```c
new->next = head;
head = new;
```

---

## 🔹 Reverse List
```c
prev=NULL; curr=head;
```

---

## 🔹 Interview Focus
- pointer manipulation

---

# 🔥 SECTION 6: FILE + SYSTEM PROGRAMMING

---

## 🔹 Safe IO
- fgets instead of gets

---

## 🔹 Buffer Overflow
- major security risk

---

# ⚙️ SECTION 7: EMBEDDED SYSTEMS

---

## 🔹 Memory-Mapped IO
```c
*(volatile int*)addr
```

---

## 🔹 volatile
- prevents optimization

---

# ⚙️ SECTION 8: RTOS

---

## 🔹 Scheduling
- preemptive

---

## 🔹 Mutex vs Semaphore

| Mutex | Semaphore |
|------|----------|

---

## 🔹 Priority Inversion

### Solution
- priority inheritance

---

# ⚙️ SECTION 9: INTERRUPTS

---

## 🔹 Flow
1. interrupt
2. ISR
3. return

---

## 🔹 Rules
- no blocking
- keep short

---

## 🔹 ISR + RTOS
- ISR signals task

---

# ⚙️ SECTION 10: ARCHITECTURE

---

## 🔹 ARM
- RISC

---

## 🔹 Cache
- hit/miss
- coherence

---

## 🔹 Multiprocessing Issues
- race
- deadlock

---

# 🔥 SECTION 11: DEBUGGING (CRITICAL)

---

## 🔹 Common Bugs
- segfault
- memory leak

---

## 🔹 Debug Strategy
1. reproduce
2. logs
3. debugger
4. isolate
5. fix

---

## 🔹 Tools
- gdb
- valgrind
- asan

---

# 🔥 SECTION 12: ADVANCED TOPICS (ADDED)

---

## 🔹 Endianness
- little vs big

---

## 🔹 Function Pointers
- callbacks

---

## 🔹 Race Condition Pattern
```c
shared++;
```

### Fix
- mutex / atomic

---

## 🔹 Atomic Operations
- lock-free concept

---

# 🚀 FINAL STRATEGY

## Qualcomm Focus
- C depth
- embedded thinking
- debugging clarity

---

## Answer Framework
1. define
2. explain
3. example
4. edge case

---

💡 This is your **ultimate prep doc**.

---

_End_

