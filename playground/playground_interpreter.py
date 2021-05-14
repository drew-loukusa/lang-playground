from playground_ast import PG_AST
from playground_token import PG_Type
from playground_parser import PlaygroundParser

class UnsupportedOperationException(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)


class Scope:
    def __init__(self, name=None):
        self.name = name 
        self.depth = 0
        self.symbols: dict = {}
        self.parent: Scope = None 
        self.children: list[Scope, ...] = []

    def resolve(self, symbol: str):
        """ 
           Attempts to locate and return whatever value was assigned to 
           'symbol' if 'symobol' exists in the current scope, or any 
           parent scope.
        """
        cur_scope = self 
        while cur_scope != None:
            if symbol in cur_scope.symbols:
                return cur_scope.symbols[symbol]
            cur_scope = cur_scope.parent 
        raise NameError(f"Symbol {symbol} could not be found!")

    def resolve_scope(self, symbol: str):
        """ 
           Attempts to locate and return the scope object of symbol
           'symbol' if 'symobol' exists in the current scope, or any 
           parent scope.
        """
        cur_scope = self 
        while cur_scope != None:
            if symbol in cur_scope.symbols:
                return cur_scope
            cur_scope = cur_scope.parent 
        return None 

class Function:
    def __init__(self, name: str, params: Scope, code: PG_AST):
        self.name = name 
        self.params = params
        self.code = code 

