# Embedded C Level 2 (Intermediate) — Interview Preparation Guide
### For 5G RAN / Modem / Real-Time Systems

---

## Goal
This guide builds on basic concepts and prepares you for:
- Product companies
- Telecom / 5G modem roles
- Real-time embedded systems

---

# 1. RTOS Basics (Real-Time Operating System)

## What is RTOS?
An RTOS manages:
- Tasks (threads)
- Scheduling
- Timing guarantees

## Key Concepts

### Task
A function that runs independently

### Scheduler
Decides which task runs

### Priority
Higher priority task runs first

---

## Important APIs (conceptual)


- create_task() 	// creates a new independent execution unit (task/thread) managed by the RTOS.
- delay()			// give time for other tasks to run (in ms).
- semaphore_take()	// blocks a task until a resource or event becomes available.
- queue_send()		// sends data from one task/ISR to another task using a message queue.

---

## Interview Tip
RTOS ensures:
👉 Predictable timing (deterministic behavior)

---

# 2. Interrupt Latency

## What is it?
Time between:
👉 Interrupt latency is the delay between an interrupt being generated and the start of its ISR execution.

## Why important?
In 5G:
- Slot = 0.5 ms
- Missing timing = system failure

## Factors affecting latency:

- Interrupt masking	// CPU temporarily ignores interrupts, so handling is delayed
- Long ISRs			// Interrupt functions take too long to run, blocking other work
- Cache misses		// CPU can’t find data in fast memory, so it becomes slower

---

# 3. Memory Barriers & Cache
```
x = 1;
flag = 1;
```
But CPU may reorder to be faster:
```
flag = 1;
x = 1;
```
CPU:
changes order
uses cache
optimizes execution
👉 BUT this breaks communication between cores

## Problem:
CPU may reorder instructions

## Solution:
Memory barriers : is like a STOP sign for CPU. It tells CPU: “Do NOT reorder beyond this point”

### Types:
- Read barrier
- Write barrier

```
data = 100;
__DMB();        // ensures ordering : data memory barrier
flag = 1;

if (flag == 1) {
    __DMB();    // ensures fresh read
    printf("%d", data);
}

You can also use atomic versions, like atomic_load_explicit(&flag, 1, memory_order_acquire), atomic_store_explicit(&flag, 1, memory_order_release)

```
## Why needed?
In multicore systems:
👉 One core may not see updates immediately

---

# 4. Multicore Basics
A system with multiple CPUs (cores) working together
Modern modems use multiple cores

## Problems:
- Race conditions
- Cache inconsistency

## Solutions:
- Locks / mutex
- Memory barriers
- Atomic operations

---

# 5. Driver Architecture
Application → Driver → Hardware
Driver architecture separates application and hardware by using a driver layer that configures hardware, handles interrupts, and provides simple APIs.
## Layers:
- Application
- Driver
- Hardware

Good drivers:
hide hardware complexity
keep ISR short
separate control and processing

## Driver responsibilities:
- Configure hardware
- Handle interrupts
- Provide APIs

---

# 6. DMA Deep Dive

## Types:

- Memory → Peripheral 	// Data goes from RAM → to hardware
- Peripheral → Memory	// Data comes from hardware → into RAM : Laptop → UART → DMA → Memory buffer

## Important:
- Buffer alignment
- Cache flush/invalidate

---

# 7. Interrupt vs Polling

Interrupt: CPU waits, hardware tells it when needed
Polling: CPU keeps checking again and again. if(flag) process();

| Interrupt | Polling |
|----------|--------|
| Efficient | Waste CPU |
| Complex | Simple |
| Real-time | Not ideal |

👉 Always prefer interrupts in embedded

---

# 8. Cache Coherency
Because CPU uses cache and DMA uses RAM, you must flush cache before DMA reads and invalidate cache before CPU reads to keep data consistent.
## Problem:
Cache and memory mismatch

## Example:
DMA updates memory
CPU reads old cache value

## Solution:
- Cache invalidate
- Cache flush

---

# 9. Atomic Operations

## Problem:
```
x++;
```
Not atomic

## Solution:
- disable interrupts
- atomic instructions
```
__disable_irq();
x++;
__enable_irq();
```

---

# 10. Priority Inversion

## Problem:
A high-priority task gets blocked by a low-priority task

This happens when:

using mutex
shared resources

👉 Common in:

RTOS
embedded systems

## Solution:
- Priority inheritance (works only with mutex, should've already implemented this considering the situation might happen after waiting for certain duration): 
increase the priority of low-priority task temporarily such that it runs faster, releases and gives it to high priority task.

---

# 11. Embedded Debugging

## Tools:
- JTAG
- GDB
- Logs

## Techniques:
- Print debugging (limited)
- Memory dump
- Register inspection

---

# 12. Common Interview Questions

1. Difference between ISR and task? // ISR is a fast, interrupt-driven function for immediate events, while a task is a scheduled function that can run longer and can block.
2. What is interrupt latency? 		// The time delay between an interrupt occurring and the CPU starting its ISR.
3. How does DMA work?				// DMA copies data and sends interrupt when done
4. What is cache coherency?			// Ensuring that data in CPU cache and main memory remain consistent across cores or DMA.
5. What is priority inversion?		// When a high-priority task is blocked by a lower-priority task holding a resource, causing execution delays.

---

# 13. Real 5G System Flow (Simplified)

1. Hardware interrupt fires			// A device signals the CPU that something important happened
2. ISR runs							// CPU immediately executes a short function to handle the event
3. ISR pushes data to queue			// ISR quickly sends data to a queue for later processing
4. Task processes data				// A task reads the data from the queue and does the main work
5. Data sent to next layer			// Processed data is passed to the next module or system

---

# 14. Key Mental Model

Think like this:

| Concept | Meaning |
|--------|--------|
| RTOS 		| Task manager |
| ISR 		| Urgent handler |
| DMA 		| Hardware copy engine |
| Cache 	| Fast memory |
| Barrier 	| Order guarantee |

---

# Final Advice

To crack interviews:
- Understand concepts deeply
- Practice explaining simply
- Solve problems

---

You are now Level 2 ready 🚀
