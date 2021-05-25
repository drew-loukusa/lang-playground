from functools import wraps

from abstract.abs_parser import AbstractParser, ParsingError
from playground_ast import PG_AST
from playground_token import PG_Type as PGT
from playground_lexer import PlaygroundLexer

DEBUG=False
def _reraise_with_rule_name(fn):
    if DEBUG: return fn
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            msg = getattr(e, "message", str(e))
            raise ParsingError(f"\nrule `{fn.__name__}`: {msg}")

    return wrapper


class PlaygroundParser(AbstractParser):
    def __init__(self, input_str):
        super().__init__(input_lexer=PlaygroundLexer(input_str), k=4, AST_Class=PG_AST)
        self.testing = False

        self.expr_LA_set = {
            PGT.LPAREN,
            PGT.NAME,
            PGT.INT,
            PGT.FLOAT,
            PGT.STRING,
            PGT.TRUE,
            PGT.FALSE,
        }

    def program(self):
        try:
            root = self.statements()
            if self.LA(1) != PGT.EOF:
                raise ParsingError(
                    f"Failed to reach EOF before parsing halted. Last token retrieved: {self.LT(1)} on line {self.input.line_number}"
                )
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
            PGT.LPAREN,
            PGT.NAME,
            PGT.PRINT,
            PGT.INT,
            PGT.FLOAT,
            PGT.LCURBRACK,
            PGT.TRUE,
            PGT.FALSE,
            PGT.IF,
            PGT.WHILE,
            PGT.DEF,
            PGT.CLASS,
            PGT.RETURN,
        }:
            root.add_child(self.statement())
        return root

    @_reraise_with_rule_name
    def statement(self):
        root = None
        # Parse built in print function
        if self.LA(1) == PGT.PRINT:
            root = self.pg_print()

        elif self.LA(1) == PGT.CLASS:
            root = self.class_def()

        elif self.LA(1) == PGT.DEF:
            root = self.func_def()

        elif self.LA(1) == PGT.RETURN:
            root = self.return_stat()

        # Block statement
        elif self.LA(1) == PGT.LCURBRACK:
            root = self.block_stat()

        # Assignment
        elif self.LA(1) == PGT.NAME and (
            self.LA(2) != PGT.SEMI_COLON and (
            self.LA(2) == PGT.ASSIGN or self.LA(4) == PGT.ASSIGN
        )):
            root = self.assign()

        # Bool Expression
        elif self.LA(1) in self.expr_LA_set:
            root = self.bool_expr()
            self.match(PGT.SEMI_COLON)

        elif self.LA(1) == PGT.IF:
            root = self.if_stat()

        elif self.LA(1) == PGT.WHILE:
            root = self.while_stat()

        else:
            raise ParsingError(
                f"Expecting a statement; found {self.LT(1)} on line {self.input.line_number}"
            )

        return root

    @_reraise_with_rule_name
    def pg_print(self):
        root = self.match(PGT.PRINT)
        self.match(PGT.LPAREN)
        root.add_child(self.arg_list())
        self.match(PGT.RPAREN)
        self.match(PGT.SEMI_COLON)
        return root

    @_reraise_with_rule_name
    def arg_list(self):
        root = PG_AST(artificial=True, name="$ARG_LIST")

        # An argument list CAN be empty
        if self.LA(1) in self.expr_LA_set:
            root.add_child(self.bool_expr())

            # Check for additional arguments
            while self.LA(1) == PGT.COMMA:
                self.match(PGT.COMMA)
                root.add_child(self.bool_expr())

        return root

    def id_list(self):
        root = PG_AST(artificial=True, name="$ID_LIST")

        # An id list CAN be empty
        if self.LA(1) == PGT.NAME:
            root.add_child(self.match(PGT.NAME))

            # Check for additional parameters
            while self.LA(1) == PGT.COMMA:
                self.match(PGT.COMMA)
                root.add_child(self.match(PGT.NAME))

        return root

    @_reraise_with_rule_name
    def assign(self):
        name = self.match(PGT.NAME)
        dot_name = None
        if self.LA(1) == PGT.DOT:
            dot_name = self.match(PGT.DOT)
            rhs = self.match(PGT.NAME)
            dot_name.add_children(name, rhs)
            name = dot_name

        root = self.match(PGT.ASSIGN)
        expr = self.bool_expr()
        self.match(PGT.SEMI_COLON)

        root.add_children(name, expr)
        return root

    @_reraise_with_rule_name
    def block_stat(self):
        self.match(PGT.LCURBRACK)
        root = self.statements()
        self.match(PGT.RCURBRACK)
        return root

    @_reraise_with_rule_name
    def if_stat(self):
        root = self.match(PGT.IF)
        test = self.bool_expr()
        block = self.block_stat()
        root.add_children(test, block)

        if self.LA(1) == PGT.ELIF:
            root.add_child(self.elif_stat())

        if self.LA(1) == PGT.ELSE:
            root.add_child(self.else_stat())

        return root

    @_reraise_with_rule_name
    def elif_stat(self):
        root = self.match(PGT.ELIF)
        test = self.bool_expr()
        block = self.block_stat()
        root.add_children(test, block)

        while self.LA(1) == PGT.ELIF:
            root.add_child(self.elif_stat())

        if self.LA(1) == PGT.ELSE:
            root.add_child(self.else_stat())

        return root

    @_reraise_with_rule_name
    def else_stat(self):
        self.match(PGT.ELSE)
        return self.block_stat()

    @_reraise_with_rule_name
    def while_stat(self):
        root = self.match(PGT.WHILE)
        test = self.bool_expr()
        block = self.block_stat()
        root.add_children(test, block)
        return root

    @_reraise_with_rule_name
    def func_def(self):
        root = self.match(PGT.DEF)
        root.add_child(self.match(PGT.NAME))
        self.match(PGT.LPAREN)
        root.add_child(self.id_list())
        self.match(PGT.RPAREN)
        root.add_child(self.block_stat())
        return root

    @_reraise_with_rule_name
    def func_call(self):
        root = self.match(PGT.NAME)
        self.match(PGT.LPAREN)
        root.add_child(self.arg_list())
        self.match(PGT.RPAREN)
        return root

    @_reraise_with_rule_name
    def return_stat(self):
        root = self.match(PGT.RETURN)
        root.add_child(self.bool_expr())
        self.match(PGT.SEMI_COLON)
        return root

    @_reraise_with_rule_name
    def class_def(self):
        root = self.match(PGT.CLASS)
        class_name = self.match(PGT.NAME)
        class_body = self.block_stat()
        root.add_children(class_name, class_body)
        return root

    @_reraise_with_rule_name
    def dotted_expr(self):
        LHS = self.match(PGT.NAME)
        root = self.match(PGT.DOT)
        RHS = None
        if self.LA(2) == PGT.LPAREN:
            RHS = self.func_call()
        else:
            RHS = self.match(PGT.NAME)

        root.add_children(LHS, RHS)
        return root

    @_reraise_with_rule_name
    def bool_expr(self):
        if self.LA(1) not in self.expr_LA_set:
            raise ParsingError(
                f"Expecting an bool expression; found {self.LT(1)} on line {self.input.line_number}"
            )
        root = None
        left = self.and_expr()

        while self.LA(1) == PGT.OR:
            if root != None:
                left = root
            root = self.match(PGT.OR)
            right = self.and_expr()
            root.add_children(left, right)

        return root if root != None else left

    @_reraise_with_rule_name
    def and_expr(self):
        if self.LA(1) not in self.expr_LA_set:
            raise ParsingError(
                f"Expecting an and expression; found {self.LT(1)} on line {self.input.line_number}"
            )
        root = None
        left = self.comp_expr()

        while self.LA(1) == PGT.AND:
            if root != None:
                left = root
            root = self.match(PGT.AND)
            right = self.comp_expr()
            root.add_children(left, right)

        return root if root != None else left

    @_reraise_with_rule_name
    def comp_expr(self):
        if self.LA(1) not in self.expr_LA_set:
            raise ParsingError(
                f"Expecting a comp expression; found {self.LT(1)} on line {self.input.line_number}"
            )
        root = None
        left = self.add_expr()

        while self.LA(1) in {
            PGT.LT,
            PGT.LE,
            PGT.GT,
            PGT.GE,
            PGT.EQ,
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
        if self.LA(1) == PGT.LT:
            root = self.match(PGT.LT)
        elif self.LA(1) == PGT.LE:
            root = self.match(PGT.LE)
        elif self.LA(1) == PGT.GT:
            root = self.match(PGT.GT)
        elif self.LA(1) == PGT.GE:
            root = self.match(PGT.GE)
        elif self.LA(1) == PGT.EQ:
            root = self.match(PGT.EQ)
        else:
            raise ParsingError(
                f"Expecting a comparison operator; found {self.LT(1)} on line {self.input.line_number}"
            )
        return root

    @_reraise_with_rule_name
    def add_expr(self):
        if self.LA(1) not in self.expr_LA_set:
            raise ParsingError(
                f"Expecting an add expression; found {self.LT(1)} on line {self.input.line_number}"
            )
        root = None
        left = self.mult_expr()

        while self.LA(1) in {PGT.PLUS, PGT.MINUS}:
            if root != None:
                left = root
            root = self.add_op()
            right = self.mult_expr()
            root.add_children(left, right)

        return root if root != None else left

    @_reraise_with_rule_name
    def mult_expr(self):
        if self.LA(1) not in self.expr_LA_set:
            raise ParsingError(
                f"Expecting an add expression; found {self.LT(1)} on line {self.input.line_number}"
            )

        root = None
        left = self.atom()

        while self.LA(1) in {PGT.STAR, PGT.FSLASH, PGT.PERCENT}:
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
        if self.LA(1) == PGT.NAME and self.LA(2) == PGT.DOT:
            root = self.dotted_expr()
        elif self.LA(1) == PGT.NAME and self.LA(2) == PGT.LPAREN:
            root = self.func_call()
        elif self.LA(1) == PGT.NAME:
            root = self.match(PGT.NAME)
        elif self.LA(1) == PGT.INT:
            root = self.match(PGT.INT)
        elif self.LA(1) == PGT.FLOAT:
            root = self.match(PGT.FLOAT)
        elif self.LA(1) == PGT.STRING:
            root = self.match(PGT.STRING)
        elif self.LA(1) == PGT.TRUE:
            root = self.match(PGT.TRUE)
        elif self.LA(1) == PGT.FALSE:
            root = self.match(PGT.FALSE)
        elif self.LA(1) == PGT.LPAREN:
            self.match(PGT.LPAREN)
            root = self.bool_expr()
            self.match(PGT.RPAREN)
        else:
            raise ParsingError(
                f"Expecting an atom; found {self.LT(1)} on line {self.input.line_number}"
            )
        return root

    @_reraise_with_rule_name
    def add_op(self):
        root = None
        if self.LA(1) == PGT.PLUS:
            root = self.match(PGT.PLUS)
        elif self.LA(1) == PGT.MINUS:
            root = self.match(PGT.MINUS)
        else:
            raise ParsingError(
                f"Expecting an add op ('+' or '-'); found {self.LT(1)} on line {self.input.line_number}"
            )
        return root

    @_reraise_with_rule_name
    def mult_op(self):
        root = None
        if self.LA(1) == PGT.STAR:
            root = self.match(PGT.STAR)
        elif self.LA(1) == PGT.FSLASH:
            root = self.match(PGT.FSLASH)

        elif self.LA(1) == PGT.PERCENT:
            root = self.match(PGT.PERCENT)
        else:
            raise ParsingError(
                f"Expecting an mult op ('*' or '/'); found {self.LT(1)} on line {self.input.line_number}"
            )
        return root


if __name__ == "__main__":
    # Sanity check, parser should parse all of this and raise no exceptions.
    input_str = """
                
                print("A test string");
                a = "String stored in a";
                print(a);
                if(True){
                    print(True);
                }
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
                if False { b; } else { print(a); }

                print(a, b, 10, 5, "hello");
                print();
                foo();
                bar(a);
                fooBar(a, b, c);
                def barfoo(){}
                def goofar(a){
                    print(a);
                }
                def doogar(a, b){
                    print(a);
                    print(b);
                }
                foo.bar;
                foo.bar();
                a = foo.bar;
                a = foo.bar();
                foo.bar = a;
    
                Class Goober {
                    this.a;
                    def Goober(a){
                        this.a = a;
                    }
                    def printA(){
                        print(this.a);
                    }
                }
                goober;
                Class Fooby{
                    poopy;
                    goopy = 5;
                }
                a = 5 % 3;

                def func_with_return_stat(arg_a){
                    arg_a = arg_a + 1;
                    print(arg_a);
                    return arg_a;
                }
                """
                
    AST = PlaygroundParser(input_str=input_str).program()
    if AST:
        print(AST.to_string_tree())
