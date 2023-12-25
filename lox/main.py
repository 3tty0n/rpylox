from lox.chunk import Chunk
from lox.opcode import OpCode
from lox.vm import VM, InterpretResult

import readline

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

    while True:
        print prompt,
        next_line = sys.stdin.readline(LINE_BUFFER_LENGTH)
        if not next_line:
            break

        print

        vm.interpret(next_line)


def run_file(filename):

    source = read_file(filename)
    vm = VM(debug=True)
    try:
        result = vm.interpret(source)
        if result == InterpretResult.INTERPRET_COMPILE_ERROR:
            print "Compile error"
        elif result == InterpretResult.INTERPRET_RUNTIME_ERROR:
            print "Runtime error"
    except ValueError:
        print "Unhandled exception in runFile"


def read_file(filename):
    try:
        # file = rfile.create_file(filename, 'r')
        file = open(filename, 'r')
    except IOError:
        print "Error opening file"
        raise SystemExit(74)
    source = file.read()
    file.close()
    return source


def main(argv):

    if len(argv) == 1:
        repl()
    elif len(argv) == 2:
        run_file(argv[1])
    else:
        sys.stderr.write("Usage: lox [path]\n")
        exit(64)

    return 0


if __name__ == "__main__":
    import sys
    main(sys.argv)
