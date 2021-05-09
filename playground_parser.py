from base.abstract_parser import AbstractParser, ParsingError
from playground_ast import PG_AST
from playground_token import PG_Type
from playground_lexer import PlaygroundLexer

import functools
def _reraise_with_rule_name(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            msg = getattr(e, 'message', str(e))
            raise ParsingError(f"\nrule `{fn.__name__}`: {msg}")
    return wrapper

class PlaygroundParser(AbstractParser):
    def __init__(self, input_str):
        super().__init__(
            input_lexer=PlaygroundLexer(input_str),
            k=2,
            AST_Class=PG_AST
        )
        self.testing = False

    def program(self): 
        try:
            root = self.statements()
            if self.LA(1) != PG_Type.EOF:
                raise ParsingError(f"Failed to reach EOF before parsing halted. Last token retrieved: {self.LT(1)} on line {self.input.line_number}")
            return root 
        except ParsingError as pe:
            print("Syntax Error:", pe)

            # If tests are being run, re-raise exception
            if self.testing:
                raise pe 
            
            return None

    @_reraise_with_rule_name
    def statements(self):
        root = PG_AST(artificial=True, name="$STATEMENTS")
        while self.LA(1) in {
                PG_Type.LPAREN, PG_Type.NAME, PG_Type.PRINT, PG_Type.INT, 
                PG_Type.FLOAT, PG_Type.LCURBRACK, PG_Type.TRUE, PG_Type.FALSE,
                PG_Type.IF, PG_Type.WHILE,
            }:
            root.add_child(self.statement())
        return root 

    @_reraise_with_rule_name
    def statement(self):
        root = None 
        # Parse built in print function 
        if self.LA(1) == PG_Type.PRINT:
            root = self.pg_print()
        
        # Block statement
        elif self.LA(1) == PG_Type.LCURBRACK:
            root = self.block_stat()
        
        # Assignment 
        elif self.LA(1) == PG_Type.NAME and self.LA(2) == PG_Type.ASSIGN:
            root = self.assign()

        # Bool Expression 
        elif self.LA(1) in {
                PG_Type.LPAREN, PG_Type.NAME, PG_Type.INT, PG_Type.FLOAT,
            }:
            root = self.bool_expr()
            self.match(PG_Type.SEMI_COLON)
        
        elif self.LA(1) == PG_Type.IF:
            root = self.if_stat()

        elif self.LA(1) == PG_Type.WHILE:
            root = self.while_stat()

        else: 
            raise ParsingError(f"Expecting a statement; found {self.LT(1)} on line {self.input.line_number}")
        
        return root 
    
    @_reraise_with_rule_name
    def pg_print(self):
        root = self.match(PG_Type.PRINT)
        self.match(PG_Type.LPAREN)
        expr = self.add_expr()
        self.match(PG_Type.RPAREN)
        self.match(PG_Type.SEMI_COLON)

        root.add_child(expr)
        return root 
    
    @_reraise_with_rule_name
    def assign(self):
        name = self.match(PG_Type.NAME)
        root = self.match(PG_Type.ASSIGN)
        expr = self.bool_expr()
        self.match(PG_Type.SEMI_COLON)

        root.add_children(name, expr)
        return root 

    @_reraise_with_rule_name
    def block_stat(self):
        self.match(PG_Type.LCURBRACK)
        root = self.statements()
        self.match(PG_Type.RCURBRACK)
        return root 

    @_reraise_with_rule_name
    def if_stat(self):
        root = self.match(PG_Type.IF)
        test = self.bool_expr()
        block = self.block_stat()
        root.add_children(test, block)

        if self.LA(1) == PG_Type.ELIF:
            root.add_child(self.elif_stat())

        if self.LA(1) == PG_Type.ELSE:
            root.add_child(self.else_stat())
        
        return root 
    
    @_reraise_with_rule_name
    def elif_stat(self):
        root = self.match(PG_Type.ELIF)
        test = self.bool_expr()
        block = self.block_stat()
        root.add_children(test, block)

        while self.LA(1) == PG_Type.ELIF:
            root.add_child(self.elif_stat())

        if self.LA(1) == PG_Type.ELSE:
            root.add_child(self.else_stat())
        
        return root 

    @_reraise_with_rule_name
    def else_stat(self):
        self.match(PG_Type.ELSE)
        return self.block_stat()

    @_reraise_with_rule_name
    def while_stat(self):
        root = self.match(PG_Type.WHILE)
        test = self.bool_expr()
        block = self.block_stat()
        root.add_children(test, block)
        return root 
    
    @_reraise_with_rule_name
    def bool_expr(self):
        if self.LA(1) not in { 
                PG_Type.LPAREN, PG_Type.NAME, PG_Type.INT, 
                PG_Type.FLOAT, PG_Type.TRUE, PG_Type.FALSE 
            }:
            raise ParsingError(f"Expecting an bool expression; found {self.LT(1)} on line {self.input.line_number}")
        root = None 
        left = self.and_expr()

        while self.LA(1) == PG_Type.OR:
            if root != None:
                left = root 
            root = self.match(PG_Type.OR)
            right = self.and_expr()
            root.add_children(left, right)
        
        return root if root != None else left

    @_reraise_with_rule_name
    def and_expr(self):
        if self.LA(1) not in { 
                PG_Type.LPAREN, PG_Type.NAME, PG_Type.INT, 
                PG_Type.FLOAT, PG_Type.TRUE, PG_Type.FALSE 
            }:
            raise ParsingError(f"Expecting an and expression; found {self.LT(1)} on line {self.input.line_number}")
        root = None 
        left = self.comp_expr()

        while self.LA(1) == PG_Type.AND:
            if root != None:
                left = root 
            root = self.match(PG_Type.AND)
            right = self.comp_expr()
            root.add_children(left, right)
        
        return root if root != None else left

    @_reraise_with_rule_name
    def comp_expr(self):
        if self.LA(1) not in { 
                PG_Type.LPAREN, PG_Type.NAME, PG_Type.INT, 
                PG_Type.FLOAT, PG_Type.TRUE, PG_Type.FALSE 
            }:
            raise ParsingError(f"Expecting a comp expression; found {self.LT(1)} on line {self.input.line_number}")
        root = None 
        left = self.add_expr()

        while self.LA(1) in { 
                PG_Type.LT, PG_Type.LE, PG_Type.GT, PG_Type.GE, PG_Type.EQ 
            }:
            if root != None:
                left = root 
            root = self.cmp_op()
            right = self.add_expr()
            root.add_children(left, right)
        
        return root if root != None else left

    @_reraise_with_rule_name
    def cmp_op(self):
        root = None 
        if self.LA(1) == PG_Type.LT:
            root = self.match(PG_Type.LT)
        elif self.LA(1) == PG_Type.LE:
            root = self.match(PG_Type.LE)
        elif self.LA(1) == PG_Type.GT:
            root = self.match(PG_Type.GT)
        elif self.LA(1) == PG_Type.GE:
            root = self.match(PG_Type.GE)
        elif self.LA(1) == PG_Type.EQ:
            root = self.match(PG_Type.EQ)
        else: 
            raise ParsingError(f"Expecting a comparison operator; found {self.LT(1)} on line {self.input.line_number}")
        return root 

    @_reraise_with_rule_name
    def add_expr(self): 
        if self.LA(1) not in { 
                PG_Type.LPAREN, PG_Type.NAME, PG_Type.INT, 
                PG_Type.FLOAT, PG_Type.TRUE, PG_Type.FALSE 
            }:
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
        
    @_reraise_with_rule_name
    def mult_expr(self):
        if self.LA(1) not in { 
                PG_Type.LPAREN, PG_Type.NAME, PG_Type.INT, 
                PG_Type.FLOAT, PG_Type.TRUE, PG_Type.FALSE 
            }:
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

    @_reraise_with_rule_name
    def atom(self):
        root = None 
        if self.LA(1) == PG_Type.NAME:
            root = self.match(PG_Type.NAME)
        elif self.LA(1) == PG_Type.INT:
            root = self.match(PG_Type.INT)
        elif self.LA(1) == PG_Type.FLOAT:
            root = self.match(PG_Type.FLOAT)
        elif self.LA(1) == PG_Type.TRUE:
            root = self.match(PG_Type.TRUE)
        elif self.LA(1) == PG_Type.FALSE:
            root = self.match(PG_Type.FALSE)
        elif self.LA(1) == PG_Type.LPAREN:
            self.match(PG_Type.LPAREN)
            root = self.bool_expr()
            self.match(PG_Type.RPAREN)
        else: 
            raise ParsingError(f"Expecting an atom; found {self.LT(1)} on line {self.input.line_number}")
        return root 

    @_reraise_with_rule_name
    def add_op(self):
        root = None 
        if self.LA(1) == PG_Type.PLUS:
            root = self.match(PG_Type.PLUS)
        elif self.LA(1) == PG_Type.MINUS:
            root = self.match(PG_Type.MINUS)
        else: 
            raise ParsingError(f"Expecting an add op ('+' or '-'); found {self.LT(1)} on line {self.input.line_number}")
        return root 

    @_reraise_with_rule_name
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
                print(5.0 + 2.3);
                { a + b; }                
                {
                    {
                        print(a + b);
                    }
                }
                (5 - 3) >= 2 + 5;
                5 > 6;
                ((5 + 3) > 2 and True) or (10 <= (2 * 20) and 3 < 2);
                if (5 > 6) { a + b; }
                if (5 > 6) { print(a+b); } elif (5 <= 6 ) { print(b); } else { print(a); }
                while (a > 0) { print(a); a = a - 1; }
                if True { a; } elif False { b; } elif True { a; } else { b; }
                if True { a; } else { b; }
                if False { b } else { print(a); }
                """
    AST = PlaygroundParser(input_str=input_str).program()
    if AST:
        print(AST.to_string_tree())