#!/usr/bin/env python3
"""
Tok Language - Version 0.1
A minimal, token-efficient experimental language.
This is a first prototype interpreter written in Python.
"""

import sys
import re
from typing import Any, Dict, List, Optional, Union

# ------------------------------------------------------------
# Lexer
# ------------------------------------------------------------

class Token:
    def __init__(self, type_: str, value: Any, line: int = 0):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


def tokenize(source: str) -> List[Token]:
    tokens = []
    lines = source.splitlines()
    for line_num, line in enumerate(lines, 1):
        # Remove comments
        if "#" in line:
            line = line[:line.index("#")]
        line = line.strip()
        if not line:
            continue

        # Very simple tokenizer
        # Strings
        string_matches = list(re.finditer(r'"([^"]*)"', line))
        for m in string_matches:
            tokens.append(Token("STRING", m.group(1), line_num))
            line = line.replace(m.group(0), f" __STR_{len(tokens)-1}__ ", 1)

        # Numbers
        for m in re.finditer(r"\b(\d+\.?\d*)\b", line):
            val = float(m.group(1)) if "." in m.group(1) else int(m.group(1))
            tokens.append(Token("NUMBER", val, line_num))

        # Keywords and identifiers
        words = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*|\.\.|->|[+\-*/%<>=!]+|[=:()\[\],.|]", line)
        for w in words:
            if w.startswith("__STR_"):
                continue
            if w in ("p", "i", "e", "f", "w", "r", "py", "true", "false", "none"):
                tokens.append(Token("KEYWORD", w, line_num))
            elif w == "..":
                tokens.append(Token("RANGE", w, line_num))
            elif w in ("=", ":", "+", "-", "*", "/", "%", "<", ">", "<=", ">=", "==", "!=", "->"):
                tokens.append(Token("OP", w, line_num))
            elif w in ("(", ")", "[", "]", ",", "."):
                tokens.append(Token("PUNCT", w, line_num))
            else:
                tokens.append(Token("IDENT", w, line_num))

        tokens.append(Token("NEWLINE", "\n", line_num))

    tokens.append(Token("EOF", None))
    return tokens


# ------------------------------------------------------------
# Simple recursive-descent style evaluator (v0.1 - limited)
# ------------------------------------------------------------

class TokInterpreter:
    def __init__(self):
        self.env: Dict[str, Any] = {
            "true": True,
            "false": False,
            "none": None,
        }
        self.functions: Dict[str, Any] = {}

    def eval_expr(self, expr: str) -> Any:
        """Very limited expression evaluator for v0.1"""
        expr = expr.strip()
        if not expr:
            return None

        # String literal
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]

        # Number
        try:
            if "." in expr:
                return float(expr)
            return int(expr)
        except ValueError:
            pass

        # Boolean / none
        if expr in self.env:
            return self.env[expr]

        # Variable
        if expr in self.env:
            return self.env[expr]

        # Simple binary ops (left to right, no precedence for v0.1)
        for op in ("==", "!=", "<=", ">=", "<", ">", "+", "-", "*", "/", "%"):
            if op in expr:
                left, right = expr.split(op, 1)
                lval = self.eval_expr(left.strip())
                rval = self.eval_expr(right.strip())
                if op == "+": return lval + rval
                if op == "-": return lval - rval
                if op == "*": return lval * rval
                if op == "/": return lval / rval
                if op == "%": return lval % rval
                if op == "==": return lval == rval
                if op == "!=": return lval != rval
                if op == "<": return lval < rval
                if op == ">": return lval > rval
                if op == "<=": return lval <= rval
                if op == ">=": return lval >= rval

        # Function call: name arg1 arg2 ...
        parts = expr.split()
        if len(parts) >= 1 and parts[0] in self.functions:
            func = self.functions[parts[0]]
            args = [self.eval_expr(a) for a in parts[1:]]
            return func(*args)

        # Simple variable lookup
        if expr in self.env:
            return self.env[expr]

        raise NameError(f"Unknown name or expression: {expr}")

    def run_line(self, line: str) -> Any:
        line = line.strip()
        if not line or line.startswith("#"):
            return None

        # print
        if line.startswith("p "):
            val = self.eval_expr(line[2:].strip())
            print(val)
            return val

        # assignment
        if "=" in line and not any(op in line for op in ("==", "!=", "<=", ">=")):
            name, expr = line.split("=", 1)
            name = name.strip()
            val = self.eval_expr(expr.strip())
            self.env[name] = val
            return val

        # simple if (single line for v0.1)
        if line.startswith("i "):
            # Very limited: i condition: statement
            if ":" in line:
                cond_part, body = line[2:].split(":", 1)
                if self.eval_expr(cond_part.strip()):
                    return self.run_line(body.strip())
            return None

        # function definition (very limited)
        # f name a b: body
        if line.startswith("f ") and ":" in line:
            header, body = line[2:].split(":", 1)
            parts = header.strip().split()
            if not parts:
                return None
            fname = parts[0]
            params = parts[1:]

            def make_func(ps, bd):
                def func(*args):
                    old_env = self.env.copy()
                    for p, a in zip(ps, args):
                        self.env[p] = a
                    try:
                        result = self.eval_expr(bd.strip())
                    finally:
                        self.env = old_env
                    return result
                return func

            self.functions[fname] = make_func(params, body)
            return None

        # fallback: expression
        return self.eval_expr(line)

    def run(self, source: str):
        lines = source.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            # Skip empty / comments
            if not line.strip() or line.strip().startswith("#"):
                i += 1
                continue

            # Multi-line blocks are not fully supported in v0.1
            # We only handle single-line constructs for the first version
            try:
                self.run_line(line)
            except Exception as e:
                print(f"Error on line {i+1}: {e}")
            i += 1

    def repl(self):
        print("Tok v0.1 REPL (type 'exit' or Ctrl-D to quit)")
        while True:
            try:
                line = input("tok> ")
                if line.strip() in ("exit", "quit"):
                    break
                result = self.run_line(line)
                if result is not None and not line.strip().startswith("p "):
                    print(result)
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    interp = TokInterpreter()

    if len(sys.argv) > 1:
        path = sys.argv[1]
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        interp.run(source)
    else:
        interp.repl()


if __name__ == "__main__":
    main()
