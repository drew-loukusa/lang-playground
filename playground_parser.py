from abstract_syntax_tree import AST
from abstract_parser import AbstractParser, ParsingError
from playground_token import PG_Type
from playground_lexer import PlaygroundLexer

class PlaygroundParser(AbstractParser):
    def __init__(self, input_str):
        super().__init__(
            input_lexer=PlaygroundLexer(input_str),
            k=2
        )
        self.testing = False

    def program(self): 
        root = AST(artificial=True, name="$PROGRAM")
        try:
            while self.LA(1) in {PG_Type.LPAREN, PG_Type.NAME, PG_Type.NUMBER} or \
                self.LT(1).text == 'print':
                root.add_child(self.statement())
            
            if self.LA(1) != PG_Type.EOF:
                raise ParsingError(f"Failed to reach EOF before parsing halted. Last token retrieved: {self.LT(1)} on line {self.input.line_number}")
            return root 
        except ParsingError as pe:
            print("Syntax Error:", pe)

            # If tests are being run, re-raise exception
            if self.testing:
                raise pe 

    def statement(self):

        root = None 
        # Parse built in print function 
        if self.LA(1) == PG_Type.NAME and self.LT(1).text == 'print':
            root = self.pg_print()

        elif self.LA(1) == PG_Type.NAME and self.LA(2) == PG_Type.EQUAL:
            root = self.assign()

        elif self.LA(1) in {PG_Type.LPAREN, PG_Type.NAME, PG_Type.NUMBER}:
            root = self.add_expr()
            self.match(PG_Type.SEMI_COLON)

        else: 
            raise ParsingError(f"Expecting a statement; found {self.LT(1)} on line {self.input.line_number}")
        
        return root 

    def pg_print(self):
        root = self.match(PG_Type.NAME)
        self.match(PG_Type.LPAREN)
        expr = self.add_expr()
        self.match(PG_Type.RPAREN)
        self.match(PG_Type.SEMI_COLON)

        root.add_child(expr)
        return root 
    
    def assign(self):
        name = self.match(PG_Type.NAME)
        root = self.match(PG_Type.EQUAL)
        expr = self.add_expr()
        self.match(PG_Type.SEMI_COLON)

        root.add_children(name, expr)
        return root 

    def add_expr(self): 
        if self.LA(1) not in { PG_Type.LPAREN, PG_Type.NAME, PG_Type.NUMBER }:
            raise ParsingError(f"Expecting an add expression; found {self.LT(1)} on line {self.input.line_number}")
        root = None 
        left = self.mult_expr()

        while self.LA(1) in { PG_Type.PLUS, PG_Type.MINUS }:
            if root != None:
                left = root 
            root = self.add_op()
            right = self.mult_expr()
            root.add_children(left, right)
        
        return root if root != None else left
        
    def mult_expr(self):
        if self.LA(1) not in { PG_Type.LPAREN, PG_Type.NAME, PG_Type.NUMBER }:
            raise ParsingError(f"Expecting an add expression; found {self.LT(1)} on line {self.input.line_number}")
        
        root = None 
        left = self.atom() 

        while self.LA(1) in { PG_Type.STAR, PG_Type.FSLASH }:
            # Root can be set if we're parsing a continuous string of 
            # multiplications:
            # 2 * 2 * 2
            # Tree looks like = * (2 2), 
            #              then * ((* (2 2)) 2)
            if root != None:
                left = root 
            root = self.mult_op()
            right = self.atom()
            root.add_children(left, right)

        return root if root != None else left

    def atom(self):
        root = None 
        if self.LA(1) == PG_Type.NAME:
            root = self.match(PG_Type.NAME)
        elif self.LA(1) == PG_Type.NUMBER:
            root = self.match(PG_Type.NUMBER)
        elif self.LA(1) == PG_Type.LPAREN:
            self.match(PG_Type.LPAREN)
            root = self.add_expr()
            self.match(PG_Type.RPAREN)
        else: 
            raise ParsingError(f"Expecting an atom; found {self.LT(1)} on line {self.input.line_number}")
        return root 

    def add_op(self):
        root = None 
        if self.LA(1) == PG_Type.PLUS:
            root = self.match(PG_Type.PLUS)
        elif self.LA(1) == PG_Type.MINUS:
            root = self.match(PG_Type.MINUS)
        else: 
            raise ParsingError(f"Expecting an add op ('+' or '-'); found {self.LT(1)} on line {self.input.line_number}")
        return root 

    def mult_op(self):
        root = None
        if self.LA(1) == PG_Type.STAR:
            root = self.match(PG_Type.STAR)
        elif self.LA(1) == PG_Type.FSLASH:
            root = self.match(PG_Type.FSLASH)
        else: 
            raise ParsingError(f"Expecting an mult op ('*' or '/'); found {self.LT(1)} on line {self.input.line_number}") 
        return root 

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
    AST = PlaygroundParser(input_str=input_str).program()
    AST.to_string_tree()