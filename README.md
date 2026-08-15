# Tok Language

**Tok** is an experimental, ultra-token-efficient programming language designed for AI-assisted development, high information density, and rapid expression of complex ideas.

> **Status: Version 0.1 (First Prototype)**  
> This is the very first working foundation. It is intentionally small and realistic.

## Goals (Long-term Vision)

- Extremely high token efficiency (better density than Python for AI code generation and fine-tuning)
- Concise, expressive syntax
- Strong support for agents and orchestration
- Systems-oriented capabilities over time
- Interop with existing high-performance runtimes

**Important reality check**: Building a language that is simultaneously the best in the world at OS kernels, 3D engines, custom web infrastructure, AGI, cybersecurity, cloud, mobile, and every other domain is not feasible in one project. Tok starts small and grows deliberately.

## Current Features (v0.1)

- Simple expressions and arithmetic
- Variables
- `p` for print
- Basic `i` / `e` conditionals
- Simple `f` loops (range-style) - limited
- Functions with `f name args: body` (single-line for now)
- Python interop via `py` (planned expansion)
- Runs as a Python-based interpreter

## Quick Start

```bash
python tok.py examples/hello.tok
```

Or run the REPL:

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
e:
  p "small"

f add a b: a + b

p add 3 4
```

## Project Structure

- `tok.py` – Main interpreter / entry point
- `examples/` – Sample Tok programs
- `docs/` – Design notes (growing)

## License

MIT

## Contributing

This is the first public version. Feedback, ideas, and realistic improvements are welcome. Please keep expectations grounded in what is actually buildable.
