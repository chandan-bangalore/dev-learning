#include <stdio.h>
#include <stdint.h>

// set bit, clear bit, test if it is on or off
// extract bits [7:4] of a byte, insert 4-bit number n at position 4

uint8_t set_bit(uint8_t io, uint8_t pos) {
	io |= (1U << pos);
	return io;
}

uint8_t clear_bit(uint8_t io, uint8_t pos) {
	io &= (~(1U << pos));
	return io;
}

bool test_bit(uint8_t inp, uint8_t pos) {
	bool flag = ((inp >> pos) & 0x01) ? true: false; 
	return flag;
}

uint8_t extract_bits(uint8_t inp) {
	uint8_t out = (inp >> 4) & 0x0F;
}

uint8_t insert_bits(uint8_t inp, uint8_t num) {
	uint8_t out = (inp & 0x0f) | ((num & 0x0f) << 4);
}
/*
gcc -g myprogram.c -o myprogram
myprogram.exe 255 2
int main(int argc, char *argv[]) {
    int byte = atoi(argv[1]);  // "255" → 255
    int pos  = atoi(argv[2]);  // "2"   → 2
    printf("byte=%d pos=%d\n", byte, pos);
	
	// useful info:
	// if unused: (void)argc; (void)argv;
	char *str = argv[1];
	// to int
	int a = atoi(str);           // "123"  → 123
	// to float
	float b = atof(str);         // "3.14" → 3.14f
	// to unsigned int (uint)
	unsigned int c = strtoul(str, NULL, 10);  // "255" → 255
	// to uint8_t
	uint8_t d = (uint8_t)strtoul(str, NULL, 10);  // "255" → 255	
}
*/
int main() {
	uint8_t setb, clearb, testb, extb, insb, posb;

    printf("Enter the byte to set: ");
    scanf("%hhu", &setb);
    printf("Enter the bit position to set: ");
    scanf("%hhu", &posb);
    uint8_t y1 = set_bit(setb, posb);
    printf("Pos %d of Byte %u is set: %u\n", posb, setb, y1);

    printf("Enter the byte to clear: ");
    scanf("%hhu", &clearb);
    printf("Enter the bit position to clear: ");
    scanf("%hhu", &posb);
    uint8_t y2 = clear_bit(clearb, posb);
    printf("Pos %d of Byte %u is clear: %u\n", posb, clearb, y2);

    printf("Enter the byte to test: ");
    scanf("%hhu", &testb);
    printf("Enter the bit position to test: ");
    scanf("%hhu", &posb);
    bool y3 = test_bit(testb, posb);
    printf("Pos %d of Byte %u is tested: %u\n", posb, testb, y3);
	
    printf("Enter the byte to extract: ");
    scanf("%hhu", &extb);
    uint8_t y4 = extract_bits(extb);
    printf("Byte %u is extracted: %u\n", extb, y4);

    printf("Enter the byte to insert: ");
    scanf("%hhu", &insb);
    uint8_t y5 = insert_bits(y4, insb);
    printf("Byte %u is inserted: %u\n", insb, y5);	
	
	return 0;
}