#include <stdio.h>
#include <stdlib.h>

// ─────────────────────────────────────────
// Node structure
// ─────────────────────────────────────────

struct Node {
    int data;
    struct Node *left, *right;
};

// Create a new node
struct Node* createNode(int val) {
    struct Node *n = (struct Node*)malloc(sizeof(struct Node));
    n->data  = val;
    n->left  = NULL;
    n->right = NULL;
    return n;
}

// ─────────────────────────────────────────
// Insert — follows BST rule
// ─────────────────────────────────────────

struct Node* insert(struct Node *root, int val) {
    if (root == NULL) return createNode(val); // empty spot found
    if (val < root->data)
        root->left  = insert(root->left,  val); // go left
    else if (val > root->data)
        root->right = insert(root->right, val); // go right
    // if val == root->data, ignore (no duplicates)
    return root;
}

// ─────────────────────────────────────────
// Search — like insert, follow BST rule
// ─────────────────────────────────────────

struct Node* search(struct Node *root, int val) {
    if (root == NULL)        return NULL; // not found
    if (val == root->data)   return root; // found!
    if (val < root->data)
        return search(root->left,  val);  // go left
    else
        return search(root->right, val);  // go right
}

// ─────────────────────────────────────────
// Traversals — 3 ways to visit all nodes
// ─────────────────────────────────────────

// Inorder: Left -> Root -> Right (gives sorted output!)
void inorder(struct Node *root) {
    if (root == NULL) return;
    inorder(root->left);
    printf("%d ", root->data);
    inorder(root->right);
}

// Preorder: Root -> Left -> Right
void preorder(struct Node *root) {
    if (root == NULL) return;
    printf("%d ", root->data);
    preorder(root->left);
    preorder(root->right);
}

// Postorder: Left -> Right -> Root
void postorder(struct Node *root) {
    if (root == NULL) return;
    postorder(root->left);
    postorder(root->right);
    printf("%d ", root->data);
}

// ─────────────────────────────────────────
// Find minimum and maximum
// ─────────────────────────────────────────

struct Node* findMin(struct Node *root) {
    while (root->left != NULL)  // keep going left
        root = root->left;
    return root;
}

struct Node* findMax(struct Node *root) {
    while (root->right != NULL) // keep going right
        root = root->right;
    return root;
}

// ─────────────────────────────────────────
// Delete a node
// ─────────────────────────────────────────

struct Node* deleteNode(struct Node *root, int val) {
    if (root == NULL) return NULL;

    if (val < root->data)
        root->left  = deleteNode(root->left,  val);
    else if (val > root->data)
        root->right = deleteNode(root->right, val);
    else {
        // Case 1: Leaf node (no children)
        if (root->left == NULL && root->right == NULL) {
            free(root);
            return NULL;
        }
        // Case 2: One child
        if (root->left == NULL) {
            struct Node *temp = root->right;
            free(root); return temp;
        }
        if (root->right == NULL) {
            struct Node *temp = root->left;
            free(root); return temp;
        }
        // Case 3: Two children
        // Find inorder successor (smallest in right subtree)
        struct Node *successor = findMin(root->right);
        root->data  = successor->data;  // copy successor's value
        root->right = deleteNode(root->right, successor->data);
    }
    return root;
}

// ─────────────────────────────────────────
// MAIN
// ─────────────────────────────────────────

int main() {
    struct Node *root = NULL;

    // Build the tree
    printf("=== Inserting: 10, 7, 15, 3, 9, 20 ===\n");
    root = insert(root, 10);
    root = insert(root, 7);
    root = insert(root, 15);
    root = insert(root, 3);
    root = insert(root, 9);
    root = insert(root, 20);

    /*  Tree looks like:
              10
             /  \
            7    15
           / \     \
          3   9    20
    */

    // Traversals
    printf("\n--- Inorder (sorted):   "); inorder(root);
    printf("\n--- Preorder (root 1st): "); preorder(root);
    printf("\n--- Postorder (root last): "); postorder(root);
    printf("\n");

    // Min and Max
    printf("\n--- Min: %d\n", findMin(root)->data);
    printf("--- Max: %d\n", findMax(root)->data);

    // Search
    printf("\n--- Search 9:  %s\n", search(root, 9)  ? "Found!" : "Not found");
    printf("--- Search 99: %s\n",   search(root, 99) ? "Found!" : "Not found");

    // Delete
    printf("\n--- Delete 7 ---\n");
    root = deleteNode(root, 7);
    printf("Inorder after delete: "); inorder(root); printf("\n");

    return 0;
}
