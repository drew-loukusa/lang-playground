from playground_token import PG_Type as PGT, PG_Token
from abstract.abs_lexer import AbstractLexer


class PlaygroundLexer(AbstractLexer):
    def __init__(self, input_str):
        super().__init__(input_str)

        self.reserved_names = {
            "def": PGT.DEF,
            "print": PGT.PRINT,
            "True": PGT.TRUE,
            "False": PGT.FALSE,
            "and": PGT.AND,
            "or": PGT.OR,
            "if": PGT.IF,
            "elif": PGT.ELIF,
            "else": PGT.ELSE,
            "while": PGT.WHILE,
            "Class": PGT.CLASS,
            "return": PGT.RETURN,
            "import": PGT.IMPORT,
        }

    def next_token(self) -> PG_Token:
        """
        Returns the next char in the input string as a Token.
        If there is no next char, returns <EOF> (End of File)
        """
        while self.c != self.EOF:
            if self.c in [" ", "\t", "\n", "\r"]:
                self._WS()
                continue

            # Skip comments:
            # ---------------------------------------
            elif self.c == "#":
                self._comment()
                continue

            elif self.c == ".":
                return PG_Token(token_type=PGT.DOT, token_text=self.consume())

            elif self.c == ";":
                return PG_Token(
                    token_type=PGT.SEMI_COLON, token_text=self.consume()
                )

            elif self.c == ",":
                return PG_Token(token_type=PGT.COMMA, token_text=self.consume())

            elif self.c == "=":
                token_type = PGT.ASSIGN
                buf = self.consume()

                if self.c == "=":
                    buf += self.consume()
                    token_type = PGT.EQ

                return PG_Token(token_type=token_type, token_text=buf)

            elif self.c == ">":
                token_type = PGT.GT
                buf = self.consume()

                if self.c == "=":
                    buf += self.consume()
                    token_type = PGT.GE

                return PG_Token(token_type=token_type, token_text=buf)

            elif self.c == "<":
                token_type = PGT.LT
                buf = self.consume()

                if self.c == "=":
                    buf += self.consume()
                    token_type = PGT.LE

                return PG_Token(token_type=token_type, token_text=buf)

            elif self.c == "(":
                return PG_Token(token_type=PGT.LPAREN, token_text=self.consume())

            elif self.c == ")":
                return PG_Token(token_type=PGT.RPAREN, token_text=self.consume())

            elif self.c == "{":
                return PG_Token(token_type=PGT.LCURBRACK, token_text=self.consume())

            elif self.c == "}":
                return PG_Token(token_type=PGT.RCURBRACK, token_text=self.consume())

            elif self.c in ["+", "-"]:
                token_type = PGT.PLUS if self.c == "+" else PGT.MINUS
                return PG_Token(token_type=token_type, token_text=self.consume())

            elif self.c in ["*", "/", "%"]:
                mult_ops = {"*": PGT.STAR, "/": PGT.FSLASH, "%": PGT.PERCENT}
                token_type = mult_ops[self.c]
                return PG_Token(token_type=token_type, token_text=self.consume())

            elif self.c == '"':
                return self.STRING()

            elif self.isDigit():
                return self.NUMBER()

            elif self.isLetter() or self.c == "_":
                return self.NAME()

            else:
                raise Exception(f"Invalid character: {self.c}")

        return PG_Token(token_type=PGT.EOF, token_text="<EOF>")

    def isDigit(self):
        return self.c >= "0" and self.c <= "9"

    def isLetter(self):
        c = self.c.lower()
        return c >= "a" and c <= "z"

    def STRING(self):
        # Discard the opening quote
        self.consume()
        buf = ""
        while not (self.c == '"'):
            buf += self.consume()

        # Discard the closing quote
        self.consume()

        token_type = PGT.STRING
        return PG_Token(token_type=token_type, token_text=buf)

    def NAME(self):
        buf = self.consume()
        while self.isLetter() or self.c == "_":
            buf += self.consume()

        token_type = PGT.NAME
        if buf in self.reserved_names:
            token_type = self.reserved_names[buf]

        return PG_Token(token_type=token_type, token_text=buf)

    def NUMBER(self):
        token_type = PGT.INT  # Assume into start
        buf = self.consume()
        while self.isDigit():
            buf += self.consume()

        if self.c == ".":
            token_type = PGT.FLOAT  # Change if float recognized
            buf += self.consume()
            while self.isDigit():
                buf += self.consume()

            if not (buf[-1] >= "0" and buf[-1] <= "9"):
                raise Exception(
                    f"A floating point number must have at least 1 digit after the dot: {buf}"
                )

        return PG_Token(token_type=token_type, token_text=buf)


if __name__ == "__main__":
    input_str = """
    +-*/ = %
    1 11 5.0 
    a ab a AB 
    print 
    () {} 
    True False and or 
    > < == <= >= 
    if elif else while 
    "A test string: 10 9, ; .ouauht."
    def
    Class
    .
    underscored_name
    _underscored_name
    _underscored_name_
    return
    import
    """
    lexer = PlaygroundLexer(input_str)
    token = lexer.next_token()
    while token.type != PGT.EOF:
        print(token)
        token = lexer.next_token()
    print(token)
