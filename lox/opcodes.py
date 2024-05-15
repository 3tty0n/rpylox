class OpCode:

    OP_RETURN = 0
    OP_NOP = OP_RETURN + 1
    OP_CONSTANT = OP_NOP + 1
    OP_NOT = OP_CONSTANT + 1
    OP_NEGATE = OP_NOT + 1
    OP_EQUAL = OP_NEGATE + 1
    OP_GREATER = OP_EQUAL + 1
    OP_LESS = OP_GREATER + 1
    OP_ADD = OP_LESS + 1
    OP_SUBTRACT = OP_ADD + 1
    OP_MULTIPLY = OP_SUBTRACT + 1
    OP_DIVIDE = OP_MULTIPLY + 1
    OP_FALSE = OP_DIVIDE + 1
    OP_TRUE = OP_FALSE + 1
    OP_NIL = OP_TRUE + 1
    OP_PRINT = OP_NIL + 1
    OP_JUMP_IF_FALSE = OP_PRINT + 1
    OP_JUMP = OP_JUMP_IF_FALSE + 1
    OP_LOOP = OP_JUMP + 1
    OP_POP = OP_LOOP + 1
    OP_DEFINE_GLOBAL = OP_POP + 1
    OP_GET_GLOBAL = OP_DEFINE_GLOBAL + 1
    OP_SET_GLOBAL = OP_GET_GLOBAL + 1
    OP_GET_LOCAL = OP_SET_GLOBAL + 1
    OP_SET_LOCAL = OP_GET_LOCAL + 1
    OP_CALL = OP_SET_LOCAL + 1

    BinaryOps = [
        OP_ADD,
        OP_SUBTRACT,
        OP_MULTIPLY,
        OP_DIVIDE,
        OP_GREATER,
        OP_LESS
    ]
