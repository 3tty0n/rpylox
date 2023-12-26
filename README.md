# RPyLox

This repository is a RPython implementation for Lox. Read more at https://craftinginterpreters.com/

## Prerequisite

### RPython and Python 2.7

This code base is built with RPython and PyPy 2.7. Please download PyPy repository and put it at the root.

```shell
wget https://downloads.python.org/pypy/pypy2.7-v7.3.14-src.tar.bz2
tar xf pypy2.7-v7.3.14-src.tar.bz2 && mv pypy2.7-v7.3.14-src pypy
```

PyPy 2.7 is based on Python 2.7. Please install Python 2.7 instead of Python 3.x.

## Build

You can use `Makefile` to build `rlox-jit` and `rlox-interp`.

`rlox-jit` support meta-tracing compialtion and runs faster for loop-heavy programs for example.

```shell
make targetlox-jit
```

`rlox-interp` is an interpreter compiled by using RPython.

```shell
make targetlox-interp
```


## Progress

- [x] Chapter 16
- [x] Chapter 17
- [x] Chapter 18
- [x] Chapter 19
- [x] Chapter 20
  - Skip this chapter because we can use built-in hash tables
- [x] Chapter 21
- [x] Chapter 22
- [x] Chapter 23
- [ ] Chapter 24
- [ ] Chapter 25
- [ ] Chapter 26
- [ ] Chapter 27
- [ ] Chapter 28
- [ ] Chapter 29
- [ ] Chapter 30
