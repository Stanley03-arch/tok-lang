# Tok Language

**Tok** is an experimental, ultra-token-efficient programming language designed for AI-assisted development and high information density.

> **Status: Version 0.2**  
> Python bootstrap interpreter. The *language* aims to be denser and more AI-friendly than Python.

## Goals

- Extremely high token efficiency (better density than Python for AI code generation)
- Concise syntax for faster coding
- Growing support for agents and complex tasks
- Practical bootstrap (currently Python) while the language itself improves

## Current Features (v0.2)

- `p` / `print` for output
- Variables and arithmetic
- Lists: `[1, 2, 3]`
- Conditionals: `i cond:` with indented blocks
- Simple for loops: `f i = 1..5:`
- Functions: `f name a b:` with indented body
- Builtins: `len`, `str`, `int`, `float`, `list`, `range`
- REPL mode

## Quick Start

```bash
python tok.py examples/hello.tok
```

REPL:

```bash
python tok.py
```

## Example

```tok
p "Hello from Tok"

x = 10
p x + 5

i x > 5:
  p "big"

f i = 1..3:
  p i

f add a b:
  a + b

p add 7 8

nums = [1, 2, 3]
p len(nums)
```

## Reality Check

Tok is **not** currently faster than Python in execution speed (it runs on Python).  
It **is** designed to be denser and more pleasant for AI-assisted coding.  
Full performance and advanced features come later.

## License

MIT
