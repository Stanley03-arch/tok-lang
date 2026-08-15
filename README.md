# Tok Language

**Tok** — experimental ultra-token-efficient language for AI-assisted development.

> **Version 0.8**

## Highlights

```tok
# List comprehensions
p [x*10 for x in nums if x > 2]

# String interpolation
p "Running {lang} v0.8"

# Records
record Person name age:
  pass
bob = Person("Bob", 30)

# Agents
a = agent("Helper", "answer questions")
remember(a, "user likes density")
add_tool(a, tool("search"))
p run_agent(a)

# Modules
import examples/math
p square(6)

# Pipes
p nums | sum
```

## Feature set

| Area            | Support |
|-----------------|---------|
| Data            | lists, dicts, indexing, records |
| Comprehensions  | `[x for x in xs if cond]` |
| Control         | if/else, while, for-range, for-in |
| Functions       | multi-arg, multi-line |
| Modules         | `import` |
| Agents          | agent, tool, remember, add_tool, run_agent, plan |
| Strings         | interpolation `{name}`, upper/lower |
| Density         | pipe `\|`, short keywords |
| I/O             | read / write / exists |

## Run

```bash
python tok.py examples/hello.tok
python tok.py          # REPL
```

## Goals

Higher token density than Python for AI generation and fine-tuning.  
Runtime is still Python; language design is the focus.

## License

MIT
