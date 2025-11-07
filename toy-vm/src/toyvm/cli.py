from __future__ import annotations
import argparse
from pathlib import Path
from typing import Optional

from .assembler import assemble, to_bytecode_json, load_source_or_bytecode
from .vm import VM


def cmd_assemble(args: argparse.Namespace) -> int:
    src_path = Path(args.input)
    text = src_path.read_text(encoding='utf-8')
    program, labels = assemble(text)
    out_path = Path(args.output) if args.output else src_path.with_suffix('.tbc')
    out_path.write_text(to_bytecode_json(program), encoding='utf-8')
    print(f"Assembled {src_path} -> {out_path} ({len(program)} instructions)")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    program = load_source_or_bytecode(args.input)
    vm = VM(program, trace=args.trace)
    vm.run()
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='toyvm', description='Tiny stack-based VM tool')
    sub = p.add_subparsers(dest='cmd', required=True)

    pa = sub.add_parser('assemble', help='Assemble .toy -> .tbc')
    pa.add_argument('input', help='Input .toy file')
    pa.add_argument('-o', '--output', help='Output .tbc file')
    pa.set_defaults(func=cmd_assemble)

    pr = sub.add_parser('run', help='Run a program (.toy or .tbc)')
    pr.add_argument('input', help='Program path')
    pr.add_argument('--trace', action='store_true', help='Enable execution trace')
    pr.set_defaults(func=cmd_run)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    raise SystemExit(main())
