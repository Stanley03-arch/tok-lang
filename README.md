# Tok Language

**Tok** — experimental ultra-token-efficient language for AI-assisted development.

> **Version 0.5**

## Features

| Feature              | Example                              |
|----------------------|--------------------------------------|
| Print                | `p "hi"`                             |
| Lists + indexing     | `nums[0]`  `nums[1] = 99`            |
| Dicts + dot access   | `d.name`  `d["key"]`                 |
| If / else            | `i x > 5:` … `e:`                    |
| For range / for-in   | `f i = 1..5:`  `f x in xs:`          |
| While                | `w n < 10:`                          |
| Functions            | `f add a b:` …                       |
| **Pipe**             | `"hello" \| upper`  `[1,2,3] \| len` |
| File I/O             | `write("f.txt", data)`  `read("f.txt")` |
| String helpers       | `upper`, `lower`, `split`, `join`    |

## Run

```bash
python tok.py examples/hello.tok
python tok.py          # REPL
```

## Density example

```tok
p "hello" | upper          # HELLO
p [1, 2, 3] | len          # 3

write("out.txt", "data")
p read("out.txt")
```

## Goals

- Higher token density than Python
- Fast to write, AI-friendly
- Growing capability

## Reality

Still Python-powered under the hood → not faster in raw speed yet.  
Focus remains language density and practical power.

## License

MIT
