import io
import sys
import unittest

from toyvm.assembler import assemble
from toyvm.vm import VM, Instruction


class TestVM(unittest.TestCase):
    def capture_output(self):
        return io.StringIO()

    def test_arithmetic(self):
        prog = [
            Instruction('PUSH', 2),
            Instruction('PUSH', 3),
            Instruction('ADD'),
            Instruction('PRINT'),
            Instruction('HALT'),
        ]
        buf = self.capture_output()
        sys_stdout = sys.stdout
        try:
            sys.stdout = buf
            VM(prog).run()
        finally:
            sys.stdout = sys_stdout
        self.assertEqual(buf.getvalue().strip(), '5')

    def test_labels_and_jumps(self):
        src = """
        PUSH 2
        START:
        PUSH 1
        SUB
        DUP
        JNZ START
        PRINT
        HALT
        """
        program, labels = assemble(src)
        self.assertIn('START', labels)
        buf = self.capture_output()
        sys_stdout = sys.stdout
        try:
            sys.stdout = buf
            VM(program).run()
        finally:
            sys.stdout = sys_stdout
        self.assertEqual(buf.getvalue().strip(), '0')


if __name__ == '__main__':
    unittest.main()
