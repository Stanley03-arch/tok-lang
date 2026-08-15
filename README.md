# Tok Language

**Tok** — experimental ultra-token-efficient language for AI-assisted development.

> **Version 1.4**

## Quick start

```bash
python tok.py --version
python tok.py examples/hello.tok
python tok.py          # REPL
```

## New in 1.4

- **`break` / `continue`** in while and for loops
- Fixed nested block execution (if/while bodies no longer leak into parent)

```tok
n = 0
w n < 10:
  n = n + 1
  i n == 3:
    break
  p n

f i = 1..5:
  i i == 3:
    continue
  p i
```

## Features

| Area | Support |
|------|---------|
| Core | vars, functions, if/else, while, for, break, continue |
| Data | lists, dicts, records, methods, inheritance |
| Density | pipes, comprehensions, short keywords |
| Agents | agent, tool, add_tool, run_agent, run_steps |
| Errors | try/catch, assert |
| I/O | files, HTTP, JSON |
| Modules | import |
| CLI | --version, --help, REPL |

## Goals

Higher token density than Python for AI-assisted coding.  
Runtime is still Python; language design is the focus.

## License

MIT
