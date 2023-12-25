from lox.compiler import Compiler
from lox.opcode import OpCode
from lox.debug import disassemble_instruction, format_line_number
from lox.value import W_Number, W_Bool, W_Nil

class InterpretResult:
    INTERPRET_OK = 0
    INTERPRET_COMPILE_ERROR = INTERPRET_OK + 1
    INTERPRET_RUNTIME_ERROR = INTERPRET_COMPILE_ERROR + 1


class VM(object):
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

    def _peek_stack(self, n):
        assert n <= self.stack_top
        return self.stack[self.stack_top - n]

    def _trace_stack(self):
        print "       ",
        if self.stack_top == 0:
            print "[]"
            return

        print "[",
        for i in range(self.stack_top):
            print self.stack[i],
        print "]"

    def _runtime_error(self, message):
        line_number = format_line_number(self.chunk, self.ip)
        print "%s\n[line %s] in script" % (message, line_number)
        self._reset_stack()

    def interpret_chunk(self, chunk):
        self.chunk = chunk
        self.ip = 0
        return self.run()

    def interpret(self, source):
        self._reset_stack()

        compiler = Compiler(source, debug_print=self.debug_trace)
        if compiler.compile():
            # print compiler.current_chunk().disassemble("code")
            return self.interpret_chunk(compiler.current_chunk())
        else:
            return InterpretResult.INTERPRET_COMPILE_ERROR

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
            elif instruction == OpCode.OP_NIL:
                self._push_stack(W_Nil())
            elif instruction == OpCode.OP_TRUE:
                self._push_stack(W_Bool(True))
            elif instruction == OpCode.OP_FALSE:
                self._push_stack(W_Bool(False))
            elif instruction == OpCode.OP_NOT:
                self._push_stack(W_Bool(self._pop_stack().is_falsy()))
            elif instruction == OpCode.OP_EQUAL:
                self._binary_op("==")
            elif instruction == OpCode.OP_LESS:
                self._binary_op("<")
            elif instruction == OpCode.OP_GREATER:
                self._binary_op(">")
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
            elif instruction == OpCode.OP_NEGATE:
                if not self._peek_stack(0).is_number():
                    self._runtime_error("Runtime error")
                    return InterpretResult.INTERPRET_RUNTIME_ERROR
                self._push_stack(W_Number(-self._pop_stack().as_number()))
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
            self._push_stack(w_x.add(w_y))
        elif op == "-":
            w_y = self._pop_stack()
            w_x = self._pop_stack()
            self._push_stack(w_x.sub(w_y))
        elif op == "*":
            w_y = self._pop_stack()
            w_x = self._pop_stack()
            self._push_stack(w_x.mul(w_y))
        elif op == "/":
            w_y = self._pop_stack()
            w_x = self._pop_stack()
            self._push_stack(w_x.div( w_y))
        elif op == "<":
            w_y = self._pop_stack()
            w_x = self._pop_stack()
            w_z = W_Bool(w_x.as_number() < w_y.as_number())
            self._push_stack(w_z)
        elif op == ">":
            w_y = self._pop_stack()
            w_x = self._pop_stack()
            w_z = W_Bool(w_x.as_number() > w_y.as_number())
            self._push_stack(w_z)
        elif op == "==":
            w_y = self._pop_stack()
            w_x = self._pop_stack()
            w_z = W_Bool(w_x.as_number() == w_y.as_number())
            self._push_stack(w_z)
