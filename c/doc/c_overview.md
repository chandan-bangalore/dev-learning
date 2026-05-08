# C Programming for Embedded Interviews — Section Overviews

> Source: embeddedshiksha.com — Helping Embedded System Engineers to Clear Interviews

---

## Section 1: Pointers (30 Questions)

Pointers are the **single most important topic** in embedded C interviews. Every embedded engineer must master them because embedded programming is fundamentally about controlling hardware memory directly.

### What are Pointers?
A pointer is a variable that stores the **memory address** of another variable. Instead of holding data like `int x = 5`, a pointer holds the location where data lives: `int *p = &x`.

### Why Pointers Matter in Embedded Systems
- **Hardware registers** are fixed memory addresses — you access them only through pointers
- **Device drivers** read/write peripherals by dereferencing hardware addresses like `*(volatile uint32_t*)0x40020000`
- **Dynamic memory**, **arrays**, **strings**, and **function callbacks** all rely on pointers
- Without pointers, you cannot write interrupt service routines, DMA transfers, or memory-mapped I/O

### Key Concepts to Master
| Concept | Why It Matters |
| --------| ---------------|
| Pointer arithmetic | Traversing arrays, buffers, memory blocks |
| NULL pointer | Safety check before dereferencing |
| Dangling pointer | Common source of crashes in embedded systems |
| void pointer | Generic memory operations like memcpy |
| Function pointer | Callbacks, ISR tables, driver interfaces |
| Double pointer | Dynamic 2D arrays, pointer-to-pointer passing |
| const with pointer | Read-only hardware registers |
| volatile with pointer | Registers that change outside program control |

### Common Pitfall
```c
int *p;        // Uninitialized — points to garbage address
*p = 10;       // CRASH — writing to unknown memory location
// Always initialize: int *p = NULL; or int *p = &some_var;
```

---

## Section 2: Memory Management (25 Questions)

Memory management is critical in embedded systems because **RAM is severely limited** — often just a few kilobytes. A memory leak or corruption can silently destroy your system.

### Process Memory Layout
```
HIGH ADDRESS
┌─────────────────┐
│   Stack         │ ← Local variables, function call frames
│   (grows ↓)     │   Fixed size, automatic allocation/free
├─────────────────┤
│   Free space    │
├─────────────────┤
│   Heap          │ ← Dynamic allocation (malloc/calloc/free)
│   (grows ↑)     │   Manual management — source of leaks!
├─────────────────┤
│   BSS segment   │ ← Uninitialized global/static variables
├─────────────────┤
│   Data segment  │ ← Initialized global/static variables
├─────────────────┤
│   Text segment  │ ← Program code (read-only)
LOW ADDRESS
```

### The Four Memory Functions
| Function | Initializes? | Use Case |
|---|---|---|
| `malloc(size)` | No (garbage) | General allocation |
| `calloc(n, size)` | Yes (zeros) | Arrays, safe buffers |
| `realloc(ptr, size)` | Partial | Resize existing allocation |
| `free(ptr)` | — | Release memory |

### Why This Matters in Embedded
- Embedded systems often run **forever** — a tiny memory leak kills the system after days
- Stack overflow corrupts adjacent memory silently
- Heap fragmentation makes malloc fail even with "enough" free memory
- Many embedded systems **avoid dynamic allocation entirely** and use static pools

### Common Pitfall
```c
char *p = malloc(10);
// ... use p ...
free(p);
*p = 'A';   // USE AFTER FREE — dangling pointer bug!
p = NULL;   // Always NULL after free
```

---

## Section 3: Bit Manipulation (25 Questions)

Bit manipulation is the **language of hardware**. Every register in a microcontroller is controlled at the bit level — you set a bit to enable a peripheral, clear a bit to reset it, toggle a bit to blink an LED.

### Why Embedded Engineers Must Master This
- GPIO, UART, SPI, I2C — all configured by setting/clearing register bits
- No library functions available in bare-metal programming
- Compact, fast operations — critical in real-time systems
- Endianness affects how you interpret multi-byte register values

