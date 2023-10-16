from opcode import OpCode
from debug import disassemble_instruction

class InterpretResult:
    INTERPRET_OK = 0
    INTERPRET_COMPILE_ERROR = INTERPRET_OK + 1
    INTERPRET_RUNTIME_ERROR = INTERPRET_COMPILE_ERROR + 1


class VM:
    chunk = None
    stack = None
    stack_top = 0

    ip = 0

    debug_trace = True

    STACK_MAX_SIZE = 8

    def __init__(self, debug=True):
        self.debug_trace = debug
        self._reset_stack()

    def _reset_stack(self):
        self.stack = [None] * self.STACK_MAX_SIZE
        self.stack_top = 0

    def _push_stack(self, value):
        self.stack[self.stack_top] = value
        self.stack_top += 1

    def _pop_stack(self):
        self.stack_top -= 1
        return self.stack[self.stack_top]

    def _trace_stack(self):
        print "       ",
        if self.stack_top == 0:
            print "[]"
            return

        print "[",
        for i in range(self.stack_top):
            print self.stack[i],
        print "]"

    def interpret(self, chunk):
        self.chunk = chunk
        self.ip = 0
        return self.run()

    def run(self):
        instruction = None
        while True:
            if self.debug_trace:
                disassemble_instruction(self.chunk, self.ip)
                self._trace_stack()

            instruction = self._read_byte()
            if instruction == OpCode.OP_RETURN:
                print self._pop_stack()
                return InterpretResult.INTERPRET_OK
            elif instruction == OpCode.OP_CONSTANT:
                w_const = self._read_constant()
                self._push_stack(w_const)
            elif instruction == OpCode.OP_NEGATE:
                self._push_stack(-self._pop_stack())
            elif instruction == OpCode.OP_ADD:
                self._binary_op("+")
            elif instruction == OpCode.OP_SUBTRACT:
                self._binary_op("-")
            elif instruction == OpCode.OP_MULTIPLY:
                self._binary_op("*")
            elif instruction == OpCode.OP_DIVIDE:
                self._binary_op("/")
            else:
                print "Unknown opcode"
                return InterpretResult.INTERPRET_RUNTIME_ERROR

    def _read_byte(self):
        instruction = self.chunk.code[self.ip]
        self.ip += 1
        return instruction

    def _read_constant(self):
        constant_index = self._read_byte()
        return self.chunk.constants[constant_index]

    def _binary_op(self, op):
        if op == "+":
            w_y = self._pop_stack()
            w_x = self._pop_stack()
            self._push_stack(w_x + w_y)
        elif op == "-":
            w_y = self._pop_stack()
            w_x = self._pop_stack()
            self._push_stack(w_x - w_y)
        elif op == "*":
            w_y = self._pop_stack()
            w_x = self._pop_stack()
            self._push_stack(w_x * w_y)
        elif op == "/":
            w_y = self._pop_stack()
            w_x = self._pop_stack()
            self._push_stack(w_x / w_y)
