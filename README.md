# Tok Language

**Tok** — experimental ultra-token-efficient language for AI-assisted development.

> **Version 1.5**

## Quick start

```bash
python tok.py --version
python tok.py examples/hello.tok
python tok.py          # REPL
```

## New in 1.5

- **`elif` chains** with `if` / `else`

```tok
i x == 1:
  p "one"
elif x == 2:
  p "two"
e:
  p "other"
```

## Features

| Area | Support |
|------|---------|
| Core | if / elif / else, while, for, break, continue, assert |
| Data | lists, dicts, records, methods, inheritance |
| Density | pipes, comprehensions, short keywords |
| Agents | agent, tools, run_agent, run_steps |
| Errors | try / catch, assert |
| I/O | files, HTTP, JSON |
| Modules | import |
| CLI | --version, --help, REPL |

## Goals

Higher token density than Python for AI-assisted coding.  
Runtime is still Python; language design is the focus.

## License

MIT
