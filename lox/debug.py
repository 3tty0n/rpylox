from lox.opcode import OpCode

def disassemble_instruction(chunk, offset):
    print "%04d" % offset,

    if offset > 0 and chunk.lines[offset] == chunk.lines[offset - 1]:
        print "   | ",
    else:
        print "%4d " % chunk.lines[offset],

    instruction = chunk.code[offset]
    if instruction == OpCode.OP_RETURN:
        return simple_instruction("OP_RETURN", offset)
    elif instruction == OpCode.OP_CONSTANT:
        return constant_instruction("OP_CONSTANT", chunk, offset)
    elif instruction == OpCode.OP_NEGATE:
        return simple_instruction("OP_NEGATE", offset)
    elif instruction == OpCode.OP_ADD:
        return simple_instruction("OP_ADD", offset)
    elif instruction == OpCode.OP_SUBTRACT:
        return simple_instruction("OP_SUBTRACT", offset)
    elif instruction == OpCode.OP_MULTIPLY:
        return simple_instruction("OP_MULTIPLY", offset)
    elif instruction == OpCode.OP_DIVIDE:
        return simple_instruction("OP_DIVIDE", offset)
    elif instruction == OpCode.OP_TRUE:
        return simple_instruction("TRUE", offset)
    elif instruction == OpCode.OP_FALSE:
        return simple_instruction("FALSE", offset)
    else:
        print "Unknown opcde %d\n" % instruction
        return offset + 1

def simple_instruction(name, offset):
    print name
    return offset + 1

def constant_instruction(name, chunk, offset):
    constant = chunk.code[offset + 1]
    print "%-16s '%4d'" % (name, constant),
    print chunk.constants.values[constant]
    return offset + 2
