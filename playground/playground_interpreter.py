from copy import deepcopy
from collections import defaultdict

from playground_ast import PG_AST
from playground_token import PG_Type as PGT
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
    
    def __repr__(self):
        return f"< Scope: {self.name}, depth: {self.depth}, parent: {self.parent.name}, num_children {len(self.children)}"

    def resolve(self, symbol: str):
        """ 
           Attempts to locate and return whatever value was assigned to 
           'symbol' if 'symbol' exists in the current scope, or any 
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
           'symbol' if 'symbol' exists in the current scope, or any 
           parent scope.
        """
        cur_scope = self 
        while cur_scope != None:
            if symbol in cur_scope.symbols:
                return cur_scope
            cur_scope = cur_scope.parent 
        return None 

class PG_Function:
    def __init__(self, name: str, params: Scope, code: PG_AST):
        self.name = name 
        self.params = params
        self.code = code  

    def __repr__(self):
        return f"<Function: {self.name}, params: {self.params} >"

class PG_Class(Scope):
    def __init__(self, name: str, is_class_def=False):
        # Is this the "original" object? I.E. the class definition?
        self.is_class_def = is_class_def
        super().__init__(name=name)
        self.methods = defaultdict(dict)
    
    def __repr__(self):
        return f"< Class: {self.name}, attrs: {self.attrs} methods: {self.methods} >"

