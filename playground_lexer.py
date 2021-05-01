from token_def import PlaygroundTokens as PGT, AbstractToken as Token
from abstract_lexer import AbstractLexer

class PlaygroundLexer(AbstractLexer):
    def __init__(self, input_str):
        super().__init__(input_str)
    
    def next_token(self) -> Token:
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
        
            elif self.c == ';':
                return Token(
                    token_type=PGT.SEMI_COLON,
                    token_text=self.consume()
                )
                
            elif self.c == '=':
                return Token(
                    token_type=PGT.EQUAL, 
                    token_text=self.consume()
                )
            
            elif self.c == '(':
                return Token(
                    token_type=PGT.LPAREN,
                    token_text=self.consume()
                )

            elif self.c == ')':
                return Token(
                    token_type=PGT.RPAREN,
                    token_text=self.consume()
                )

            elif self.c in ['+', '-']:
                token_type = PGT.PLUS if self.c == '+' else PGT.MINUS
                return Token(
                    token_type=token_type,
                    token_text=self.consume()
                )
            
            elif self.c in ['*', '/']:
                token_type = PGT.STAR if self.c == '*' else PGT.FSLASH
                return Token(
                    token_type=token_type,
                    token_text=self.consume()
                )

            elif self.isNumber():
                return self.NUMBER()
                
            elif self.isLetter():
                return self.NAME()

            else:
                raise Exception(f"Invalid character: {self.c}")
        
        return Token(
            token_type=PGT.EOF, 
            token_text="<EOF>"
        )
    
    def isNumber(self): 
        return self.c >= '0' and self.c <= '9'
    
    def isLetter(self):
        c = self.c.lower()
        return c >= 'a' and c <= 'z'

    def NAME(self):
        buf = self.consume()
        while self.isLetter():
            buf += self.consume()
        return Token(
            token_type=PGT.NAME,
            token_text=buf
        )

    def NUMBER(self):
        buf = self.consume()
        while self.isNumber():
            buf += self.consume()
        return Token(
            token_type=PGT.NUMBER,
            token_text=buf
        )

if __name__ == "__main__":
    input_str = "+-*/ = 1 11 a ab a AB ()"
    lexer = PlaygroundLexer(input_str)
    token = lexer.next_token()
    while token.type != PGT.EOF:
        print(token)
        token = lexer.next_token()
    print(token)