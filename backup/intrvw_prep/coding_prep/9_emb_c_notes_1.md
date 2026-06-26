# Multi-Threading & Multi-Core in `nr_ue_phy`

> Covers everything discussed in the April 29 chat session.
> All code references are from nr_ue_phy repo.

---

## Table of Contents

1. [Core Concept — What Is a Thread?](#1-core-concept--what-is-a-thread)
2. [What Is Multi-Core?](#2-what-is-multi-core)
3. [The PHY Thread Architecture](#3-the-phy-thread-architecture)
4. [What Each Thread Does](#4-what-each-thread-does)
5. [How Threads Are Created](#5-how-threads-are-created)
6. [How Threads Are Pinned to Cores](#6-how-threads-are-pinned-to-cores)
7. [SCHED_FIFO — Real-Time Scheduling](#7-sched_fifo--real-time-scheduling)
8. [How Threads Communicate — Message Passing](#8-how-threads-communicate--message-passing)
9. [How a Thread Knows It Has a Message — Semaphore & `pthread_cond_signal`](#9-how-a-thread-knows-it-has-a-message)
10. [Mutex — Protecting Shared Data](#10-mutex--protecting-shared-data)
11. [Semaphore — Counting & Signalling](#11-semaphore--counting--signalling)
12. [Can Multiple Threads Run in Parallel?](#12-can-multiple-threads-run-in-parallel)
13. [How L1C Decides When to Send a Message](#13-how-l1c-decides-when-to-send-a-message)
14. [PDCCH → PDSCH Data Flow (Slot Timing)](#14-pdcch--pdsch-data-flow-slot-timing)
15. [Heterogeneous Multi-Core — Beyond ARM Threads](#15-heterogeneous-multi-core--beyond-arm-threads)
16. [How to Change a Thread's Core Affinity](#16-how-to-change-a-threads-core-affinity)
17. [Quick-Fire Interview Q&A](#17-quick-fire-interview-qa)

---

## 1. Core Concept — What Is a Thread?

A **thread** is the smallest unit of execution (like a worker) inside a process. By default a process has one worker (one thread) — it can only do one thing at a time. Multi-threading means creating multiple workers inside the same process so they can do multiple things concurrently.

All threads in a process share the same memory (code, global variables, heap). This sharing is both the power and the danger — multiple threads can accidentally overwrite each other's data, which is why synchronization primitives (mutex, semaphore) exist.

```
Process (uephy)
├── thread 1: L1C / Control
├── thread 2: PDCCH
├── thread 3: PDSCH
├── thread 4: SYNC
└── thread 5: ULCOMP
    └── all share the same memory space
```

---

## 2. What Is Multi-Core?

A **CPU core** is a physical execution unit on the processor chip. Having multiple cores means you can run multiple threads truly simultaneously — one per core.

| Scenario | Result |
|---|---|
| 4 threads, 1 core | Threads take turns (time-sliced by OS) |
| 4 threads, 4 cores | Threads run truly in parallel at the same instant |

**Multi-threading** = multiple workers.
**Multi-core** = multiple desks.
Real parallelism needs both.

---

## 3. The PHY Thread Architecture

```
CORE 0 (Control core)              CORE 1 (DSP core)
──────────────────────────         ──────────────────────────────
L1C_RX thread                      BASEBAND_HANDLER (L1C) thread
  listen on UDP socket               orchestrate slot processing

CONTROL / L1C thread               PDCCH thread
  state machine, dispatch            blind DCI decode

RESET thread                       PDSCH thread
  startup/shutdown only              data decode (FFT→LDPC)

                                   SYNC thread
                                     cell search, PSS/SSS, PBCH

                                   ULCOMP thread
                                     build UL TX slot
```

**Affinity config (NXP hardware)** — `lib/skeleton/nxp/skeleton_config.h`:

```c
#define SKL_BASEBAND_HANDLER_TASK_AFFINITY   1   // DSP core
#define SKL_PDSCH_HANDLER_TASK_AFFINITY      1   // DSP core
#define SKL_SYNC_TASK_AFFINITY               1   // DSP core
#define SKL_CONTROL_TASK_AFFINITY            0   // Control core
#define SKL_L1C_RX_TASK_AFFINITY             0   // Control core
#define SKL_RESET_TASK_AFFINITY              0   // Control core
```

**Priority config** — same file:

```c
#define SKL_RESET_TASK_PRIORITY             WRP_Task_Priority_1   // → Linux RT 94
#define SKL_CONTROL_TASK_PRIORITY           WRP_Task_Priority_2   // → Linux RT 93
#define SKL_BASEBAND_HANDLER_TASK_PRIORITY  WRP_Task_Priority_3   // → Linux RT 92
#define SKL_PDSCH_HANDLER_TASK_PRIORITY     WRP_Task_Priority_4   // → Linux RT 91
#define SKL_SYNC_TASK_PRIORITY              WRP_Task_Priority_5   // → Linux RT 90
```

Linux formula (in `wrp_task.c`): `sched_priority = 80 + (15 - our_priority)`

---

## 4. What Each Thread Does

### L1C_RX Thread (`trd_l1c_rx.c`)
**The receptionist.** Sits blocked on a UDP socket waiting for messages from the MAC layer (config requests, UL/DL grants). When a packet arrives it puts a message in the L1C inbox and goes back to listening. Does zero signal processing. Isolated so a slow network read never stalls the DSP threads.

### L1C / Control Thread (`trd_l1c.c`)
**The foreman / brain.** A 2500-line state machine with states:
`L1C_POWER_DOWN → L1C_INITIALIZED → L1C_CONFIGURED → L1C_RUNNING`

Every slot it decides what to dispatch:
- "SYNC, please track timing"
- "PDCCH, here is a slot of antenna data, find the DCI"
- "PDSCH, the grant said RBs 12–48, MCS 16, decode them"
- "ULCOMP, build me an uplink slot"

Collects responses, manages HARQ state, applies CFO/timing corrections, sends KPIs to MAC. Does very little signal processing itself — pure orchestration.

### SYNC Thread (`trd_sync.c`)
**The navigator.** On first power-on hunts for:
1. **PSS** (Primary Sync Signal) — locate cell in time
2. **SSS** (Secondary Sync Signal) — get cell ID
3. **PBCH** — decode master information block
4. **CFO estimation** — correct local oscillator error

Once connected, runs periodically to refine timing and frequency so the UE doesn't drift. Compute-heavy (processes many samples), on the DSP core with high RT priority.

### PDCCH Thread (`trd_pdcch.c`)
**The mailbox checker.** Every slot, receives the CORESET symbols (sym 0 or 0–1) and performs **blind decoding**:
- Tries all candidate DCI locations and formats (each Agg Lev, each cand idx)
- For each: demod → descramble → Polar decode → CRC check
- Accepts the one that passes CRC

Sends the decoded DCI result (resource blocks, MCS, HARQ info) immediately to PDSCH via `SEND_PDSCH_DL_CONFIG_REQ`. Also sends a DCI indication to MAC over UDP.

### PDSCH Thread (`trd_pdsch.c`)
**The package opener.** Most compute-heavy thread. Receives:
1. DCI grant from PDCCH (immediately when PDCCH finishes)
2. Data symbols (sym 2–13) from DFE (arrives a few µs later when captured from antenna)

Then runs the full receive chain:
- FFT (time → frequency domain)
- DMRS channel estimation
- Equalization (undo the channel)
- Demodulation (constellation → soft bits / LLRs)
- Descrambling
- Rate recovery
- LDPC decode
- HARQ combining (`dl_harq.c`)
- CRC check → pass decoded bytes to MAC

### ULCOMP Thread (`trd_ulcomp.c`)
**The outgoing-mail packer.** When an uplink grant arrives, builds the UL TX slot:
- **PUSCH**: encode bits → LDPC → rate-match → scramble → modulate → DMRS → IFFT
- **PUCCH**: HARQ ACK/NACK, CSI, scheduling requests
- **PRACH**: random-access preamble when first contacting a cell

Also handles TX power scaling (using `txScaling`, `txAtt`, `txPowerHeadroom`) and timing advance (transmit early so signal arrives at gNB on time).

### RESET Thread (skeleton)
**The building manager.** Runs only at startup and shutdown. Sends INIT messages to each component in order, waits for "OK ready" replies, then sleeps forever. Highest RT priority because it must complete startup before anything else runs.

---

## 5. How Threads Are Created

There is a table of all threads in `toplevel/phy/phy_skeleton.c`. At startup, a loop in `lib/skeleton/skeleton.c` reads the table and creates each thread:

```c
// skeleton.c — the creation loop
for (c = 0; c < g_GNB_SKL.initConfigPtr->numSklContext; c++) {
    SKL_initContext(&g_GNB_SKL.initConfigPtr->sklContextPtr[c], memSegPtr);
}
```

`SKL_initContext` does three things for each thread:

```c
// lib/skeleton/skeleton.c  lines 568–592
SKL_SEMAPHORE_INIT(suspendSemaphore);   // create the wakeup semaphore
SKL_MESSAGE_QUEUE_INIT(msgQueue);        // create the inbox
SKL_TASK_INIT(task, entry, stack, priority, affinity);  // create the thread
```

`SKL_TASK_INIT` → `WRP_Task_init` → `pthread_create` (the actual Linux thread creation).

Each thread's entry function is `SKL_EntryPoint` which runs the message dispatch loop forever.


"
We use a framework-based initialization where all thread contexts are defined in a configuration table. During startup, a loop initializes each context by creating its semaphore, message queue, and thread. 
The threads are created via pthread_create and all run a common entry function that implements a message-driven loop
"
---

## 6. How Threads Are Pinned to Cores

**Step 1** — Declare which core in config:
```c
// lib/skeleton/nxp/skeleton_config.h
#define SKL_PDSCH_HANDLER_TASK_AFFINITY  1   // core 1
```

**Step 2** — Applied at thread creation in `wrp_task.c`:
```c
// lib/os/linux/osal/src/wrp_task.c  lines 410–422
#if defined(MULTI_CORE) && !defined(__APPLE__)
    CPU_ZERO(&mask);
    CPU_SET(a_affinity, &mask);   // a_affinity = 1 for PDSCH
    status = pthread_setaffinity_np(taskPtr->taskHandle, sizeof(mask), &mask);
#endif
```

After this call, the Linux kernel will **never** migrate the thread to a different core, even if that core is idle. The DSP threads are always on core 1; they never compete with control traffic on core 0.

Also called `mlockall(MCL_CURRENT | MCL_FUTURE)` to lock all memory into RAM — eliminates page-fault stalls.

---

## 7. SCHED_FIFO — Real-Time Scheduling

Linux has two scheduler classes:

| Scheduler | Behaviour |
|---|---|
| `SCHED_OTHER` | Default for all processes. Time-sliced — the OS pauses your thread every few ms to run something else. |
| `SCHED_FIFO` | Real-time. A thread runs **until it voluntarily blocks** (waits on queue/semaphore). No time slicing. Higher priority always preempts lower. All RT threads preempt any `SCHED_OTHER` thread. |

Our threads use `SCHED_FIFO`:
```c
// lib/os/linux/osal/src/wrp_task.c  lines 353–376
pthread_attr_setschedpolicy(&taskPtr->taskAttr, SCHED_FIFO);
taskPtr->taskScedParam.sched_priority = 80 + (WRP_Task_Priority_15 - a_priority);
pthread_attr_setschedparam(&taskPtr->taskAttr, &taskPtr->taskScedParam);
```

Our threads sit at Linux RT priorities 90–94. All normal system threads (loggers, shells, kernel workers) are at priority 0 — they can **never** preempt our PHY threads. This is critical: a 500 µs slot deadline cannot be missed because a shell command happened to run at the wrong time.

---

## 8. How Threads Communicate — Message Passing

Threads **never** read/write each other's private variables directly. All communication is through **typed messages** placed in a receiver's inbox (message queue).

**The message structure** — every ICM has a common header:
```c
// lib/mt/itc.h
typedef struct _itc_message_shared_struct {
    uint32_t senderComponent;
    uint32_t destinationComponent;
    uint32_t messageID;      // what type of message is this?
    uint32_t messageSize;
} itc_message_shared_struct_t;
```

**Sending a message** — e.g. L1C → PDCCH:
```c
// toplevel/phy/trd_pdcch_icm.h  (macro expands to):
pdcchDlConfigIcmPtr->interCompMessageSharedStruct.destinationComponent = COMPONENT_ID_PDCCH;
pdcchDlConfigIcmPtr->interCompMessageSharedStruct.messageID = INTERCOMP_MSG_ID_PDCCH_DL_CONFIG_REQ;
SKL_POST_MESSAGE(pdcchDlConfigIcmPtr, SKL_SENDING_METHOD_DEFAULT);
```
**puts message in PDCCH's queue, increments its semaphore → PDCCH wakes up**
** trd_pdsch gets FFT data indirectly. NXP writes the bulk FFT IQ into shared memory. NXP sends a small completion indication through a shared-memory queue.
** The A35 DFE RX task receives that indication, converts/shared-passes pointers, then posts an internal message to trd_pdsch.

**Queue properties:**
- Each thread has its own queue — multiple sub-queues inside it
- Sub-queues have priorities (ICM control messages drain before data messages)
- Queue size for PDCCH: 14 elements (`PDCCH_RX_Q_MAX_NUM_ELEMENTS = 4 + 10`)
- Messages are FIFO within each sub-queue

---

## 9. How a Thread Knows It Has a Message

### The mechanism: semaphore + condition variable

Each thread has a **suspend semaphore** initialized to 0. The thread's main loop:

```
PDCCH thread main loop:
  loop forever:
    sem_wait(suspendSemaphore)   ← SLEEP here if count = 0 (uses 0 CPU)
    while (queue has messages):
      msg = queue.receive()
      dispatch to handler function based on messageID
```

When a sender puts a message in PDCCH's queue it calls `sem_post` (semaphore give):
```
L1C sends to PDCCH:
  queue.put(message)
  sem_post(pdcch.suspendSemaphore)  ← count 0→1, PDCCH wakes up
```

### `pthread_cond_signal` — the simpler mailbox (used in `itc.c`)

For the lightweight mailbox (`itc_shared_msg_t`), the same idea uses `pthread_cond_signal`:

```c
// Sender (producer) — lib/mt/itc.c
pthread_mutex_lock(&me->mutex);
me->msg_ptr = msg_ptr;
me->type    = type;
pthread_mutex_unlock(&me->mutex);
pthread_cond_signal(&me->cond);    // ring the bell — wake the receiver
```

```c
// Receiver (consumer) — lib/mt/itc.c
pthread_mutex_lock(&me->mutex);
while (me->type == ITC_MSG_NONE) {
    pthread_cond_wait(&me->cond, &me->mutex);  // sleep, 0 CPU
}
// message is here — read it
pthread_mutex_unlock(&me->mutex);
```

The `while` (not `if`) handles **spurious wakeups** — Linux can occasionally wake a thread without a signal; the loop re-checks and goes back to sleep if nothing is there.

**Key difference: semaphore vs `pthread_cond_signal`:**
- `pthread_cond_signal`: if nobody is waiting, the signal is **lost**
- `sem_post`: increments the counter — the next `sem_wait` picks it up even if called later. The semaphore **remembers** the signal.

---

## 10. Mutex — Protecting Shared Data

A **mutex** (mutual exclusion lock) ensures only one thread at a time can access a shared resource.

**The toilet analogy:** One key, one toilet. Lock when you enter, unlock when you leave. If locked, the next person waits outside.

```c
// Two threads both want to write to 'counter':

// Thread A:
pthread_mutex_lock(&mutex);     // lock — Thread B must wait
counter++;                       // safe: only A is here
pthread_mutex_unlock(&mutex);   // unlock — Thread B can enter

// Thread B (was waiting):
pthread_mutex_lock(&mutex);     // now B gets the lock
counter++;
pthread_mutex_unlock(&mutex);
```

**Without the mutex:** Both threads read `counter = 5` at the same moment, both write `6` — the second increment is lost. This is a **race condition**.

**From our code** (`wrp_mutex.c`):
```c
// Lock
status = pthread_mutex_lock(&a_mutexPtr->pthreadMutex);

// ... protected section — only one thread here at a time ...

// Unlock
status = pthread_mutex_unlock(&a_mutexPtr->pthreadMutex);
```

In `itc.c`, the mutex protects the shared message slot so L1C writing `msg_ptr` and PDCCH reading `msg_ptr` never overlap.

---

## 11. Semaphore — Counting & Signalling

A **semaphore** is a counter with a waiting room.

**Operations:**
- `sem_post` / **give**: counter + 1. If any thread is sleeping on this semaphore, one of them wakes up.
- `sem_wait` / **take**: counter - 1. If counter is already 0, the thread sleeps until someone gives.

**Parking lot analogy (initial count = 1):**
- Thread A → take → counter 1→0 → parks
- Thread B → take → counter is 0 → B sleeps in waiting room
- Thread A done → give → counter 0→1 → B wakes up

**From our code** (`wrp_semaphore.c`):
```c
// Init with count = 0 (thread starts sleeping)
sem_init(&semaphorePtr->pthreadSemaphore, 0, 0);

// Take (sleep if count = 0)
sem_wait(&semaphorePtr->pthreadSemaphore);

// Give (wake a sleeper)
sem_post(&semaphorePtr->pthreadSemaphore);
```

**Semaphore vs Mutex:**

| | Mutex | Semaphore |
|---|---|---|
| Counter range | 0 or 1 only | 0, 1, 2, 3, ... any |
| Who can unlock | Only the locker | Any thread can give |
| Primary use | Protect shared data | Signal between threads / count resources |
| Memory of signal | N/A | Yes — counter remembers |

In our PHY, each thread's suspend semaphore starts at 0. The thread sleeps until a message sender posts to it. Multiple posts accumulate — if 3 messages arrive while PDSCH is decoding, the count becomes 3 and PDSCH processes all 3 immediately after it finishes.

---

## 12. Can Multiple Threads Run in Parallel?

**Yes — truly parallel across cores.**

- Core 0 threads (L1C, L1C_RX) run **at the same physical moment** as Core 1 threads (PDCCH, PDSCH, SYNC).
- On the same core, threads interleave: one runs while the other sleeps on its queue. But with `SCHED_FIFO`, a running thread is never time-sliced — it runs until it voluntarily blocks.

**PDCCH and PDSCH concurrency example:**

```
Time →
Slot N:                              Slot N+1:
──────────────────────────────────   ────────────────────────────
PDCCH decodes DCI for slot N         PDCCH decodes DCI for slot N+1
  → sends grant to PDSCH             (starts immediately after, independently)
  → PDCCH sleeps

                  PDSCH decoding slot N data
                  (FFT, ChEst, Equalize, LDPC...)
                                              PDSCH decoding slot N+1 data
```

PDCCH for slot N+1 and PDSCH for slot N can overlap in real time. PDCCH finishes quickly (just control symbols) and goes to sleep. PDSCH takes longer but runs independently. This pipelined execution is what makes the 500 µs slot budget achievable.

---

## 13. How L1C Decides When to Send a Message

L1C is a state machine. Every slot tick from the DFE triggers it. Based on its current state and what came from MAC, it dispatches:

```c
// trd_l1c.c — L1C dispatching during a configured DL slot
SEND_PDCCH_DL_CONFIG_REQ(dlCfgReqIcmPtr);   // tell PDCCH: process this slot
SEND_PDSCH_DL_CONFIG_REQ(pdschCfgIcmPtr);   // already forwarded by PDCCH, but also from L1C
SEND_ULCOMP_UL_CONFIG_REQ(ulCfgReqIcmPtr);  // tell ULCOMP: build UL slot N+4
```

**Multiple messages in queue:** The queue is FIFO with depth 14 (PDCCH) or 30+ (control). Messages are served in order within each sub-queue. Higher-priority sub-queues (control ICMs like DESTROY, STOP) are drained before data sub-queues (slot data indications).

**Queue overflow:** If the queue is full (DFE too fast for PDCCH), the message is dropped and a KPI counter is incremented:
```c
// trd_pdcch.c
if (Queue_isQueueFull(g_TrdDlPdcch_Ptr->pdcchQueue)) {
    LOG_EXCEPTION("Queue is Full. DFE too slow. Dropping...");
    KPI_PDCCH_CONFIG_QUEUE_FULL();
}
```

---

## 14. PDCCH → PDSCH Data Flow (Slot Timing)

### The key variable: `intermediateDataIndicationSymb`

This is the **cut point** between PDCCH symbols and PDSCH symbols. Set by L1C based on CORESET:

```c
// trd_l1c.c  lines 1792–1796
intermediateDataIndicationSymb = coreset.startSymbolIndex + coreset.duration;
// Example: startSymbol=0, duration=1 → cut point = symbol 1
// PDCCH gets: sym 0
// PDSCH gets: sym 1–13
```

### The DFE delivers in two bursts (same slot)

```c
// dfe_if_socket.c  (x86 simulation) / dfe_if_rx.c (NXP hardware)
if (firstPartRx == false) {
    // FIRST BURST: symbols 0 to (intermediateDataIndicationSymb - 1)
    SEND_PDCCH_DATA_AVAILABLE(pdcchDataIndIcmPtr);   // → PDCCH wakes up

} else {
    // SECOND BURST: symbols intermediateDataIndicationSymb to 13
    SEND_PDSCH_DATA_AVAILABLE(pdschDataIndIcmPtr);   // → PDSCH wakes up
}
```

### The complete flow

```
PHYSICS: gNB transmits symbols one by one, 71.4 µs per symbol
─────────────────────────────────────────────────────────────────
 sym 0    sym 1    sym 2   sym 3  ...  sym 13
[PDCCH]           [────────── PDSCH data ──────────────────]
  ↑ captured first          ↑ still arriving over the air

SOFTWARE:
─────────────────────────────────────────────────────────────────
DFE delivers sym 0 → SEND_PDCCH_DATA_AVAILABLE
  → PDCCH wakes up
  → dl_pdcch_process() — blind decode DCI
  → SEND_PDSCH_DL_CONFIG_REQ (grant sent immediately to PDSCH)
  → PDCCH sleeps

    PDSCH wakes up, stores the grant, sleeps again (data not here yet)

DFE delivers sym 2–13 → SEND_PDSCH_DATA_AVAILABLE
  → PDSCH wakes up — grant already known!
  → FFT → ChEst → Equalize → Demod → Descramble → LDPC → CRC
  → decoded bytes sent to MAC
```

### Why can't DFE send PDSCH data with the DCI?

**Physics.** Symbols arrive sequentially over the air, one every 71.4 µs. The gNB transmits them in order; the UE can only receive what has arrived. Sym 2 is literally still in the air while sym 0 is being decoded by PDCCH. There is no shortcut.

The clever design is that PDSCH already knows its job (which RBs, MCS, HARQ process) before the data arrives, so when the data symbols finally land, decoding starts immediately with zero decision delay.

---

## 15. Heterogeneous Multi-Core — Beyond ARM Threads

The NXP LA9310 chip has three processors inside:

```
┌─────────────────────────────────────────────────────────────┐
│                      NXP LA9310 Chip                        │
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────┐  │
│  │  VSPA DSP    │   │  Cortex-M4   │   │   RF (ADC/DAC) │  │
│  │              │   │  (FreeRTOS)  │   │                │  │
│  │ • FFT        │   │ • RF control │   │ • Antenna I/O  │  │
│  │ • PSS xcorr  │   │ • AGC        │   │ • ADC capture  │  │
│  │ • FIR filter │   │ • Slot timer │   │ • DAC TX       │  │
│  └──────┬───────┘   └──────┬───────┘   └──────┬─────────┘  │
│         └──────────────────┴───────────────────┘           │
│                       internal bus                         │
└────────────────────────────┬────────────────────────────────┘
                             │ PCIe / shared memory
                             ▼
                 ARM Cortex-A (Linux, our code)
                 Core 0              Core 1
                 L1C, L1C_RX        SYNC, PDCCH, PDSCH, ULCOMP
```

**VSPA DSP** (`toplevel/dfe_vspa/`): Vector signal processor, runs FFT and PSS cross-correlation in hardware. Instead of the ARM computing FFT in software (slow), VSPA does it in nanoseconds. Source: `Sources/fir_rx.sx`, `tasks_rx.c`.

**Cortex-M4 / FreeRTOS** (`3rdparty/nxp/la93xx_freertos/`): Controls the RF — turns on receiver, sets gain (AGC), manages symbol timing. Every 500 µs it fires a **slot indication** to the ARM: *"new slot captured, IQ data is at address X"*. The ARM's `dfe_if_rx.c` picks this up and injects it into the ICM system.

**Connection:** Shared memory + PCIe mailbox interrupt. M4 writes to shared memory, raises interrupt on ARM. ARM's DFE thread reads the buffer pointer, creates a `PDCCH_DATA_AVAILABLE` or `PDSCH_DATA_AVAILABLE` ICM, and posts it to the relevant thread's queue.

---

## 16. How to Change a Thread's Core Affinity

One-line change in the config:

```c
// lib/skeleton/nxp/skeleton_config.h
// Change:
#define SKL_PDSCH_HANDLER_TASK_AFFINITY   1

// To:
#define SKL_PDSCH_HANDLER_TASK_AFFINITY   0
```

Rebuild. At next startup, `WRP_Task_init` will call `CPU_SET(0, &mask)` instead of `CPU_SET(1, &mask)` and PDSCH runs on core 0.

**Why you should NOT do this in production:**
PDSCH is the heaviest thread. Moving it to core 0 means it competes with L1C and L1C_RX for that core's time. Even with `SCHED_FIFO`, they take turns on the same core. The 500 µs slot budget may not be met. The control/DSP core separation exists precisely to avoid this competition.

---

## 17. Quick-Fire Interview Q&A

**Q: What is the difference between a thread and a process?**
> A process is an independent program with its own memory space. Threads share memory within the same process. Threads are lighter to create and communicate faster (shared memory vs IPC), but need careful synchronization to avoid race conditions.

**Q: What is a race condition?**
> When two threads access shared data simultaneously without synchronization and the result depends on who gets there first. Fixed with a mutex.

**Q: What is a deadlock?**
> Thread A holds lock X and waits for lock Y. Thread B holds lock Y and waits for lock X. Both wait forever. Prevention: always acquire locks in the same consistent order everywhere in the code.

**Q: What is priority inversion?**
> A high-priority thread waits for a lock held by a low-priority thread. A medium-priority thread keeps preempting the low-priority one, so the high-priority thread is indirectly blocked by a medium one. We avoid this by keeping lock hold times extremely short.

**Q: Why message passing instead of shared memory between threads?**
> Message passing means each thread owns its own data. The only synchronization point is the queue. Shared memory requires locking everywhere — error-prone and a source of priority inversion. Our design also naturally maps to the pipeline: data flows in one direction through PDCCH → PDSCH → MAC.

**Q: What is `SCHED_FIFO`?**
> A Linux real-time scheduling class. A `SCHED_FIFO` thread runs until it voluntarily blocks — no time-slicing. Higher RT priority always preempts lower. All `SCHED_FIFO` threads preempt normal `SCHED_OTHER` threads. Used to meet hard real-time deadlines (our 500 µs slot budget).

**Q: What does `pthread_setaffinity_np` do?**
> Pins a thread to a specific CPU core. The Linux kernel will not migrate it to any other core, even if that core is idle. Ensures predictable cache behaviour and prevents DSP threads from being preempted by control-plane threads on a different core.

**Q: What is `mlockall`?**
> Locks all process memory into RAM, preventing the kernel from swapping it to disk. Eliminates page-fault stalls in real-time threads — a page fault could stall a thread for milliseconds, which would blow a slot deadline.

**Q: How does PDCCH pass the DCI to PDSCH?**
> After `dl_pdcch_process()` finishes, PDCCH calls `SEND_PDSCH_DL_CONFIG_REQ` which puts a typed ICM message in PDSCH's queue immediately. PDSCH wakes up, stores the grant, and goes back to sleep to wait for the data symbols from the DFE.

**Q: Why does PDSCH have to wait for data symbols if PDCCH already decoded the DCI?**
> Physics. OFDM symbols arrive sequentially over the air — each takes ~71 µs. PDCCH symbols (sym 0–1) arrive and are decoded first. The PDSCH data symbols (sym 2–13) are still in the air, arriving one by one. The UE cannot receive what hasn't been transmitted yet.

**Q: Describe the full DL receive chain.**
> gNB transmits → VSPA/M4 capture → DFE splits slot at CORESET boundary → PDCCH gets sym 0–1, blind decodes DCI, sends grant to PDSCH → DFE sends sym 2–13 to PDSCH → PDSCH runs FFT, channel estimation, equalization, demodulation, descrambling, rate recovery, LDPC decode, HARQ combining, CRC → decoded bytes sent to MAC.

---

*Generated from the April 29, 2026 interview prep session.*
*Code references verified against branch `NRUEL1-1389-components`.*


## 18. Microprocessor architecture
A microprocessor architecture is the basic design of how a CPU (the brain of a system) works internally.

At a simple level, it has three main parts:

**ALU (Arithmetic Logic Unit) → does calculations (add, subtract, compare)
**Registers → very small, fast storage inside the CPU
**Control Unit → decides what to do next (like a manager)

The CPU follows a cycle:
**Fetch → Decode → Execute

Fetch → get instruction from memory
Decode → understand what it means
Execute → perform the action

It also connects to:

Memory (RAM) → stores data and programs
Peripherals → devices like UART, timers, etc.

Modern processors may have:

Cache (fast memory)
Multiple cores
Pipelines (do multiple steps in parallel)

In short: **Microprocessor architecture defines how the CPU processes instructions and interacts with memory and hardware.

## 19. ARM architecture
ARM architecture is a type of CPU design used in most embedded systems, smartphones, and IoT devices.

It is known for being **simple, fast, and power-efficient.

ARM processors follow a RISC (Reduced Instruction Set Computer) design, meaning:
👉 fewer, simpler instructions → faster execution and lower power use

There are different ARM families:

Cortex-M → microcontrollers (simple devices like sensors)
Cortex-R → real-time systems (automotive, 5G modems)
Cortex-A → high-performance systems (phones, Linux)

ARM CPUs use a pipeline:
**Fetch → Decode → Execute (often overlapping for speed)**

They also include features like:

Registers for fast data access
Cache for speed
MMU/MPU for memory control

In short: **ARM architecture is a power-efficient CPU design widely used in embedded and mobile systems, optimized for performance with low energy consumption.