### The Five Core Operations
```c
uint8_t reg = 0b00110101;   // Example register value

// SET bit n:    reg |=  (1 << n)
// CLEAR bit n:  reg &= ~(1 << n)
// TOGGLE bit n: reg ^=  (1 << n)
// CHECK bit n:  (reg >> n) & 1
// MASK:         reg & 0xFF  (keep lower 8 bits)
```

### Real Hardware Example
```c
// ARM Cortex-M GPIO — enable clock for GPIOA
// RCC_AHB1ENR register, bit 0 = GPIOAEN
#define RCC_AHB1ENR  (*(volatile uint32_t*)0x40023830)
RCC_AHB1ENR |= (1 << 0);   // SET bit 0 to enable GPIOA clock
```

### Key Topics
| Topic | Application |
|---|---|
| Bit masking | Isolating register fields |
| Shift operators | Multiplying/dividing by powers of 2 |
| XOR tricks | Swap without temp, find missing number |
| Endianness | Protocol parsing, network byte order |
| Bit fields in struct | Hardware register modeling |
| Power of 2 check | Memory alignment validation |

---

## Section 4: Structures and Unions (20 Questions)

Structures and unions are how embedded C represents **hardware registers, protocol packets, and device data** in a structured, readable way.

### Struct vs Union — Core Difference
```
STRUCT — each member has its OWN memory
┌────────┬────────┬────────┐
│  int a │ char b │float c │   Total = 4 + 1 + 4 = 9+ bytes (with padding)
└────────┴────────┴────────┘

UNION — all members SHARE the same memory
┌────────────────────────┐
│  int a  OR             │   Total = size of LARGEST member only
│  char b OR             │
│  float c               │
└────────────────────────┘
```

### Structure Padding
The compiler inserts padding bytes to align members to their natural boundary (int on 4-byte boundary, char on 1-byte). This affects `sizeof()` and is critical for protocol parsing.

```c
struct Example {
    char  a;    // 1 byte + 3 bytes padding
    int   b;    // 4 bytes
    char  c;    // 1 byte + 3 bytes padding
};
// sizeof = 12, NOT 6!
```

### Why Unions Matter in Embedded
```c
// Access same register as full word OR individual bytes
typedef union {
    uint32_t full;
    uint8_t  bytes[4];
} Register;

Register r;
r.full = 0x12345678;
printf("%02X\n", r.bytes[0]);  // Access individual bytes
```

### Packed Structs
```c
// Tell compiler: NO padding — used for protocol packets
typedef struct __attribute__((packed)) {
    uint8_t  header;
    uint32_t data;
    uint8_t  checksum;
} Packet;   // sizeof = exactly 6, not 8
```

---

## Section 5: Arrays and Strings (20 Questions)

Arrays and strings are the foundation of **buffers, communication protocols, and data processing** in embedded systems. Understanding their memory layout is essential.

### Arrays in Memory
```c
int arr[5] = {10, 20, 30, 40, 50};

Memory layout (each int = 4 bytes):
Address:  100  104  108  112  116
Value:     10   20   30   40   50

arr       → points to address 100 (first element)
arr + 1   → points to address 104
*(arr+2)  → value at address 108 = 30
```

### String in C — Critical Points
- A string is just a `char` array ending with `'\0'` (null terminator)
- `"hello"` is stored as `['h','e','l','l','o','\0']` — 6 bytes, not 5
- Missing null terminator → **undefined behavior** (strlen reads garbage)

### Array vs Pointer
```c
int arr[5];      // arr is a fixed address — cannot be reassigned
int *p = arr;    // p is a variable — can be moved

p++;    // Legal — move pointer forward
arr++;  // ILLEGAL — array name is not a variable
```

### Why This Matters in Embedded
- DMA transfers use array buffers
- UART/SPI/I2C use circular buffers (arrays with wrap-around)
- Protocol parsing requires careful substring and offset operations
- Buffer overflow is a critical security and stability vulnerability

