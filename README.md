# Tok Language

**Tok** — experimental ultra-token-efficient language for AI-assisted development.

> **Version 0.4**

## Features

| Feature              | Example                          |
|----------------------|----------------------------------|
| Print                | `p "hi"`                         |
| Variables            | `x = 10`                         |
| Lists                | `nums = [1, 2, 3]`               |
| Dicts                | `d = {"a": 1}`                   |
| Indexing             | `nums[0]`  `d["key"]`            |
| Dot access (dicts)   | `d.name`                         |
| Indexed assign       | `nums[1] = 99`                   |
| If / else            | `i x > 5:` … `e:`                |
| For range            | `f i = 1..5:`                    |
| For-in               | `f x in xs:`                     |
| While                | `w n < 10:`                      |
| Functions            | `f add a b:` …                   |
| Builtins             | `len`, `str`, `int`, `type`…     |

## Run

```bash
python tok.py examples/hello.tok
python tok.py          # REPL
```

## Example

```tok
nums = [10, 20, 30]
p nums[1]
nums[0] = 99

d = {"lang": "Tok", "ver": 4}
p d.name

f x in nums:
  p x
```

## Goals

- Higher token density than Python (better for AI)
- Fast to write
- Growing power over time

## Reality

Runtime is still Python → execution speed is not better than Python yet.  
Language density and AI-friendliness are the current focus.

## License

MIT
