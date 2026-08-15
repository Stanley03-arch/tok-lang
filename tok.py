#!/usr/bin/env python3
"""
Tok Language - Version 0.3
Ultra-token-efficient experimental language.
Python bootstrap. The language aims for higher density than Python.
"""

import sys
import re
from typing import Any, Dict, List, Optional, Union

VERSION = "0.3"


class TokError(Exception):
    def __init__(self, msg: str, line: int = 0):
        super().__init__(f"Line {line}: {msg}" if line else msg)


class Environment:
    def __init__(self, parent: Optional["Environment"] = None):
        self.values: Dict[str, Any] = {}
        self.parent = parent

    def get(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise TokError(f"Undefined '{name}'")

    def set(self, name: str, value: Any):
        self.values[name] = value

    def define(self, name: str, value: Any):
        self.values[name] = value


class TokFunction:
    def __init__(self, name: str, params: List[str], body: List[str], closure: Environment):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure

    def __call__(self, interp: "Interpreter", args: List[Any]) -> Any:
        if len(args) != len(self.params):
            raise TokError(f"{self.name} expected {len(self.params)} args, got {len(args)}")
        local = Environment(self.closure)
        for p, a in zip(self.params, args):
            local.define(p, a)
        return interp.execute_block(self.body, local)


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.env = self.global_env
        self._builtins()

    def _builtins(self):
        g = self.global_env
        g.define("true", True)
        g.define("false", False)
        g.define("none", None)
        g.define("len", len)
        g.define("str", str)
        g.define("int", int)
        g.define("float", float)
        g.define("list", list)
        g.define("dict", dict)
        g.define("range", range)
        g.define("type", lambda x: type(x).__name__)

    def eval_expr(self, expr: str, env: Optional[Environment] = None) -> Any:
        env = env or self.env
        expr = expr.strip()
        if not expr:
            return None

        if len(expr) >= 2 and expr[0] in "\"'" and expr[-1] == expr[0]:
            return expr[1:-1]

        try:
            return float(expr) if "." in expr else int(expr)
        except ValueError:
            pass

        if expr.startswith("[") and expr.endswith("]"):
            inner = expr[1:-1].strip()
            if not inner:
                return []
            return [self.eval_expr(p, env) for p in self._split(inner)]

        if expr.startswith("{") and expr.endswith("}"):
            return self._eval_dict(expr[1:-1].strip(), env)

        m = re.match(r"^([a-zA-Z_][\w]*)\((.*)\)$", expr, re.DOTALL)
        if m:
            fname, args_s = m.group(1), m.group(2).strip()
            args = [self.eval_expr(a, env) for a in self._split(args_s)] if args_s else []
            return self._call(fname, args, env)

        for ops in (
            ("or",),
            ("and",),
            ("==", "!=", "<=", ">=", "<", ">"),
            ("+", "-"),
            ("*", "/", "%"),
        ):
            for op in ops:
                if op in ("and", "or"):
                    parts = re.split(rf"\s+{op}\s+", expr, maxsplit=1)
                else:
                    parts = expr.split(op, 1)
                if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                    l = self.eval_expr(parts[0].strip(), env)
                    r = self.eval_expr(parts[1].strip(), env)
                    if op == "+": return l + r
                    if op == "-": return l - r
                    if op == "*": return l * r
                    if op == "/": return l / r
                    if op == "%": return l % r
                    if op == "==": return l == r
                    if op == "!=": return l != r
                    if op == "<": return l < r
                    if op == ">": return l > r
                    if op == "<=": return l <= r
                    if op == ">=": return l >= r
                    if op == "and": return l and r
                    if op == "or": return l or r

        if expr.startswith("not "):
            return not self.eval_expr(expr[4:].strip(), env)

        parts = expr.split()
        if parts:
            try:
                val = env.get(parts[0])
                if callable(val) or isinstance(val, TokFunction):
                    args = [self.eval_expr(a, env) for a in parts[1:]]
                    return self._call(parts[0], args, env)
            except TokError:
                pass

        try:
            return env.get(expr)
        except TokError:
            raise TokError(f"Unknown: {expr}")

    def _eval_dict(self, inner: str, env: Environment) -> dict:
        if not inner:
            return {}
        result = {}
        for part in self._split(inner):
            if ":" not in part:
                raise TokError(f"Bad dict entry: {part}")
            k_s, v_s = part.split(":", 1)
            k = self.eval_expr(k_s.strip(), env)
            v = self.eval_expr(v_s.strip(), env)
            result[k] = v
        return result

    def _split(self, s: str) -> List[str]:
        parts, cur, depth = [], [], 0
        in_str = None
        i = 0
        while i < len(s):
            c = s[i]
            if in_str:
                cur.append(c)
                if c == in_str and (i == 0 or s[i-1] != "\\"):
                    in_str = None
                i += 1
                continue
            if c in "\"'":
                in_str = c
                cur.append(c)
            elif c in "([{":
                depth += 1
                cur.append(c)
            elif c in ")]}":
                depth -= 1
                cur.append(c)
            elif c == "," and depth == 0:
                parts.append("".join(cur).strip())
                cur = []
            else:
                cur.append(c)
            i += 1
        if cur:
            parts.append("".join(cur).strip())
        return [p for p in parts if p]

    def _call(self, name: str, args: List[Any], env: Environment) -> Any:
        try:
            fn = env.get(name)
        except TokError:
            raise TokError(f"Undefined function '{name}'")
        if isinstance(fn, TokFunction):
            return fn(self, args)
        if callable(fn):
            return fn(*args)
        raise TokError(f"'{name}' not callable")

    def execute_block(self, lines: List[str], env: Environment) -> Any:
        old = self.env
        self.env = env
        result = None
        try:
            i = 0
            while i < len(lines):
                line = lines[i]
                if not line.strip() or line.strip().startswith("#"):
                    i += 1
                    continue
                result = self.execute_line(line, lines, i, env)
                i += 1
        finally:
            self.env = old
        return result

    def execute_line(self, line: str, all_lines: List[str], idx: int, env: Environment) -> Any:
        s = line.strip()
        if not s or s.startswith("#"):
            return None

        if s.startswith("p ") or s.startswith("print "):
            val = self.eval_expr(s.split(" ", 1)[1], env)
            print(val)
            return val

        if s.startswith("r ") or s.startswith("return "):
            return self.eval_expr(s.split(" ", 1)[1], env)

        if "=" in s and not any(op in s for op in ("==", "!=", "<=", ">=")):
            left, right = s.split("=", 1)
            name = left.strip()
            if re.match(r"^[a-zA-Z_]\w*$", name):
                val = self.eval_expr(right.strip(), env)
                env.set(name, val)
                return val

        if s.startswith("i ") or s.startswith("if "):
            return self._if(s, all_lines, idx, env)

        if s.startswith("w ") or s.startswith("while "):
            return self._while(s, all_lines, idx, env)

        if s.startswith("f ") and ".." in s:
            return self._for_range(s, all_lines, idx, env)

        if s.startswith("f ") and ":" in s:
            return self._def_func(s, all_lines, idx, env)

        return self.eval_expr(s, env)

    def _body(self, lines: List[str], idx: int) -> List[str]:
        body = []
        base = len(lines[idx]) - len(lines[idx].lstrip())
        j = idx + 1
        while j < len(lines):
            l = lines[j]
            if not l.strip() or l.strip().startswith("#"):
                j += 1
                continue
            ind = len(l) - len(l.lstrip())
            if ind > base:
                body.append(l)
                j += 1
            else:
                break
        return body

    def _if(self, header: str, lines: List[str], idx: int, env: Environment) -> Any:
        if ":" not in header:
            raise TokError("if needs :")
        cond_s, first = header.split(":", 1)
        cond_s = re.sub(r"^(i|if)\s+", "", cond_s).strip()
        cond = self.eval_expr(cond_s, env)

        body = []
        if first.strip():
            body.append(first.strip())
        body.extend(self._body(lines, idx))

        else_body = []
        base = len(lines[idx]) - len(lines[idx].lstrip())
        j = idx + 1 + len(body)
        while j < len(lines) and (not lines[j].strip() or lines[j].strip().startswith("#")):
            j += 1
        if j < len(lines):
            es = lines[j].strip()
            if es.startswith("e:") or es.startswith("else:") or es.startswith("e ") or es.startswith("else "):
                if ":" in es:
                    _, efirst = es.split(":", 1)
                    if efirst.strip():
                        else_body.append(efirst.strip())
                else_body.extend(self._body(lines, j))

        if cond:
            return self.execute_block(body, env)
        elif else_body:
            return self.execute_block(else_body, env)
        return None

    def _while(self, header: str, lines: List[str], idx: int, env: Environment) -> Any:
        if ":" not in header:
            raise TokError("while needs :")
        cond_s, first = header.split(":", 1)
        cond_s = re.sub(r"^(w|while)\s+", "", cond_s).strip()
        body = []
        if first.strip():
            body.append(first.strip())
        body.extend(self._body(lines, idx))

        result = None
        for _ in range(100000):
            if not self.eval_expr(cond_s, env):
                break
            result = self.execute_block(body, env)
        return result

    def _for_range(self, header: str, lines: List[str], idx: int, env: Environment) -> Any:
        m = re.match(r"f\s+(\w+)\s*=\s*(-?\d+)\.\.(-?\d+)\s*:", header)
        if not m:
            raise TokError("Use: f i = 1..5:")
        var, a, b = m.group(1), int(m.group(2)), int(m.group(3))
        body = self._body(lines, idx)
        result = None
        step = 1 if b >= a else -1
        for val in range(a, b + step, step):
            env.set(var, val)
            result = self.execute_block(body, env)
        return result

    def _def_func(self, header: str, lines: List[str], idx: int, env: Environment) -> Any:
        if ":" not in header:
            raise TokError("Function needs :")
        left, first = header.split(":", 1)
        parts = re.sub(r"^f\s+", "", left).strip().split()
        if not parts:
            raise TokError("Function needs name")
        fname, params = parts[0], parts[1:]
        body = []
        if first.strip():
            body.append(first.strip())
        body.extend(self._body(lines, idx))
        env.define(fname, TokFunction(fname, params, body, env))
        return None

    def run(self, source: str):
        lines = source.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            s = line.strip()
            if not s or s.startswith("#"):
                i += 1
                continue
            try:
                consumes = (
                    s.startswith(("i ", "if ", "w ", "while ")) or
                    (s.startswith("f ") and (".." in s or ":" in s)) or
                    s.startswith(("e:", "else:", "e ", "else "))
                )
                self.execute_line(line, lines, i, self.env)
                if consumes:
                    base = len(line) - len(line.lstrip())
                    i += 1
                    while i < len(lines):
                        l = lines[i]
                        if not l.strip():
                            i += 1
                            continue
                        ind = len(l) - len(l.lstrip())
                        if ind > base or l.strip().startswith(("e:", "else:", "e ", "else ")):
                            if l.strip().startswith(("e:", "else:", "e ", "else ")):
                                i += 1
                                while i < len(lines):
                                    ll = lines[i]
                                    if not ll.strip():
                                        i += 1
                                        continue
                                    if len(ll) - len(ll.lstrip()) > base:
                                        i += 1
                                    else:
                                        break
                                break
                            i += 1
                        else:
                            break
                    continue
            except TokError as e:
                print(f"TokError: {e}")
            except Exception as e:
                print(f"Error line {i+1}: {e}")
            i += 1

    def repl(self):
        print(f"Tok v{VERSION}  (exit to quit)")
        while True:
            try:
                line = input("tok> ")
                if line.strip() in ("exit", "quit"):
                    break
                if not line.strip():
                    continue
                r = self.execute_line(line, [line], 0, self.env)
                if r is not None and not line.strip().startswith(("p ", "print ")):
                    print(r)
            except EOFError:
                print()
                break
            except TokError as e:
                print(f"TokError: {e}")
            except Exception as e:
                print(f"Error: {e}")


def main():
    interp = Interpreter()
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            interp.run(f.read())
    else:
        interp.repl()


if __name__ == "__main__":
    main()
