#include <stdio.h>
#include <stdlib.h>

// ─────────────────────────────────────────
// METHOD 1: Simple Array Queue
// ─────────────────────────────────────────
// Problem: front keeps moving right, wasting space

#define MAX 5

struct ArrayQueue {
    int data[MAX];
    int front, rear;
};

void initArrayQueue(struct ArrayQueue *q) {
    q->front = -1;
    q->rear  = -1;
}

int isFullArray(struct ArrayQueue *q)  { return q->rear == MAX - 1; }
int isEmptyArray(struct ArrayQueue *q) { return q->front == -1; }

void enqueueArray(struct ArrayQueue *q, int val) {
    if (isFullArray(q)) { printf("Queue Full!\n"); return; }
    if (q->front == -1) q->front = 0; // first element
    q->data[++(q->rear)] = val;
    printf("Enqueued %d\n", val);
}

int dequeueArray(struct ArrayQueue *q) {
    if (isEmptyArray(q)) { printf("Queue Empty!\n"); return -1; }
    int val = q->data[q->front++]; // return front, move front right
    if (q->front > q->rear) initArrayQueue(q); // reset if empty
    return val;
}

void printArrayQueue(struct ArrayQueue *q) {
    if (isEmptyArray(q)) { printf("Queue is empty!\n"); return; }
    printf("Queue (front -> rear): ");
    for (int i = q->front; i <= q->rear; i++)
        printf("[%d] ", q->data[i]);
    printf("\n");
}

// ─────────────────────────────────────────
// METHOD 2: Circular Queue (smarter array)
// ─────────────────────────────────────────
// Reuses freed-up slots at the front using modulo (%)

struct CircularQueue {
    int data[MAX];
    int front, rear, size;
};

void initCircular(struct CircularQueue *q) {
    q->front = 0;
    q->rear  = -1;
    q->size  = 0;
}

int isFullCircular(struct CircularQueue *q)  { return q->size == MAX; }
int isEmptyCircular(struct CircularQueue *q) { return q->size == 0; }

void enqueueCircular(struct CircularQueue *q, int val) {
    if (isFullCircular(q)) { printf("Queue Full!\n"); return; }
    q->rear = (q->rear + 1) % MAX; // wrap around using modulo
    q->data[q->rear] = val;
    q->size++;
    printf("Enqueued %d\n", val);
}

int dequeueCircular(struct CircularQueue *q) {
    if (isEmptyCircular(q)) { printf("Queue Empty!\n"); return -1; }
    int val = q->data[q->front];
    q->front = (q->front + 1) % MAX; // wrap around using modulo
    q->size--;
    return val;
}

void printCircularQueue(struct CircularQueue *q) {
    if (isEmptyCircular(q)) { printf("Queue is empty!\n"); return; }
    printf("Circular Queue (front -> rear): ");
    for (int i = 0; i < q->size; i++)
        printf("[%d] ", q->data[(q->front + i) % MAX]);
    printf("\n");
}

// ─────────────────────────────────────────
// METHOD 3: Linked List Queue
// ─────────────────────────────────────────
// No size limit, grows dynamically

struct Node {
    int data;
    struct Node *next;
};

struct LinkedQueue {
    struct Node *front, *rear;
};

void initLinkedQueue(struct LinkedQueue *q) {
    q->front = q->rear = NULL;
}

void enqueueLinked(struct LinkedQueue *q, int val) {
    struct Node *newNode = (struct Node*)malloc(sizeof(struct Node));
    newNode->data = val;
    newNode->next = NULL;
    if (q->rear == NULL) {          // empty queue
        q->front = q->rear = newNode;
    } else {
        q->rear->next = newNode;    // link new node at rear
        q->rear = newNode;          // update rear
    }
    printf("Enqueued %d\n", val);
}

int dequeueLinked(struct LinkedQueue *q) {
    if (q->front == NULL) { printf("Queue Empty!\n"); return -1; }
    struct Node *temp = q->front;
    int val = temp->data;
    q->front = q->front->next;      // move front forward
    if (q->front == NULL)           // if queue is now empty
        q->rear = NULL;             // reset rear too
    free(temp);
    return val;
}

void printLinkedQueue(struct LinkedQueue *q) {
    if (q->front == NULL) { printf("Queue is empty!\n"); return; }
    printf("Queue (front -> rear): ");
    struct Node *temp = q->front;
    while (temp != NULL) {
        printf("[%d] ", temp->data);
        temp = temp->next;
    }
    printf("\n");
}

// ─────────────────────────────────────────
// MAIN
// ─────────────────────────────────────────

int main() {
    // --- Simple Array Queue ---
    printf("=== Simple Array Queue ===\n");
    struct ArrayQueue aq;
    initArrayQueue(&aq);
    enqueueArray(&aq, 10);
    enqueueArray(&aq, 20);
    enqueueArray(&aq, 30);
    printArrayQueue(&aq);
    printf("Dequeued: %d\n", dequeueArray(&aq));
    printArrayQueue(&aq);

    // --- Circular Queue ---
    printf("\n=== Circular Queue ===\n");
    struct CircularQueue cq;
    initCircular(&cq);
    enqueueCircular(&cq, 10);
    enqueueCircular(&cq, 20);
    enqueueCircular(&cq, 30);
    printCircularQueue(&cq);
    printf("Dequeued: %d\n", dequeueCircular(&cq));
    enqueueCircular(&cq, 40); // reuses the freed slot!
    printCircularQueue(&cq);

    // --- Linked List Queue ---
    printf("\n=== Linked List Queue ===\n");
    struct LinkedQueue lq;
    initLinkedQueue(&lq);
    enqueueLinked(&lq, 10);
    enqueueLinked(&lq, 20);
    enqueueLinked(&lq, 30);
    printLinkedQueue(&lq);
    printf("Dequeued: %d\n", dequeueLinked(&lq));
    printLinkedQueue(&lq);

    return 0;
}
