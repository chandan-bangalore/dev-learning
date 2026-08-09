# Embedded Linux E + F + G — Study Notes

The runtime architecture of `nr_ue_phy`. Once you have these three sections in your head,
the toplevel/ + lib/os/ code stops looking like magic.

**POSIX** stands for Portable Operating System Interface. 
It's a family of standards defined by the IEEE (and later adopted by ISO/IEC) that specifies how an operating system should behave, 
not how it's built internally, but what interface it exposes to programs.
The goal: write a program once, run it on any POSIX-compliant OS without changes.

- **E** — POSIX Linux user-space the project actually uses
- **F** — Multi-threading patterns specific to this repo (ICM, one-thread-per-channel)
- **G** — Real-time on Linux (why stock Linux isn't RT, and what mitigations live in this code)

For each topic:
1. **Layman** — what it actually is, in plain English
2. **In this project** — how nr_ue_phy uses it
3. **Minimal example** — a tiny self-contained snippet you can compile on your RPi
4. **In tree** — concrete pointer into nr_ue_phy with file:line so you can read the real thing

---

## Table of contents

- [E1. POSIX threads (pthreads)](#e1-posix-threads-pthreads)
- [E2. Mutexes (mutual exclusion)](#e2-mutexes-mutual-exclusion)
- [E3. Condition variables](#e3-condition-variables)
- [E4. POSIX semaphores](#e4-posix-semaphores)
- [E5. Message queues (the project's own — not POSIX mqueue)](#e5-message-queues-the-projects-own--not-posix-mqueue)
- [E6. Sockets — AF\_UNIX and AF\_INET](#e6-sockets--af_unix-and-af_inet)
- [E7. File descriptors and epoll](#e7-file-descriptors-and-epoll)
- [E8. Signals](#e8-signals)
- [E9. Process model — fork/exec/exit](#e9-process-model--forkexecexit)
- [F1. One-thread-per-channel](#f1-one-thread-per-channel)
- [F2. ICM (inter-component messaging)](#f2-icm-inter-component-messaging)
- [F3. Producer / consumer with bounded queues](#f3-producer--consumer-with-bounded-queues)
- [F4. Lock-free vs lock-based](#f4-lock-free-vs-lock-based)
- [F5. Real-time scheduling — SCHED\_FIFO and priorities](#f5-real-time-scheduling--sched_fifo-and-priorities)
- [F6. CPU affinity / pinning](#f6-cpu-affinity--pinning)
- [G1. Why stock Linux is not real-time](#g1-why-stock-linux-is-not-real-time)
- [G2. PREEMPT\_RT](#g2-preempt_rt)
- [G3. CPU isolation, IRQ affinity, NUMA](#g3-cpu-isolation-irq-affinity-numa)
- [G4. Monotonic clocks and TSC](#g4-monotonic-clocks-and-tsc)
- [G5. Watching for jitter — cyclictest, ftrace, perf sched](#g5-watching-for-jitter--cyclictest-ftrace-perf-sched)
- [G6. Memory locking — mlockall](#g6-memory-locking--mlockall)

---

# E. Linux user-space the project uses

## E1. POSIX threads (pthreads)

**Layman.** A thread is "another flow of execution inside the same program," sharing memory
with the rest of the program. `pthread_create` starts one; `pthread_join` waits for it to
finish. Threads are cheap compared to processes, and they share the heap, so you don't pay
to copy data between them — but that's also why you need locks.

**In this project.** Every PHY channel gets its own thread: sync, PDCCH, PDSCH, L1C, ULCOMP.
The repo does not call `pthread_create` from random places — there is one wrapper layer
(`WRP_Task_init`) that creates threads with the right priority, stack size, scheduling policy,
and CPU affinity all in one call. Read the wrapper if you want to understand what knobs the
project exposes; read pthreads man pages to understand each knob individually.

**Minimal example.**
```c
#include <pthread.h>
#include <stdio.h>

void *worker(void *arg) {
    int id = *(int *)arg;
    printf("hello from thread %d\n", id);
    return NULL;
}

int main(void) {
    pthread_t t;
    int id = 42;
    pthread_create(&t, NULL, worker, &id);
    pthread_join(t, NULL);
    return 0;
}
/* compile: gcc -pthread t.c -o t */
```

**In tree.**
- The wrapper that all PHY threads go through:
  [lib/os/linux/osal/src/wrp_task.c:387](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_task.c#L387)
  — note how this single call sets attributes, priority, policy, affinity, then
  finally `pthread_create`.
- A simpler raw wrapper (no message-queue layer) used in test code:
  [lib/mt/mt_task.c:65](/home/cb24/workspace/nr_ue_phy/lib/mt/mt_task.c#L65)
- Where threads are actually launched per channel: see the `g_SKL_gNB_contextArray`
  table in [toplevel/phy/phy_skeleton.c:114](/home/cb24/workspace/nr_ue_phy/toplevel/phy/phy_skeleton.c#L114)
  — every entry becomes one running thread.

---

## E2. Mutexes (mutual exclusion)

**Layman.** A lock that exactly one thread can hold at a time. While Thread A holds the
mutex, Thread B that calls `pthread_mutex_lock` on the same mutex blocks until A releases
it. Use it whenever two threads might touch the same memory and at least one is writing.

**In this project.** The repo wraps mutexes in `WRP_MUTEX_*`. Important quirk: the wrapper
defaults to **recursive mutexes** (`PTHREAD_MUTEX_RECURSIVE`) — the same thread can lock
twice and must unlock twice. That's friendlier when functions call each other, slower than
plain mutexes. Mutexes mostly protect the message-queue internals (every subqueue has a
mutex protecting its enqueue path).

**Minimal example.**
```
#include <pthread.h>
#include <stdio.h>

static long counter = 0;
static pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

void *bump(void *_) {
    for (int i = 0; i < 100000; i++) {
        pthread_mutex_lock(&lock);
        counter++; // atomic_fetch_add(&counter, 1); // atomic int counter = 0;
        pthread_mutex_unlock(&lock);
    }
    return NULL;
}

int main(void) {
    pthread_t a, b;
    pthread_create(&a, NULL, bump, NULL);
    pthread_create(&b, NULL, bump, NULL);
    pthread_join(a, NULL);
    pthread_join(b, NULL);
    printf("counter = %ld\n", counter);   /* 200000 */
}
```

**In tree.**
- Wrapper `init` that sets the recursive attribute:
  [lib/os/linux/osal/src/wrp_mutex.c:96](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_mutex.c#L96)
- Lock / unlock used to guard a shared subqueue around an enqueue:
  [lib/os/linux/osal/src/wrp_message_queue.c:458-483](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_message_queue.c#L458-L483)

---

## E3. Condition variables

**Layman.** A "wait until something is true" primitive. You hold a mutex, check a condition,
and if it's not true you `pthread_cond_wait` — the kernel atomically unlocks the mutex and
puts you to sleep. Another thread that changes the state calls `pthread_cond_signal` to wake
you. Always re-check the condition after waking up (spurious wakeups exist).

**In this project.** Used inside the wrapper to implement `WRP_Task_suspend` /
`WRP_Task_resume` — a classic "block this thread until somebody else nudges it." Most
real PHY work doesn't use condvars directly; it uses semaphores instead (see E4) because
semaphores compose better with the message-queue model.

**Minimal example.**
```c
#include <pthread.h>
#include <stdio.h>

static pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t  c = PTHREAD_COND_INITIALIZER;
static int ready = 0;

void *consumer(void *_) {
    pthread_mutex_lock(&m);
    while (!ready)                  /* re-check; protect against spurious wake */
        pthread_cond_wait(&c, &m);
    printf("got it\n");
    pthread_mutex_unlock(&m);
    return NULL;
}

int main(void) {
    pthread_t t;
    pthread_create(&t, NULL, consumer, NULL);
    sleep(1);

    pthread_mutex_lock(&m);
    ready = 1;
    pthread_cond_signal(&c);
    pthread_mutex_unlock(&m);

    pthread_join(t, NULL);
}
```

**In tree.**
- The wrapper's suspend/resume pair — textbook condvar usage:
  [lib/os/linux/osal/src/wrp_task.c:543](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_task.c#L543)
  and [lib/os/linux/osal/src/wrp_task.c:579](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_task.c#L579)

---

## E4. POSIX semaphores

**Layman.** A counter you can `wait` on (decrement, blocks if zero) and `post` to (increment,
wakes one waiter). Use it as "I have N items available — readers, please consume." Unlike a
mutex, a semaphore can be signalled by a different thread than the one that's waiting, and
its count can mean "items pending."

**In this project.** Each task that owns a message queue also owns a semaphore. Sending a
message to that task increments the semaphore (`sem_post`); the task's main loop sits on
`sem_wait`, waking up exactly when work has arrived. This is the heart of the ICM dispatch
loop — "block until the next ICM message lands."

**Minimal example.**
```c
#include <semaphore.h>
#include <pthread.h>
#include <stdio.h>

static sem_t s;

void *worker(void *_) {
    sem_wait(&s);                  /* sleep until count > 0 */
    printf("woken\n");
    return NULL;
}

int main(void) {
    pthread_t t;
    sem_init(&s, 0, 0);            /* unshared, initial count = 0 */
    pthread_create(&t, NULL, worker, NULL);
    sleep(1);
    sem_post(&s);                  /* count -> 1, wakes worker */
    pthread_join(t, NULL);
    sem_destroy(&s);
}
```

**In tree.**
- Wrapper init using `sem_init`:
  [lib/os/linux/osal/src/wrp_semaphore.c:117](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_semaphore.c#L117)
- Where the message-queue layer posts on send and waits on receive:
  [lib/os/linux/osal/src/wrp_message_queue.c:301](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_message_queue.c#L301) (post) and
  [lib/os/linux/osal/src/wrp_message_queue.c:429](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_message_queue.c#L429) (wait).

---

## E5. Message queues (the project's own — not POSIX `mqueue`)

**Layman.** A FIFO of pointers between threads. The producer drops a pointer in, the
consumer pulls it out and processes it. POSIX has its own `mq_*` API (see `man mq_open`),
but this project does **not** use it — too generic, too slow, byte-oriented. It rolls its
own.

**In this project.** `WRP_MsgQueue` is a multi-subqueue structure: one queue per task, but
inside that queue there are several **subqueues** (e.g. high-priority control, normal data,
non-RT). Each task has a fixed serving order with quanta — process N from subqueue A,
then M from subqueue B, etc. When you `WRP_MsgQueue_sendMessage`, you pick which subqueue;
when the task receives, the dispatch order is decided by the priority list. This is how the
PHY guarantees control messages get serviced even under heavy data load.

**Minimal example (just the idea — circular FIFO of pointers, mutex + sem).**
```c
typedef struct {
    void *items[64];
    int   head, tail;
    pthread_mutex_t lock;
    sem_t           pending;
} mq_t;

void mq_init(mq_t *q) {
    q->head = q->tail = 0;
    pthread_mutex_init(&q->lock, NULL);
    sem_init(&q->pending, 0, 0);
}

int mq_send(mq_t *q, void *p) {
    pthread_mutex_lock(&q->lock);
    int next = (q->head + 1) % 64;
    if (next == q->tail) { pthread_mutex_unlock(&q->lock); return -1; } /* full */
    q->items[q->head] = p;
    q->head = next;
    pthread_mutex_unlock(&q->lock);
    sem_post(&q->pending);
    return 0;
}

void *mq_recv(mq_t *q) {                 /* blocking */
    sem_wait(&q->pending);
    pthread_mutex_lock(&q->lock);
    void *p = q->items[q->tail];
    q->tail = (q->tail + 1) % 64;
    pthread_mutex_unlock(&q->lock);
    return p;
}
```

**In tree.**
- The full implementation — read it once, top to bottom, it's only 550 lines:
  [lib/os/linux/osal/src/wrp_message_queue.c](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_message_queue.c)
- How a PHY thread declares its subqueues (note the names — `FRAME_HANDLER_*`):
  [toplevel/phy/phy_skeleton.c:127-138](/home/cb24/workspace/nr_ue_phy/toplevel/phy/phy_skeleton.c#L127-L138)

---

## E6. Sockets — AF_UNIX and AF_INET

**Layman.** A socket is a bidirectional byte (or message) channel between two processes,
or two machines. `AF_UNIX` sockets live as files on disk and are how processes on the same
host talk fastest; `AF_INET` sockets are TCP/UDP over IP. UDP is connectionless ("send a
packet"); TCP is a stream.

**In this project.** The PHY (uephy binary) talks to the upper-layer MAC emulator (macemu)
over sockets. PDCCH for example sends DCI indications via `WRP_Socket_udpSendTo` to the
PAL/PLM layer. Wireshark traces are written by the same code path so you can replay or
inspect interactions. The wrapper file `wrp_sockets.c` adds a multi-message send path
(`sendmmsg`) for batched UDP — sending one syscall per slot is too slow.

**Minimal UDP example.**
```c
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>

int main(void) {
    int s = socket(AF_INET, SOCK_DGRAM, 0);

    struct sockaddr_in dst = {0};
    dst.sin_family = AF_INET;
    dst.sin_port   = htons(9000);
    inet_pton(AF_INET, "127.0.0.1", &dst.sin_addr);

    const char *msg = "hello";
    sendto(s, msg, strlen(msg), 0, (struct sockaddr *)&dst, sizeof(dst));
    close(s);
}
```
On the receiver side: `socket`, `bind`, `recvfrom`. Try it on the RPi against `nc -u -l 9000`.

**In tree.**
- Wrapper file (open it once, skim — handles UDP, TCP, multi-message, broadcast):
  [lib/os/linux/osal/src/wrp_sockets.c](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_sockets.c)
- Real PHY use — PDCCH sends DCI indications to MAC over UDP:
  [toplevel/phy/trd_pdcch.c:102-111](/home/cb24/workspace/nr_ue_phy/toplevel/phy/trd_pdcch.c#L102-L111)

---

## E7. File descriptors and epoll

**Layman.** In Linux, *almost everything* — files, sockets, pipes, timers, signals, even
some hardware — is accessed through a small integer called a file descriptor. `epoll` is
the modern way to wait for *many* file descriptors at once efficiently. You add the FDs
you care about, then call `epoll_wait` and the kernel hands back exactly the ones that are
ready. It scales to thousands of FDs without the O(N) cost of `select`.

**In this project.** `WRP_Socket_*` exposes `epoll_create`/`epoll_ctl`/`epoll_wait` to the
sockets layer; the IF threads (e.g. `trd_ctrl`, `trd_aif`, `trd_nmm_if`) use this to wait
on multiple sockets without spinning a thread per socket. Less central than mutex/semaphore
in the PHY data path but unavoidable in the IF/MAC-emulator boundary.

**Minimal example.**
```c
#include <sys/epoll.h>
#include <unistd.h>
#include <stdio.h>

int main(void) {
    int ep = epoll_create1(0);

    struct epoll_event ev = { .events = EPOLLIN, .data.fd = 0 };  /* watch stdin */
    epoll_ctl(ep, EPOLL_CTL_ADD, 0, &ev);

    struct epoll_event got;
    while (1) {
        int n = epoll_wait(ep, &got, 1, -1);   /* block forever */
        if (n > 0) {
            char c;
            read(got.data.fd, &c, 1);
            printf("got byte 0x%02x\n", c);
        }
    }
}
```
Type characters; each one wakes `epoll_wait`.

**In tree.**
- Search the sockets wrapper for `epoll`:
  ```bash
  grep -n "epoll" lib/os/linux/osal/src/wrp_sockets.c
  ```

---

## E8. Signals

**Layman.** A signal is an asynchronous notification delivered by the kernel to a process —
`SIGINT` (ctrl-C), `SIGTERM` (please exit), `SIGSEGV` (you dereferenced bad memory), etc.
You can register a handler with `sigaction`. Inside a handler you can do almost nothing
safely (only async-signal-safe functions). The standard pattern in multithreaded code is to
**block** signals in worker threads and dedicate one thread (or `signalfd`) to receive them.

**In this project.** All worker threads block almost every signal at start-up via
`pthread_sigmask`, exactly so signals aren't delivered to data-path threads. There is also
a project-wide `WRP_Task_setupSignals` that installs a generic handler — this is what
catches segfaults, prints a stack, and exits cleanly.

**Minimal example.**
```c
#include <signal.h>
#include <stdio.h>
#include <unistd.h>

void on_sigint(int sig) { (void)sig; write(1, "bye\n", 4); _exit(0); }

int main(void) {
    struct sigaction sa = { .sa_handler = on_sigint };
    sigemptyset(&sa.sa_mask);
    sigaction(SIGINT, &sa, NULL);

    while (1) pause();              /* block until any signal */
}
```

**In tree.**
- Worker threads block signals at the very start of their entry point:
  [lib/os/linux/osal/src/wrp_task.c:99-121](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_task.c#L99-L121)
- Process-wide signal handler installation:
  [lib/os/linux/osal/src/wrp_task.c:808](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_task.c#L808)

---

## E9. Process model — fork/exec/exit

**Layman.** `fork()` clones the current process into a parent and a child; the child gets
a copy of all memory (copy-on-write). `exec*()` replaces the current process image with a
new program — typical pattern: parent forks, child immediately execs the program it wanted
to run. `exit()` ends the process; the parent collects the exit code with `wait`.

**In this project.** Mostly *not* used inside `nr_ue_phy` itself — the PHY is a single
multi-threaded process. Where you'll see fork/exec is around it: launch scripts, the Python
test harness in `scripts/test/submodule/x86_emulation/`, and the macemu launcher. Useful
to understand because the operational picture is "two processes (uephy + macemu) talking
over sockets," and that's a fork/exec story even if you never call those functions yourself.

**Minimal example.**
```c
#include <unistd.h>
#include <sys/wait.h>
#include <stdio.h>

int main(void) {
    pid_t pid = fork();
    if (pid == 0) {                              /* child */
        execlp("ls", "ls", "-l", (char *)NULL);
        _exit(127);                              /* only reached if exec fails */
    }
    int status;
    waitpid(pid, &status, 0);
    printf("child exited: %d\n", WEXITSTATUS(status));
}
```

**In tree.** No direct usage in PHY code; look at `scripts/` Python where the test harness
spawns subprocesses, or `build_x86_and_run_phy_macemu.sh` to see the operational layout.

---

# F. Multi-threading patterns specific to this repo

## F1. One-thread-per-channel

**Layman.** Rather than one thread that does "everything for the next slot in sequence,"
you assign each PHY channel its own thread (or small set). Each thread owns its state,
keeps its data hot in its core's caches, and processes a stream of messages.

**In this project.** Five main PHY threads:
- `trd_sync` — cell search, PSS/SSS/PBCH (synchronisation)
- `trd_pdcch` — control channel blind decoding
- `trd_pdsch` — shared data channel (downlink data)
- `trd_l1c` — Layer-1 control / coordination
- `trd_ulcomp` — uplink composition

Plus IF/control threads (`trd_ctrl`, `trd_aif`, `trd_armm_ind`, `trd_nmm_if`) and DFE-side
threads (`trd_slotInd`, `trd_vspaMsgHndlr`, `trd_rmtCmdHndlr`). They communicate **only**
through ICM message queues — no shared globals on the data path.

The reason this design is right: a slot is 1 ms (or shorter at higher SCS), and you have to
finish sync → PDCCH-decode → PDSCH-decode within a small budget. Pipelining by channel lets
the slot-N PDSCH thread keep working while the slot-(N+1) sync thread is already doing its
first FFT.

**Minimal example.** Two-stage pipeline using two threads + a queue:
```c
/* producer: receive samples, hand to pdcch thread */
void *t_sync(void *q)  { for(;;) { sample_t *s = capture(); mq_send(q, s); } }
void *t_pdcch(void *q) { for(;;) { sample_t *s = mq_recv(q); decode_dci(s); } }
```

**In tree.**
- Threads as a table — every entry becomes one running thread:
  [toplevel/phy/phy_skeleton.c:114](/home/cb24/workspace/nr_ue_phy/toplevel/phy/phy_skeleton.c#L114)
- A typical thread file showing the message handlers it registers:
  [toplevel/phy/trd_pdcch.c:113](/home/cb24/workspace/nr_ue_phy/toplevel/phy/trd_pdcch.c#L113)

---

## F2. ICM (inter-component messaging)

**Layman.** ICM stands for "inter-component message." Instead of calling a function in
another thread (illegal) or touching its state (dangerous), you **build a message struct**,
pick a recipient, and drop it on its message queue. The recipient's main loop pulls messages
and dispatches each by message-ID to a registered handler function.

**In this project.** Every thread has an ICM file declaring its inbox messages
(`trd_pdcch_icm.h`, `trd_pdsch_icm.h`, etc.). Message IDs are an enum in
`phy_icm_msg_ids.h` (e.g. `INTERCOMP_MSG_ID_PDCCH_DL_CONFIG_REQ`). Each thread registers
handlers via `SKL_MESSAGE_HANDLER_REGISTER(msg_id, handler_fn, ...)` at startup. That is
*all* a thread does in `init`: register, then loop on its queue.

This is the single most important architectural pattern in the codebase. Read three ICM
headers and you understand the whole control flow.

**Minimal example.**
```c
typedef enum { MSG_HELLO, MSG_BYE } msg_id_t;
typedef struct { msg_id_t id; int payload; } msg_t;

static void hello_handler(int payload) { printf("hello %d\n", payload); }
static void bye_handler  (int payload) { printf("bye %d\n",   payload); }

void *worker(void *q) {
    for (;;) {
        msg_t *m = mq_recv(q);
        switch (m->id) {
            case MSG_HELLO: hello_handler(m->payload); break;
            case MSG_BYE:   bye_handler(m->payload);   break;
        }
        free(m);
    }
}
```

**In tree.**
- The big enum of every ICM message id in the system:
  [toplevel/phy/phy_icm_msg_ids.h:20](/home/cb24/workspace/nr_ue_phy/toplevel/phy/phy_icm_msg_ids.h#L20)
- A thread registering its handlers in init:
  [toplevel/phy/trd_pdcch.c:153-156](/home/cb24/workspace/nr_ue_phy/toplevel/phy/trd_pdcch.c#L153-L156)
- A handler being invoked when a message arrives:
  [toplevel/phy/trd_pdcch.c:180](/home/cb24/workspace/nr_ue_phy/toplevel/phy/trd_pdcch.c#L180)

---

## F3. Producer / consumer with bounded queues

**Layman.** A producer puts items into a fixed-size buffer; a consumer takes them out. The
size is bounded so the producer can't overwhelm the consumer — once full, the producer
either drops, blocks, or returns an error. In real-time code you usually **drop or error**:
blocking would extend the producer's deadline.

**In this project.** PDCCH has a small per-channel ring (`PDCCH_RX_Q_MAX_NUM_ELEMENTS = 14`)
that holds DL config requests waiting for baseband data. If it's ever full when DFE delivers
new config, the message is dropped with `KPI_PDCCH_CONFIG_QUEUE_FULL()` so it shows up on
the dashboard — that means the DFE has gotten *ahead* of PDCCH (or PDCCH is too slow). The
ICM queues higher up (`SKL_DATA_HANDLER_TASK_MSG_QUEUE_SIZE = 30`) follow the same rule:
the size is sized to the worst-case slot lead-time, never grown.

**Minimal example.**
```c
#define N 16
static int  buf[N];
static int  head, tail;
static pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;

int try_put(int v) {                 /* drop on full */
    pthread_mutex_lock(&m);
    int next = (head + 1) % N;
    if (next == tail) { pthread_mutex_unlock(&m); return -1; }
    buf[head] = v; head = next;
    pthread_mutex_unlock(&m);
    return 0;
}
```

**In tree.**
- The PDCCH internal queue and its drop-on-full path:
  [toplevel/phy/trd_pdcch.c:36-51](/home/cb24/workspace/nr_ue_phy/toplevel/phy/trd_pdcch.c#L36-L51)
  and
  [toplevel/phy/trd_pdcch.c:182-189](/home/cb24/workspace/nr_ue_phy/toplevel/phy/trd_pdcch.c#L182-L189)

---

## F4. Lock-free vs lock-based

**Layman.** A lock-based queue uses a mutex on every push/pop. A lock-free queue uses atomic
compare-and-swap operations on shared indices, so a thread can never block another. Lock-free
is faster for high-contention single-producer/single-consumer cases and avoids priority
inversion; the price is much harder to reason about (memory ordering, ABA problems).

**In this project.** The `WRP_MsgQueue` distinguishes two enqueue paths:
- `WRP_MsgQueue_enqueueShared` — locks the subqueue's mutex (`WRP_MSG_QUEUE_TYPE_MANY_SENDERS`)
- `WRP_MsgQueue_enqueueNonShared` — no lock, only valid when there is exactly one sender

The total `pendingMessagesCount` is bumped atomically (`WRP_Atomic_IncAndFetch`) on every
send, regardless of which path. Most PHY queues are declared single-sender precisely to
avoid the lock — the design starts from "if only one thread can possibly send to this
subqueue, don't take a lock at all."

**Minimal example — atomic counter (no lock).**
```c
#include <stdatomic.h>
static _Atomic int counter = 0;
/* on a hot path */
atomic_fetch_add_explicit(&counter, 1, memory_order_relaxed);
```

**In tree.**
- The two enqueue paths side by side:
  [lib/os/linux/osal/src/wrp_message_queue.c:447](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_message_queue.c#L447) (shared, locked)
  and
  [lib/os/linux/osal/src/wrp_message_queue.c:499](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_message_queue.c#L499) (non-shared, lock-free)
- Single-sender vs many-sender decision happens at queue init time:
  [lib/os/linux/osal/src/wrp_message_queue.c:169-179](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_message_queue.c#L169-L179)

---

## F5. Real-time scheduling — SCHED_FIFO and priorities

**Layman.** Linux has two real-time scheduler classes: `SCHED_FIFO` and `SCHED_RR`. With
`SCHED_FIFO`, a thread runs until it blocks or until a higher-priority RT thread becomes
runnable — there is *no* time-slicing within a priority. Priority is 1..99; higher number
wins. The default `SCHED_OTHER` (also called CFS) is fairness-oriented and *will* preempt
your work for completely unrelated processes. PHY threads cannot tolerate that.

**In this project.** The wrapper sets all PHY threads to `SCHED_FIFO` and assigns priority
in the range 80..95 (16 priority levels mapped to RT priorities 80–95) — see
`taskScedParam.sched_priority = 80 + (15 - prio)` at
[lib/os/linux/osal/src/wrp_task.c:370-372](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_task.c#L370-L372).
The build can opt out of RT (`-DNO_REALTIME`) for unit-test runs on dev machines without
RT capabilities, but production runs all use FIFO.

**Minimal example.**
```c
#include <pthread.h>
#include <sched.h>

void make_rt(pthread_attr_t *a, int prio) {
    pthread_attr_init(a);
    pthread_attr_setinheritsched(a, PTHREAD_EXPLICIT_SCHED);  /* don't inherit OTHER */
    pthread_attr_setschedpolicy (a, SCHED_FIFO);
    struct sched_param p = { .sched_priority = prio };        /* 1..99 */
    pthread_attr_setschedparam  (a, &p);
}
```
Note: setting RT priority requires `CAP_SYS_NICE` (or running as root, or
`/etc/security/limits.conf` rules). On RPi: `sudo` your binary or set capabilities.

**In tree.**
- PHY task config:
  [lib/os/linux/osal/src/wrp_task.c:355](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_task.c#L355)
- Test-utility wrapper (currently FIFO disabled with `#if 0` for portability):
  [lib/mt/mt_task.c:43-56](/home/cb24/workspace/nr_ue_phy/lib/mt/mt_task.c#L43-L56)

---

## F6. CPU affinity / pinning

**Layman.** A CPU affinity mask tells the kernel "this thread is only allowed to run on
these specific cores." Pinning a thread:
1. Keeps its caches hot (no migration cost)
2. Stops two heavy threads from fighting over the same core
3. Lets you keep specific cores clean for the most critical work

**In this project.** Each PHY thread has an affinity field (`SKL_*_TASK_AFFINITY`) in the
context array. The wrapper sets `cpu_set_t` and calls `pthread_setaffinity_np`. Combined
with kernel-cmdline `isolcpus=` (see G3), this is how the PHY guarantees a core that the
rest of Linux never touches.

**Minimal example.**
```c
#include <pthread.h>
#define _GNU_SOURCE
#include <sched.h>

void pin_self_to(int core) {
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(core, &set);
    pthread_setaffinity_np(pthread_self(), sizeof(set), &set);
}
```
Verify on RPi with `taskset -pc <pid>`.

**In tree.**
- Affinity applied during task init:
  [lib/os/linux/osal/src/wrp_task.c:410-422](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_task.c#L410-L422)
- Same pattern in the simpler test wrapper:
  [lib/mt/mt_task.c:58-66](/home/cb24/workspace/nr_ue_phy/lib/mt/mt_task.c#L58-L66)

---

# G. Real-time on Linux

## G1. Why stock Linux is not real-time

**Layman.** "Real-time" doesn't mean "fast" — it means "responds within a guaranteed bound."
Stock Linux makes no such guarantee. Reasons:
- The kernel is preemptible, but big sections (long syscalls, IRQ handlers, `BKL`-style
  paths) used to run with preemption disabled. Even on a modern kernel, NMI/IPIs and some
  driver paths block preemption briefly.
- Page faults: if your code touches an un-paged page, the kernel must do disk I/O.
- TLB shootdowns, RCU grace periods, scheduler ticks, etc. — all measurable as jitter.

For a PHY processing a 1 ms slot, "average latency 100 µs" isn't acceptable. We need
"99.999% of slots under 200 µs." That's the whole point of switching to RT.

**In this project.** The build is intended to run on a kernel that has been tuned for
real-time (PREEMPT_RT, isolated cores, locked-down NIC IRQs). The `-DNO_REALTIME` build
flag exists for cases where you can't do that — e.g. running unit tests on a developer
laptop — and it explicitly skips `SCHED_FIFO` setup and `mlockall`.

**Reading.** kernel.org's *Real-Time Linux Wiki*; LWN article series on PREEMPT_RT.

---

## G2. PREEMPT_RT

**Layman.** A long-running patch series (recently merged upstream, but historically external)
that turns most spinlocks into priority-inheritance mutexes, makes interrupt handlers run
in preemptible kthreads, and shrinks the regions where preemption is disabled. Net effect:
worst-case scheduling latency on commodity hardware drops from milliseconds to hundreds of
microseconds.

**In this project.** The deployed StarTag platform uses an RT-patched kernel (the BSP comes
with one). On your RPi you can install `linux-image-rt-*` from Debian/RPiOS repos and boot
into it — `uname -a` should mention `PREEMPT_RT`. Then `cyclictest` is the first thing to
run.

**Try on RPi.**
```bash
sudo apt install rt-tests
sudo cyclictest -t1 -p99 -i1000 -l100000   # 100k samples, 1 ms period, prio 99
```
Look at the maximum latency reported. On a stock Linux kernel: a few hundred µs to several
ms. On PREEMPT_RT and an isolated core: tens of µs.

**In tree.**
- The `NO_REALTIME` build flag — search to see what's gated on RT:
  ```bash
  grep -rn "NO_REALTIME" lib/ src/ toplevel/
  ```

---

## G3. CPU isolation, IRQ affinity, NUMA

**Layman.**
- **`isolcpus=N,M`** in the kernel cmdline removes those cores from the scheduler's normal
  pool. Nothing runs there unless you explicitly pin it (see F6).
- **IRQ affinity** controls which cores receive hardware interrupts. By default, all cores
  may. You'd rather keep IRQs *off* the cores running PHY data — they cause cache pollution
  and preemption.
- **NUMA** (Non-Uniform Memory Access): on multi-socket boxes, RAM attached to socket 0 is
  fast for cores on socket 0, slow for cores on socket 1. Pin both the thread *and* its
  memory to the same node.

**In this project.** This is **deployment configuration**, not code. The PHY application
requires:
- `isolcpus=2,3,4,5` (typical for a 6-core box keeping cores 0–1 for OS)
- IRQs steered off the isolated cores via `/proc/irq/<n>/smp_affinity`
- On NUMA boxes, `numactl --cpunodebind=0 --membind=0 ./uephy ...`

The thread-affinity numbers in `phy_skeleton.c` assume specific cores are isolated. If you
boot without isolation, the threads still pin themselves but Linux will schedule unrelated
work on those cores too.

**Try on RPi.**
```bash
cat /proc/cmdline                          # check current kernel cmdline
sudo cat /proc/irq/24/smp_affinity         # default IRQ mask for IRQ 24
sudo bash -c 'echo 1 > /proc/irq/24/smp_affinity'   # restrict to core 0 only
```

**In tree.** Look at the `SKL_*_TASK_AFFINITY` macros referenced from
[toplevel/phy/phy_skeleton.c:151](/home/cb24/workspace/nr_ue_phy/toplevel/phy/phy_skeleton.c#L151)
and trace them to the per-platform config files under `toplevel/phy/config/`.

---

## G4. Monotonic clocks and TSC

**Layman.**
- `gettimeofday()` and `CLOCK_REALTIME` give wall-clock time, which can **jump backwards**
  if NTP corrects the clock. **Never use it for measuring durations.**
- `clock_gettime(CLOCK_MONOTONIC, ...)` is the right answer: never goes backwards, ticks at
  ns resolution, fast (vDSO).
- `RDTSC` reads the CPU's timestamp counter directly — sub-nanosecond resolution but you
  must know the TSC frequency, and on multi-socket boxes TSCs may not be synchronised.
  Use it only for tight micro-benchmarks, not for slot timing.

**In this project.** The PHY uses `clock_gettime(CLOCK_MONOTONIC, ...)` everywhere it needs
to measure: DFE buffer allocation timestamps, RX-path latency, equalizer benchmark timing
in test code. There is no use of `RDTSC` directly in PHY code.

**Minimal example.**
```c
#include <time.h>
#include <stdio.h>

int main(void) {
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    /* work */
    clock_gettime(CLOCK_MONOTONIC, &t1);
    long ns = (t1.tv_sec - t0.tv_sec) * 1000000000L + (t1.tv_nsec - t0.tv_nsec);
    printf("%ld ns\n", ns);
}
```

**In tree.**
- Equalizer timing harness:
  [testcases/components/equalizer/main.c:477](/home/cb24/workspace/nr_ue_phy/testcases/components/equalizer/main.c#L477)
- DFE RX-path timestamping:
  [toplevel/phy/dfe_if/9310/dfe_if_rx.c:218](/home/cb24/workspace/nr_ue_phy/toplevel/phy/dfe_if/9310/dfe_if_rx.c#L218)
- A helper that diffs two `CLOCK_MONOTONIC` timespecs:
  [testcases/components/test_helpers/test_helpers.h:95](/home/cb24/workspace/nr_ue_phy/testcases/components/test_helpers/test_helpers.h#L95)

---

## G5. Watching for jitter — cyclictest, ftrace, perf sched

**Layman.**
- **`cyclictest`** sleeps for a fixed period in a tight loop and measures how late it wakes
  up. The maximum latency over hours of running is the system's worst-case scheduling
  jitter. The number to brag about is "max latency under load."
- **`ftrace`** is the kernel's built-in tracer. Two killer reports:
  - `wakeup_rt`: time from "RT thread becomes runnable" to "RT thread runs." Should be µs.
  - `irqsoff`: longest stretch with interrupts disabled. Should be very short.
- **`perf sched`** records every context switch and tells you who preempted whom and for
  how long. Great when you're chasing "thread X ran late by 80 µs in slot 1234" — perf
  shows you it was preempted by kworker/3.

**In this project.** Not built-in to the codebase — these are external tools you run when
investigating jitter. The `KPI_*` macros (e.g. `KPI_PDCCH_CONFIG_QUEUE_FULL()`) are the
in-app symptom; ftrace/perf are how you find the root cause when those KPIs fire.

**Try on RPi.**
```bash
# generate background load to make jitter visible
sudo apt install stress-ng
stress-ng --cpu 4 --io 2 &
sudo cyclictest -t4 -p90 -i1000 -l60000   # ~1 minute, 4 RT threads
```
Compare max latency with and without the load. With `isolcpus` and `SCHED_FIFO` it should
barely move.

---

## G6. Memory locking — `mlockall`

**Layman.** Linux can swap any of your process's pages out to disk if it thinks the memory
is needed elsewhere. Touching a swapped-out page costs **milliseconds** while the kernel
pages it back. Call `mlockall(MCL_CURRENT | MCL_FUTURE)` and the kernel pins all your
process's pages in RAM — current pages and any allocated later. Combined with no-overcommit
and pre-fault-on-startup, you get bounded memory access time.

**In this project.** The wrapper calls `mlockall` exactly once, at signal-handler setup
time, and only when RT is enabled:
[lib/os/linux/osal/src/wrp_task.c:838-843](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_task.c#L838-L843).
Without this, the very first page fault into a fresh memory pool would create a slot-time
spike at startup. With it, you may see "mlockall failed" warnings if the binary lacks
`CAP_IPC_LOCK` — fix with `setcap cap_ipc_lock+ep ./uephy` or `sudo`.

**Minimal example.**
```c
#include <sys/mman.h>
#include <stdio.h>

int main(void) {
    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("mlockall");
        return 1;
    }
    /* now no page in this process can be swapped out */
}
```

**In tree.**
- The single call site:
  [lib/os/linux/osal/src/wrp_task.c:839](/home/cb24/workspace/nr_ue_phy/lib/os/linux/osal/src/wrp_task.c#L839)

---

# Suggested order of attack

Pick a topic, read the layman + project sections, compile the minimal example on your RPi,
then read the in-tree code with the file:line reference open. The whole E+F+G section,
worked end-to-end this way, is a solid 2-3 weeks of focused study.

1. **E1, E2, E4** (threads + mutex + semaphore) — without these E5/F2 are unreadable.
2. **E5 + F2** (message queues + ICM) — the heart of the runtime.
3. **F1 + F3 + F4** (one-thread-per-channel, bounded queues, lock-free) — design rationale.
4. **F5 + F6** (`SCHED_FIFO`, affinity) — what the wrapper actually does.
5. **G1 + G2** (why stock Linux isn't RT, PREEMPT_RT) — context, then run cyclictest.
6. **G3 + G6** (isolcpus, mlockall) — how production deployments are tuned.
7. **G4 + G5** (monotonic clocks, ftrace/perf) — comes naturally when you start measuring.

Optional: **E6, E7, E8, E9** (sockets, epoll, signals, fork/exec) — useful for the
PHY/MAC-emulator boundary but not on the slot critical path.
