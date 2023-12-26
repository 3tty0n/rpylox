from lox.debug import disassemble_instruction
from lox.value import Value, ValueArray


class Chunk:
    def __init__(self):
        self.count = 0
        self.capacity = 0
        self.code = []
        self.lines = []
        self.constants = ValueArray()

    def write_chunk(self, byte, line):
        self.code.append(byte)
        self.count += 1
        self.lines.append(line)

    def disassemble(self, name):
        print "== %s ==\n" % name,
        i = 0
        while i < len(self.code):
            i = disassemble_instruction(self, i)

    def free_chunk(self):
        self.count = 0
        self.capacity = 0
        self.code = []
        self.lines = []

    def add_constant(self, value):
        self.constants.append(value)
        return len(self.constants) - 1

    def get_count(self):
        return self.count

    def set_to_code(self, offset, value):
        self.code[offset] = value
