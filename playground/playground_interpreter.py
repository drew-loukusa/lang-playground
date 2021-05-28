import sys
from os import path
from copy import deepcopy

from playground_ast import PG_AST
from playground_token import PG_Type as PGT, PG_Token
from playground_parser import PlaygroundParser
from playground_scope import PG_Scope, PG_Function, PG_Class


class UnsupportedOperationException(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)


class PlaygroundInterpreter:
    def __init__(self):
        self.globals = PG_Scope(name="globals")
        self.current_space = self.globals
        self.root = None
        self.parser = None

        self.operators = {PGT.PLUS, PGT.MINUS, PGT.STAR, PGT.FSLASH, PGT.PERCENT}

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

        self.booleans = {PGT.TRUE, PGT.FALSE}

    def _push_scope(self, name="", scope_to_use=None):
        """
        Creates a new scope (if one was not passed in via 'scope_to_use'),
        places new scope in child list of the current scope, and then sets
        the current scope to the new scope.

        Returns None
        """
        new_scope = PG_Scope(name=name) if scope_to_use is None else scope_to_use
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
        return (
            token_type == PGT.NAME
            and len(t.children) > 0
            and t.children[0].name == "$ARG_LIST"
        )

    def _get_enclosing_class(self):
        scope = self.current_space 
        while type(scope) != PG_Class and scope != None:
            scope = scope.parent
        return scope

    def _exec(self, t: PG_AST):
        """
        Executes node 't' according to it's token type.

        May return an INT, a FLOAT, or a BOOL
        """
        try:
            token_type = t.token.type if t.token != None else None

            if t.artificial == True and t.name == "$STATEMENTS":
                self._statements(t)
            
            elif token_type is PGT.IMPORT:
                self._import(t)

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

            elif token_type is PGT.RETURN:
                return self._return(t)

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
                raise UnsupportedOperationException(
                    f"Node {t.name}: <{t.token}> not handled"
                )

        except UnsupportedOperationException as e:
            print("Problem executing", t.to_string_tree(), e)
        return None

    def _program(self, t: PG_AST):
        """
        Executes the program.

        returns None
        """
        self._statements(t, push_scope=False)

    def _statements(self, t: PG_AST, push_scope=True):
        """
        Executes nested statements;
        This is what is called to handle "block" statements.

        Returns None
        """
        if push_scope:
            self._push_scope()

        ret_val = None
        for statement in t.children:
            ret_val = self._exec(statement)
        
        if push_scope:
            self._pop_scope()
            
        return ret_val

    def _import(self, t: PG_AST):
        cwd = sys.path[0]
        module_name = t.children[0].token.text
        cur_path = path.join(cwd, module_name)
        module_text = open(cur_path, mode='r').read()
        import_parser = PlaygroundParser(input_str=module_text)

        import_root = import_parser.program()
        if import_root != None:
           self._program(import_root)

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
                print(self._exec(arg), end="")
            print()
        else:
            print()

    def _dotted_expr(self, t: PG_AST):
        lhs = t.children[0]
        rhs = t.children[1]

        instance = self._load(lhs) if lhs.token.text != "this" else None

        rhs_tk_type = rhs.token.type
        rhs_child_len = len(rhs.children)
        # Dotted function call
        if self.is_function_call(rhs):
            self._push_scope(name="", scope_to_use=instance)
            result = self._func_call(rhs)
            self._pop_scope()
            return result

        # Dotted field access
        elif rhs_tk_type is PGT.NAME:
            self._push_scope(name="", scope_to_use=instance)
            result = None 
            if instance != None:
                result = self._load(rhs)
            else:
                result = self._load(rhs, this=True)

            self._pop_scope()
            return result

    def _func_def(self, t: PG_AST, add_to_current_scope=True):
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
        if add_to_current_scope:
            if name not in self.current_space.symbols:
                self.current_space.symbols[name] = {}
            self.current_space.symbols[name][len(params)] = new_func
        return new_func

    def _py_str(self, obj):
        return str(obj)

    def _func_call(self, t: PG_AST):
        """
        Executes a function call.
        Loads the previously created function object (which holds the definition
        for the function) and uses it to execute the function.

        The function object holds the function name, function parameters, 
        and function code (as a PG_AST sub-tree)

        May return a value or a class instance, by default returns None 
        """
        name = t.token.text
        args_list = []
        if len(t.children) > 0:
            for arg in t.children[0].children:
                args_list.append(self._exec(arg))
        args_len = len(args_list)

        if name == 'str':
            if len(args_list) != 1:
                raise TypeError("built in str() only takes 1 argument")
            return self._py_str(args_list[0])

        # Because class instantiation looks like a function call, handle that here
        # Well, it IS a function call, but it's a special case of one, where we call a constructor
        # if it is defined
        obj = self._load(t)
        enclosing_class = self._get_enclosing_class()
        if type(obj) == PG_Class or (
            enclosing_class != None 
            and enclosing_class.name == name 
        ):
            interior_call = (
                type(obj) != PG_Class 
                and self._get_enclosing_class().name == name
            )
            return self._class_instantiation(
                t, 
                args_list=args_list,
                interior_call=interior_call
            )
        
        # Maybe, check here, if enclosing scope is a class?
        # Then, use it's methods dict to get the func object
        # Yeah. Make sure to delete the comment in _load

        func_dict = obj 
        func = func_dict.get(args_len) 

        if func is None:
            raise TypeError(
                f"No function with name {name} and param length {args_len} found!"
            )

        self._push_scope(name=f"func_scope_{name}")

        for param, arg in zip(func.params, args_list):
            self.current_space.symbols[param] = arg

        ret_val = self._statements(func.code)
        self._pop_scope()

        return ret_val

    def _return(self, t: PG_AST):
        expr = t.children[0]
        return self._exec(expr)

    def _class_def(self, t: PG_AST):
        # Create PG_Class object
        name = t.children[0].token.text
        class_def = PG_Class(name=name, is_class_def=True)
        # Iterate through the statements:
        for statement in t.children[1].children:
            # Fill in attrs
            stmnt_tk_type = statement.token.type
            if stmnt_tk_type in {PGT.ASSIGN, PGT.NAME}:
                if stmnt_tk_type == PGT.ASSIGN:
                    attr_name = statement.children[0].token.text
                    rhs = statement.children[1]
                    class_def.symbols[attr_name] = self._exec(rhs)

                elif stmnt_tk_type == PGT.NAME:
                    stmnt_text = statement.token.text
                    class_def.symbols[stmnt_text] = None

            # Create func objects to put in methods
            elif stmnt_tk_type is PGT.DEF:
                func_name = statement.children[0].token.text
                class_method = self._func_def(
                    statement,
                    add_to_current_scope=False,
                )
                params_len = len(class_method.params)
                if func_name not in class_def.symbols:
                    class_def.symbols[func_name] = {}
                class_def.symbols[func_name][params_len] = class_method
            else:
                self._exec(statement)

        # Place class object into current scope/symbol table
        self.current_space.symbols[name] = class_def

    def _class_instantiation(self, t: PG_AST ,args_list, interior_call=False):
        
        obj = self._load(t)
        class_def = obj
        args_len = len(args_list)

        # Check if we are being called from inside the same class
        # If so, _load() will resolve t to a constructor, when we 
        # need the class def object, so get that instead 
        if interior_call:
            class_name = obj[args_len].name
            class_def = self.globals.resolve(class_name)

        constructors = class_def.methods[class_def.name]

        # Lookup in the class def, a function that shares the name of the
        # class, and has the same number of parameters as the called constructor
        # That will be the correct constructor to call.
        constructor = constructors.get(args_len)

        # Create a new copy of the class, and mark it as a copy of the definition
        # aka, an instance of said class
        new_instance = deepcopy(class_def)
        new_instance.is_class_def = False

        # If calling a constructor, push the new instance as a scope first
        if constructor != None:
            self._push_scope(
                name=f"instance_of_{class_def.name}", 
                scope_to_use=new_instance
            )

        # Don't try to "call" a constructor if none defined on class
        # or if no constructor was selected 
        if len(constructors) > 0 and constructor != None:
            for param, arg in zip(constructor.params, args_list):
                self.current_space.symbols[param] = arg

            self._statements(constructor.code)

        # If a constructor was called, remove the class scope from the tree
        if constructor != None:
            self._pop_scope()

        return new_instance

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
        elif instance_name == "this":
            symbol_scope = self._get_enclosing_class()
            if symbol_scope is None:
                raise UnsupportedOperationException(
                    "Use of keyword 'this' only supported inside of class methods."
                )
        else:
            symbol_scope = self._load(lhs.children[0])

        # If none, symbol has not yet been defined
        if symbol_scope is None:
            symbol_scope = self.current_space

        # Assign symbol it's new value
        symbol_scope.symbols[name] = value
    
    def _load_from_name(self, name):
        token = PG_Token(token_type=PGT.NAME, token_text=name)
        node = PG_AST(token=token)
        return self._load(node)

    def _load(self, t: PG_AST, this=False):
        """
        Returns the value or object referenced by the symbol in 't',
        if it exists in the current scope, or any parent scopes.

        If t.token.text == 'this', then function goes up scope tree until it 
        finds a Class object, which it then returns.
        """
        name = t.token.text
        symbol_scope = self.current_space 
        if this:
            symbol_scope = self._get_enclosing_class()
            if symbol_scope is None:
                raise UnsupportedOperationException(
                    "Use of keyword 'this' only supported inside of class methods."
                )
        return symbol_scope.resolve(name)

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
        a = self._exec(t.children[0])
        b = self._exec(t.children[1])

        if   token_type is PGT.PLUS:    return a + b
        elif token_type is PGT.MINUS:   return a - b
        elif token_type is PGT.STAR:    return a * b
        elif token_type is PGT.FSLASH:  return a / b
        elif token_type is PGT.PERCENT: return a % b

    def _and(self, t: PG_AST):
        """
        Performs an AND operation.
        The operands of the operation are the
        left and right sub-trees of PG_AST node 't'.

        Returns Python BOOL
        """
        token_type = t.token.type
        a = self._exec(t.children[0])

        # Short circuit the AND
        if a == False:
            return False

        else:
            b = self._exec(t.children[1])
            return b == True

    def _or(self, t: PG_AST):
        """
        Performs an OR operation.
        The operands of the operation are the
        left and right sub-trees of PG_AST node 't'.

        Returns Python BOOL
        """
        token_type = t.token.type
        a = self._exec(t.children[0])

        # Short Circuit 'or' statement
        if a == True:
            return True

        else:
            b = self._exec(t.children[1])
            return b == True

    def _cmp(self, t: PG_AST):
        """
        Performs a comparison operation.
        The operands of the operation are the
        left and right sub-trees of PG_AST node 't'.

        Returns Python BOOL
        """
        token_type = t.token.type
        a = self._exec(t.children[0])
        b = self._exec(t.children[1])

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
    """
    code = """
    Class FooClass {
        class_attr_a = 5;
        class_attr_b; 
        bar = 1;

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

        def func_with_shadowing_param(bar){
            bar = 12;
            print("shadowing func param bar is: ", bar);
            print("Printing shadowed class attr using keyword 'this': ", this.bar);
            print("Set shadowed class attr bar to 15");
            this.bar = 15;
        }
    }
    instance_foo = FooClass(10);
    instance_foo = FooClass();
    instance_foo.NotAConstructor();
    print("Accessing class attr outside the class: ", instance_foo.class_attr_a);
    instance_foo.class_attr_a = 10;
    print("After changing it: ", instance_foo.class_attr_a);
    print("instance_foo.bar: ", instance_foo.bar);
    instance_foo.func_with_shadowing_param(5);
    print("instance_foo.bar: ", instance_foo.bar);
    print("5 % 3 == ", 5 % 3);


    def add(a, b){
        return a + b;
    }

    print("Adding 5 and 10 via a func: ", add(5, 10));
    print(add);
    alias_for_add = add;
    print(alias_for_add);
    print(alias_for_add(10, 52));
    """
    code = """
    def foo(){
        print("foo called");
    }
    foo();
    import "..\\examples\\ex_module_Point.plgd";

    k = Point(10, 10);
    f = Point(20, 5);
    print("point k: ", k.to_str());
    print("point f: ", f.to_str());

    k.Add(f);
    p = k.Add(f);
    print("k + f = ", p.to_str());
    """
    PI = PlaygroundInterpreter()
    PI.interp(input_str=code)
