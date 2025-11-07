🧩 Toy VM

A tiny, educational virtual machine with a simple assembly language.

Overview

Toy VM is a small, stack-based virtual machine written in Python.
It includes a simple assembler, command-line interface, and examples for learning low-level execution concepts such as stack operations, variable storage, and branching.

✨ Features

Stack-based VM runtime (Python)

Assembler with labels and variables

Command-line interface (CLI) to assemble and run programs

Example programs and unit tests

🧠 Instruction Set (Baseline)
Instruction	Description
PUSH <value>	Push an immediate value (integer or quoted string) onto the stack
ADD, SUB, MUL, DIV	Perform arithmetic on the top two stack values (integers)
DUP, SWAP	Stack manipulation operations
LOAD <var>	Push the value of a named variable onto the stack
STORE <var>	Pop and store the top stack value into a named variable
JMP <label>	Unconditional jump
JZ <label>	Pop and jump if the value equals 0
JNZ <label>	Pop and jump if the value is not 0
PRINT	Pop and print the top stack value
HALT	Stop execution

All operations validate stack depth and types.
Meaningful errors are raised for invalid operations.

⚡ Quick Start
1. Assemble a source file (.toy) to bytecode (.tbc, JSON format)
python -m toyvm.cli assemble .\examples\hello.toy -o .\examples\hello.tbc

2. Run a program directly from source (auto-assembles in-memory)
python -m toyvm.cli run .\examples\hello.toy --trace

3. Run a pre-assembled bytecode file
python -m toyvm.cli run .\examples\hello.tbc

🔧 Optional: Installable CLI Command

If you prefer a global command, install this project in editable mode:

pip install -e .


Then you can use:

toyvm assemble .\examples\hello.toy -o .\examples\hello.tbc
toyvm run .\examples\hello.tbc

🧩 Extending the VM

To add new functionality:

Add new opcodes in src/toyvm/vm.py (update the dispatch table and semantics).

Add corresponding assembler mnemonics in src/toyvm/assembler.py.
       

🧪 Example

A simple program that prints “Hello, World!” might look like this:

PUSH "Hello, World!"
PRINT
HALT

