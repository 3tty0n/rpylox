from lox.compiler import Compiler
from lox.opcodes import OpCode
from lox.debug import disassemble_instruction, format_line_number
from lox.value import ValueNil, ValueNumber, ValueBool, ValueNil, ValueObj, Value
from lox.object import ObjString, Obj

class InterpretResult:
    INTERPRET_OK = 0
    INTERPRET_COMPILE_ERROR = INTERPRET_OK + 1
    INTERPRET_RUNTIME_ERROR = INTERPRET_COMPILE_ERROR + 1


class InterpretCompileError(RuntimeError):
    pass


class InterpretRuntimeError(RuntimeError):
    pass


class VM(object):
    chunk = None
    stack = None
    stack_top = 0

    ip = 0

    global_objects = {}

    debug_trace = True

    STACK_MAX_SIZE = 8

    def __init__(self, debug=True):
        self.debug_trace = debug
        self._reset_stack()

    def _reset_stack(self):
        self.stack = [None] * self.STACK_MAX_SIZE
        self.stack_top = 0

    def _reset_global_objects(self):
        self.global_objects = {}

    def _reset(self):
        self._reset_stack()
        self._reset_global_objects()

    def _push_stack(self, value):
        self.stack[self.stack_top] = value
        self.stack_top += 1

    def _pop_stack(self):
        self.stack_top -= 1
        assert self.stack_top >= 0
        return self.stack[self.stack_top]

    def _peek_stack(self, n):
        assert n < self.stack_top
        return self.stack[self.stack_top - (n + 1)]

    def _trace_stack(self):
        print "       ",
        if self.stack_top == 0:
            print "[]"
            return

        print "[",
        for i in range(self.stack_top):
            print self.stack[i].repr(),
        print "]"

        print "       "
        # print self.global_objects

    def _runtime_error(self, message):
        line_number = format_line_number(self.chunk, self.ip)
        print "%s\n[line %s] in script" % (message, line_number)
        self._reset()

    def interpret_chunk(self, chunk):
        self.chunk = chunk
        self.ip = 0
        return self.run()

    def interpret(self, source):
        self._reset()

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
                return InterpretResult.INTERPRET_OK
            elif instruction == OpCode.OP_NOP:
                pass
            elif instruction == OpCode.OP_CONSTANT:
                w_const = self._read_constant()
                self._push_stack(w_const)
            elif instruction == OpCode.OP_NIL:
                self._push_stack(ValueNil())
            elif instruction == OpCode.OP_TRUE:
                self._push_stack(ValueBool(True))
            elif instruction == OpCode.OP_FALSE:
                self._push_stack(ValueBool(False))
            elif instruction == OpCode.OP_NOT:
                self._push_stack(ValueBool(self._pop_stack().is_falsy()))
            elif instruction == OpCode.OP_EQUAL:
                self._binary_op("==")
            elif instruction == OpCode.OP_LESS:
                self._binary_op("<")
            elif instruction == OpCode.OP_GREATER:
                self._binary_op(">")
            elif instruction == OpCode.OP_NEGATE:
                self._push_stack(self._pop_stack().negate())
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
                self._push_stack(ValueNumber(-self._pop_stack().as_number()))
            elif instruction == OpCode.OP_PRINT:
                value = self._pop_stack()
                if isinstance(value, Value) or isinstance(value, Obj):
                    print value.repr()
                else:
                    print value
            elif instruction == OpCode.OP_POP:
                self._pop_stack()
            elif instruction == OpCode.OP_DEFINE_GLOBAL:
                name = self._read_string()
                assert isinstance(name, ObjString)
                name_hash = name.hash()
                self.global_objects[name_hash] = self._pop_stack()
            elif instruction == OpCode.OP_GET_GLOBAL:
                name = self._read_string()
                assert isinstance(name, ObjString)
                name_hash = name.hash()
                if name_hash not in self.global_objects:
                    self._runtime_error("Undefined variable '%s'." % name)
                    raise InterpretRuntimeError()
                self._push_stack(self.global_objects[name_hash])
            elif instruction == OpCode.OP_SET_GLOBAL:
                name = self._read_string()
                assert isinstance(name, ObjString)
                name_hash = name.hash()
                if not name_hash in self.global_objects:
                    self._runtime_error("Undefined variable '%s'." % name)
                    raise InterpretRuntimeError()
                self.global_objects[name_hash] = self._pop_stack()
                self._push_stack(ValueNil()) # To handle with OP_POP
            elif instruction == OpCode.OP_GET_LOCAL:
                slot = self._read_byte()
                self._push_stack(self.stack[slot])
            elif instruction == OpCode.OP_SET_LOCAL:
                slot = self._read_byte()
                self.stack[slot] = self._peek_stack(0)
            elif instruction == OpCode.OP_JUMP_IF_FALSE:
                offset = self._read_short()
                if self._peek_stack(0).is_falsy():
                    self.ip += offset
            elif instruction == OpCode.OP_JUMP:
                offset = self._read_short()
                self.ip += offset
            elif instruction == OpCode.OP_LOOP: # backward jump
                offset = self._read_short()
                self.ip -= offset
            else:
                print "Unknown opcode"
                raise InterpretRuntimeError()

    def _read_byte(self):
        instruction = self.chunk.code[self.ip]
        self.ip += 1
        return instruction

    def _read_short(self):
        offset1 = self.chunk.code[self.ip]
        offset2 = self.chunk.code[self.ip + 1]
        self.ip += 2
        return offset1 << 8 | offset2


    def _read_constant(self):
        constant_index = self._read_byte()
        return self.chunk.constants[constant_index]

    def _read_string(self):
        w_const = self._read_constant()
        assert isinstance(w_const, ValueObj)
        obj_str = w_const.get_value()
        isinstance(obj_str, ObjString)
        return obj_str

    def _binary_op(self, op):
        if op == "+":
            w_y = self._pop_stack()
            w_x = self._pop_stack()
            if w_x.is_string() and w_y.is_string():
                self._concatinate(w_x, w_y)
            elif w_x.is_number() and w_y.is_number():
                self._push_stack(w_x.add(w_y))
            else:
                self._runtime_error("Operands must be two numbers or two strings.")
                raise InterpretRuntimeError()
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
            w_z = ValueBool(w_x.as_number() < w_y.as_number())
            self._push_stack(w_z)
        elif op == ">":
            w_y = self._pop_stack()
            w_x = self._pop_stack()
            w_z = ValueBool(w_x.as_number() > w_y.as_number())
            self._push_stack(w_z)
        elif op == "==":
            w_y = self._pop_stack()
            w_x = self._pop_stack()
            w_z = ValueBool(w_x.as_number() == w_y.as_number())
            self._push_stack(w_z)

    def _concatinate(self, w_x, w_y):
        assert isinstance(w_x, ValueObj)
        assert isinstance(w_y, ValueObj)
        obj_str1 = w_x.get_value()
        obj_str2 = w_y.get_value()
        w_z = ValueObj(obj_str1.concat(obj_str2))
        self._push_stack(w_z)
