#!/usr/bin/env python3
"""
Tok Language - Version 0.2
Ultra-token-efficient experimental language.
Python bootstrap interpreter (the language itself aims to be denser than Python).
"""

import sys
import re
from typing import Any, Dict, List, Optional

VERSION = "0.2"


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
        raise TokError(f"Undefined name '{name}'")

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

    def __call__(self, interpreter: "Interpreter", args: List[Any]) -> Any:
        if len(args) != len(self.params):
            raise TokError(f"Function {self.name} expected {len(self.params)} args, got {len(args)}")
        local = Environment(self.closure)
        for p, a in zip(self.params, args):
            local.define(p, a)
        return interpreter.execute_block(self.body, local)


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.env = self.global_env
        self._setup_builtins()

    def _setup_builtins(self):
        self.global_env.define("true", True)
        self.global_env.define("false", False)
        self.global_env.define("none", None)
        self.global_env.define("len", len)
        self.global_env.define("str", str)
        self.global_env.define("int", int)
        self.global_env.define("float", float)
        self.global_env.define("list", list)
        self.global_env.define("range", range)

    def eval_expr(self, expr: str, env: Optional[Environment] = None) -> Any:
        env = env or self.env
        expr = expr.strip()
        if not expr:
            return None

        # String
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        # Number
        try:
            if "." in expr:
                return float(expr)
            return int(expr)
        except ValueError:
            pass

        # List literal [1, 2, 3]
        if expr.startswith("[") and expr.endswith("]"):
            inner = expr[1:-1].strip()
            if not inner:
                return []
            parts = self._split_args(inner)
            return [self.eval_expr(p, env) for p in parts]

        # Function call with parentheses: name(arg1, arg2)
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\((.*)\)$", expr)
        if m:
            fname = m.group(1)
            args_str = m.group(2).strip()
            args = []
            if args_str:
                args = [self.eval_expr(a, env) for a in self._split_args(args_str)]
            return self.call_function(fname, args, env)

        # Binary operators (simple left-to-right)
        for op in ("==", "!=", "<=", ">=", "and", "or", "<", ">", "+", "-", "*", "/", "%"):
            if op in ("and", "or"):
                parts = re.split(rf"\s+{op}\s+", expr, maxsplit=1)
            else:
                parts = expr.split(op, 1)
            if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                left = self.eval_expr(parts[0].strip(), env)
                right = self.eval_expr(parts[1].strip(), env)
                if op == "+": return left + right
                if op == "-": return left - right
                if op == "*": return left * right
                if op == "/": return left / right
                if op == "%": return left % right
                if op == "==": return left == right
                if op == "!=": return left != right
                if op == "<": return left < right
                if op == ">": return left > right
                if op == "<=": return left <= right
                if op == ">=": return left >= right
                if op == "and": return left and right
                if op == "or": return left or right

        # Unary not
        if expr.startswith("not "):
            return not self.eval_expr(expr[4:].strip(), env)

        # Space-separated call: add 3 4
        parts = expr.split()
        if len(parts) >= 1:
            name = parts[0]
            try:
                val = env.get(name)
                if callable(val) or isinstance(val, TokFunction):
                    args = [self.eval_expr(a, env) for a in parts[1:]]
                    return self.call_function(name, args, env)
            except TokError:
                pass

        # Variable lookup
        try:
            return env.get(expr)
        except TokError:
            raise TokError(f"Unknown expression or name: {expr}")

    def _split_args(self, s: str) -> List[str]:
        args = []
        current = []
        depth = 0
        for c in s:
            if c in "([{":
                depth += 1
                current.append(c)
            elif c in ")]}":
                depth -= 1
                current.append(c)
            elif c == "," and depth == 0:
                args.append("".join(current).strip())
                current = []
            else:
                current.append(c)
        if current:
            args.append("".join(current).strip())
        return args

    def call_function(self, name: str, args: List[Any], env: Environment) -> Any:
        try:
            fn = env.get(name)
        except TokError:
            raise TokError(f"Undefined function '{name}'")
        if isinstance(fn, TokFunction):
            return fn(self, args)
        if callable(fn):
            return fn(*args)
        raise TokError(f"'{name}' is not callable")

    def execute_block(self, lines: List[str], env: Environment) -> Any:
        old_env = self.env
        self.env = env
        result = None
        try:
            i = 0
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    i += 1
                    continue
                result = self.execute_line(line, lines, i, env)
                i += 1
        finally:
            self.env = old_env
        return result

    def execute_line(self, line: str, all_lines: List[str], idx: int, env: Environment) -> Any:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            return None

        # print
        if stripped.startswith("p ") or stripped.startswith("print "):
            rest = stripped.split(" ", 1)[1]
            val = self.eval_expr(rest, env)
            print(val)
            return val

        # return
        if stripped.startswith("r ") or stripped.startswith("return "):
            rest = stripped.split(" ", 1)[1]
            return self.eval_expr(rest, env)

        # assignment
        if "=" in stripped and not any(op in stripped for op in ("==", "!=", "<=", ">=")):
            left, right = stripped.split("=", 1)
            name = left.strip()
            if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
                val = self.eval_expr(right.strip(), env)
                env.set(name, val)
                return val

        # if
        if stripped.startswith("i ") or stripped.startswith("if "):
            return self._handle_if(stripped, all_lines, idx, env)

        # simple for: f i = 1..5:
        if stripped.startswith("f ") and ".." in stripped:
            return self._handle_simple_for(stripped, all_lines, idx, env)

        # function definition
        if stripped.startswith("f ") and ":" in stripped:
            return self._handle_function_def(stripped, all_lines, idx, env)

        # expression
        return self.eval_expr(stripped, env)

    def _collect_body(self, lines: List[str], idx: int) -> List[str]:
        body = []
        base_indent = len(lines[idx]) - len(lines[idx].lstrip())
        j = idx + 1
        while j < len(lines):
            l = lines[j]
            if not l.strip() or l.strip().startswith("#"):
                j += 1
                continue
            ind = len(l) - len(l.lstrip())
            if ind > base_indent:
                body.append(l)
                j += 1
            else:
                break
        return body

    def _handle_if(self, header: str, lines: List[str], idx: int, env: Environment) -> Any:
        if ":" not in header:
            raise TokError("if needs ':'")
        cond_part, first = header.split(":", 1)
        cond_part = re.sub(r"^(i|if)\s+", "", cond_part).strip()
        cond = self.eval_expr(cond_part, env)

        body = []
        if first.strip():
            body.append(first.strip())
        body.extend(self._collect_body(lines, idx))

        if cond:
            return self.execute_block(body, env)
        return None

    def _handle_simple_for(self, header: str, lines: List[str], idx: int, env: Environment) -> Any:
        m = re.match(r"f\s+(\w+)\s*=\s*(\d+)\.\.(\d+)\s*:", header)
        if not m:
            raise TokError("Invalid for. Use: f i = 1..5:")
        var, start, end = m.group(1), int(m.group(2)), int(m.group(3))
        body = self._collect_body(lines, idx)
        result = None
        for val in range(start, end + 1):
            env.set(var, val)
            result = self.execute_block(body, env)
        return result

    def _handle_function_def(self, header: str, lines: List[str], idx: int, env: Environment) -> Any:
        if ":" not in header:
            raise TokError("Function needs ':'")
        left, first = header.split(":", 1)
        parts = re.sub(r"^f\s+", "", left).strip().split()
        if not parts:
            raise TokError("Function needs a name")
        fname = parts[0]
        params = parts[1:]

        body = []
        if first.strip():
            body.append(first.strip())
        body.extend(self._collect_body(lines, idx))

        fn = TokFunction(fname, params, body, env)
        env.define(fname, fn)
        return None

    def run(self, source: str):
        lines = source.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                i += 1
                continue
            try:
                consumes_body = (
                    stripped.startswith("i ") or stripped.startswith("if ") or
                    (stripped.startswith("f ") and (".." in stripped or ":" in stripped))
                )
                self.execute_line(line, lines, i, self.env)
                if consumes_body:
                    base = len(line) - len(line.lstrip())
                    i += 1
                    while i < len(lines):
                        l = lines[i]
                        if not l.strip():
                            i += 1
                            continue
                        ind = len(l) - len(l.lstrip())
                        if ind > base:
                            i += 1
                        else:
                            break
                    continue
            except TokError as e:
                print(f"TokError: {e}")
            except Exception as e:
                print(f"Error on line {i+1}: {e}")
            i += 1

    def repl(self):
        print(f"Tok v{VERSION} REPL  (exit / quit to leave)")
        while True:
            try:
                line = input("tok> ")
                if line.strip() in ("exit", "quit"):
                    break
                if not line.strip():
                    continue
                result = self.execute_line(line, [line], 0, self.env)
                if result is not None and not line.strip().startswith(("p ", "print ")):
                    print(result)
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
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            interp.run(f.read())
    else:
        interp.repl()


if __name__ == "__main__":
    main()
