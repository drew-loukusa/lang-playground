from playground_ast import PG_AST
from playground_token import PG_Type
from playground_parser import PlaygroundParser

class UnsupportedOperationException(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)

class PlaygroundInterpreter:

    def __init__(self):
        self.globals = dict()
        self.current_space = self.globals
        self.root = None
        self.parser = None 
   
    def interp(self, input_str):
        self.parser = PlaygroundParser(input_str=input_str)

        self.root = self.parser.program()
        if self.root != None: 
            self.program(self.root)

    def exec(self, t: PG_AST):
        try:
            token_type = t.token.type
            if token_type == PG_Type.PRINT:     self.pg_print(t) 
            elif token_type == PG_Type.EQUAL:   self.assign(t)
            elif token_type == PG_Type.PLUS:    return self.op(t)
            elif token_type == PG_Type.MINUS:   return self.op(t)
            elif token_type == PG_Type.STAR:    return self.op(t)
            elif token_type == PG_Type.FSLASH:  return self.op(t)
            elif token_type == PG_Type.NAME:    return self.load(t)
            elif token_type == PG_Type.NUMBER:  return int(t.token.text)
            else:
                raise UnsupportedOperationException(f"Node {t.name}: <{t.token}> not handled")
          
        except UnsupportedOperationException as e:
            print("Problem executing", t.to_string_tree(), e)
        return None 
    
    def program(self, t):
        for statement in t.children:
            self.exec(statement)

    def pg_print(self, t):
        expr = t.children[0]
        print( self.exec(expr) )
    
    def assign(self, t):
        lhs = t.children[0]
        expr = t.children[1]
        value = self.exec(expr)
        self.globals[lhs.token.text] = value 

    def load(self, t):
        # Since Playground currently utilizes global scope, and does not 
        # support forward references, loading variables is fairly easy.
        # Simply retrive the needed variable from the "globals" dict 

        # If this experiment is continued, and nested scoping is to be added,
        # additional behavior will need to be added here (and many other places)
        return self.globals[t.token.text]
    
    def op(self, t): 
        token_type = t.token.type 
        a = self.exec( t.children[0] )
        b = self.exec( t.children[1] )

        if   token_type == PG_Type.PLUS:    return a + b 
        elif token_type == PG_Type.MINUS:   return a - b 
        elif token_type == PG_Type.STAR:    return a * b 
        elif token_type == PG_Type.FSLASH:  return a / b

if __name__ == "__main__":
    code = """
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
"""
    PI = PlaygroundInterpreter()
    PI.interp(input_str=code)