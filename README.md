# Tok Language

**Tok** — experimental ultra-token-efficient language for AI-assisted development.

> **Version 1.2**

## Highlights

```tok
# Agents with multiple real tools + multi-step runs
f search q:
  "found:" + q
a = agent("Bot", "research")
add_tool(a, tool("search", search))
p run_agent(a, "density")
p run_steps(a, ["density", "tokens"])

# HTTP
# p http_get("https://example.com")
# p http_json("https://api.example.com/data")

# Files
write("f.txt", "hello")
append("f.txt", "!")
p read("f.txt")

# OOP, try/catch, JSON, comprehensions, pipes… all still there
```

## Feature set

| Area | Support |
|------|---------|
| Agents + executable tools | ✅ + `run_steps` |
| HTTP | `http_get`, `http_json` |
| Files | read, write, append, readlines, exists |
| OOP | records, methods, inheritance |
| try / catch | ✅ |
| JSON | json_dumps / json_loads |
| Stdlib | first, last, rev, uniq, contains, replace, … |
| Density | pipes, comprehensions, short keywords |

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
