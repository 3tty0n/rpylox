from lox.opcode import OpCode

def leftpad_string(string, width, char=" "):
    l = len(string)
    if l > width:
        return string
    return char * (width - l) + string

def disassemble_instruction(chunk, offset):
    print "%04d" % offset,

    if offset > 0 and chunk.lines[offset] == chunk.lines[offset - 1]:
        print "   | ",
    else:
        print "%4d " % chunk.lines[offset],

    instruction = chunk.code[offset]
    if instruction == OpCode.OP_RETURN:
        return simple_instruction("OP_RETURN", offset)
    elif instruction == OpCode.OP_PRINT:
        return simple_instruction("OP_PRINT", offset)
    elif instruction == OpCode.OP_POP:
        return simple_instruction("OP_POP", offset)
    elif instruction == OpCode.OP_DEFINE_GLOBAL:
        return constant_instruction("OP_DEFINE_GLOBAL", chunk, offset)
    elif instruction == OpCode.OP_GET_GLOBAL:
        return constant_instruction("OP_GET_GLOBAL", chunk, offset)
    elif instruction == OpCode.OP_SET_GLOBAL:
        return constant_instruction("OP_SET_GLOBAL", chunk, offset)
    elif instruction == OpCode.OP_CONSTANT:
        return constant_instruction("OP_CONSTANT", chunk, offset)
    elif instruction == OpCode.OP_NIL:
        return simple_instruction("OP_NIL", offset)
    elif instruction == OpCode.OP_NOT:
        return simple_instruction("OP_NOT", offset)
    elif instruction == OpCode.OP_TRUE:
        return simple_instruction("OP_TRUE", offset)
    elif instruction == OpCode.OP_FALSE:
        return simple_instruction("OP_FALSE", offset)
    elif instruction == OpCode.OP_NEGATE:
        return simple_instruction("OP_NEGATE", offset)
    elif instruction == OpCode.OP_EQUAL:
        return simple_instruction("OP_EQUAL", offset)
    elif instruction == OpCode.OP_GREATER:
        return simple_instruction("OP_GREATER", offset)
    elif instruction == OpCode.OP_LESS:
        return simple_instruction("OP_LESS", offset)
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

def format_line_number(chunk, offset):
    if offset > 0 and chunk.lines[offset] == chunk.lines[offset - 1]:
        return "   |"
    else:
        return leftpad_string(str(chunk.lines[offset]), 4)
