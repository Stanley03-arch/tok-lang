# Tok Language

**Tok** — experimental ultra-token-efficient language for AI-assisted development.

> **Version 0.9**

## Highlights

```tok
# Records with methods
record Person name age:
  f greet:
    "Hi, I am " + self.name
  f older n:
    self.age + n

bob = Person("Bob", 30)
p bob.greet()          # Hi, I am Bob
p bob.older(5)         # 35

# Agents
a = agent("Helper", "help users")
remember(a, "prefers density")
add_tool(a, tool("search"))
p run_agent(a)

# Comprehensions + pipes
p [x*2 for x in nums if x > 1]
p nums | sum

# Modules
import examples/math
```

## Feature set

| Area            | Support |
|-----------------|---------|
| Records + methods | `record Person name:` + `f method:` |
| Agents          | agent, tool, remember, add_tool, run_agent |
| Comprehensions  | `[x for x in xs if cond]` |
| Modules         | `import` |
| Pipes           | `xs \| sorted \| sum` |
| Strings         | `"Hi {name}"` interpolation |
| Control         | if/else, while, for, functions |
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
