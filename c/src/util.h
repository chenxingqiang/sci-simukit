#ifndef SIMUKIT_UTIL_H
#define SIMUKIT_UTIL_H

#include <stddef.h>

char *simukit_strdup(const char *s);
int simukit_strlcpy(char *dst, const char *src, size_t dst_size);
char *simukit_read_file(const char *path, size_t *out_len);
void simukit_trim(char *s);
int simukit_starts_with(const char *s, const char *prefix);
int simukit_ends_with(const char *s, const char *suffix);

#endif
