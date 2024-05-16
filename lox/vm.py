from lox.compiler import Compiler
from lox.opcodes import OpCode
from lox.debug import disassemble_instruction, format_line_number, get_printable_location
from lox.value import ValueNil, ValueNumber, ValueBool, ValueNil, ValueObj, Value
from lox.object import ObjString, Obj, ObjFunction

from rpython.rlib import jit
from rpython.rlib.jit import JitDriver, we_are_translated, we_are_jitted


jitdriver = JitDriver(greens=['ip', 'chunk',],
                      reds=['stack_top', 'stack', 'frame', 'self'],
                      get_printable_location=get_printable_location)


def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()


class InterpretResult:
    INTERPRET_OK = 0
    INTERPRET_COMPILE_ERROR = INTERPRET_OK + 1
    INTERPRET_RUNTIME_ERROR = INTERPRET_COMPILE_ERROR + 1


class InterpretCompileError(RuntimeError):
    pass


class InterpretRuntimeError(RuntimeError):
    pass


class CallFrame(object):
    def __init__(self, function, ip, slots):
        self.function = function
        self.ip = ip
        self.slots = slots

    # def pop_slot(self):
    #     slot_top = jit.promote(self.slot_top)
    #     w_x = self.slots[slot_top]
    #     slot_top -= 1
    #     self.slots[slot_top] = None
    #     self.slot_top = slot_top
    #     return w_x

    # def push_slot(self, w_x):
    #     slot_top = jit.promote(self.stlot_top)
    #     self.slots[slot_top] = w_x
    #     self.stack_top = stack_top + 1


