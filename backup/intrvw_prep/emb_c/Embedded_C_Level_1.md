# Embedded C Beginner Guide (Simple + Interview Ready)

## Who is this for?
If you know basic C but **don't understand embedded concepts**, this guide explains everything in a **simple, no-jargon way**.

---

# 1. What is Embedded Systems?

An embedded system = **a small computer inside a device that does specific task**

Examples:
- Washing machine
- Mobile modem (5G)
- Router
- Car ECU

👉 Unlike normal software:
- No keyboard/mouse
- Talks to **hardware directly**
- Must be **fast and real-time**

UART is a hardware module that sends and receives data serially between devices using TX and RX lines without a shared clock.
Device A  ←→  UART  ←→  Device B

---

# 2. Memory-Mapped Registers (VERY IMPORTANT)

### What is it?

Hardware is controlled using **special memory addresses**

Example:
```c
#define REG (*(volatile int*)0x40000000)
```

👉 This is NOT normal memory  
👉 Writing here controls hardware

### Simple analogy:
Think:
- Address = switch location
- Writing value = turning switch ON/OFF

---
```

# 3. Volatile Keyword

### Problem:
Compiler optimizes code too much

Example:
```c
while(flag == 0) {}
```

Compiler may assume flag never changes → infinite loop

### Solution:
```c
volatile int flag;
```

### Meaning:
👉 "This value can change anytime externally"

Used in:
- Hardware registers
- ISR variables
- DMA buffers

---

# 4. ISR (Interrupt Service Routine)

### What is an interrupt?

CPU is doing work → suddenly hardware says:
👉 "STOP! handle this NOW!"

Example:
- Data received on UART
- Timer expired

### ISR = function that runs immediately

```
ISR() {
    process_data();   // ❌ too slow
}
```
Why bad? Blocks system, Misses next interrupt.
```
ISR() {
    data_ready_flag = 1;   // ✅ fast
}
if (data_ready_flag) {
    process_data(buffer);  // CPU processing
}
```

### Rules:
- Must be FAST
- No printf / malloc
- Just signal main code

---

# 5. DMA (Direct Memory Access)

### Problem:
CPU copying data is slow

### Solution:
DMA = hardware copies data directly

👉 CPU says:

copy from src address to dest address, of N bytes.
DMA does it without CPU

Example: FFT IQ samples are copied from vspa local memory to dma shared memory for DFE. Later it can do memcpy() in ARM

### Why important?
Used in:
- 5G modem data transfer
- High-speed networking

---

# 6. Bit Manipulation

Hardware registers use bits:

```
reg |= (1 << 3);   // set bit
reg &= ~(1 << 3);  // clear bit
```

Example:
- Bit 0 → enable RX
- Bit 1 → enable TX

---

# 7. Race Condition

A race condition happens when two execution contexts touch the same state at the same time, and the final result depends on timing.

### Problem:
Two things access same variable

Example:
task vs task
ISR vs task
DMA/hardware vs CPU
CPU core vs CPU core
host side vs coprocessor through shared memory


```c
counter++; // use atomics to avoid race conditions.
```

This is NOT safe. If two tasks do it at once, one increment can be lost.

### Solution:
Critical section

```c
disable_irq();  // turn off interrupt requests
counter++;		// protect shared data
enable_irq();	// 
```

An operation is atomic if the CPU does it in one single instruction, so:
- it cannot be interrupted midway
- no partial update happens

counter++ is not atomic because it involves multiple CPU instructions (load, modify, store), and can be interrupted in between, leading to race conditions.
On a 32-bit ARM processor, aligned 32-bit loads and stores are atomic because they are executed in a single instruction.
```
uint32_t x = counter;   // atomic
counter = 10;			// atomic
```

Global/shared state = use atomics, locks, barriers, or strict ownership.
```
#include <stdatomic.h>

atomic_uint counter = 0;
atomic_fetch_add(&counter, 1);

but, counter should be declared as : atomic_uint counter;

```
---

# 8. Circular Buffer (Very Important)
A circular buffer is a fixed-size ring-like data structure that efficiently stores and processes continuous data using head and tail pointers without dynamic memory allocation.
```
void push(uint8_t data) {
    buffer[head] = data;
    head = (head + 1) % SIZE;   // wrap around
}
```
Used everywhere:
- UART
- Network data
- 5G data flow

### Idea:
Buffer acts like a ring

```text
[1][2][3][4]
 ↑      ↓
tail   head
```

No memory allocation needed

---

# 9. Endianness

### Big vs Little Endian

Number: 0x12345678

Stored as:
- Little: 78 56 34 12
- Big:    12 34 56 78

### Important for:
- Networking (always BIG endian)
- nr_ue_phy (always little endian)

---

# 10. Struct Padding

Compiler adds gaps in struct

```
struct A {
    char a;
    int b;
};
```

Size is NOT 5 → becomes 8

char = 1 byte  
int  = 4 bytes  
Total = 5 bytes

char is placed every 1 byte(0,1,2,..), int is placed every 4 bytes (0,4,8,..) -> because aligned access is faster.

char is at 0 address, int cannot be at 1, it will be at 4 and takes 4 bytes : so total = 8 bytes


### Why?
Alignment for speed

---

# 11. Static Keyword

```
static int x;
```
inside a function: stores the variable between the calls
outside a function: stored globally for this file only (private)

Means:
- Stored permanently
- Not visible outside file

Used for:
- Driver internal data

---

# 12. Real-Time Systems
A system that must finish work within a fixed time (deadline)
### Meaning:
Must respond within time

Example:
- 5G slot = 0.5 ms
- car airbags

Miss deadline → system fails

---

# 13. SPSC (Single Producer Single Consumer)

Example: (like a circular buffer)
- ISR writes data
- Task reads data

👉 No locks needed if designed properly

---

# 14. Embedded Interview Key Topics

You MUST know:
- Volatile
- ISR
- DMA
- Circular buffer
- Bit manipulation
- Memory-mapped registers
- Race conditions

---

# 15. Simple Mental Model

Think like this:

| Concept 			| Simple Meaning |
|--------|-------|
| ISR 				| Urgent function |
| DMA 				| Hardware copying data |
| Volatile 			| "Don't trust compiler" |
| Register 			| Hardware variable |
| Circular buffer 	| Ring queue |
| Critical section 	| No interrupt zone |

---

# Final Advice

- Focus on **understanding**, not memorizing
- Practice small C programs
- Visualize hardware behavior

---

You are now ready to start Embedded C interviews 🚀
