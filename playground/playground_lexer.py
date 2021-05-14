from playground_token import PG_Type, PG_Token
from abstract.abs_lexer import AbstractLexer

class PlaygroundLexer(AbstractLexer):
    def __init__(self, input_str):
        super().__init__(input_str)

        self.reserved_names = {
            'def': PG_Type.DEF,
            'print': PG_Type.PRINT,
            'True': PG_Type.TRUE,
            'False': PG_Type.FALSE,
            'and': PG_Type.AND, 
            'or': PG_Type.OR,
            'if': PG_Type.IF,
            'elif': PG_Type.ELIF,
            'else': PG_Type.ELSE,
            'while': PG_Type.WHILE,
            'Class': PG_Type.CLASS,
        }
    
    def next_token(self) -> PG_Token:
        """ Returns the next char in the input string as a Token. 
            If there is no next char, returns <EOF> (End of File) """
        while self.c != self.EOF:
            if self.c in [' ','\t','\n','\r']: 
                self._WS() 
                continue 
            
            # Skip comments: 
            # ---------------------------------------
            elif self.c == '#': 
                self._comment()
                continue
                
            elif self.c == '.':
                return PG_Token(
                    token_type=PG_Type.DOT,
                    token_text=self.consume()
                )

            elif self.c == ';':
                return PG_Token(
                    token_type=PG_Type.SEMI_COLON,
                    token_text=self.consume()
                )
        
            elif self.c == ',':
                return PG_Token(
                    token_type=PG_Type.COMMA,
                    token_text=self.consume()
                )
                
            elif self.c == '=':
                token_type = PG_Type.ASSIGN
                buf = self.consume()

                if self.c == '=':
                    buf += self.consume()
                    token_type = PG_Type.EQ

                return PG_Token(
                    token_type=token_type, 
                    token_text=buf
                )
            
            elif self.c == '>':
                token_type = PG_Type.GT
                buf = self.consume()

                if self.c == '=':
                    buf += self.consume()
                    token_type = PG_Type.GE

                return PG_Token(
                    token_type=token_type, 
                    token_text=buf
                )

            elif self.c == '<':
                token_type = PG_Type.LT
                buf = self.consume()

                if self.c == '=':
                    buf += self.consume()
                    token_type = PG_Type.LE
              
                return PG_Token(
                    token_type=token_type, 
                    token_text=buf
                )
            
            elif self.c == '(':
                return PG_Token(
                    token_type=PG_Type.LPAREN,
                    token_text=self.consume()
                )

            elif self.c == ')':
                return PG_Token(
                    token_type=PG_Type.RPAREN,
                    token_text=self.consume()
                )

            elif self.c == '{':
                return PG_Token(
                    token_type=PG_Type.LCURBRACK,
                    token_text=self.consume()
                )

            elif self.c == '}':
                return PG_Token(
                    token_type=PG_Type.RCURBRACK,
                    token_text=self.consume()
                )

            elif self.c in ['+', '-']:
                token_type = PG_Type.PLUS if self.c == '+' else PG_Type.MINUS
                return PG_Token(
                    token_type=token_type,
                    token_text=self.consume()
                )
            
            elif self.c in ['*', '/']:
                token_type = PG_Type.STAR if self.c == '*' else PG_Type.FSLASH
                return PG_Token(
                    token_type=token_type,
                    token_text=self.consume()
                )

            elif self.c == '"':
                return self.STRING()

            elif self.isDigit():
                return self.NUMBER()
                
            elif self.isLetter():
                return self.NAME()

            else:
                raise Exception(f"Invalid character: {self.c}")
        
        return PG_Token(
            token_type=PG_Type.EOF, 
            token_text="<EOF>"
        )
    
    def isDigit(self): 
        return self.c >= '0' and self.c <= '9'
    
    def isLetter(self):
        c = self.c.lower()
        return c >= 'a' and c <= 'z'

    def STRING(self):
        # Discard the opening quote 
        self.consume()
        buf = ""
        while not (self.c == '"'):
            buf += self.consume()

        # Discard the closing quote
        self.consume()
        
        token_type = PG_Type.STRING
        return PG_Token(
            token_type=token_type,
            token_text=buf
        )

    def NAME(self):
        buf = self.consume()
        while self.isLetter():
            buf += self.consume()
        
        token_type = PG_Type.NAME
        if buf in self.reserved_names:
            token_type = self.reserved_names[buf]
        
        return PG_Token(
            token_type=token_type,
            token_text=buf
        )

    def NUMBER(self):
        token_type = PG_Type.INT # Assume into start
        buf = self.consume()
        while self.isDigit():
            buf += self.consume()

        if self.c == '.':
            token_type = PG_Type.FLOAT # Change if float recognized
            buf += self.consume()
            while self.isDigit():
                buf += self.consume()
            
            if not (buf[-1] >= '0' and buf[-1] <= '9'):
                raise Exception(f"A floating point number must have at least 1 digit after the dot: {buf}")

        return PG_Token(
            token_type=token_type,
            token_text=buf
        )

if __name__ == "__main__":
    input_str = """
    +-*/ =
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
    """
    lexer = PlaygroundLexer(input_str)
    token = lexer.next_token()
    while token.type != PG_Type.EOF:
        print(token)
        token = lexer.next_token()
    print(token)