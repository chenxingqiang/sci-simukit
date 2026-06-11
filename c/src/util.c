#include "util.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *simukit_strdup(const char *s) {
    size_t n;
    char *d;
    if (!s) {
        return NULL;
    }
    n = strlen(s) + 1;
    d = (char *)malloc(n);
    if (d) {
        memcpy(d, s, n);
    }
    return d;
}

int simukit_strlcpy(char *dst, const char *src, size_t dst_size) {
    size_t i;
    if (dst_size == 0) {
        return 0;
    }
    for (i = 0; i + 1 < dst_size && src[i]; i++) {
        dst[i] = src[i];
    }
    dst[i] = '\0';
    return (int)i;
}

char *simukit_read_file(const char *path, size_t *out_len) {
    FILE *f;
    long sz;
    char *buf;
    size_t n;

    f = fopen(path, "rb");
    if (!f) {
        return NULL;
    }
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return NULL;
    }
    sz = ftell(f);
    if (sz < 0) {
        fclose(f);
        return NULL;
    }
    if (fseek(f, 0, SEEK_SET) != 0) {
        fclose(f);
        return NULL;
    }
    buf = (char *)malloc((size_t)sz + 1);
    if (!buf) {
        fclose(f);
        return NULL;
    }
    n = fread(buf, 1, (size_t)sz, f);
    fclose(f);
    buf[n] = '\0';
    /* Some CP2K outputs embed NUL bytes; normalize for line parsing. */
    for (size_t i = 0; i < n; i++) {
        if (buf[i] == '\0') {
            buf[i] = ' ';
        }
    }
    if (out_len) {
        *out_len = n;
    }
    return buf;
}

void simukit_trim(char *s) {
    char *start;
    size_t len;
    if (!s || !*s) {
        return;
    }
    start = s;
    while (*start && isspace((unsigned char)*start)) {
        start++;
    }
    if (start != s) {
        memmove(s, start, strlen(start) + 1);
    }
    len = strlen(s);
    while (len > 0 && isspace((unsigned char)s[len - 1])) {
        s[--len] = '\0';
    }
}

int simukit_starts_with(const char *s, const char *prefix) {
    return s && prefix && strncmp(s, prefix, strlen(prefix)) == 0;
}

int simukit_ends_with(const char *s, const char *suffix) {
    size_t ls, lx;
    if (!s || !suffix) {
        return 0;
    }
    ls = strlen(s);
    lx = strlen(suffix);
    if (lx > ls) {
        return 0;
    }
    return memcmp(s + ls - lx, suffix, lx) == 0;
}
