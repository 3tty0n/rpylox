import sys

from lox.chunk import Chunk
from lox.opcodes import OpCode
from lox.object import ObjString
from lox.scanner import Scanner, TokenTypes, debug_token
from lox.value import Value, ValueNumber, ValueBool, ValueObj

class Parser(object):
    def __init__(self):
        self.current = None
        self.previous = None
        self.panic_mdoe = False
        self.had_error = False

class Precedence(object):
    NONE = 0
    ASSIGNMENT = 1    # =
    OR = 2            # or
    AND = 3           # and
    EQUALITY = 4      # == !=
    COMPARISON = 5    # < > <= >=
    TERM = 6          # + -
    FACTOR = 7        # * /
    UNARY = 8         # ! -
    CALL = 9          # . ()
    PRIMARY = 10


class ParseRule(object):
    def __init__(self, prefix, infix, precedence):
        self.prefix = prefix
        self.infix = infix
        self.precedence = precedence

    def __getitem__(self, item):
        if item == 0:
            return self.prefix
        elif item == 1:
            return self.infix
        elif item == 2:
            return self.precedence
        else:
            raise Exception("unsupported item: %d " % item)


class Compiler(object):

    def __init__(self, source, debug_print=False):
        self.source = source
        self.scanner = Scanner(source)
        self.parser = Parser()
        self.chunk = Chunk()
        self.debug_print = debug_print

    def compile(self):
        line = -1
        self.advance()

        # self.expression()
        # self.consume(TokenTypes.EOF, "Expect end of expression.")

        while not self.match(TokenTypes.EOF):
            self.declaration()

        self.end_compiler()

        return not self.parser.had_error

    def advance(self):
        self.parser.previous = self.parser.current

        while True:
            token = self.scanner.scan_token()
            if self.debug_print:
                print "Scanning token %s" % (debug_token(token))
            self.parser.current = token
            if self.parser.current.type != TokenTypes.ERROR:
                break
            self._error_at_current(self.parser.current.message)

    def consume(self, token_type, message):
        if self.parser.current.type == token_type:
            self.advance()
            return

        self._error_at_current(message)

    def match(self, token_type):
        if not self._check(token_type):
            return False

        self.advance()
        return True

    def _check(self, token_type):
        return self.parser.current.type == token_type

    def end_compiler(self):
        self.emit_return()

        if self.debug_print:
            if not self.parser.had_error:
                self.current_chunk().disassemble("code")

    def number(self, can_assign):
        value = float(self.scanner.get_token_string(self.parser.previous))
        lox_value = ValueNumber(value)
        self.emit_constant(lox_value)

    def string(self, can_assign):
        # the value itself has decorated with double quotes
        string_value = self.scanner.get_token_string(self.parser.previous)
        # remove " and extract the value
        slice_end = len(string_value) - 1
        assert slice_end > 0
        string_obj = ObjString(string_value[1:slice_end])
        w_x = ValueObj(string_obj)
        self.emit_constant(w_x)

    def variable(self, can_assign):
        self._named_variable(self.parser.previous, can_assign)

    def _named_variable(self, token, can_assign):
        name = self.scanner.get_token_string(token)
        arg = self._identifier_constant(name)

        if self.match(TokenTypes.EQUAL):
            self.expression()
            self.emit_bytes(OpCode.OP_SET_GLOBAL, arg)
        else:
            self.emit_bytes(OpCode.OP_GET_GLOBAL, arg)

    def literal(self, can_assign):
        op_type = self.parser.previous.type
        if op_type == TokenTypes.FALSE:
            self.emit_byte(OpCode.OP_FALSE)
        elif op_type == TokenTypes.NIL:
            self.emit_byte(OpCode.OP_NIL)
        elif op_type == TokenTypes.TRUE:
            self.emit_byte(OpCode.OP_TRUE)

    def unary(self, can_assign):
        operator_type = self.parser.previous.type

        # Compile the operand
        self.parse_precedence(Precedence.UNARY)

        # Emit the instruction
        if operator_type == TokenTypes.BANG:
            self.emit_byte(OpCode.OP_NOT)
        elif operator_type == TokenTypes.MINUS:
            self.emit_byte(OpCode.OP_NEGATE)

    def binary(self, can_assign):
        op_type = self.parser.previous.type
        rule = self._get_rule(op_type)
        self.parse_precedence(rule.precedence + 1)

        if op_type == TokenTypes.PLUS:
            self.emit_byte(OpCode.OP_ADD)
        if op_type == TokenTypes.MINUS:
            self.emit_byte(OpCode.OP_SUBTRACT)
        if op_type == TokenTypes.STAR:
            self.emit_byte(OpCode.OP_MULTIPLY)
        if op_type == TokenTypes.SLASH:
            self.emit_byte(OpCode.OP_DIVIDE)
        if op_type == TokenTypes.BANG_EQUAL:
            self.emit_bytes(OpCode.OP_EQUAL, OpCode.OP_NEGATE)
        if op_type == TokenTypes.EQUAL_EQUAL:
            self.emit_byte(OpCode.OP_EQUAL)
        if op_type == TokenTypes.GREATER:
            self.emit_byte(OpCode.OP_GREATER)
        if op_type == TokenTypes.GREATER_EQUAL:
            self.emit_bytes(OpCode.OP_LESS, OpCode.OP_NEGATE)
        if op_type == TokenTypes.LESS:
            self.emit_byte(OpCode.OP_LESS)
        if op_type == TokenTypes.LESS_EQUAL:
            self.emit_bytes(OpCode.OP_GREATER, OpCode.OP_NEGATE)

    def parse_precedence(self, precedence):
        self.advance()
        prefix_rule = self._get_rule(self.parser.previous.type).prefix
        if prefix_rule is None:
            self._error("Expect expression.")
            return

        can_assign = precedence <= Precedence.ASSIGNMENT
        prefix_rule(self, can_assign)

        while precedence <= self._get_rule(self.parser.current.type).precedence:
            self.advance()
            infix_rule = self._get_rule(self.parser.previous.type).infix
            infix_rule(self, can_assign)

        if can_assign and self.match(TokenTypes.EQUAL):
            self._error("Invalid assignment target.")

    def _identifier_constant(self, name):
        w_obj = ValueObj(ObjString(name))
        return self._make_constant(w_obj)

    def _parse_variable(self, message):
        self.consume(TokenTypes.IDENTIFIER, message)

        name = self.scanner.get_token_string(self.parser.previous)
        return self._identifier_constant(name)

    def define_variable(self, global_var):
        self.emit_bytes(OpCode.OP_DEFINE_GLOBAL, global_var)

    def expression(self):
        self.parse_precedence(Precedence.ASSIGNMENT)

    def var_declaration(self):
        global_var = self._parse_variable("Expect variable name.")

        if self.match(TokenTypes.EQUAL):
            self.expression()
        else:
            self.emit_byte(OpCode.OP_NIL)

        self.consume(TokenTypes.SEMICOLON, "Expect ';' aster variable declaration.")

        self.define_variable(global_var)

    def expression_statement(self):
        self.expression()
        self.consume(TokenTypes.SEMICOLON, "Expect ';' after expression.")
        self.emit_byte(OpCode.OP_POP)

    def print_statement(self):
        self.expression()
        self.consume(TokenTypes.SEMICOLON, "Expect ';' after value.")
        self.emit_byte(OpCode.OP_PRINT)

    def synchronize(self):
        self.parser.panic_mdoe = False

        while self.parser.current.type != TokenTypes.EOF:
            if self.parser.previous.type == TokenTypes.SEMICOLON:
                return
            if self.parser.current.type in (
                    TokenTypes.CLASS,
                    TokenTypes.FUN,
                    TokenTypes.VAR,
                    TokenTypes.FOR,
                    TokenTypes.IF,
                    TokenTypes.WHILE,
                    TokenTypes.PRINT,
                    TokenTypes.RETURN
            ):
                return

            self.advance()

    def declaration(self):

        if self.match(TokenTypes.VAR):
            self.var_declaration()
        else:
            self.statement()

        if self.parser.panic_mdoe:
            self.synchronize()

    def statement(self):
        if self.match(TokenTypes.PRINT):
            self.print_statement()
        else:
            self.expression_statement()

    def emit_byte(self, byte1):
        self.current_chunk().write_chunk(byte1, self.parser.previous.line)

    def emit_bytes(self, byte1, byte2):
        self.emit_byte(byte1)
        self.emit_byte(byte2)

    def emit_return(self):
        self.emit_byte(OpCode.OP_RETURN)

    def grouping(self, can_assign):
        self.expression()
        self.consume(TokenTypes.RIGHT_PAREN, "Expect ')' after expression.")

    def _make_constant(self, value):
        chunk = self.current_chunk()
        constant = chunk.add_constant(value)
        if constant > 255:
            self._error("Too many constants in one chunk.")
            return 0
        return constant

    def emit_constant(self, value):
        self.emit_bytes(OpCode.OP_CONSTANT, self._make_constant(value))

    def _error_at(self, token, msg):
        if self.parser.panic_mdoe:
            return

        print "[line %d] Error" % token.line,

        if token.type == TokenTypes.EOF:
            print " at end"
        elif token.type == TokenTypes.ERROR:
            pass
        else:
            print " at '%s'" % self.scanner.get_token_string(token)
        print ": %s\n" % msg

        self.parser.had_error = True

    def _error_at_current(self, message):
        self._error_at(self.parser.current, message)

    def _error(self, message):
        self._error_at(self.parser.previous, message)

    def current_chunk(self):
        return self.chunk

    @staticmethod
    def _get_rule(op_type):
        return rules[op_type]


