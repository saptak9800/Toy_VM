from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Instruction:
    op: str
    arg: Optional[Any] = None


class VMError(Exception):
    pass


class VM:
    def __init__(self, program: List[Instruction], trace: bool = False):
        self.program = program
        self.ip = 0  # instruction pointer
        self.stack: List[Any] = []
        self.mem: Dict[str, Any] = {}
        self.trace = trace

    def debug(self, msg: str) -> None:
        if self.trace:
            print(f"[ip={self.ip}] {msg} | stack={self.stack} mem={self.mem}")

    def fetch(self) -> Instruction:
        if not (0 <= self.ip < len(self.program)):
            raise VMError(f"IP out of range: {self.ip}")
        return self.program[self.ip]

    def step(self) -> bool:
        instr = self.fetch()
        op = instr.op
        arg = instr.arg
        self.debug(f"EXEC {op} {arg if arg is not None else ''}")

        # Arithmetic and stack ops
        if op == "PUSH":
            self.stack.append(arg)
        elif op == "ADD":
            b = self._pop_int(); a = self._pop_int(); self.stack.append(a + b)
        elif op == "SUB":
            b = self._pop_int(); a = self._pop_int(); self.stack.append(a - b)
        elif op == "MUL":
            b = self._pop_int(); a = self._pop_int(); self.stack.append(a * b)
        elif op == "DIV":
            b = self._pop_int(); a = self._pop_int();
            if b == 0:
                raise VMError("Division by zero")
            self.stack.append(a // b)
        elif op == "DUP":
            self._require_stack(1)
            self.stack.append(self.stack[-1])
        elif op == "SWAP":
            self._require_stack(2)
            self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]

        # Memory
        elif op == "STORE":
            self._require_type(arg, str, "STORE expects variable name")
            val = self._pop()
            self.mem[arg] = val
        elif op == "LOAD":
            self._require_type(arg, str, "LOAD expects variable name")
            if arg not in self.mem:
                raise VMError(f"Undefined variable: {arg}")
            self.stack.append(self.mem[arg])

        # Control flow
        elif op == "JMP":
            self._require_type(arg, int, "JMP expects target index")
            self.ip = arg
            return True
        elif op == "JZ":
            self._require_type(arg, int, "JZ expects target index")
            val = self._pop_int()
            if val == 0:
                self.ip = arg
                return True
        elif op == "JNZ":
            self._require_type(arg, int, "JNZ expects target index")
            val = self._pop_int()
            if val != 0:
                self.ip = arg
                return True

        elif op == "PRINT":
            val = self._pop()
            print(val)
        elif op == "HALT":
            return False
        else:
            raise VMError(f"Unknown opcode: {op}")

        self.ip += 1
        return True

    def run(self) -> None:
        while self.step():
            pass

    # Helpers
    def _pop(self) -> Any:
        self._require_stack(1)
        return self.stack.pop()

    def _pop_int(self) -> int:
        v = self._pop()
        if not isinstance(v, int):
            raise VMError(f"Expected integer, got {type(v).__name__}")
        return v

    def _require_stack(self, n: int) -> None:
        if len(self.stack) < n:
            raise VMError(f"Stack underflow: need {n}, have {len(self.stack)}")

    def _require_type(self, val: Any, typ: type, msg: str) -> None:
        if not isinstance(val, typ):
            raise VMError(msg)
