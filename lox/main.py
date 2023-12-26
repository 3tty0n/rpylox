import os
import readline
import math

from lox.chunk import Chunk
from lox.opcodes import OpCode
from lox.vm import VM, InterpretCompileError, InterpretRuntimeError

from rpython.rlib import rfile, jit

def test_chunk(argv):
    chunk = Chunk()
    constant = chunk.add_constant(1.2)
    chunk.write_chunk(OpCode.OP_CONSTANT, 123)
    chunk.write_chunk(constant, 123)

    constant = chunk.add_constant(3.4)
    chunk.write_chunk(OpCode.OP_CONSTANT, 123)
    chunk.write_chunk(constant, 123)

    chunk.write_chunk(OpCode.OP_ADD, 123)

    constant = chunk.add_constant(5.6)
    chunk.write_chunk(OpCode.OP_CONSTANT, 123)
    chunk.write_chunk(constant, 123)

    chunk.write_chunk(OpCode.OP_DIVIDE, 123)
    chunk.write_chunk(OpCode.OP_NEGATE, 123)
    chunk.write_chunk(OpCode.OP_RETURN, 123)

    chunk.disassemble("test chunk")
    vm = VM()
    vm.interpret(chunk)
    chunk.free_chunk()
    return 0


def repl():
    prompt = '> '
    LINE_BUFFER_LENGTH = 4096
    vm = VM(debug=True)

    print "Welcome to lox"

    stdin, stdout, stderr = rfile.create_stdio()

    try:
        while True:
            stdout.write("> ")
            next_line = stdin.readline()
            if not next_line:
                break

            print
            vm.interpret(next_line)

    except KeyboardInterrupt:
        stdout.write("Byte!\n")


def run_file(filename):

    source = read_file(filename)
    vm = VM(debug=True)
    try:
        result = vm.interpret(source)
    except InterpretCompileError as e:
        print "Compile error"
        raise e
    except InterpretRuntimeError as e:
        print "RUntime error"
        raise e
    except ValueError:
        print "Unhandled exception in runFile"


def read_file(filename):
    try:
        # file = rfile.create_file(filename, 'r')
        file = os.open(filename, os.O_RDONLY, 0777)
    except IOError:
        print "Error opening file"
        raise SystemExit(74)
    source = os.read(file, int(math.pow(2, 20)))
    os.close(file)
    return source


def main(argv):

    if len(argv) == 1:
        repl()
    elif len(argv) == 2:
        run_file(argv[1])
    else:
        print "Usage: lox [path]"
        raise SystemExit(64)

    return 0
