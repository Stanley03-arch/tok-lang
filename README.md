# Tok Language

**Tok** — experimental ultra-token-efficient language for AI-assisted development.

> **Version 0.6**

## Highlights

```tok
p "hello" | upper | lower          # pipe chains
p [5,1,8,3] | sorted | sum         # denser data flow
write "out.txt" "data"             # space args now better
p read "out.txt"
```

## Feature Summary

| Area            | Support                                      |
|-----------------|----------------------------------------------|
| Data            | lists, dicts, indexing, dot access           |
| Control         | if/else, while, for-range, for-in            |
| Functions       | multi-line, params, return                   |
| Density         | pipe `\|`, short keywords (`p`,`i`,`f`,`w`)  |
| I/O             | read / write / exists                        |
| Helpers         | upper, lower, sorted, sum, max, min, filter… |

## Run

```bash
python tok.py examples/hello.tok
python tok.py          # REPL
```

## Goals

- Higher token density than Python (AI-friendly)
- Fast to write
- Practical power that grows over time

## Reality

Runtime is still Python. Execution speed is not better than Python yet.  
Language density and usability are the current focus.

## License

MIT
