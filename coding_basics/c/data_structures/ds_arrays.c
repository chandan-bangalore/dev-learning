#include <stdio.h>

// Function to print the array
void printArray(int *arr, int size) {
    printf("Array: ");
    for (int i = 0; i < size; i++) {
        printf("[%d] ", arr[i]);
    }
    printf("\n");
}

// Insert element at a given position (shift right)
void insertAt(int arr[], int *size, int pos, int value) {
    // Shift elements to the right from the end up to pos
    for (int i = *size; i > pos; i--) {
        arr[i] = arr[i - 1];
    }
    arr[pos] = value;
    (*size)++;
}

// Delete element at a given position (shift left)
void deleteAt(int arr[], int *size, int pos) {
    for (int i = pos; i < *size - 1; i++) {
        arr[i] = arr[i + 1];
    }
    (*size)--;
}

// Linear search — find index of a value
int search(int arr[], int size, int target) {
    for (int i = 0; i < size; i++) {
        if (arr[i] == target) return i;
    }
    return -1; // not found
}

int main() {
    int arr[10] = {10, 20, 30, 40, 50}; // max size 10, but 5 used
    int size = 5;

    printf("--- Initial Array ---\n");
    printArray(arr, size);

    // Access by index
    printf("\n--- Access ---\n");
    printf("Element at index 2: %d\n", arr[2]);

    // Insert 99 at position 2
    printf("\n--- Insert 99 at index 2 ---\n");
    insertAt(arr, &size, 2, 99);
    printArray(arr, size);

    // Delete element at position 1
    printf("\n--- Delete element at index 1 ---\n");
    deleteAt(arr, &size, 1);
    printArray(arr, size);

    // Search for value 40
    printf("\n--- Search for 40 ---\n");
    int idx = search(arr, size, 40);
    if (idx != -1)
        printf("Found 40 at index %d\n", idx);
    else
        printf("40 not found\n");

    return 0;
}