class PlaygroundInterpreter:

    def __init__(self):
        self.globals = Scope(name="globals")       
        self.current_space = self.globals
        self.root = None
        self.parser = None

    def _push_scope(self, name=""): 
        """ 
           Creates a new scope, places new scope in child list of the 
           current scope, and then sets the current scope to the new scope.
           
           Returns None 
        """
        new_scope = Scope(name=name)
        new_scope.depth = self.current_space.depth + 1
        new_scope.parent = self.current_space
        self.current_space.children.append(new_scope)
        self.current_space = new_scope 

    def _pop_scope(self): 
        """ 
           Sets the current scope to the parent of the current scope.
           
           Returns None 
        """
        parent_scope = self.current_space.parent 
        # In some cases, like function defs, or class or struct defs, 
        # We should not pop the scope. We want those symbols defined.
        parent_scope.children.pop()
        self.current_space = parent_scope

    def interp(self, input_str):
        """ 
            Call this to run your program.

            Returns None 
        """
        self.parser = PlaygroundParser(input_str=input_str)

        self.root = self.parser.program()
        if self.root != None:
            self._program(self.root)

    def _exec(self, t: PG_AST):
        """ 
            Executes node 't' according to it's token type.
            
            May return an INT, a FLOAT, or a BOOL
        """
        try:
            token_type = t.token.type if t.token != None else None

            if t.artificial == True and t.name == "$STATEMENTS": 
                self._statements(t)
            
            elif token_type == PG_Type.PRINT:   
                self._print(t)

            # Function call 
            elif token_type == PG_Type.NAME and len(t.children) > 0 and \
                 t.children[0].name == "$ARG_LIST":
                self._func_call(t)

            elif token_type == PG_Type.DEF:
                self._func_def(t)

            elif token_type == PG_Type.ASSIGN:  
                self._assign(t)

            elif token_type in {
                    PG_Type.IF,
                    PG_Type.ELIF,
                }: 
                self._conditional(t)

            elif token_type == PG_Type.WHILE:
                self._while(t)

            elif token_type in { 
                    PG_Type.PLUS, 
                    PG_Type.MINUS, 
                    PG_Type.STAR, 
                    PG_Type.FSLASH
                }:
                return self._op(t)

            elif token_type == PG_Type.AND: 
                return self._and(t)
            elif token_type == PG_Type.OR: 
                return self._or(t)

            elif token_type in { 
                    PG_Type.EQ, 
                    PG_Type.LT, 
                    PG_Type.LE, 
                    PG_Type.GT,
                    PG_Type.GE,
                }:
                return self._cmp(t)

            elif token_type in { PG_Type.TRUE, PG_Type.FALSE }:    
                return True if t.token.text == "True" else False

            elif token_type == PG_Type.NAME:    return self._load(t)
            elif token_type == PG_Type.INT:     return int(t.token.text)
            elif token_type == PG_Type.FLOAT:   return float(t.token.text)
            elif token_type == PG_Type.STRING:  return str(t.token.text)
            else:
                raise UnsupportedOperationException(f"Node {t.name}: <{t.token}> not handled")

        except UnsupportedOperationException as e:
            print("Problem executing", t.to_string_tree(), e)
        return None

    def _program(self, t: PG_AST):
        """ 
            Executes the program.

            returns None
        """
        self._statements(t)

    def _statements(self, t: PG_AST):
        """ 
            Executes nested statements;
            This is what is called to handle "block" statements.

            Returns None
        """
        self._push_scope()
        for statement in t.children:
            self._exec(statement)
        self._pop_scope()

    def _print(self, t: PG_AST):
        """ 
            Prints out the result of 't's only substree using pythons built in print.
            t may have a single child, which will be an artificial node with name 
            $ARG_LIST containing a list of arguments.

            Each argument in the $ARG_LIST.children list will be executed, and printed
            on a single line. A new line will be appended automatically.

            Returns None
        """
        if len(t.children) > 0:
            arg_list = t.children[0]
            for arg in arg_list.children:
                print( self._exec(arg), end='')
            print()
        else:
            print()

    def _func_def(self, t: PG_AST):
        """ 
            Defines a function. 

            Raises an exception if a function is already defined with that name in the current scope, 
            or any parent scopes.

            Returns None
        """
        name = t.children[0].token.text
        params = []
        if len(t.children[1].children) > 0:
            param_list = t.children[1]
            for param in param_list.children:
                params.append(param.token.text)
        
        code = t.children[2]

        new_func = Function(name=name, params=params, code=code)
        self.current_space.symbols[name] = new_func


    def _func_call(self, t: PG_AST):
        """ 
            Executes a function call.
            Returns None

            FUTURE FEATUER: WILL OPTIONALY RETURN VALUES
        """
        name = t.token.text 
        args_list = []
        if len(t.children) > 0:
            for arg in t.children[0].children:
                args_list.append(
                    self._exec(arg)
                )

        func = self._load(t)

        args_len = len(args_list)
        params_len = len(func.params)
        if args_len < params_len:
            raise TypeError(f"{name}() called, but {params_len - args_len} parameters were missing")
    
        if args_len > params_len:
            raise TypeError(f"Function {name} called, but too many parameters were given")
        
        self._push_scope(name=f"func_scope_{name}")
        for param, arg in zip(func.params, args_list):
            self.current_space.symbols[param] = arg

        self._statements(func.code)
        self._pop_scope()

    def _assign(self, t: PG_AST):
        """ 
            Performs an assignment operation.

            Assigns the result of 't's right subtree 
            to the symbol referenced by 't's left subtree, (a leaf node)

            The scope where the symbol was originally defined is located,
            then the symbol is given it's new value in said scope.

            Returns None
        """
        lhs = t.children[0]
        expr = t.children[1]
        value = self._exec(expr)

        # Get the scope where the symbol was originally defined 
        symbol_scope = self.current_space.resolve_scope(lhs.token.text)

        # If none, symbol has not yet been defined
        if symbol_scope is None: 
            symbol_scope = self.current_space

        # Assign symbol it's new value 
        symbol_scope.symbols[lhs.token.text] = value

    def _load(self, t: PG_AST):
        """ 
            Returns the value or object refrenced by the symbol in 't',
            if it exists in the current scope, or any parent scopes.   
        """
        return self.current_space.resolve(t.token.text)

    def _conditional(self, t: PG_AST):
        """ 
            Executes a conditional statement: 'if' 'elif' 'else'
            Returns None   
        """
        test = t.children[0]
        block = t.children[1]
        if self._exec(test):
            self._exec(block)

        # elif or else clause present
        elif len(t.children) == 3:
           self._exec(t.children[2])

    def _while(self, t: PG_AST):
        """ 
            Executes a while statement.
            Returns None   
        """
        test = t.children[0]
        block = t.children[1]
        while self._exec(test):
            self._exec(block)

    def _op(self, t: PG_AST):
        """ 
            Performs a math operation.
            The operands of the operation are the 
            left and right sub-trees of 't'.

            Returns Python INT or FLOAT
        """
        token_type = t.token.type
        a = self._exec( t.children[0] )
        b = self._exec( t.children[1] )

        if   token_type == PG_Type.PLUS:    return a + b
        elif token_type == PG_Type.MINUS:   return a - b
        elif token_type == PG_Type.STAR:    return a * b
        elif token_type == PG_Type.FSLASH:  return a / b

    def _and(self, t: PG_AST):
        """
            Performs an AND operation.
            The operands of the operation are the 
            left and right sub-trees of PG_AST node 't'.

            Returns Python BOOL 
        """
        token_type = t.token.type
        a = self._exec( t.children[0] )

        # Short circuit the AND
        if a == False:
            return False 

        else:
            b = self._exec( t.children[1] )
            return b == True 

    def _or(self, t: PG_AST):
        """
            Performs an OR operation.
            The operands of the operation are the 
            left and right sub-trees of PG_AST node 't'.

            Returns Python BOOL 
        """ 
        token_type = t.token.type
        a = self._exec( t.children[0] )

        # Short Circuit 'or' statement 
        if a == True:
            return True  

        else:
            b = self._exec( t.children[1] )
            return b == True 
        

    def _cmp(self, t: PG_AST):
        """ 
            Performs a comparison operation.
            The operands of the operation are the 
            left and right sub-trees of PG_AST node 't'.

            Returns Python BOOL 
        """
        token_type = t.token.type
        a = self._exec( t.children[0] )
        b = self._exec( t.children[1] )

        if   token_type == PG_Type.EQ:  return a == b
        elif token_type == PG_Type.LT:  return a < b
        elif token_type == PG_Type.LE:  return a <= b
        elif token_type == PG_Type.GT:  return a > b
        elif token_type == PG_Type.GE:  return a >= b

