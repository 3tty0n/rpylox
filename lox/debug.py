# Based on https://github.com/hardbyte/pylox/blob/master/lox/debug.py
from lox.opcodes import OpCode

OpCodeToInstructionName = {getattr(OpCode, op): op
                           for op in dir(OpCode) if op.startswith('OP_')}


def leftpad_string(string, width, char=" "):
    l = len(string)
    if l > width:
        return string
    fmt = ""
    for i in range(width - l):
        fmt += char
    return fmt + string


def rightpad_string(string, width, char=" "):
    l = len(string)
    if l > width:
        return string
    return string + char * (width - l)


def simple_instruction(name, offset):
    return "", offset + 1


def binary_instruction(name, chunk, offset):
    #op_name = OpCode.BinaryOps[chunk.code[offset - 1]]
    return "", offset + 1


def byte_instruction(name, chunk, offset):
    slot = chunk.code[offset + 1]
    return str(slot), offset + 2


def format_constant(name, chunk, constant):
    return "(%s) %s" % (
        leftpad_string("%d" % constant, 2, '0'),
        leftpad_string("'%s'" % chunk.constants[constant].repr(), 10)
    )


def constant_instruction(name, chunk, offset):
    constant = chunk.code[offset + 1]
    return format_constant(name, chunk, constant), offset + 2


def jump_instruction(name, chunk, offset):
    jump1 = chunk.code[offset + 1] << 8 & 0xff
    jump2 = chunk.code[offset + 2] & 0xff
    return "%d %d" % (jump1, jump2), offset + 3


def get_printable_location(ip, chunk):
    line_number = format_line_number(chunk, ip)
    instruction_index = format_ip(ip)
    instruction = chunk.code[ip]
    instruction_name = format_instruction(get_instruction_name(instruction))
    _, instruction_extras = format_instruction_extended(chunk, instruction, instruction_name, ip)
    return "%s %s %s %s" % (line_number, instruction_index, instruction_name, instruction_extras)


def disassemble_instruction(chunk, offset):
    print format_ip(offset),

    instruction = chunk.code[offset]
    if instruction not in OpCodeToInstructionName:
        print "Unknown opcode %s" % instruction
        return offset + 1

    # Print the line number
    print format_line_number(chunk, offset),

    # Print the opcode's name
    instruction_name = get_instruction_name(instruction)
    print format_instruction(instruction_name),

    # Now the opcode specific output
    ip, repr = format_instruction_extended(chunk, instruction, instruction_name, offset)
    print repr
    return ip


def format_instruction_extended(chunk, instruction, instruction_name, offset):
    # Enrich the representation for constants, binary ops etc

    if instruction == OpCode.OP_CONSTANT:
        repr, ip = constant_instruction(instruction_name, chunk, offset)
    elif instruction == OpCode.OP_FALSE:
        repr = "FALSE"
        ip = offset + 1
    elif instruction == OpCode.OP_TRUE:
        repr = "TRUE"
        ip = offset + 1
    elif instruction in OpCode.BinaryOps:
        repr, ip = binary_instruction(instruction_name, chunk, offset)
    elif instruction in (
            OpCode.OP_SET_LOCAL,
            OpCode.OP_GET_LOCAL,
            OpCode.OP_GET_GLOBAL,
            OpCode.OP_SET_GLOBAL,
            OpCode.OP_CALL,
            OpCode.OP_DEFINE_GLOBAL,
    ):
        repr, ip = byte_instruction(instruction_name, chunk, offset)
    elif instruction in (
            OpCode.OP_JUMP_IF_FALSE,
            OpCode.OP_JUMP,
            OpCode.OP_LOOP
    ):
        repr, ip = jump_instruction(instruction_name, chunk, offset)
    else:
        repr, ip = simple_instruction(instruction_name, offset)
    return ip, repr


def format_ip(ip):
    return leftpad_string("%d" % ip, 4, '0')


def get_instruction_name(instruction):
    return OpCodeToInstructionName[instruction]


def format_instruction(instruction_name):
    return rightpad_string("%s " % instruction_name, 12)


def format_line_number(chunk, offset):
    if offset > 0 and chunk.lines[offset] == chunk.lines[offset - 1]:
        return "   |"
    else:
        return leftpad_string(str(chunk.lines[offset]), 4)
