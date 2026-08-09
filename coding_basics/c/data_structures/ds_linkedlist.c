#include <stdio.h>
#include <stdlib.h>

struct Node {
    int data;
    struct Node *next;
};

// ─────────────────────────────────────────
// Create a new node
// ─────────────────────────────────────────
struct Node* createNode(int val) {
    struct Node *n = (struct Node*)malloc(sizeof(struct Node));
    n->data = val;
    n->next = NULL;
    return n;
}

// ─────────────────────────────────────────
// Insert at the Front
// ─────────────────────────────────────────
void insertFront(struct Node **head, int val) {
    struct Node *newNode = createNode(val);
    newNode->next = *head; // new node points to old head
    *head = newNode;       // head now points to new node
}

// ─────────────────────────────────────────
// Insert at the End
// ─────────────────────────────────────────
void insertEnd(struct Node **head, int val) {
    struct Node *newNode = createNode(val);
    if (*head == NULL) { *head = newNode; return; }
    struct Node *curr = *head;
    while (curr->next != NULL)  // walk until last node
        curr = curr->next;
    curr->next = newNode;       // last node points to new node
}

// ─────────────────────────────────────────
// Insert at a specific position (0-based)
// ─────────────────────────────────────────
void insertAt(struct Node **head, int pos, int val) {
    if (pos == 0) { insertFront(head, val); return; }
    struct Node *curr = *head;
    for (int i = 0; i < pos - 1 && curr != NULL; i++)
        curr = curr->next;        // walk to node just before pos
    if (curr == NULL) { printf("Position out of range!\n"); return; }
    struct Node *newNode = createNode(val);
    newNode->next = curr->next;   // new node points to node after
    curr->next = newNode;         // previous node points to new node
}

// ─────────────────────────────────────────
// Delete from Front
// ─────────────────────────────────────────
void deleteFront(struct Node **head) {
    if (*head == NULL) { printf("List is empty!\n"); return; }
    struct Node *temp = *head;
    *head = (*head)->next; // move head to next node
    free(temp);            // free old head
}

// ─────────────────────────────────────────
// Delete from End
// ─────────────────────────────────────────
void deleteEnd(struct Node **head) {
    if (*head == NULL) { printf("List is empty!\n"); return; }
    if ((*head)->next == NULL) { // only one node
        free(*head);
        *head = NULL;
        return;
    }
    struct Node *curr = *head;
    while (curr->next->next != NULL) // walk to second last node
        curr = curr->next;
    free(curr->next);  // free last node
    curr->next = NULL; // second last now points to NULL
}

// ─────────────────────────────────────────
// Delete by value
// ─────────────────────────────────────────
void deleteValue(struct Node **head, int val) {
    if (*head == NULL) { printf("List is empty!\n"); return; }
    if ((*head)->data == val) { deleteFront(head); return; }
    struct Node *curr = *head, *prev = NULL;
    while (curr != NULL && curr->data != val) {
        prev = curr;
        curr = curr->next;
    }
    if (curr == NULL) { printf("%d not found!\n", val); return; }
    prev->next = curr->next; // bypass the node
    free(curr);
}

// ─────────────────────────────────────────
// Search
// ─────────────────────────────────────────
void search(struct Node *head, int val) {
    struct Node *curr = head;
    int pos = 0;
    while (curr != NULL) {
        if (curr->data == val) {
            printf("Found %d at position %d\n", val, pos);
            return;
        }
        curr = curr->next;
        pos++;
    }
    printf("%d not found!\n", val);
}

// ─────────────────────────────────────────
// Reverse the list
// ─────────────────────────────────────────
void reverse(struct Node **head) {
    struct Node *prev = NULL, *curr = *head, *next = NULL;
    while (curr != NULL) {
        next = curr->next; // save next
        curr->next = prev; // reverse the pointer
        prev = curr;       // move prev forward
        curr = next;       // move curr forward
    }
    *head = prev; // prev is now the new head
}

// ─────────────────────────────────────────
// Print the list
// ─────────────────────────────────────────
void printList(struct Node *head) {
    struct Node *curr = head;
    while (curr != NULL) {
        printf("[%d] -> ", curr->data);
        curr = curr->next;
    }
    printf("NULL\n");
}

// ─────────────────────────────────────────
// MAIN
// ─────────────────────────────────────────
int main() {
    struct Node *head = NULL;

    printf("=== Insert at End ===\n");
    insertEnd(&head, 10);
    insertEnd(&head, 20);
    insertEnd(&head, 30);
    printList(head);

    printf("\n=== Insert at Front ===\n");
    insertFront(&head, 5);
    printList(head);

    printf("\n=== Insert 15 at position 2 ===\n");
    insertAt(&head, 2, 15);
    printList(head);

    printf("\n=== Delete from Front ===\n");
    deleteFront(&head);
    printList(head);

    printf("\n=== Delete from End ===\n");
    deleteEnd(&head);
    printList(head);

    printf("\n=== Delete value 15 ===\n");
    deleteValue(&head, 15);
    printList(head);

    printf("\n=== Search ===\n");
    search(head, 20);
    search(head, 99);

    printf("\n=== Reverse ===\n");
    reverse(&head);
    printList(head);

    return 0;
}