if __name__ == "__main__":
    code = """
print(10 < True);
if(True and True){print(True);}
if(True or True){print(True);}
if(False or True){print(True);}
if(True){print(True);} 
print((True and True))
;
a = 5;
b = 5;
print(a + b);

print(5 - 2);
print(5 * 2);
print(5 / 2);

a = 5 / 2;
print(a + 3);
foo = 3 * 5;
print(foo + (a * (3  -  4)));
print(3 - 4);
print(2.4 + 1.3);

a = 2;
b = 3;
c = 2;
{
    c = 1;
    print(c);
}
print(c);

if (5 < 6){
    print("5 is less than 6");
}
elif (6 > 3){
    print("6 is greater than 3");
}
print("Printing 10 through 1 in decreasing order");
a = 10;
while (a > 0) {
    print(a);
    a = a - 1;
}
print("A test string");
a = "String stored in a";
print(a);
a = 5;
b = 3;
c = 2;
print("a: ", a, ", b: ", b, ", c: ", c);
def goobar(a, b, c){
    print("func goobar called!");
    print(a);
    print(b + c);
}
goobar(1, 2, 3);
def foo(d, e, f){
    print("func foo called!");
    print("d: ", d);
    print("e: ", e);
    print("f: ", f);
}
foo(1, 2, 3);

def noParams(){
    print("func noParams called!");
    print("This func has no params");
}
noParams();

foo(5, 6, 7);

{
    foo(3, 1, 2);
}

def outer(outA){
    def inner(inA){
        print("Inner a: ", inA);
    }
    inner(10);
    print("outer a: ", outA);
}
outer(15);
inner(10);
"""
    PI = PlaygroundInterpreter()
    PI.interp(input_str=code)