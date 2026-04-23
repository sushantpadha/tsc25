# GDB Workshop

Four puzzles to motivate GDB. Tried to add CTF flavour.

## Build

```bash
# Ch1
gcc -O0 -g -no-pie password.c -o password

# Ch2
gcc -O0 -g -pie -fPIE ilikepie.c -o ilikepie

# Ch3
g++ -O0 -g -no-pie orderbook.cpp -o orderbook

# Ch4
g++ -O0 -g -no-pie astar.cpp -o astar
```

## Challenges

| # | Binary | Core bug | GDB features |
|---|--------|----------|--------------|
| 1 | `password` | XOR-obfuscated flag, password gate | `b`, `info locals`, `x/s`, `finish`, `n/s` |
| 2 | `ilikepie` | PIE binary, function pointer input | `info functions`, `p`, address arithmetic, `disas` |
| 3 | `orderbook` | Vector invalidation + object slicing + shallow copy | `watch`, `bt`, `ptype`, `catch throw`, `disas` ctor |
| 4 | `astar` | A* computes wrong answer silently | `display`, `b if`, `info locals`, `finish`, `bt` |

## Test inputs

**Ch3 — simple mode** (`simple.txt`):
```
10 8
1 1 101.00 10
2 2 102.50 5
3 3 103.00 8
4 4 104.75 3
5 5 105.00 12
6 6 106.25 7
7 7 107.00 4
8 8 108.50 6
9 9 109.00 9
10 1 50.00 0
```
```bash
./orderbook simple < simple.txt
```

**Ch3 — advanced mode** (`advanced.txt`):
```
L 1 99.50 100 0
M 2 50 2
I 3 98.00 20 80
```
```bash
./orderbook advanced < advanced.txt
```

**Ch4:**
```
5 5
0 0.0 0.0
1 5.0 0.0
2 1.0 0.0
3 2.0 3.0
4 4.0 3.0
0 2 0.1
2 3 0.1
3 4 0.1
4 1 0.1
0 1 1.0
0 1
```
```bash
./astar < test.txt
```