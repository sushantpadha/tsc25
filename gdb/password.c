#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// unused
static unsigned char encrypted_flag[] = {
    0x3f, 0x35, 0x38, 0x3e, 0x22, 0x20, 0x36, 0x2c,
    0x06, 0x3f, 0x30, 0x37, 0x38, 0x35, 0x35, 0x20,
    0x06, 0x2c, 0x2a, 0x3c, 0x3d, 0x06, 0x3e, 0x3d,
    0x3b, 0x06, 0x38, 0x37, 0x3d, 0x06, 0x37, 0x36,
    0x2d, 0x06, 0x29, 0x2b, 0x30, 0x37, 0x2d, 0x06,
    0x2a, 0x2d, 0x38, 0x2d, 0x3c, 0x34, 0x3c, 0x37,
    0x2d, 0x2a, 0x24,
};

// unused
static unsigned char encrypted_password[] = {
    0x31, 0x2c, 0x37, 0x2d, 0x3c, 0x2b, 0x6d, 0x6b,
};

// ooh what does this do
static unsigned char compute_xor_key(void) {
    unsigned char k = 0x5b;
    for (int i = 0; i < 3; i++)
        k ^= (unsigned char)(i * 7 + 13);
    return k;
}

static void xor_decrypt(const unsigned char *enc, int len, unsigned char key, char *out) {
    for (int i = 0; i < len; i++)
        out[i] = enc[i] ^ key;
    out[len] = '\0';
}

static int gate_to_mordor(const char *input) {
    unsigned char key = compute_xor_key();
    char pw[32];
    xor_decrypt(encrypted_password, sizeof(encrypted_password), key, pw);
    return strcmp(input, pw) == 0;
}

static void release_flag(void) {
    unsigned char key = compute_xor_key();
    int len = sizeof(encrypted_flag);
    char decrypted_flag[256];
    xor_decrypt(encrypted_flag, len, key, decrypted_flag);
    printf("%s\n", decrypted_flag);
}

int main(void) {
    char input[128];
    printf("=== Password Vault ===\n");
    while (1) {
        printf("Password: ");
        if (!fgets(input, sizeof(input), stdin)) break;
        int l = strlen(input);
        if (l > 0 && input[l-1] == '\n') input[l-1] = '\0';
        int ok = gate_to_mordor(input);
        if (ok) {
            release_flag();
            return 0;
        }
        printf("Access denied.\n");
    }
    return 1;
}