---

## Section 6: Functions and Function Pointers (15 Questions)

Function pointers are the backbone of **device drivers, RTOS task tables, interrupt vector tables, and callback architectures** in embedded systems.

### Function Pointer Syntax
```c
// Normal function
int add(int a, int b) { return a + b; }

// Function pointer declaration
int (*fp)(int, int);   // fp points to function taking 2 ints, returning int

// Assign and call
fp = add;
int result = fp(3, 4);   // calls add(3, 4) = 7
```

### Real Embedded Use Case — Driver Interface
```c
// Generic driver structure using function pointers
typedef struct {
    void (*init)(void);
    int  (*read)(uint8_t *buf, int len);
    int  (*write)(uint8_t *buf, int len);
    void (*close)(void);
} Driver;

// UART driver implements these
Driver uart_driver = {
    .init  = uart_init,
    .read  = uart_read,
    .write = uart_write,
    .close = uart_close
};

// Application code is hardware-agnostic
uart_driver.write(data, len);
```

### Interrupt Vector Table
```c
// ARM Cortex-M vector table — array of function pointers
void (*vector_table[])(void) __attribute__((section(".vectors"))) = {
    (void*)&_stack_top,   // Initial stack pointer
    Reset_Handler,         // Reset
    NMI_Handler,           // NMI
    HardFault_Handler,     // Hard Fault
    // ...
};
```

### Key Concepts
| Concept | Use in Embedded |
|---|---|
| Static function | Limits scope to file — prevents name conflicts in drivers |
| Inline function | Zero call overhead — used in tight ISR loops |
| Recursion | Carefully avoided — uses stack; can overflow in embedded |
| Callback | ISR completion notification, RTOS event handling |

---

## Section 7: Debugging and Runtime Concepts (15 Questions)

Debugging embedded systems is harder than desktop — **no console, limited tools, real-time constraints**. Understanding common bugs and how to find them is a core interview skill.

### The Most Common Embedded Bugs
| Bug | Cause | Detection |
|---|---|---|
| Segmentation fault | NULL/invalid pointer dereference | GDB, address sanitizer |
| Stack overflow | Deep recursion, large local arrays | Stack canary, MPU |
| Memory leak | malloc without free | Valgrind, heap monitoring |
| Dangling pointer | Accessing freed memory | Static analysis, ASan |
| Race condition | Shared variable without mutex | Thread sanitizer |
| Undefined behavior | Signed overflow, out-of-bounds | UBSan, -Wall -Wextra |
| Buffer overflow | Writing past array end | Bounds checking, ASan |

### The volatile Keyword — Critical for Embedded
```c
// WITHOUT volatile — compiler may cache value in register
uint32_t *reg = (uint32_t*)0x40020000;
while (*reg == 0) {}   // Compiler might optimize to infinite loop!

// WITH volatile — compiler always reads from actual address
volatile uint32_t *reg = (volatile uint32_t*)0x40020000;
while (*reg == 0) {}   // Correctly re-reads register each iteration
```

### Debugging Tools
| Tool | Purpose |
|---|---|
| GDB | Step-through debugging, breakpoints, memory inspection |
| Valgrind | Memory leak and invalid access detection |
| AddressSanitizer (ASan) | Buffer overflow, use-after-free |
| Static analysis (cppcheck, clang-tidy) | Find bugs without running code |
| JTAG/SWD | On-chip debugging for embedded targets |
| Core dump | Snapshot of process state at crash |

### Race Condition Example
```c
// Two threads both incrementing counter — UNSAFE
int counter = 0;
// Thread 1: counter++   (read 0, write 1)
// Thread 2: counter++   (read 0, write 1) — LOST UPDATE
// Result: counter = 1, not 2!

// Fix: use mutex or atomic operation
pthread_mutex_lock(&lock);
counter++;
pthread_mutex_unlock(&lock);
```

---

*Master these 7 sections and you will be well-prepared for any embedded C interview.*
