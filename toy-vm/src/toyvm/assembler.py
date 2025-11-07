from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import json
import re

from .vm import Instruction

TOKEN_RE = re.compile(r"\s*(?:(;.*)$|([A-Za-z_][A-Za-z0-9_]*)|(-?\d+)|(\"[^\"]*\"|'[^']*')|(:)|(.))")


@dataclass
class ParsedLine:
    label: Optional[str]
    op: Optional[str]
    arg: Optional[Any]
    source_idx: int


def tokenize(line: str) -> List[str]:
    tokens: List[str] = []
    i = 0
    while i < len(line):
        m = TOKEN_RE.match(line, i)
        if not m:
            break
        i = m.end()
        if m.group(1):  # comment
            break
        if m.group(2):  # identifier
            tokens.append(m.group(2))
            continue
        if m.group(3):  # integer
            tokens.append(int(m.group(3)))
            continue
        if m.group(4):  # string literal
            s = m.group(4)
            if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
                tokens.append(s[1:-1])
                continue
        if m.group(5):  # colon
            tokens.append(':')
            continue
        if m.group(6):  # other single char
            tokens.append(m.group(6))
            continue
    return tokens


def parse_lines(src: str) -> List[ParsedLine]:
    lines = src.splitlines()
    parsed: List[ParsedLine] = []
    for i, raw in enumerate(lines):
        tokens = tokenize(raw)
        if not tokens:
            continue
        # label:
        label = None
        if len(tokens) >= 2 and isinstance(tokens[0], str) and tokens[1] == ':':
            label = tokens[0]
            tokens = tokens[2:]
            if not tokens:
                parsed.append(ParsedLine(label, None, None, i))
                continue
        op = tokens[0] if tokens else None
        arg = tokens[1] if len(tokens) > 1 else None
        if isinstance(op, str):
            op = op.upper()
        parsed.append(ParsedLine(label, op, arg, i))
    return parsed


def assemble(src: str) -> Tuple[List[Instruction], Dict[str, int]]:
    parsed = parse_lines(src)
    # First pass: label addresses
    addr = 0
    labels: Dict[str, int] = {}
    for pl in parsed:
        if pl.label is not None:
            if pl.label in labels:
                raise ValueError(f"Duplicate label {pl.label} at line {pl.source_idx+1}")
            labels[pl.label] = addr
        if pl.op is not None:
            addr += 1
    # Second pass: emit instructions
    prog: List[Instruction] = []
    for pl in parsed:
        if pl.op is None:
            continue
        op = pl.op
        arg = pl.arg
        # Resolve label operand for jumps
        if op in {"JMP", "JZ", "JNZ"}:
            if isinstance(arg, str):
                if arg not in labels:
                    raise ValueError(f"Unknown label {arg} at line {pl.source_idx+1}")
                arg = labels[arg]
            elif isinstance(arg, int):
                pass
            elif arg is None:
                raise ValueError(f"Missing label for {op} at line {pl.source_idx+1}")
            else:
                raise ValueError(f"Invalid jump target at line {pl.source_idx+1}")
        elif op in {"LOAD", "STORE"}:
            if not isinstance(arg, str):
                raise ValueError(f"{op} expects identifier at line {pl.source_idx+1}")
        elif op == "PUSH":
            if arg is None:
                raise ValueError(f"PUSH expects a value at line {pl.source_idx+1}")
            # ints or strings allowed; already parsed
        else:
            # ops with no args
            arg = None
        prog.append(Instruction(op=op, arg=arg))
    return prog, labels


def to_bytecode_json(program: List[Instruction]) -> str:
    return json.dumps([
        {"op": instr.op, "arg": instr.arg} for instr in program
    ], ensure_ascii=False, indent=2)


def from_bytecode_json(data: str) -> List[Instruction]:
    raw = json.loads(data)
    program = [Instruction(op=item["op"], arg=item.get("arg")) for item in raw]
    return program


def load_source_or_bytecode(path: str) -> List[Instruction]:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    if path.lower().endswith('.tbc'):
        return from_bytecode_json(text)
    else:
        program, _ = assemble(text)
        return program
