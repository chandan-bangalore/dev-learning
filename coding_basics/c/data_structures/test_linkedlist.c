#include <stdio.h>
#include <stdlib.h>

// struct for linked list
struct Node {
	int val;
	struct Node *next;
};

// local functions
struct Node *createNode(int val) {
	struct Node *n = (struct Node *)malloc(sizeof(struct Node));
	n->val = val;
	n->next = NULL;
	return n;
}

void insertEnd(struct Node **head, int val) {
	struct Node *n = createNode(val);
	if (*head == NULL) {
		*head = n; 
		return; 
	}
	struct Node *temp = *head;
	while (temp->next != NULL) {
		temp = temp->next;
	}
	temp->next = n;
}

void insertFront(struct Node **head, int val) {
	struct Node *n = createNode(val);
	n->next = *head;
	*head = n;
}


void insertAt(struct Node **head, int pos, int val) {
	struct Node *n = createNode(val);
	// test {0,..,pos,..end,..out_of_bound}
	if (pos == 0) {
		n->next = *head;
		*head = n;
		return;
	}
	struct Node *temp = *head;
	for (int i = 0; i < pos-1; i++) {
		temp = temp->next;
	}
	n->next = temp->next;
	temp->next = n;
}	

void deleteFront(struct Node **head) {
	struct Node *temp = *head;
	*head = (*head)->next;
	free(temp);
}

void deleteEnd(struct Node **head) {
	struct Node *temp = *head;
	while (temp->next->next != NULL) {
		temp = temp->next;
	}
	free(temp->next);
	temp->next = NULL;
}

void deleteValue(struct Node **head, int val) {
	if (*head == NULL) { printf("Empty list\n"); }
	struct Node *curr = *head, *prev = NULL;
	while (curr->val != val) {
		prev = curr;
		curr = curr->next;
	}
	prev->next = curr->next;
	free(curr);
}

void search(struct Node **head, int val) {
	if (*head == NULL) { printf("Empty list\n"); return;}
	struct Node *temp = *head;
	int i = 0;
	while ( (temp != NULL) ) {
		if ((temp->val == val) ) {
			printf("%d found at index %d\n",val, i);
			return;
		}
		i++;
		temp = temp->next;
	}
	printf("%d not found\n", val);
}

void search_new(struct Node **head, int val) {
	if (*head == NULL) { printf("Empty list\n"); return;}
	struct Node *temp = *head;
	int i = 0;
	while ( temp->next != NULL && (temp->val != val) ) {
		temp = temp->next;
		i++;
	}
	if(temp->val == val) {
		printf("%d found at index %d\n",val, i);
	} else {
		printf("%d not found\n", val);
	}
}

void reverse(struct Node **head) {
	struct Node *curr = *head, *prev = NULL, *next = NULL;
	while (curr != NULL) {
		next = curr->next;
		curr->next = prev;
		prev = curr;
		curr = next;
	}
	*head = prev;
}

void print(struct Node *head) {
	struct Node *curr = head;
	while (curr != NULL) {
		printf("%d,", curr->val);
		curr = curr->next;
	}
	printf("NULL\n");
}
	

// main
int main() {
	
	struct Node *head = NULL;
	
	bool rev = false;
	
	if (0) {
		struct Node *n0 = createNode(10);
		struct Node *n1 = createNode(20);
		struct Node *n2 = createNode(30);
		n1->next = n2;
		n0->next = n1;
		head = n0;
	}
	
	if (!rev) {
		insertEnd(&head, 10); 	// pass the address of head
		insertEnd(&head, 20);	
		insertEnd(&head, 30);
		
		//print(head);
		
		insertFront(&head, 5);
		//print(head);
		
		insertAt(&head, 2, 15);
		//print(head);
		
		deleteFront(&head);
		//print(head);
		
		deleteEnd(&head);
		//print(head);
		
		deleteValue(&head, 15);
		print(head);
		
		search_new(&head, 20); // and print
		search_new(&head, 99); // and print		
	} else {
		struct Node *n1 = createNode(10);
		struct Node *n2 = createNode(20);
		struct Node *n3 = createNode(30);
		struct Node *n4 = createNode(40);
		struct Node *n5 = createNode(50);
		
		n4->next = n5;
		n3->next = n4;
		n2->next = n3;
		n1->next = n2;
		head = n1;		
		
		print(head);
		reverse(&head);
		print(head);		
	}

	return 0;
}


