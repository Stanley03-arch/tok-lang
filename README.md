# Tok Language

**Tok** — experimental ultra-token-efficient language for AI-assisted development.

> **Version 1.3**

## Quick start

```bash
python tok.py --version
python tok.py examples/hello.tok
python tok.py          # REPL
```

## New in 1.3

- `assert` statement
- CLI: `--version`, `--help`
- `version()` builtin

## Language surface

```tok
# assert
assert 1 + 1 == 2

# records + methods
record Point x y:
  f sum:
    self.x + self.y
p Point(3, 4).sum()

# agents with Tok tools
f echo q:
  "echo:" + q
a = agent("T", "test")
add_tool(a, tool("echo", echo))
p run_agent(a, "hi")

# density
p [x * 10 for x in [1, 2, 3] if x > 1]
p nums | sum
```

## Features

| Area | Support |
|------|---------|
| Core | vars, functions, if/else, while, for |
| Data | lists, dicts, records, methods, inheritance |
| Density | pipes, comprehensions, short keywords |
| Agents | agent, tool, add_tool, run_agent, run_steps |
| Errors | try / catch, assert |
| I/O | read, write, append, HTTP, JSON |
| Modules | import |
| CLI | --version, --help, REPL |

## Goals

Higher token density than Python for AI-assisted coding.  
Runtime is still Python; language design is the focus.

## License

MIT
