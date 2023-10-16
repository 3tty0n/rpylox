from chunk import Chunk
from opcode import OpCode
from vm import VM

def main(argv):
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


if __name__ == "__main__":
    import sys
    main(sys.argv)
