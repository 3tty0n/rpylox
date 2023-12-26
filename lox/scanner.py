from rpython.rlib import jit

class TokenTypes(object):
    # Single-character tokens
    LEFT_PAREN = 0
    RIGHT_PAREN = LEFT_PAREN + 1
    LEFT_BRACE = RIGHT_PAREN + 1
    RIGHT_BRACE = LEFT_BRACE + 1
    COMMA = RIGHT_BRACE + 1
    DOT = COMMA + 1
    MINUS = DOT + 1
    PLUS = MINUS + 1
    SEMICOLON = PLUS + 1
    SLASH = SEMICOLON + 1
    STAR = SLASH + 1

    # one or two character tokens
    BANG = STAR + 1
    BANG_EQUAL = BANG + 1
    EQUAL = BANG_EQUAL + 1
    EQUAL_EQUAL = EQUAL + 1
    GREATER = EQUAL_EQUAL + 1
    GREATER_EQUAL = GREATER + 1
    LESS = GREATER_EQUAL + 1
    LESS_EQUAL = LESS + 1

    # Primitives
    IDENTIFIER = LESS_EQUAL + 1
    STRING = IDENTIFIER + 1
    NUMBER = STRING + 1

    # keyword
    AND = NUMBER + 1
    CLASS = AND + 1
    ELSE = CLASS + 1
    FALSE = ELSE + 1
    FUN = FALSE + 1
    FOR = FUN + 1
    IF = FOR + 1
    NIL = IF + 1
    OR = NIL + 1
    PRINT = OR + 1
    RETURN = PRINT + 1
    SUPER = RETURN + 1
    THIS = SUPER + 1
    TRUE = THIS + 1
    VAR = TRUE + 1
    WHILE  = VAR + 1

    ERROR = WHILE + 1
    EOF = ERROR + 1


TokenTypeToTokenName = {getattr(TokenTypes, token_type):
                         token_type for token_type in dir(TokenTypes) if not token_type.startswith("__")}


def debug_token(token):
    token_type = token.type
    return TokenTypeToTokenName[token_type]


class BaseToken(object):
    def __init__(self, type, line):
        self.type = type
        self.line = line


class Token(BaseToken):
    def __init__(self, type, start, length, line):
        self.type = type
        self.start = start
        self.length = length
        self.line = line


class ErrorToken(BaseToken):
    def __init__(self, message, line):
        self.type = TokenTypes.ERROR
        self.message = message
        self.line = line


