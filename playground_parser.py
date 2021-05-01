from token_def import PlaygroundTokens as PGT
from playground_lexer import PlaygroundLexer
from abstract_parser import AbstractParser, ParsingError

class PlaygroundParser(AbstractParser):
    def __init__(self, input_str):
        super().__init__(
            input_lexer=PlaygroundLexer(input_str),
            k=2
        )
        self.testing = False

    def program(self): 
        try:
            while self.LA(1) in {PGT.LPAREN, PGT.NAME, PGT.NUMBER} or \
                self.LT(1).text == 'print':
                self.statement()
            
            if self.LA(1) != PGT.EOF:
                raise ParsingError(f"Failed to reach EOF before parsing halted. Last token retrieved: {self.LT(1)} on line {self.input.line_number}")
        except ParsingError as pe:
            print("Syntax Error:", pe)

            # If tests are being run, re-raise exception
            if self.testing:
                raise pe 

    def statement(self):

        # Parse built in print function 
        if self.LA(1) == PGT.NAME and self.LT(1).text == 'print':
            self.pg_print()

        elif self.LA(1) == PGT.NAME and self.LA(2) == PGT.EQUAL:
            self.assign()

        elif self.LA(1) in {PGT.LPAREN, PGT.NAME, PGT.NUMBER}:
            self.add_expr()
            self.match(PGT.SEMI_COLON)

        else: 
            raise ParsingError(f"Expecting a statement; found {self.LT(1)} on line {self.input.line_number}")

    def pg_print(self):
        self.match(PGT.NAME)
        self.match(PGT.LPAREN)
        self.add_expr()
        self.match(PGT.RPAREN)
        self.match(PGT.SEMI_COLON)
    
    def assign(self):
        self.match(PGT.NAME)
        self.match(PGT.EQUAL)
        self.add_expr()
        self.match(PGT.SEMI_COLON)

    def add_expr(self): 
        if self.LA(1) not in { PGT.LPAREN, PGT.NAME, PGT.NUMBER }:
            raise ParsingError(f"Expecting an add expression; found {self.LT(1)} on line {self.input.line_number}")
        
        self.mult_expr()

        while self.LA(1) in { PGT.PLUS, PGT.MINUS }:
            self.add_op()
            self.mult_expr()

    def mult_expr(self):
        if self.LA(1) not in { PGT.LPAREN, PGT.NAME, PGT.NUMBER }:
            raise ParsingError(f"Expecting an add expression; found {self.LT(1)} on line {self.input.line_number}")

        self.atom()

        while self.LA(1) in { PGT.STAR, PGT.FSLASH }:
            self.mult_op()
            self.atom()

    def atom(self):
        if self.LA(1) == PGT.NAME:
            self.match(PGT.NAME)
        elif self.LA(1) == PGT.NUMBER:
            self.match(PGT.NUMBER)
        elif self.LA(1) == PGT.LPAREN:
            self.match(PGT.LPAREN)
            self.add_expr()
            self.match(PGT.RPAREN)
        else: 
            raise ParsingError(f"Expecting an atom; found {self.LT(1)} on line {self.input.line_number}")

    def add_op(self):
        if self.LA(1) == PGT.PLUS:
            self.match(PGT.PLUS)
        elif self.LA(1) == PGT.MINUS:
            self.match(PGT.MINUS)
        else: 
            raise ParsingError(f"Expecting an add op ('+' or '-'); found {self.LT(1)} on line {self.input.line_number}")

    def mult_op(self):
        if self.LA(1) == PGT.STAR:
            self.match(PGT.STAR)
        elif self.LA(1) == PGT.FSLASH:
            self.match(PGT.FSLASH)
        else: 
            raise ParsingError(f"Expecting an mult op ('*' or '/'); found {self.LT(1)} on line {self.input.line_number}") 

if __name__ == "__main__":
    # Sanity check, parser should parse all of this and raise no exceptions.
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