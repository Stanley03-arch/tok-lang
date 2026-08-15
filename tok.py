#!/usr/bin/env python3
"""
Tok Language - Version 0.7
Ultra-token-efficient experimental language.
Adds: modules, denser map/comprehensions, records/classes,
      agent primitives, better string formatting.
"""

import sys
import re
import os
from typing import Any, Dict, List, Optional, Callable

VERSION = "0.7"


class TokError(Exception):
    def __init__(self, msg: str, line: int = 0):
        self.line = line
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


class TokRecord:
    def __init__(self, fields: Dict[str, Any], methods: Optional[Dict[str, TokFunction]] = None):
        self.fields = dict(fields)
        self.methods = methods or {}

    def __getattr__(self, name):
        if name in self.fields:
            return self.fields[name]
        if name in self.methods:
            return self.methods[name]
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in ("fields", "methods"):
            object.__setattr__(self, name, value)
        else:
            self.fields[name] = value

    def __repr__(self):
        return f"Record({self.fields})"


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.env = self.global_env
        self.current_line = 0
        self.loaded_modules: set = set()
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
        g.define("print", print)
        g.define("read", lambda path: open(path, encoding="utf-8").read())
        g.define("write", lambda path, data: open(path, "w", encoding="utf-8").write(str(data)))
        g.define("exists", os.path.exists)
        g.define("upper", lambda s: str(s).upper())
        g.define("lower", lambda s: str(s).lower())
        g.define("split", lambda s, sep=" ": str(s).split(sep))
        g.define("join", lambda sep, xs: str(sep).join(str(x) for x in xs))
        g.define("filter", lambda pred, xs: [x for x in xs if pred(x)])
        g.define("sum", sum)
        g.define("min", min)
        g.define("max", max)
        g.define("abs", abs)
        g.define("sorted", sorted)

        def _map(fn, xs):
            if isinstance(fn, TokFunction):
                return [fn(self, [x]) for x in xs]
            return [fn(x) for x in xs]
        g.define("map", _map)

        def _fmt(template, **kwargs):
            try:
                return str(template).format(**kwargs)
            except Exception:
                return str(template)
        g.define("fmt", _fmt)

        def _agent(name, goal=""):
            return {"type": "agent", "name": name, "goal": goal, "tools": [], "memory": []}
        g.define("agent", _agent)

        def _tool(name, fn=None):
            return {"type": "tool", "name": name, "fn": fn}
        g.define("tool", _tool)

        def _plan(steps):
            return {"type": "plan", "steps": list(steps)}
        g.define("plan", _plan)

        def _remember(agent, item):
            if isinstance(agent, dict) and "memory" in agent:
                agent["memory"].append(item)
            return agent
        g.define("remember", _remember)

        def _run_agent(ag, *args):
            return f"Agent[{ag.get('name','?')}] goal={ag.get('goal','')} tools={len(ag.get('tools',[]))} mem={len(ag.get('memory',[]))}"
        g.define("run_agent", _run_agent)

    def eval_expr(self, expr: str, env: Optional[Environment] = None) -> Any:
        env = env or self.env
        expr = expr.strip()
        if not expr:
            return None

        if " | " in expr:
            parts = [p.strip() for p in expr.split(" | ")]
            val = self.eval_expr(parts[0], env)
            for part in parts[1:]:
                if re.match(r"^[a-zA-Z_]\w*$", part):
                    val = self._call(part, [val], env)
                else:
                    env2 = Environment(env)
                    env2.define("_", val)
                    val = self.eval_expr(part, env2)
            return val

        m = re.match(r"^\[(.+)\s+for\s+(\w+)\s+in\s+(.+?)(?:\s+if\s+(.+))?\]$", expr)
        if m:
            body_e, var, iter_e, cond_e = m.group(1), m.group(2), m.group(3), m.group(4)
            iterable = self.eval_expr(iter_e.strip(), env)
            result = []
            for item in iterable:
                local = Environment(env)
                local.define(var, item)
                if cond_e is None or self.eval_expr(cond_e.strip(), local):
                    result.append(self.eval_expr(body_e.strip(), local))
            return result

        if "->" in expr and not expr.startswith("f "):
            left, right = expr.split("->", 1)
            params = [p.strip() for p in left.split() if p.strip()]
            body = right.strip()
            def make_lambda(ps, bd, clos):
                def lam(*args):
                    local = Environment(clos)
                    for p, a in zip(ps, args):
                        local.define(p, a)
                    return self.eval_expr(bd, local)
                return lam
            return make_lambda(params, body, env)

        if len(expr) >= 2 and expr[0] in "\"'" and expr[-1] == expr[0]:
            s = expr[1:-1]
            def repl(m):
                key = m.group(1)
                try:
                    return str(env.get(key))
                except TokError:
                    return m.group(0)
            s = re.sub(r"\{(\w+)\}", repl, s)
            return s

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

        m = re.match(r"^(.+)\[(.+)\]$", expr)
        if m:
            obj = self.eval_expr(m.group(1).strip(), env)
            key = self.eval_expr(m.group(2).strip(), env)
            try:
                return obj[key]
            except Exception as e:
                raise TokError(f"Index error: {e}", self.current_line)

        m = re.match(r"^([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)\.([a-zA-Z_]\w*)$", expr)
        if m:
            base = self.eval_expr(m.group(1), env)
            attr = m.group(2)
            if isinstance(base, TokRecord):
                return getattr(base, attr)
            if isinstance(base, dict):
                return base.get(attr)
            return getattr(base, attr, None)

        m = re.match(r"^([a-zA-Z_][\w]*)\((.*)\)$", expr, re.DOTALL)
        if m:
            fname, args_s = m.group(1), m.group(2).strip()
            args = [self.eval_expr(a, env) for a in self._split(args_s)] if args_s else []
            return self._call(fname, args, env)

        for ops in (("or",), ("and",), ("==", "!=", "<=", ">=", "<", ">"), ("+", "-"), ("*", "/", "%")):
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

        parts = self._smart_split(expr)
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
            raise TokError(f"Unknown: {expr}", self.current_line)

    def _smart_split(self, s: str) -> List[str]:
        parts, cur, in_str = [], [], None
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
            elif c.isspace() and not in_str:
                if cur:
                    parts.append("".join(cur))
                    cur = []
            else:
                cur.append(c)
            i += 1
        if cur:
            parts.append("".join(cur))
        return parts

    def _eval_dict(self, inner: str, env: Environment) -> dict:
        if not inner:
            return {}
        result = {}
        for part in self._split(inner):
            if ":" not in part:
                raise TokError(f"Bad dict entry: {part}", self.current_line)
            k_s, v_s = part.split(":", 1)
            result[self.eval_expr(k_s.strip(), env)] = self.eval_expr(v_s.strip(), env)
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
            raise TokError(f"Undefined function '{name}'", self.current_line)
        if isinstance(fn, TokFunction):
            return fn(self, args)
        if callable(fn):
            return fn(*args)
        raise TokError(f"'{name}' not callable", self.current_line)

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
        self.current_line = idx + 1
        s = line.strip()
        if not s or s.startswith("#"):
            return None

        if s.startswith("import ") or s.startswith("use "):
            mod = s.split(" ", 1)[1].strip().strip("\"'")
            return self._import(mod, env)

        if s.startswith("record ") or s.startswith("class "):
            return self._def_record(s, all_lines, idx, env)

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
            m = re.match(r"^(.+)\[(.+)\]$", name)
            if m:
                obj = self.eval_expr(m.group(1).strip(), env)
                key = self.eval_expr(m.group(2).strip(), env)
                val = self.eval_expr(right.strip(), env)
                obj[key] = val
                return val

        if s.startswith("i ") or s.startswith("if "):
            return self._if(s, all_lines, idx, env)

        if s.startswith("w ") or s.startswith("while "):
            return self._while(s, all_lines, idx, env)

        if s.startswith("f ") and " in " in s and ":" in s:
            return self._for_in(s, all_lines, idx, env)

        if s.startswith("f ") and ".." in s:
            return self._for_range(s, all_lines, idx, env)

        if s.startswith("f ") and ":" in s:
            return self._def_func(s, all_lines, idx, env)

        return self.eval_expr(s, env)

    def _import(self, mod: str, env: Environment):
        path = mod if mod.endswith(".tok") else mod + ".tok"
        if not os.path.exists(path):
            for candidate in (path, os.path.join("examples", path), os.path.join(os.path.dirname(__file__) or ".", path)):
                if os.path.exists(candidate):
                    path = candidate
                    break
            else:
                raise TokError(f"Module not found: {mod}", self.current_line)
        if path in self.loaded_modules:
            return None
        self.loaded_modules.add(path)
        with open(path, encoding="utf-8") as f:
            source = f.read()
        self.run(source)
        return f"imported {path}"

    def _def_record(self, header: str, lines: List[str], idx: int, env: Environment):
        if ":" not in header:
            raise TokError("record needs :", self.current_line)
        left, first = header.split(":", 1)
        parts = re.sub(r"^(record|class)\s+", "", left).strip().split()
        if not parts:
            raise TokError("record needs a name", self.current_line)
        name = parts[0]
        fields = parts[1:]
        body = []
        if first.strip():
            body.append(first.strip())
        body.extend(self._body(lines, idx))

        def make_ctor(field_names, methods_body):
            def ctor(*args):
                data = {}
                for i, f in enumerate(field_names):
                    data[f] = args[i] if i < len(args) else None
                return TokRecord(data)
            return ctor
        env.define(name, make_ctor(fields, body))
        return None

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
            raise TokError("if needs :", self.current_line)
        cond_s, first = header.split(":", 1)
        cond_s = re.sub(r"^(i|if)\s+", "", cond_s).strip()
        cond = self.eval_expr(cond_s, env)
        body = []
        if first.strip():
            body.append(first.strip())
        body.extend(self._body(lines, idx))
        else_body = []
        base = len(lines[idx]) - len(lines[idx].lstrip())
        j = idx + 1
        while j < len(lines):
            l = lines[j]
            if not l.strip() or l.strip().startswith("#"):
                j += 1
                continue
            ind = len(l) - len(l.lstrip())
            if ind > base:
                j += 1
                continue
            break
        if j < len(lines):
            es = lines[j].strip()
            if es.startswith(("e:", "else:", "e ", "else ")):
                if ":" in es:
                    _, efirst = es.split(":", 1)
                    if efirst.strip():
                        else_body.append(efirst.strip())
                else_body.extend(self._body(lines, j))
        if cond:
            return self.execute_block(body, env)
        if else_body:
            return self.execute_block(else_body, env)
        return None

    def _while(self, header: str, lines: List[str], idx: int, env: Environment) -> Any:
        if ":" not in header:
            raise TokError("while needs :", self.current_line)
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
            raise TokError("Use: f i = 1..5:", self.current_line)
        var, a, b = m.group(1), int(m.group(2)), int(m.group(3))
        body = self._body(lines, idx)
        result = None
        step = 1 if b >= a else -1
        for val in range(a, b + step, step):
            env.set(var, val)
            result = self.execute_block(body, env)
        return result

    def _for_in(self, header: str, lines: List[str], idx: int, env: Environment) -> Any:
        m = re.match(r"f\s+(\w+)\s+in\s+(.+):", header)
        if not m:
            raise TokError("Use: f x in xs:", self.current_line)
        var, iter_expr = m.group(1), m.group(2).strip()
        iterable = self.eval_expr(iter_expr, env)
        body = self._body(lines, idx)
        result = None
        for val in iterable:
            env.set(var, val)
            result = self.execute_block(body, env)
        return result

    def _def_func(self, header: str, lines: List[str], idx: int, env: Environment) -> Any:
        if ":" not in header:
            raise TokError("Function needs :", self.current_line)
        left, first = header.split(":", 1)
        parts = re.sub(r"^f\s+", "", left).strip().split()
        if not parts:
            raise TokError("Function needs name", self.current_line)
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
                    s.startswith(("i ", "if ", "w ", "while ", "record ", "class ")) or
                    (s.startswith("f ") and (":" in s)) or
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