class VM(object):
    _immutable_fields_ = ['chunk', 'STACK_MAX_SIZE', 'FRAMES_MAX']

    global_objects = {}
    STACK_MAX_SIZE = 16
    FRAMES_MAX = 64

    def __init__(self, debug=True):
        self.debug_trace = debug
        self._reset_stack()

        # self.FRAMES_MAX = 64
        # self.frames = [None] * self.FRAMES_MAX

        self.chunk = None
        self.stack = None
        self.stack_top = 0

        self.frames = [None] * self.FRAMES_MAX
        self.frame_ptr = 0
        self.frame = None

        # self.ip = 0 # Moved to CallFrame

    def _reset_stack(self):
        self.stack = [None] * self.STACK_MAX_SIZE
        self.stack_top = 0

    def _reset_global_objects(self):
        self.global_objects = {}

    def _reset(self):
        self._reset_stack()
        self._reset_global_objects()

    def _push_stack(self, value):
        stack_top = jit.promote(self.stack_top)
        self.stack[stack_top] = value
        self.stack_top = stack_top + 1

    def _pop_stack(self):
        stack_top = jit.promote(self.stack_top)
        stack_top -= 1
        assert stack_top >= 0
        self.stack_top = stack_top
        return self.stack[stack_top]

    def _peek_stack(self, n):
        stack_top = jit.promote(self.stack_top)
        assert n < stack_top
        return self.stack[stack_top - (n + 1)]

    def _take_stack(self, n):
        assert n < self.stack_top
        assert 0 <= n
        return self.stack[n]

    def _trace_stack(self):
        print "       ",
        if self.stack_top == 0:
            print "[]"
            return

        print "[",
        for i in range(self.stack_top):
            w_x = self.stack[i]
            if w_x: print w_x.repr(),
            else: print "None",
        print "]"

        # print "       ",
        # print self.global_objects

    def _runtime_error(self, message):
        line_number = format_line_number(self.frame.function.chunk, self.frame.ip)
        print "%s\n[line %s] in script" % (message, line_number)
        self._reset()

    # def interpret_chunk(self, chunk):
    #     self.chunk = chunk
    #     self.ip = 0
    #     return self.run()

    def _read_byte(self):
        chunk = self.frame.function.chunk
        jit.promote(chunk)
        instruction = chunk.code[self.frame.ip]
        self.frame.ip += 1
        return instruction

    def _read_short(self):
        chunk = self.frame.function.chunk
        jit.promote(chunk)
        offset1 = chunk.code[self.frame.ip]
        offset2 = chunk.code[self.frame.ip + 1]
        self.frame.ip += 2
        return offset1 << 8 | offset2

    def _read_constant(self):
        constant_index = self._read_byte()
        return self.frame.function.chunk.constants[constant_index]

    def _read_string(self):
        w_const = self._read_constant()
        assert isinstance(w_const, ValueObj)
        obj_str = w_const.get_value()
        isinstance(obj_str, ObjString)
        return obj_str

    def interpret(self, source):
        self._reset()

        compiler = Compiler(source, debug_print=self.debug_trace)
        function = compiler.compile()
        if function:
            self._push_stack(ValueObj(function))
            self.frame = CallFrame(function=function, ip=0, slots=self.stack[:])
            self.frames[self.frame_ptr] = self.frame
            self.frame_ptr += 1
            return self.run()
        else:
            return InterpretResult.INTERPRET_COMPILE_ERROR

    def run(self):
        instruction = None
        self.frame_ptr -= 1
        self.frame = self.frames[self.frame_ptr]
        if we_are_jitted():
            self.frames[self.frame_ptr + 1] = None
        while True:
            if not we_are_translated():
                if self.debug_trace:
                    disassemble_instruction(self.frame.function.chunk, self.frame.ip)
                    self._trace_stack()

            jitdriver.jit_merge_point(ip=self.frame.ip, chunk=self.frame.function.chunk,
                                      stack=self.stack, stack_top=self.stack_top,
                                      frame=self.frame, self=self)

            instruction = self._read_byte()
            if instruction == OpCode.OP_RETURN:
                return InterpretResult.INTERPRET_OK
            elif instruction == OpCode.OP_NOP:
                pass
            elif instruction == OpCode.OP_CONSTANT:
                self._constant()
            elif instruction == OpCode.OP_NIL:
                self._push_stack(ValueNil())
            elif instruction == OpCode.OP_TRUE:
                self._push_stack(ValueBool(True))
            elif instruction == OpCode.OP_FALSE:
                self._push_stack(ValueBool(False))
            elif instruction == OpCode.OP_NOT:
                self._unary_op("!")
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
                self._unary_op("-")
            elif instruction == OpCode.OP_PRINT:
                self._print()
            elif instruction == OpCode.OP_POP:
                self._pop_stack()
            elif instruction == OpCode.OP_DEFINE_GLOBAL:
                self._define_global()
            elif instruction == OpCode.OP_GET_GLOBAL:
                self._get_global()
            elif instruction == OpCode.OP_SET_GLOBAL:
                self._set_global()
            elif instruction == OpCode.OP_GET_LOCAL:
                self._get_local()
            elif instruction == OpCode.OP_SET_LOCAL:
                self._set_local()
            elif instruction == OpCode.OP_JUMP_IF_FALSE:
                offset = self._read_short()
                if self._peek_stack(0).is_falsy():
                    self.frame.ip += offset
            elif instruction == OpCode.OP_JUMP:
                offset = self._read_short()
                self.frame.ip += offset
            elif instruction == OpCode.OP_LOOP: # backward jump
                offset = self._read_short()
                self.frame.ip -= offset
                jitdriver.can_enter_jit(ip=self.ip, chunk=self.chunk,
                                        stack=self.stack, stack_top=self.stack_top,
                                        frame=self.frame, self=self)
            elif instruction == OpCode.OP_CALL:
                arg_count = self._read_byte()
                if not self._call_value(self._peek_stack(arg_count), arg_count):
                    raise InterpretRuntimeError
            else:
                print "Unknown opcode"
                raise InterpretRuntimeError()

    def _unary_op(self, op):
        if op == "-":
            if not self._peek_stack(0).is_number():
                self._runtime_error("Runtime error")
                raise InterpretRuntimeError()
            self._push_stack(self._pop_stack().negate())
        elif op == "!":
            self._push_stack(ValueBool(self._pop_stack().is_falsy()))

    def _binary_op(self, op):
        w_y = self._pop_stack()
        w_x = self._pop_stack()
        if op == "+":
            if w_x.is_string() and w_y.is_string():
                self._concatinate(w_x, w_y)
            elif w_x.is_number() and w_y.is_number():
                self._push_stack(w_x.add(w_y))
            else:
                self._runtime_error("Operands must be two numbers or two strings.")
                raise InterpretRuntimeError()
        elif op == "-":
            self._push_stack(w_x.sub(w_y))
        elif op == "*":
            self._push_stack(w_x.mul(w_y))
        elif op == "/":
            self._push_stackt(w_x.div(w_y))
        elif op == "<":
            w_z = ValueBool(w_x.as_number() < w_y.as_number())
            self._push_stack(w_z)
        elif op == ">":
            w_z = ValueBool(w_x.as_number() > w_y.as_number())
            self._push_stack(w_z)
        elif op == "==":
            w_z = ValueBool(w_x.as_number() == w_y.as_number())
            self._push_stack(w_z)

    def _concatinate(self, w_x, w_y):
        assert isinstance(w_x, ValueObj)
        assert isinstance(w_y, ValueObj)
        obj_str1 = w_x.get_value()
        obj_str2 = w_y.get_value()
        w_z = ValueObj(obj_str1.concat(obj_str2))
        self._push_stack(w_z)

    def _call_value(self, callee, arg_count):
        if isinstance(callee, ValueObj):
            objfun = callee.get_value()
            if isinstance(objfun, ObjFunction):
                return self._call(objfun, arg_count)
            else:
                self._runtime_error("Can only call functions and classes.")
        return False

    def _call(self, function, arg_count):
        new_frame = CallFrame(function, ip=0,
                              slots=self.stack[self.stack_top - (arg_count + 1):][:])
        self.frame = new_frame
        self.stack = new_frame.slots[:]
        self.stack_top = arg_count + 1
        return True

    def _set_local(self):
        slot = self._read_byte()
        self.stack[slot] = self._peek_stack(0)

    def _set_global(self):
        name = self._read_string()
        assert isinstance(name, ObjString)
        name_hash = name.hash()
        if not name_hash in self.global_objects:
            self._runtime_error("Undefined variable '%s'." % name)
            raise InterpretRuntimeError()
        self.global_objects[name_hash] = self._pop_stack()
        self._push_stack(ValueNil()) # To handle with OP_POP

    def _get_local(self):
        slot = self._read_byte()
        self._push_stack(self._take_stack(slot + 1))

    def _get_global(self):
        name = self._read_string()
        assert isinstance(name, ObjString)
        name_hash = name.hash()
        if name_hash not in self.global_objects:
            self._runtime_error("Undefined variable '%s'." % name)
            raise InterpretRuntimeError()
        self._push_stack(self.global_objects[name_hash])

    def _define_global(self):
        name = self._read_string()
        assert isinstance(name, ObjString)
        name_hash = name.hash()
        self.global_objects[name_hash] = self._pop_stack()

    def _constant(self):
        w_const = self._read_constant()
        self._push_stack(w_const)

    def _print(self):
        value = self._pop_stack()
        if isinstance(value, Value) or isinstance(value, Obj):
            print value.repr()
        else:
            print value
