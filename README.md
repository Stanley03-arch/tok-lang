# Tok Language

**Tok** — experimental ultra-token-efficient language for AI-assisted development.

> **Version 1.0**

## What's new in 1.0

1. **Actual tool execution inside agents**
2. **Inheritance / better OOP**
3. **Standard library growth**
4. **Error handling (`try` / `catch`)**

## Examples

```tok
# Error handling
try:
  bad = 1 / 0
catch e:
  p e

# Records + methods + inheritance
record Person name age:
  f greet:
    "Hi, I am " + self.name

record Worker(Person) name job:
  f greet:
    "Worker " + self.name

w = Worker("Ann", "engineer")
p w.greet()

# Agents
a = agent("Researcher", "find info")
add_tool(a, tool("echo"))
p run_agent(a, "query")

# Stdlib
p first([1,2,3])
p uniq([1,1,2])
p keys({"a":1})
```

## Full feature set

| Area | Support |
|------|---------|
| Records + methods + inheritance | `record Child(Parent) fields:` |
| Agents + tools | agent, tool, add_tool, remember, run_agent |
| try / catch | `try:` … `catch e:` |
| Comprehensions | `[x for x in xs if cond]` |
| Modules | `import` |
| Pipes | `xs \| sorted \| sum` |
| Strings | `"Hi {name}"` |
| Stdlib | first, last, rev, uniq, keys, any, all, … |
| Control | if/else, while, for, functions |
| I/O | read / write / exists |

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
