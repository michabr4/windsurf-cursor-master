---
trigger: glob
globs: **/*.c,**/*.cc,**/*.cpp,**/*.cxx,**/*.h,**/*.hpp
title: Safe C Functions and Memory and String Safety Guidelines
version: 1.0.1
---

rule_id: codeguard-0-safe-c-functions

# Safe Memory & String Functions — C/C++

## Banned String Functions → Safe Replacements

| Banned | Safe Alternative |
| ------ | ---------------- |
| `gets()` | `fgets(buf, n, stream)` — CRITICAL, no bounds check |
| `strcpy()` | `strcpy_s(dest, sizeof(dest), src)` |
| `strcat()` | `strcat_s(dest, sizeof(dest), src)` |
| `sprintf()` / `vsprintf()` | `snprintf()` / `vsnprintf()` |
| `scanf("%s", ...)` | `fgets()` + `sscanf()` or width-limited `scanf("%127s", buf)` |
| `strtok()` | `strtok_r()` (POSIX) or `strtok_s()` (C11) |
| `strcmp()` | `strcmp_s(dest, dmax, src, &indicator)` |
| `strlen()` | `strnlen_s(str, strsz)` |
| `strstr()` | `strstr_s(dest, dmax, src, slen, &substring)` |

## Banned Memory Functions → Safe Replacements

| Banned | Safe Alternative |
| ------ | ---------------- |
| `memcpy()` | `memcpy_s(dest, dest_size, src, count)` |
| `memset()` | `memset_s(dest, dest_size, value, count)` |
| `memmove()` | `memmove_s(dest, dest_size, src, count)` |
| `memcmp()` | `memcmp_s(s1, s1max, s2, s2max, count, &ind)` |
| `bzero()` / `memzero()` | `memset_s(dest, dest_size, 0, count)` |

## Code Generation Rules

- NEVER generate `gets()`, `strcpy()`, `strcat()`, `sprintf()`, `memcpy()`, `memset()`.
- DEFAULT to `snprintf()` for string formatting/concatenation.
- DEFAULT to `fgets()` for reading input.
- Always use `sizeof(dest)` (not `strlen(src)`) as the size parameter.
- Always check `errno_t` return values from `*_s()` functions.
- When buffer is a pointer parameter, pass `buffer_size` as an explicit argument.
- `strncpy` pitfall: always null-terminate — `dest[sizeof(dest)-1] = '\0'`.

## Compiler Flags (Enforce in Build)

- `-fstack-protector-strong` — stack overflow detection
- `-D_FORTIFY_SOURCE=2` — runtime bounds checking on string/mem functions
- `-fsanitize=address` — dev/test builds only
- `-Wformat -Wformat-security` — format string vulnerabilities

## Code Review Checklist

- [ ] No banned memory or string functions present
- [ ] All `*_s()` calls use `sizeof(dest)` not `strlen(src)` for size
- [ ] All `errno_t` return values checked and handled
- [ ] Strings explicitly null-terminated after `strncpy`
- [ ] Pointer parameters accompanied by explicit size argument
- [ ] Static analysis / pre-commit hook scanning enabled for banned functions

You must always explain how this rule was applied and why it was applied.