class PlaygroundInterpreter:

    def __init__(self):
        self.globals = Scope(name="globals")       
        self.current_space = self.globals
        self.root = None
        self.parser = None

        self.operators = { 
            PGT.PLUS, 
            PGT.MINUS, 
            PGT.STAR, 
            PGT.FSLASH
        }

        self.conditionals = {
            PGT.IF,
            PGT.ELIF,
        }

        self.comparisons = { 
            PGT.EQ, 
            PGT.LT, 
            PGT.LE, 
            PGT.GT,
            PGT.GE,
        }

        self.booleans = { 
            PGT.TRUE, 
            PGT.FALSE 
        }

    
    def _push_scope(self, name="", scope_to_use=None): 
        """ 
           Creates a new scope (if one was not passed in via 'scope_to_use'), 
           places new scope in child list of the current scope, and then sets
           the current scope to the new scope.
           
           Returns None 
        """
        new_scope = Scope(name=name) if scope_to_use is None else scope_to_use
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

    def is_function_call(self, t: PG_AST):
        token_type = t.token.type if t.token != None else None
        return token_type == PGT.NAME and \
            len(t.children) > 0 and \
            t.children[0].name == "$ARG_LIST"

    def _exec(self, t: PG_AST):
        """ 
            Executes node 't' according to it's token type.
            
            May return an INT, a FLOAT, or a BOOL
        """
        try:
            token_type = t.token.type if t.token != None else None

            if t.artificial == True and t.name == "$STATEMENTS": 
                self._statements(t)

            elif token_type is PGT.CLASS:   
                self._class_def(t)
            
            elif token_type is PGT.PRINT:   
                self._print(t)

            elif token_type is PGT.DOT:
                return self._dotted_expr(t)

            elif self.is_function_call(t):
                return self._func_call(t)

            elif token_type is PGT.DEF:
                self._func_def(t)

            elif token_type is PGT.ASSIGN:  
                self._assign(t)

            elif token_type in self.conditionals: 
                self._conditional(t)

            elif token_type == PGT.WHILE:
                self._while(t)

            elif token_type in self.operators:
                return self._op(t)

            elif token_type is PGT.AND: 
                return self._and(t)

            elif token_type is PGT.OR: 
                return self._or(t)

            elif token_type in self.comparisons:
                return self._cmp(t)

            elif token_type in self.booleans:    
                return t.token.text == "True"

            elif token_type is PGT.NAME:    return self._load(t)
            elif token_type is PGT.INT:     return int(t.token.text)
            elif token_type is PGT.FLOAT:   return float(t.token.text)
            elif token_type is PGT.STRING:  return str(t.token.text)
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
            Prints out the result of 't's only subtree using pythons built in print.
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

    def _dotted_expr(self, t: PG_AST):
        lhs = t.children[0]
        rhs = t.children[1]

        instance = self._load(lhs)

        rhs_tk_type = rhs.token.type 
        rhs_child_len = len(rhs.children)
        # Dotted function call 
        if rhs_tk_type is PGT.NAME and rhs_child_len > 0 and \
                 rhs.children[0].name == "$ARG_LIST":
            self._push_scope(
                name="", 
                scope_to_use=instance
            )
            result = self._func_call(rhs)
            self._pop_scope()
            return result 

        # Dotted field access
        elif rhs_tk_type is PGT.NAME:
            self._push_scope(
                name="", 
                scope_to_use=instance
            )
            result = self._load(rhs)
            self._pop_scope()
            return result


    def _func_def(self, t: PG_AST):
        """ 
            Defines a function. 

            Raises an exception if a function is already defined with that name in the current scope, 
            or any parent scopes.

            Returns a PG_Function object
        """
        name = t.children[0].token.text
        params = []
        if len(t.children[1].children) > 0:
            param_list = t.children[1]
            for param in param_list.children:
                params.append(param.token.text)
        
        code = t.children[2]

        new_func = PG_Function(name=name, params=params, code=code)
        self.current_space.symbols[name] = new_func
        return new_func

    def _func_call(self, t: PG_AST):
        """ 
            Executes a function call. 
            Loads the previously created function object (which holds the definition
            for the function) and uses it to execute the function. 

            The function object holds the function name, function parameters,
            and function code (as a PG_AST sub-tree)

            Returns None

            FUTURE FEATURE: WILL OPTIONALY RETURN VALUES
        """
        name = t.token.text 
        args_list = []
        if len(t.children) > 0:
            for arg in t.children[0].children:
                args_list.append(
                    self._exec(arg)
                )

        obj = self._load(t)

        # Because class instantiation looks like a function call, handle that here 
        # Well, it IS a function call, but it's a special case of one, where we call a constructor
        # if it is defined 

        # So, look up the instance, or create it if it does not yet exist.
        # Retrieve the class instance and method, push class instance as scope, call method 

        class_instance, constructor = None, None
        if type(obj) is PG_Class:
            # If the retrieved object is the class definition object, then we are creating a new instance
            if obj.is_class_def: 
                class_instance, constructor = self._class_instantiation(
                    class_def=obj, 
                    args_list=args_list
                )
            else:
                # If instance is NOT class def
                pass

        func = obj if constructor is None else constructor 

        args_len = len(args_list)
        params_len = len(func.params)
        if args_len < params_len:
            raise TypeError(f"{name}() called, but {params_len - args_len} parameters were missing")
    
        if args_len > params_len:
            raise TypeError(f"Function {name} called, but too many parameters were given")
        
        # If calling a constructor, push the class as a scope first
        if constructor != None and class_instance != None:
            self._push_scope(
                name="", 
                scope_to_use=class_instance
            )

        self._push_scope(name=f"func_scope_{name}")

        for param, arg in zip(func.params, args_list):
            self.current_space.symbols[param] = arg

        # Don't try to "call" a constructor if none defined on class
        if not (class_instance != None and constructor is None and args_len == 0):
            self._statements(func.code)

        self._pop_scope()

        # If a constructor was called, remove the class scope from the tree
        if constructor != None and class_instance != None:
            self._pop_scope()

        if class_instance != None:
            return class_instance

    def _class_def(self, t: PG_AST):
        # Create PG_Class object 
        name = t.children[0].token.text
        class_def = PG_Class(name=name, is_class_def=True)
        # Iterate through the statements:
        for statement in t.children[1].children:
            # Fill in attrs
            stmnt_tk_type = statement.token.type
            if stmnt_tk_type in { PGT.ASSIGN, PGT.NAME }:
                if stmnt_tk_type == PGT.ASSIGN:
                    attr_name = statement.children[0].token.text
                    rhs = statement.children[1]
                    class_def.symbols[attr_name] = self._exec(rhs)

                elif stmnt_tk_type == PGT.NAME:
                    stmnt_text = statement.token.text
                    class_def.symbols[stmnt_text] = None

            # Create func objects to put in methods
            elif stmnt_tk_type is PGT.DEF:
                func_name    = statement.children[0].token.text
                class_method = self._func_def(statement)
                params_len   = len(class_method.params)
                class_def.methods[func_name][params_len] = class_method
            else:
                self._exec(statement)
        
        # Place class object into current scope/symbol table 
        self.current_space.symbols[name] = class_def

    def _class_instantiation(self, class_def: PG_Class, args_list):
        # Lookup in the class def, a function that shares the name of the
        # class, and has the same number of parameters as the called constructor
        # That will be the correct constructor to call.
        new_instance = deepcopy(class_def)
        
        # Based on the length of the args list, select the correct constructor 
        # If a constructor does not exist for the length, raise an exception
        # However, if the length is zero, and there is no constructor that takes zero args,
        # DO NOT raise an exception. Simply init any attrs that don't get assigned a value to None
        args_len = len(args_list)
        name = new_instance.name
        constructor = None
        constructors = new_instance.methods.get(name)

        # If there is at least one constructor defined, retrieve it
        # but only if it has the correct number of params
        if constructors != None:
            constructor = constructors.get(args_len)
            
        return new_instance, constructor

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

        # Handle assigning a value to dotted expressions:
        name, instance_name = None, None
        if lhs.token.type is PGT.DOT:
            instance_name = lhs.children[0].token.text 
            name = lhs.children[1].token.text 

        # Normal assignment 
        else:
            name = lhs.token.text

        # Get the scope where the symbol was originally defined
        # For class attributes, this will be a class object  
        symbol_scope = None 

        if instance_name is None:
            symbol_scope = self.current_space.resolve_scope(name)
        else:
            symbol_scope = self._load(lhs.children[0])

        # If none, symbol has not yet been defined
        if symbol_scope is None:    
            symbol_scope = self.current_space

        # Assign symbol it's new value 
        symbol_scope.symbols[name] = value

    def _load(self, t: PG_AST):
        """ 
            Returns the value or object referenced by the symbol in 't',
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

        if   token_type is PGT.PLUS:    return a + b
        elif token_type is PGT.MINUS:   return a - b
        elif token_type is PGT.STAR:    return a * b
        elif token_type is PGT.FSLASH:  return a / b

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

        if   token_type is PGT.EQ:  return a == b
        elif token_type is PGT.LT:  return a < b
        elif token_type is PGT.LE:  return a <= b
        elif token_type is PGT.GT:  return a > b
        elif token_type is PGT.GE:  return a >= b

if __name__ == "__main__":
    code = """
        print(10 < True);
        if(True and True){print(True);}
        if(True or True){print(True);}
        if(False or True){print(True);}
        if(True){print(True);} 
        print((True and True));
        a = 5;b = 5; print(a + b);

        print(5 - 2); print(5 * 2); print(5 / 2);

        a = 5 / 2; print(a + 3); foo = 3 * 5;
        print(foo + (a * (3  -  4)));
        print(3 - 4); print(2.4 + 1.3);

        a = 2; b = 3; c = 2;
        { c = 1; print(c); } print(c);

        if (5 < 6){ print("5 is less than 6"); }
        elif (6 > 3){ print("6 is greater than 3"); }
        print("Printing 10 through 1 in decreasing order");
        a = 10;
        while (a > 0) { print(a); a = a - 1; }
        print("A test string");

        a = "String stored in a"; print(a);

        a = 5; b = 3; c = 2;
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

        foo(5, 6, 7); { foo(3, 1, 2); }

        def outer(outA){
            def inner(inA){
                print("Inner a: ", inA);
            }
            inner(10);
            print("outer a: ", outA);
        }
        outer(15);
    
    Class FooClass {
        class_attr_a = 5;
        class_attr_b; 

        def FooClass(){
            print("Empty constructor!");
            print("class_attr_b: ", class_attr_b);
            print("class_attr_a: ", class_attr_a);
        }

        def FooClass(a){
            print("Constructor called! I have one arg!");
            print("Assign a to 'class_attr_a' !");
            print("class_attr_a before: ", class_attr_a);
            class_attr_a = a;
            print("class_attr_a: ", class_attr_a);
        }

        def NotAConstructor(){
            print("I don't have any params, and I'm not a constructor");
            print("here's class_attr_a: ", class_attr_a);
        }

        def another_normal_class_method_with_params(a, b, c){
            print("I have 3 params, a, b, c");
        }
    }
    instance_foo = FooClass(10);
    instance_foo = FooClass();
    instance_foo.NotAConstructor();
    print("Accessing class attr outside the class: ", instance_foo.class_attr_a);
    instance_foo.class_attr_a = 10;
    print("After changing it: ", instance_foo.class_attr_a);
    
    """
    PI = PlaygroundInterpreter()
    PI.interp(input_str=code)