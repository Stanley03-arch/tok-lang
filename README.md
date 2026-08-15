# Tok Language

**Tok** — experimental ultra-token-efficient language for AI-assisted development.

> **Version 1.1**

## Highlights

```tok
# Stdlib
p contains([1,2,3], 2)
p replace("hello world", "world", "Tok")
p json_dumps({"lang": "Tok"})

# try/catch
try:
  x = 1 / 0
catch e:
  p e

# OOP + inheritance
record Worker(Person) name job:
  f greet:
    "Worker " + self.name

# Agents with real Tok tools
f search q:
  "results for: " + q
a = agent("Bot", "search")
add_tool(a, tool("search", search))
p run_agent(a, "token density")
# → results=[{'search': 'results for: token density'}]
```

## Feature set

| Area | Support |
|------|---------|
| Records + methods + inheritance | ✅ |
| Agents + **executable Tok tools** | ✅ |
| try / catch | ✅ |
| JSON | `json_dumps` / `json_loads` |
| Stdlib | first, last, rev, uniq, keys, contains, replace, slice, … |
| Comprehensions, pipes, modules | ✅ |
| String interpolation | `"Hi {name}"` |

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
