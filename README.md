# Tok Language

**Tok** — experimental ultra-token-efficient language for AI-assisted development.

> **Version 0.3**  
> Python bootstrap. The language itself is designed to be denser than Python.

## Features (v0.3)

| Feature            | Syntax example                  |
|--------------------|---------------------------------|
| Print              | `p "hello"`                     |
| Variables          | `x = 10`                        |
| Lists              | `nums = [1, 2, 3]`              |
| Dicts              | `d = {"a": 1, "b": 2}`          |
| If / else          | `i x > 5:` … `e:`               |
| For range          | `f i = 1..5:`                   |
| While              | `w n < 10:`                     |
| Functions          | `f add a b:` …                  |
| Builtins           | `len`, `str`, `int`, `type`…    |

## Run

```bash
python tok.py examples/hello.tok
python tok.py          # REPL
```

## Example

```tok
p "Tok v0.3"

x = 10
i x > 5:
  p "big"
e:
  p "small"

f i = 1..3:
  p i

f add a b:
  a + b
p add 7 8

d = {"lang": "Tok", "ver": 3}
p d
```

## Goals

- Higher token density than Python (better for AI generation & fine-tuning)
- Fast to write
- Growing agent / systems capabilities over time

## Reality

Current runtime is Python → not faster than Python in execution.  
Language design targets density and AI friendliness first.

## License

MIT
