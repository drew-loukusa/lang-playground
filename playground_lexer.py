from playground_token import PG_Type, PG_Token
from abstract_lexer import AbstractLexer

class PlaygroundLexer(AbstractLexer):
    def __init__(self, input_str):
        super().__init__(input_str)
    
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
        
            elif self.c == ';':
                return PG_Token(
                    token_type=PG_Type.SEMI_COLON,
                    token_text=self.consume()
                )
                
            elif self.c == '=':
                return PG_Token(
                    token_type=PG_Type.EQUAL, 
                    token_text=self.consume()
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

            elif self.isNumber():
                return self.NUMBER()
                
            elif self.isLetter():
                return self.NAME()

            else:
                raise Exception(f"Invalid character: {self.c}")
        
        return PG_Token(
            token_type=PG_Type.EOF, 
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
        return PG_Token(
            token_type=PG_Type.NAME,
            token_text=buf
        )

    def NUMBER(self):
        buf = self.consume()
        while self.isNumber():
            buf += self.consume()
        return PG_Token(
            token_type=PG_Type.NUMBER,
            token_text=buf
        )

if __name__ == "__main__":
    input_str = "+-*/ = 1 11 a ab a AB ()"
    lexer = PlaygroundLexer(input_str)
    token = lexer.next_token()
    while token.type != PG_Type.EOF:
        print(token)
        token = lexer.next_token()
    print(token)