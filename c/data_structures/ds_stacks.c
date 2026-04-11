#include <stdio.h>
#include <stdlib.h>

// ─────────────────────────────────────────
// METHOD 1: Stack using Array
// ─────────────────────────────────────────

#define MAX 5

struct ArrayStack {
    int data[MAX];
    int top; // index of the topmost element
};

void initArrayStack(struct ArrayStack *s) {
    s->top = -1; // -1 means empty
}

int isFullArray(struct ArrayStack *s)  { return s->top == MAX - 1; }
int isEmptyArray(struct ArrayStack *s) { return s->top == -1; }

void pushArray(struct ArrayStack *s, int value) {
    if (isFullArray(s)) { printf("Stack Overflow!\n"); return; }
    s->data[++(s->top)] = value; // increment top, then insert
    printf("Pushed %d\n", value);
}

int popArray(struct ArrayStack *s) {
    if (isEmptyArray(s)) { printf("Stack Underflow!\n"); return -1; }
    return s->data[(s->top)--]; // return top, then decrement
}

int peekArray(struct ArrayStack *s) {
    if (isEmptyArray(s)) { printf("Stack is empty!\n"); return -1; }
    return s->data[s->top];
}

void printArrayStack(struct ArrayStack *s) {
    if (isEmptyArray(s)) { printf("Stack is empty!\n"); return; }
    printf("Stack (top -> bottom): ");
    for (int i = s->top; i >= 0; i--)
        printf("[%d] ", s->data[i]);
    printf("\n");
}

// ─────────────────────────────────────────
// METHOD 2: Stack using Linked List
// ─────────────────────────────────────────

struct Node {
    int data;
    struct Node *next;
};

// The top of stack = head of linked list
void pushLinked(struct Node **top, int value) {
    struct Node *newNode = (struct Node*)malloc(sizeof(struct Node));
    newNode->data = value;
    newNode->next = *top; // new node points to old top
    *top = newNode;       // update top
    printf("Pushed %d\n", value);
}

int popLinked(struct Node **top) {
    if (*top == NULL) { printf("Stack Underflow!\n"); return -1; }
    struct Node *temp = *top;
    int val = temp->data;
    *top = (*top)->next; // move top down
    free(temp);
    return val;
}

int peekLinked(struct Node *top) {
    if (top == NULL) { printf("Stack is empty!\n"); return -1; }
    return top->data;
}

void printLinkedStack(struct Node *top) {
    if (top == NULL) { printf("Stack is empty!\n"); return; }
    printf("Stack (top -> bottom): ");
    struct Node *temp = top;
    while (temp != NULL) {
        printf("[%d] ", temp->data);
        temp = temp->next;
    }
    printf("\n");
}

// ─────────────────────────────────────────
// BONUS: Practical use — Balanced Brackets
// ─────────────────────────────────────────

// Check if brackets in a string are balanced using a stack
void checkBrackets(char *expr) {
    char stack[100];
    int top = -1;
    for (int i = 0; expr[i] != '\0'; i++) {
        char c = expr[i];
        if (c == '(' || c == '{' || c == '[')
            stack[++top] = c;          // push opening bracket
        else if (c == ')' || c == '}' || c == ']') {
            if (top == -1) { printf("\"%s\" -> NOT balanced\n", expr); return; }
            char open = stack[top--];  // pop
            if ((c == ')' && open != '(') ||
                (c == '}' && open != '{') ||
                (c == ']' && open != '[')) {
                printf("\"%s\" -> NOT balanced\n", expr);
                return;
            }
        }
    }
    printf("\"%s\" -> %s\n", expr, top == -1 ? "Balanced" : "NOT balanced");
}

// ─────────────────────────────────────────
// MAIN
// ─────────────────────────────────────────

int main() {
    // --- Array Stack ---
    printf("=== Array Stack ===\n");
    struct ArrayStack s;
    initArrayStack(&s);
    pushArray(&s, 10);
    pushArray(&s, 20);
    pushArray(&s, 30);
    printArrayStack(&s);
    printf("Peek: %d\n", peekArray(&s));
    printf("Popped: %d\n", popArray(&s));
    printArrayStack(&s);

    // --- Linked List Stack ---
    printf("\n=== Linked List Stack ===\n");
    struct Node *top = NULL;
    pushLinked(&top, 10);
    pushLinked(&top, 20);
    pushLinked(&top, 30);
    printLinkedStack(top);
    printf("Peek: %d\n", peekLinked(top));
    printf("Popped: %d\n", popLinked(&top));
    printLinkedStack(top);

    // --- Balanced Brackets ---
    printf("\n=== Balanced Bracket Checker ===\n");
    checkBrackets("{[()]}");
    checkBrackets("{[(])}");
    checkBrackets("((()))");
    checkBrackets("((()");

    return 0;
}