# The table that drives our whole parser. Entries per token of:
# [ prefix, infix, precedence]
rules = [
    ParseRule(Compiler.grouping,    None,               Precedence.CALL),        # TOKEN_LEFT_PAREN
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_RIGHT_PAREN
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_LEFT_BRACE
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_RIGHT_BRACE
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_COMMA
    ParseRule(None,                 None,               Precedence.CALL),        # TOKEN_DOT
    ParseRule(Compiler.unary,       Compiler.binary,    Precedence.TERM),        # TOKEN_MINUS
    ParseRule(None,                 Compiler.binary,    Precedence.TERM),        # TOKEN_PLUS
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_SEMICOLON
    ParseRule(None,                 Compiler.binary,    Precedence.FACTOR),      # TOKEN_SLASH
    ParseRule(None,                 Compiler.binary,    Precedence.FACTOR),      # TOKEN_STAR
    ParseRule(Compiler.unary,       None,               Precedence.NONE),        # TOKEN_BANG
    ParseRule(None,                 Compiler.binary,    Precedence.EQUALITY),    # TOKEN_BANG_EQUAL
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_EQUAL
    ParseRule(None,                 Compiler.binary,    Precedence.EQUALITY),    # TOKEN_EQUAL_EQUAL
    ParseRule(None,                 Compiler.binary,    Precedence.COMPARISON),  # TOKEN_GREATER
    ParseRule(None,                 Compiler.binary,    Precedence.COMPARISON),  # TOKEN_GREATER_EQUAL
    ParseRule(None,                 Compiler.binary,    Precedence.COMPARISON),  # TOKEN_LESS
    ParseRule(None,                 Compiler.binary,    Precedence.COMPARISON),  # TOKEN_LESS_EQUAL
    ParseRule(Compiler.variable,    None,               Precedence.NONE),        # TOKEN_IDENTIFIER
    ParseRule(Compiler.string,      None,               Precedence.NONE),        # TOKEN_STRING
    ParseRule(Compiler.number,      None,               Precedence.NONE),        # TOKEN_NUMBER
    ParseRule(None,                 None,               Precedence.AND),         # TOKEN_AND
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_CLASS
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_ELSE
    ParseRule(Compiler.literal,     None,               Precedence.NONE),        # TOKEN_FALSE
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_FUN
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_FOR
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_IF
    ParseRule(Compiler.literal,     None,               Precedence.NONE),        # TOKEN_NIL
    ParseRule(None,                 None,               Precedence.OR),          # TOKEN_OR
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_PRINT
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_RETURN
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_SUPER
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_THIS
    ParseRule(Compiler.literal,     None,               Precedence.NONE),        # TOKEN_TRUE
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_VAR
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_WHILE
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_ERROR
    ParseRule(None,                 None,               Precedence.NONE),        # TOKEN_EOF
]
