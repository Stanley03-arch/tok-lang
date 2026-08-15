# Tok Language

**Tok** — experimental ultra-token-efficient language for AI-assisted development.

> **Version 0.7**

## New in 0.7

- **Modules / import** — `import examples/math`
- **List comprehensions** — `[x*2 for x in nums]` and with `if`
- **Records / classes** — `record Point x y:`
- **Agent primitives** — `agent`, `tool`, `plan`, `remember`, `run_agent`
- **String interpolation** — `"Hello {name} v{ver}"`

## Full feature set

| Area              | Syntax / Example                          |
|-------------------|-------------------------------------------|
| Print             | `p "hi"`                                  |
| Lists + index     | `nums[0]`  `nums[1]=99`                   |
| Dicts + dot       | `d.name`                                  |
| Comprehensions    | `[x*2 for x in xs if x>0]`                |
| Pipe              | `xs \| sorted \| sum`                     |
| Records           | `record Point x y:`  `pt = Point(1,2)`    |
| Modules           | `import mymod`                            |
| Agents            | `a = agent("Name", "goal")`               |
| String interp     | `"Hi {name}"`                             |
| Control           | `i`/`e`, `w`, `f i=1..n`, `f x in xs`     |
| Functions         | `f add a b:`                              |
| File I/O          | `read` / `write` / `exists`               |

## Run

```bash
python tok.py examples/hello.tok
python tok.py          # REPL
```

## Density focus

Tok aims for higher token density than Python so AI generation and fine-tuning are cheaper and faster. The runtime is still Python; the language design is what we optimize.

## License

MIT
