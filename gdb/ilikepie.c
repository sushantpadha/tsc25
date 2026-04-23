/*
 * Challenge 2: I Like PIE
 * Compile: gcc -O0 -g -pie -fPIE ilikepie.c -o ilikepie
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

void secret(void) {
    puts("FLAG{michaels_entire_chicken_pot_pie_lunch}");
}

void decoy_a(void) { puts("nothing here"); }
void decoy_b(void) { puts("nope");         }
void decoy_c(void) { puts("keep looking"); }

int main(void) {
    printf("main() @ %p\n", (void*)main);
    printf("Enter a value (eg: 0xabc): ");
    fflush(stdout);

    uintptr_t addr = 0;
    if (scanf("%lx", &addr) != 1) {
        fprintf(stderr, "bad input\n");
        return 1;
    }

    void (*fn)(void) = (void(*)(void))addr;
    fn();
    return 0;
}