class Scanner(object):
    def __init__(self, source):
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_token(self):
        self._skip_whitespace()
        self.start = self.current

        if self._is_at_end():
            return self.make_token(TokenTypes.EOF)

        c = self.advance()

        if c.isalpha():
            return self._make_identifier()

        if c.isdigit():
            return self._number()

        if c == '(':
            return self.make_token(TokenTypes.LEFT_PAREN)
        if c == ')':
            return self.make_token(TokenTypes.RIGHT_PAREN)
        if c == '{':
            return self.make_token(TokenTypes.LEFT_BRACE)
        if c == '}':
            return self.make_token(TokenTypes.RIGHT_BRACE)
        if c == ';':
            return self.make_token(TokenTypes.SEMICOLON)
        if c == ',':
            return self.make_token(TokenTypes.COMMA)
        if c == '.':
            return self.make_token(TokenTypes.DOT)
        if c == '-':
            return self.make_token(TokenTypes.MINUS)
        if c == '+':
            return self.make_token(TokenTypes.PLUS)
        if c == '/':
            return self.make_token(TokenTypes.SLASH)
        if c == '*':
            return self.make_token(TokenTypes.STAR)
        if c ==  '!':
            return self.make_token(
                TokenTypes.BANG_EQUAL if self._match('=') else TokenTypes.BANG
            )
        if c == '=':
            return self.make_token(
                TokenTypes.EQUAL_EQUAL if self._match('=') else TokenTypes.EQUAL
            )
        if c == '<':
            return self.make_token(
                TokenTypes.LESS_EQUAL if self._match('=') else TokenTypes.LESS
            )
        if c == '>':
            return self.make_token(
                TokenTypes.GREATER_EQUAL if self._match('=') else TokenTypes.GREATER
            )
        if c == '"':
            return self.make_string()

        return self.make_error_token("Unexpected character: %s" % (c))

    def advance(self):
        self.current += 1
        return self.source[self.current - 1]

    def _is_at_end(self):
        return self.current == len(self.source)

    def _match(self, expected):
        if self._is_at_end():
            return False
        elif self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def _skip_whitespace(self):
        while True:
            c = self._peek()
            if c in ' \r\t':
                self.advance()
            elif c == '\n':
                self.line += 1
                self.advance()
            elif c == '/':
                if self._peek_next() == '/':
                    while self._peek() != '\n' and not self._is_at_end():
                        self.advance()
                else:
                    break
            else:
                return


    def _peek(self):
        if self.current == len(self.source):
            return '\0'
        return self.source[self.current]

    def _peek_next(self):
        if self._is_at_end():
            return '\0'
        return self.source[self.current + 1]

    def _number(self):
        while self._peek().isdigit():
            self.advance()

        # Floating point
        if self._peek() == '.' and self._peek_next().isdigit():
            self.advance()
            while self._peek().isdigit():
                self.advance()

        return self.make_token(TokenTypes.NUMBER)

    def _make_identifier(self):
        while self._peek().isalpha() or self._peek().isdigit():
            self.advance()
        return self.make_token(self._identifier())

    def _identifier(self):
        char = self.source[self.start]

        if char == 'a':
            return self._check_keyword(1, 2, "nd", TokenTypes.AND)
        if char == 'c':
            return self._check_keyword(1, 4, "lass", TokenTypes.CLASS)
        if char == 'e':
            return self._check_keyword(1, 3, "lse", TokenTypes.ELSE)
        if char == 'f':
            if self.current - self.start > 1:
                char2 = self.source[self.start + 1]
                if char2 == 'a':
                    return self._check_keyword(2, 3, 'lse', TokenTypes.FALSE)
                elif char2 == 'o':
                    return self._check_keyword(2, 1, 'r', TokenTypes.FOR)
                elif char2 == 'u':
                    return self._check_keyword(2, 1, 'n', TokenTypes.FUN)
        if char == 'i':
            return self._check_keyword(1, 1, "f", TokenTypes.IF)
        if char == 'n':
            return self._check_keyword(1, 2, "il", TokenTypes.NIL)
        if char == 'o':
            return self._check_keyword(1, 1, "r", TokenTypes.OR)
        if char == 'p':
            return self._check_keyword(1, 4, "rint", TokenTypes.PRINT)
        if char == 'r':
            return self._check_keyword(1, 5, "eturn", TokenTypes.RETURN)
        if char == 's':
            return self._check_keyword(1, 4, "uper", TokenTypes.SUPER)
        if char == 't':
            if self.current - self.start > 1:
                char2 = self.source[self.start + 1]
                if char2 == 'h':
                    return self._check_keyword(2, 2, 'is', TokenTypes.THIS)
                elif char2 == 'r':
                    return self._check_keyword(2, 2, 'ue', TokenTypes.TRUE)
        if char == 'v':
            return self._check_keyword(1, 2, "ar", TokenTypes.VAR)
        if char == 'w':
            return self._check_keyword(1, 4, "hile", TokenTypes.WHILE)

        return TokenTypes.IDENTIFIER

    def _check_keyword(self, start, length, rest, type):
        if self.source[self.start + start: self.start + start+ length] == rest:
            return type
        else:
            return TokenTypes.IDENTIFIER

    def make_string(self):
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == '\n':
                self.line += 1
            self.advance()

        if self._is_at_end():
            return self.make_error_token("Unterminated string.")

        # The closing quote
        self.advance()
        return self.make_token(TokenTypes.STRING)

    def make_token(self, token_type):
        return Token(
            type=token_type,
            start=self.start,
            length=(self.current - self.start),
            line=self.line
        )

    def make_error_token(self, message):
        return ErrorToken(
            message=message,
            line=self.line
        )

    @jit.elidable
    def get_token_string(self, token):
        if isinstance(token, ErrorToken):
            return token.message
        else:
            end_loc = token.start + token.length
            assert end_loc < len(self.source)
            assert end_loc > 0
            return self.source[token.start:end_loc]
