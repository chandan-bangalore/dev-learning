#include <stdio.h>
#include <stdlib.h>

// ─────────────────────────────────────────
// Node — now has both prev and next
// ─────────────────────────────────────────
struct Node {
    int data;
    struct Node *prev;
    struct Node *next;
};

// ─────────────────────────────────────────
// Create a new node
// ─────────────────────────────────────────
struct Node* createNode(int val) {
    struct Node *n = (struct Node*)malloc(sizeof(struct Node));
    n->data = val;
    n->prev = NULL;
    n->next = NULL;
    return n;
}

// ─────────────────────────────────────────
// Insert at end
// ─────────────────────────────────────────
void insertEnd(struct Node **head, int val) {
    struct Node *newNode = createNode(val);
    if (*head == NULL) { *head = newNode; return; }
    struct Node *curr = *head;
    while (curr->next != NULL)
        curr = curr->next;
    curr->next = newNode;  // forward link
    newNode->prev = curr;  // backward link  ← extra step vs singly
}

// ─────────────────────────────────────────
// Print forward
// ─────────────────────────────────────────
void printForward(struct Node *head) {
    struct Node *curr = head;
    printf("Forward:  ");
    while (curr != NULL) {
        printf("[%d] -> ", curr->data);
        curr = curr->next;
    }
    printf("NULL\n");
}

// ─────────────────────────────────────────
// Print backward (to verify prev pointers)
// ─────────────────────────────────────────
void printBackward(struct Node *head) {
    if (head == NULL) return;
    struct Node *curr = head;
    while (curr->next != NULL)  // walk to last node
        curr = curr->next;
    printf("Backward: ");
    while (curr != NULL) {
        printf("[%d] -> ", curr->data);
        curr = curr->prev;      // follow prev pointers back
    }
    printf("NULL\n");
}

// ─────────────────────────────────────────
// Reverse — just swap prev and next of every node
// ─────────────────────────────────────────
void reverse(struct Node **head) {
    struct Node *curr = *head;
    struct Node *temp = NULL;

    while (curr != NULL) {
        // swap prev and next pointers of current node
        temp       = curr->prev;
        curr->prev = curr->next;
        curr->next = temp;

        // move to next node (which is curr->prev now, after the swap!)
        curr = curr->prev;
    }

    // update head — temp is the last node we processed
    // before curr became NULL, temp held curr->prev (old prev = new next)
    // so we go back one step
    if (temp != NULL)
        *head = temp->next;
}

// ─────────────────────────────────────────
// MAIN
// ─────────────────────────────────────────
int main() {
    struct Node *head = NULL;

    insertEnd(&head, 10);
    insertEnd(&head, 20);
    insertEnd(&head, 30);
    insertEnd(&head, 40);

    printf("=== Original List ===\n");
    printForward(head);
    printBackward(head);

    printf("\n=== After Reverse ===\n");
    reverse(&head);
    printForward(head);
    printBackward(head);

    return 0;
}
