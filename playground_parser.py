from token import PlaygroundTokens as PGT
from abstract_parser import Parser 
from playground_lexer import PlaygroundLexer
class PlaygroundParser(Parser):
    def __init__(self, input_str):
        super().__init__(
            input_lexer=PlaygroundLexer(input_str),
            k=2
        )

    def program(self): 
        while self.LA(1) in {PGT.LPAREN, PGT.NAME, PGT.NUMBER} or \
            self.LT(1).text == 'print':
            self.statement()

    def statement(self):

        # Parse built in print function 
        if self.LA(1) == PGT.NAME and self.LT(1).text == 'print':
            self.pg_print()

        elif self.LA_SEQ_IS( PGT.NAME, PGT.EQUAL ):
            self.assign()

        elif self.LA(1) in {PGT.LPAREN, PGT.NAME, PGT.NUMBER}:
            self.expr()

        else: 
            raise Exception(f"Expecting a statement; found {self.LT(1)}")

    def pg_print(self):
        self.match(PGT.NAME)
        self.match(PGT.LPAREN)
        self.expr()
        self.match(PGT.RPAREN)
        self.match(PGT.SEMI_COLON)
    
    def assign(self):
        self.match(PGT.NAME)
        self.match(PGT.EQUAL)
        self.expr()
        self.match(PGT.SEMI_COLON)

    def expr(self):
        if self.LA(1) == PGT.LPAREN:
            self.match(PGT.LPAREN)
            self.add_expr()
            self.match(PGT.RPAREN)
        
        elif self.LA(1) in { PGT.NAME, PGT.NUMBER }:
            self.add_expr()

        else: 
            raise Exception(f"Expecting an expression; found {self.LT(1)}")

    def add_expr(self): 
        if self.LA(1) not in { PGT.LPAREN, PGT.NAME, PGT.NUMBER }:
            raise Exception(f"Expecting an add expression; found {self.LT(1)}")
        
        self.mult_expr()

        while self.LA(1) in { PGT.PLUS, PGT.MINUS }:
            self.add_op()
            self.mult_expr()

    def mult_expr(self):
        if self.LA(1) not in { PGT.LPAREN, PGT.NAME, PGT.NUMBER }:
            raise Exception(f"Expecting an add expression; found {self.LT(1)}")

        self.atom()

        while self.LA(1) in { PGT.STAR, PGT.FSLASH }:
            self.mult_op()
            self.atom()

    def atom(self):
        if self.LA(1) == PGT.NAME:
            self.match(PGT.NAME)
        elif self.LA(1) == PGT.NUMBER:
            self.match(PGT.NUMBER)
        elif self.LA(1) in { PGT.LPAREN, PGT.NAME, PGT.NUMBER }:
            self.expr()
        else: 
            raise Exception(f"Expecting an atom; found {self.LT(1)}")

    def add_op(self):
        if self.LA(1) == PGT.PLUS:
            self.match(PGT.PLUS)
        elif self.LA(1) == PGT.MINUS:
            self.match(PGT.MINUS)
        else: 
            raise Exception(f"Expecting an add op ('+' or '-'); found {self.LT(1)}")

    def mult_op(self):
        if self.LA(1) == PGT.STAR:
            self.match(PGT.STAR)
        elif self.LA(1) == PGT.FSLASH:
            self.match(PGT.FSLASH)
        else: 
            raise Exception(f"Expecting an mult op ('*' or '/'); found {self.LT(1)}") 

if __name__ == "__main__":
    input_str = """
5 + 5;
10 + 10;
5 - 5;
5 * 5;
5 / 5; 
5 + 5 * 5;
5 * 5 + 5;
a * a - a;
foo + foo * bar;
(5 + 5) * foo;
goo = 5;
goo = bar;
goo = 5 + 5;
goo = (5 + 5);
goo = (5 + 5) * 5;
print(5);
print(goo);
print(5 + 5);
print(a + a); 
print(5 * (3 + 2));
"""
    PlaygroundParser(input_str=input_str).program()

    input_str = "5 + 5"
    PlaygroundParser(input_str=input_str).program()